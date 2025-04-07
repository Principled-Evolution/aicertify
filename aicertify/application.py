"""
AICertify Application Module

This module provides a simple interface for creating and evaluating AI applications
against a set of regulations.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from uuid import uuid4

from aicertify.models.contract import AiCertifyContract, ModelInfo, Interaction
from aicertify.regulations import RegulationSet
from aicertify.api import aicertify_app_for_policy
from aicertify.utils.logging_config import (
    get_logger,
    info,
    success,
    warning,
    error,
    debug,
)

logger = get_logger(__name__)


class Application:
    """
    Represents an AI application that can be evaluated against various regulations.

    This class encapsulates the functionality to create, configure, and evaluate
    an AI application, and to generate reports about its compliance with regulations.
    """

    def __init__(
        self,
        name: str,
        model_name: str = "Unknown Model",
        model_version: Optional[str] = None,
        model_metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a new application.

        Args:
            name: Name of the application
            model_name: Name of the AI model
            model_version: Version of the AI model
            model_metadata: Additional metadata about the model
        """
        self.name = name
        self.model_name = model_name
        self.model_version = model_version
        self.model_metadata = model_metadata or {}

        # Create model info and contract
        self.model_info = ModelInfo(
            model_name=model_name,
            model_version=model_version,
            metadata=self.model_metadata,
        )

        self.contract = AiCertifyContract(
            contract_id=uuid4(),
            application_name=name,
            model_info=self.model_info,
            interactions=[],
        )

        self.evaluation_results = {}
        self.report_paths = {}

    def add_interaction(
        self,
        input_text: str,
        output_text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Add a single interaction to the application.

        Args:
            input_text: The user input or prompt
            output_text: The AI model's response
            metadata: Additional metadata about the interaction
        """
        interaction = Interaction(
            input_text=input_text, output_text=output_text, metadata=metadata or {}
        )
        self.contract.interactions.append(interaction)
        debug(
            f"Added interaction {len(self.contract.interactions)} to application '{self.name}'",
            category="INTERACTION",
            logger=logger,
        )

    def add_interactions(self, interactions: List[Dict[str, Any]]) -> None:
        """
        Add multiple interactions to the application.

        Args:
            interactions: List of dictionaries containing 'input_text', 'output_text',
                         and optional 'metadata' fields
        """
        for interaction_data in interactions:
            self.add_interaction(
                input_text=interaction_data["input_text"],
                output_text=interaction_data["output_text"],
                metadata=interaction_data.get("metadata", {}),
            )
        info(
            f"Added {len(interactions)} interactions to application '{self.name}'",
            category="INTERACTION",
            logger=logger,
        )

    def save_contract(self, output_dir: str = "contracts") -> str:
        """
        Save the contract to a file.

        Args:
            output_dir: Directory to save the contract

        Returns:
            Path to the saved contract file
        """
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.name.replace(' ', '_')}_{timestamp}.json"
        file_path = os.path.join(output_dir, filename)

        # Save contract
        with open(file_path, "w") as f:
            json.dump(self.contract.dict(), f, indent=2, default=str)

        info(f"Saved contract to {file_path}", category="FILE", logger=logger)
        return file_path

    async def evaluate(
        self,
        regulations: RegulationSet,
        generate_report: bool = True,
        report_format: str = "markdown",
        output_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate the application against a set of regulations.

        Args:
            regulations: Set of regulations to evaluate against
            generate_report: Whether to generate a report
            report_format: Format of the report ('markdown', 'pdf', 'json')
            output_dir: Directory to save the report

        Returns:
            Dictionary containing evaluation results
        """
        results = {}

        if not self.contract.interactions:
            warning(
                f"No interactions in application '{self.name}'. Evaluation may be incomplete.",
                category="APPLICATION",
                logger=logger,
            )

        # If no output directory specified, create one
        if output_dir is None:
            output_dir = "reports"

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Evaluate against each regulation
        for policy_folder in regulations.get_regulations():
            # Extract regulation name from folder path
            regulation_name = policy_folder.split("/")[-1]

            info(
                f"Evaluating application '{self.name}' against regulation '{regulation_name}'",
                category="EVALUATION",
                logger=logger,
            )

            try:
                # Evaluate the contract against the regulation
                result = await aicertify_app_for_policy(
                    contract=self.contract,
                    policy_folder=policy_folder,
                    generate_report=generate_report,
                    report_format=report_format,
                    output_dir=output_dir,
                )

                # Store results
                results[regulation_name] = result

                # Store report path if available
                if "report_path" in result:
                    self.report_paths[regulation_name] = result["report_path"]

                success(
                    f"Completed evaluation against '{regulation_name}'",
                    category="EVALUATION",
                    logger=logger,
                )

            except Exception as e:
                error(
                    f"Error evaluating against '{regulation_name}': {e}",
                    category="EVALUATION",
                    logger=logger,
                )
                results[regulation_name] = {"error": str(e)}

        # Store evaluation results
        self.evaluation_results = results

        return results

    def get_report(
        self, regulation_name: Optional[str] = None
    ) -> Union[str, Dict[str, str]]:
        """
        Get the path to the evaluation report for a specific regulation or all regulations.

        Args:
            regulation_name: Name of the regulation to get the report for, or None for all

        Returns:
            Path to the report file, or dictionary mapping regulation names to report paths
        """
        if regulation_name:
            if regulation_name in self.report_paths:
                return self.report_paths[regulation_name]
            else:
                warning(
                    f"No report found for regulation '{regulation_name}'",
                    category="REPORT",
                    logger=logger,
                )
                return ""
        else:
            return self.report_paths


def create(
    name: str,
    model_name: str = "Unknown Model",
    model_version: Optional[str] = None,
    model_metadata: Optional[Dict[str, Any]] = None,
) -> Application:
    """
    Create a new application.

    Args:
        name: Name of the application
        model_name: Name of the AI model
        model_version: Version of the AI model
        model_metadata: Additional metadata about the model

    Returns:
        A new Application instance
    """
    return Application(
        name=name,
        model_name=model_name,
        model_version=model_version,
        model_metadata=model_metadata,
    )
