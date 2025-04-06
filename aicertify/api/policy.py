"""
AICertify API Policy Module

This module provides functions for evaluating AI contracts against OPA policies.
"""

import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime


# Import models
from aicertify.models.contract_models import AiCertifyContract

# Import core utilities
from aicertify.api.core import CustomJSONEncoder

# Import OPA components
from aicertify.opa_core.policy_loader import PolicyLoader
from aicertify.opa_core.evaluator import OpaEvaluator

# Import evaluators
from aicertify.evaluators import ComplianceEvaluator

# Configure logging
logger = logging.getLogger(__name__)
# Create instances of key components for API functions
debug_mode = os.environ.get("OPA_DEBUG", "0") == "1"
opa_evaluator = OpaEvaluator(
    use_external_server=False,  # Force local evaluator
    server_url=os.environ.get("OPA_SERVER_URL", "http://localhost:8181"),
    debug=debug_mode,
    skip_opa_check=os.environ.get("CI", "false").lower() in ("1", "true", "yes"),  # Skip OPA check in CI environments
)
policy_loader = PolicyLoader()


async def aicertify_app_for_policy(
    contract: AiCertifyContract,
    policy_folder: str,
    custom_params: Optional[Dict[str, Any]] = None,
    generate_report: bool = True,
    report_format: str = "markdown",
    output_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Evaluate contract interactions for a specific policy.

    Args:
        contract: The AiCertifyContract object to evaluate
        policy_folder: The folder containing the policy to evaluate against
        custom_params: Optional custom parameters to pass to the OPA evaluator
        generate_report: Whether to generate a report
        report_format: Format of the report (json, markdown, pdf)
        output_dir: Directory to save the report

    Returns:
        Dictionary containing evaluation results and report paths
    """
    logger.info(
        f"Evaluating contract {contract.contract_id} for policy {policy_folder}"
    )

    # Create a simple evaluator result for OPA
    evaluation_result = {
        "contract_id": str(contract.contract_id),
        "application_name": contract.application_name,
        "interaction_count": len(contract.interactions),
    }

    # Find OPA policy folder
    opa_evaluator = OpaEvaluator()
    matching_folders = opa_evaluator.find_matching_policy_folders(policy_folder)
    if not matching_folders:
        logger.warning(f"No matching policy folders found for: {policy_folder}")
        return {"error": f"No matching policy folders found for: {policy_folder}"}

    # Get policies from the matching folder
    logger.info(f"Getting policies from folder: {matching_folders[0]}")
    policies = opa_evaluator.policy_loader.get_policies_by_folder(matching_folders[0])
    if not policies:
        logger.warning(f"No policies found in folder {matching_folders[0]}")
        return {"error": f"No policies found in folder {matching_folders[0]}"}

    # get metrics for policy folder
    metrics = opa_evaluator.policy_loader.get_required_metrics_for_folder(
        matching_folders[0]
    )
    logger.info(f"Required metrics for folder: {metrics}")

    # discover evaluators from evaluator registry that support the metrics
    from aicertify.evaluators.evaluator_registry import get_default_registry

    evaluator_registry = get_default_registry()
    evaluators = evaluator_registry.discover_evaluators(metrics)

    # Debug evaluators mapping
    evaluator_names = [
        evaluator.__name__ for evaluator in evaluators if hasattr(evaluator, "__name__")
    ]
    logger.info(f"Discovered evaluator classes: {evaluator_names}")

    # Convert evaluator classes to names for evaluate_contract_with_phase1_evaluators
    # The function expects string names, not class objects
    evaluator_names_from_mapping = {
        name
        for name, cls in ComplianceEvaluator.EVALUATOR_CLASSES.items()
        if cls in evaluators
    }
    logger.info(f"Converted evaluator classes to names: {evaluator_names_from_mapping}")

    # Run Phase 1 evaluators, relying on default configurations from evaluator classes
    from aicertify.api.evaluators import evaluate_contract_with_phase1_evaluators

    phase1_results = await evaluate_contract_with_phase1_evaluators(
        contract=contract,
        evaluators=(
            list(evaluator_names_from_mapping) if evaluator_names_from_mapping else None
        ),
        # No explicit evaluator_config provided - will use defaults from evaluator classes
        generate_report=False,
    )

    # evaluate with OPA
    opa_results = opa_evaluator.evaluate_policy_category(
        policy_category=policy_folder,
        input_data=phase1_results,
        custom_params=custom_params,
    )

    # Generate combined report if requested
    report_path = None
    if generate_report:
        if output_dir:
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)

            # Generate filename
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            if report_format == "json":
                filename = f"folder_report_{contract.application_name}_{timestamp}.json"
            elif report_format == "markdown":
                filename = f"folder_report_{contract.application_name}_{timestamp}.md"
            elif report_format == "pdf":
                filename = f"folder_report_{contract.application_name}_{timestamp}.pdf"
            elif report_format == "html":
                filename = f"folder_report_{contract.application_name}_{timestamp}.html"
            else:
                filename = f"folder_report_{contract.application_name}_{timestamp}.txt"

            # Generate report data based on the requested format
            if report_format.lower() == "json":
                # For JSON format, include the complete evaluation results with all metrics
                report_data = {
                    "evaluation_result": phase1_results,  # Use the full evaluator results with all metrics
                    "opa_results": opa_results,
                }
            else:
                from aicertify.report_generation.report_generator import (
                    ReportGenerator,
                    create_report_data,
                )
                from aicertify.report_generation.data_extraction import (
                    create_evaluation_report,
                )

                report_gen = ReportGenerator()
                report_data = create_evaluation_report(
                    eval_result=evaluation_result, opa_results=opa_results
                )

            # Generate and write the report file based on the format
            if report_format.lower() == "markdown":
                report_content = report_gen.generate_markdown_report(report_data)
                report_path = os.path.join(output_dir, filename)
                abs_path = os.path.abspath(report_path)
                with open(report_path, "w") as f:
                    f.write(report_content)
                logger.info(
                    f"\033[32m📄 Report generated at: \033]8;;file://{abs_path}\033\\{abs_path}\033]8;;\033\\\033[0m"
                )
                logger.info(f'   To open in VS Code: code "{abs_path}"')
                logger.info(f'   To open in nano: nano "{abs_path}"')
            elif report_format.lower() == "pdf":
                md_content = report_gen.generate_markdown_report(report_data)
                pdf_path = os.path.join(
                    output_dir, f"report_{contract.application_name}_{timestamp}.pdf"
                )
                report_gen.generate_pdf_report(md_content, pdf_path)
                report_path = pdf_path
                abs_path = os.path.abspath(report_path)
                logger.info(
                    f"\033[32m📊 PDF Report generated at: \033]8;;file://{abs_path}\033\\{abs_path}\033]8;;\033\\\033[0m"
                )
            elif report_format.lower() == "html":
                # Create HTML report data
                html_report_data = create_report_data(report_data)
                report_path = os.path.join(output_dir, filename)
                abs_path = os.path.abspath(report_path)
                # store the policy requested by the user as the regulations assessed
                html_report_data["REGULATIONS_LIST"] = [policy_folder]

                # Generate HTML report
                if report_gen.generate_html_report(html_report_data, report_path):
                    abs_path = str(Path(report_path).resolve())
                    file_url = f"file://{abs_path}"
                    logger.info(
                        f"\033[32m🌐 HTML Report generated at: {abs_path}\033[0m"
                    )

                    # Check if running in WSL
                    if "microsoft" in Path("/proc/version").read_text().lower():
                        # In WSL, suggest using Windows browser
                        windows_path = (
                            subprocess.check_output(["wslpath", "-w", abs_path])
                            .decode()
                            .strip()
                        )
                        logger.info(
                            f"\033[32m📂 To view in Windows browser: {windows_path}\033[0m"
                        )
                    else:
                        # For native Linux, try xdg-open but handle failure gracefully
                        try:
                            subprocess.run(
                                ["xdg-open", file_url], check=True, capture_output=True
                            )
                            logger.info(
                                "\033[32m🌐 Report opened in default browser\033[0m"
                            )
                        except subprocess.CalledProcessError:
                            logger.info(
                                f"\033[33mℹ️  To view the report manually:\033[0m"
                            )
                            logger.info(
                                f"\033[33m   - Linux: xdg-open '{abs_path}'\033[0m"
                            )
                            logger.info(
                                f"\033[33m   - Windows: start '{abs_path}'\033[0m"
                            )
                            logger.info(
                                f"\033[33m   - Or open the file directly in your preferred browser\033[0m"
                            )
            elif report_format.lower() == "json":
                report_path = os.path.join(output_dir, filename)
                abs_path = os.path.abspath(report_path)
                with open(report_path, "w") as f:
                    json.dump(report_data, f, indent=2, cls=CustomJSONEncoder)
                logger.info(
                    f"\033[32m🔍 JSON Report generated at: \033]8;;file://{abs_path}\033\\{abs_path}\033]8;;\033\\\033[0m"
                )
                logger.info(f'   To open in VS Code: code "{abs_path}"')
                logger.info(f'   To open in nano: nano "{abs_path}"')
            else:
                # Fallback: generate as markdown
                report_content = report_gen.generate_markdown_report(report_data)

    # Return results
    return {
        "phase1_results": phase1_results,
        "opa_results": opa_results,
        "report_path": report_path,
        "contract_id": str(contract.contract_id),
        "application_name": contract.application_name,
    }


async def evaluate_by_policy(
    contract: Union[str, AiCertifyContract, Dict[str, Any]],
    policy_folder: str,
    evaluators: Optional[List[str]] = None,
    evaluator_config: Optional[Dict[str, Any]] = None,
    custom_params: Optional[Dict[str, Any]] = None,
    generate_report: bool = True,
    report_format: str = "markdown",
    output_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Evaluate a contract against a specific policy folder.

    Args:
        contract: Contract to evaluate (file path, contract object, or dictionary)
        policy_folder: Policy folder to evaluate against
        evaluators: Optional list of specific evaluators to use
        evaluator_config: Optional configuration for evaluators
        custom_params: Optional custom parameters for policy evaluation
        generate_report: Whether to generate a report
        report_format: Format of the report
        output_dir: Directory to save the report

    Returns:
        Dictionary containing evaluation results and report paths
    """
    # Handle different input types
    from aicertify.models.contract_models import load_contract

    contract_obj = None
    if isinstance(contract, str):
        # Assume it's a file path
        contract_obj = load_contract(contract)
    elif isinstance(contract, AiCertifyContract):
        # Already a contract object
        contract_obj = contract
    elif isinstance(contract, dict):
        # Convert dictionary to contract object
        contract_obj = AiCertifyContract.parse_obj(contract)
    else:
        raise ValueError(f"Unsupported contract type: {type(contract)}")

    # Use aicertify_app_for_policy with the contract object
    return await aicertify_app_for_policy(
        contract=contract_obj,
        policy_folder=policy_folder,
        custom_params=custom_params,
        generate_report=generate_report,
        report_format=report_format,
        output_dir=output_dir,
    )
