"""
AICertify Compliance Evaluator

This module provides the ComplianceEvaluator class that combines multiple evaluators
to perform comprehensive compliance evaluations.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
import json
from datetime import datetime
import inspect

from aicertify.evaluators.base_evaluator import BaseEvaluator, EvaluationResult, Report
from aicertify.evaluators.fairness_evaluator import FairnessEvaluator
from aicertify.evaluators.content_safety_evaluator import ContentSafetyEvaluator
from aicertify.evaluators.risk_management_evaluator import RiskManagementEvaluator
from aicertify.evaluators.accuracy_evaluator import AccuracyEvaluator
from aicertify.evaluators.biometric_categorization_evaluator import (
    BiometricCategorizationEvaluator,
)
from aicertify.evaluators.prohibited_practices import (
    ManipulationEvaluator,
    VulnerabilityExploitationEvaluator,
    SocialScoringEvaluator,
    EmotionRecognitionEvaluator,
)
from aicertify.evaluators.documentation import ModelCardEvaluator

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class EvaluatorConfig:
    """Configuration container for evaluators."""

    def __init__(self, **kwargs):
        """Initialize configuration with optional evaluator-specific configs."""
        self.fairness = kwargs.get("fairness", {})
        self.content_safety = kwargs.get("content_safety", {})
        self.risk_management = kwargs.get("risk_management", {})
        self.accuracy = kwargs.get("accuracy", {})
        self.biometric_categorization = kwargs.get("biometric_categorization", {})
        self.manipulation = kwargs.get("manipulation", {})
        self.vulnerability_exploitation = kwargs.get("vulnerability_exploitation", {})
        self.social_scoring = kwargs.get("social_scoring", {})
        self.emotion_recognition = kwargs.get("emotion_recognition", {})
        self.model_card = kwargs.get("model_card", {})
        self.general = kwargs.get("general", {})

    def _config(self, section_name):
        """Access configuration section as a dictionary."""
        return getattr(self, section_name)


class ComplianceEvaluator:
    """
    Main evaluator that combines multiple specialized evaluators.

    This class orchestrates the evaluation process across multiple domains:
    1. Fairness (via LangFair)
    2. Content Safety (via DeepEval)
    3. Risk Management
    4. Accuracy and Hallucination (via DeepEval)
    5. Biometric Categorization (via LangFair)
    6. Prohibited Practices (via DeepEval)
    7. Documentation Compliance

    It provides a unified interface for comprehensive compliance evaluation.
    """

    # Mapping of evaluator names to their classes for dynamic initialization
    EVALUATOR_CLASSES = {
        "fairness": FairnessEvaluator,
        "content_safety": ContentSafetyEvaluator,
        "risk_management": RiskManagementEvaluator,
        "accuracy": AccuracyEvaluator,
        "biometric_categorization": BiometricCategorizationEvaluator,
        "manipulation": ManipulationEvaluator,
        "vulnerability_exploitation": VulnerabilityExploitationEvaluator,
        "social_scoring": SocialScoringEvaluator,
        "emotion_recognition": EmotionRecognitionEvaluator,
        "model_card": ModelCardEvaluator,
    }

    def __init__(
        self,
        evaluators: Optional[List[str]] = None,
        evaluator_config: Optional[Dict[str, Any]] = None,
        supported_metrics: Optional[List[str]] = None,
    ):
        """
        Initialize the compliance evaluator.

        Args:
            evaluators: List of evaluator names to use. If None, all evaluators will be used.
            evaluator_config: Configuration for evaluators.
            supported_metrics: List of supported metrics.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Initializing ComplianceEvaluator")

        self.all_evaluators = {}

        # Initialize all evaluator instances with their default configurations
        for name, evaluator_class in self.EVALUATOR_CLASSES.items():
            self.logger.info(
                f"Initializing evaluator: {name} ({evaluator_class.__name__})"
            )

            # Get default configuration from evaluator class if available
            default_config = getattr(evaluator_class, "DEFAULT_CONFIG", {})

            # Merge with user-provided config if available
            config = {}
            if evaluator_config and name in evaluator_config:
                # Deep merge the configurations
                config = {**default_config, **(evaluator_config.get(name) or {})}
            else:
                config = default_config

            self.logger.debug(f"Configuration for {name}: {config}")

            # Initialize the evaluator based on its init signature
            try:
                if "config" in inspect.signature(evaluator_class.__init__).parameters:
                    self.all_evaluators[name] = evaluator_class(config=config)
                else:
                    self.all_evaluators[name] = evaluator_class(**config)

                self.logger.info(f"Successfully initialized {name}")
            except Exception as e:
                self.logger.error(f"Failed to initialize {name}: {str(e)}")

        self.logger.info(f"Available evaluators: {list(self.all_evaluators.keys())}")

        # Select which evaluators to use
        if evaluators is None:
            self.logger.info(
                "No specific evaluators requested, using all available evaluators"
            )
            # Use all available evaluators
            self.active_evaluators = self.all_evaluators
        else:
            self.logger.info(f"Requested evaluators: {evaluators}")
            # Use only the specified evaluators
            self.active_evaluators = {
                name: evaluator
                for name, evaluator in self.all_evaluators.items()
                if name in evaluators
            }

            # Log which evaluators were found and which weren't
            found_evaluators = [
                name for name in evaluators if name in self.all_evaluators
            ]
            missing_evaluators = [
                name for name in evaluators if name not in self.all_evaluators
            ]

            if found_evaluators:
                self.logger.info(f"Found evaluators: {found_evaluators}")
            if missing_evaluators:
                self.logger.warning(f"Evaluators not found: {missing_evaluators}")

        self.logger.info(f"Active evaluators: {list(self.active_evaluators.keys())}")

        # If no active evaluators were found by name, try a case-insensitive match or match by class name
        if not self.active_evaluators and evaluators:
            self.logger.warning(
                "No active evaluators found by exact name match. Trying fallback matching..."
            )

            # Try case-insensitive matching
            lower_case_map = {name.lower(): name for name in self.all_evaluators.keys()}
            for evaluator_name in evaluators:
                if evaluator_name.lower() in lower_case_map:
                    original_name = lower_case_map[evaluator_name.lower()]
                    self.active_evaluators[original_name] = self.all_evaluators[
                        original_name
                    ]
                    self.logger.info(
                        f"Found case-insensitive match: '{evaluator_name}' -> '{original_name}'"
                    )

            # Try matching by class name
            if not self.active_evaluators:
                class_to_name = {
                    cls.__name__: name for name, cls in self.EVALUATOR_CLASSES.items()
                }
                for evaluator_name in evaluators:
                    if evaluator_name in class_to_name:
                        name = class_to_name[evaluator_name]
                        self.active_evaluators[name] = self.all_evaluators[name]
                        self.logger.info(
                            f"Found match by class name: '{evaluator_name}' -> '{name}'"
                        )

        if not self.active_evaluators:
            self.logger.warning(
                "No active evaluators found after all matching attempts!"
            )

        # Set supported metrics
        self.supported_metrics = supported_metrics

    def evaluate(self, data: Dict) -> Dict[str, EvaluationResult]:
        """
        Evaluate compliance using all active evaluators.

        Args:
            data: Dictionary containing the contract data to evaluate
                Should include 'interactions' with a list of input/output pairs

        Returns:
            Dictionary mapping evaluator names to EvaluationResult objects
        """
        results = {}

        for name, evaluator in self.active_evaluators.items():
            logger.info(f"Running {name} evaluator")
            try:
                result = evaluator.evaluate(data)
                results[name] = result
                logger.info(
                    f"{name} evaluation complete: compliant={result.compliant}, score={result.score:.2f}"
                )
            except Exception as e:
                logger.error(f"Error in {name} evaluator: {str(e)}")
                # Create an error result
                results[name] = EvaluationResult(
                    evaluator_name=name.replace("_", " ").title() + " Evaluator",
                    compliant=False,
                    score=0.0,
                    threshold=0.7,  # Default threshold
                    reason=f"Evaluation error: {str(e)}",
                    details={"error": str(e)},
                )

        return results

    async def evaluate_async(self, data: Dict) -> Dict[str, EvaluationResult]:
        """
        Asynchronously evaluate compliance using all active evaluators.

        Args:
            data: Dictionary containing the contract data to evaluate

        Returns:
            Dictionary mapping evaluator names to EvaluationResult objects
        """
        results = {}
        tasks = []

        # Create tasks for all evaluators
        for name, evaluator in self.active_evaluators.items():
            tasks.append(self._run_evaluator_async(name, evaluator, data))

        # Run all evaluators concurrently
        completed_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for name, result in completed_results:
            results[name] = result

        return results

    async def _run_evaluator_async(
        self, name: str, evaluator: BaseEvaluator, data: Dict
    ) -> Tuple[str, EvaluationResult]:
        """
        Run an evaluator asynchronously and handle exceptions.

        Args:
            name: Name of the evaluator
            evaluator: Evaluator instance
            data: Data to evaluate

        Returns:
            Tuple of (evaluator_name, evaluation_result)
        """
        logger.info(f"Running {name} evaluator asynchronously")
        try:
            result = await evaluator.evaluate_async(data)
            logger.info(
                f"{name} evaluation complete: compliant={result.compliant}, score={result.score:.2f}"
            )
            return name, result
        except Exception as e:
            logger.error(f"Error in {name} evaluator: {str(e)}")
            # Create an error result
            error_result = EvaluationResult(
                evaluator_name=name.replace("_", " ").title() + " Evaluator",
                compliant=False,
                score=0.0,
                threshold=0.7,  # Default threshold
                reason=f"Evaluation error: {str(e)}",
                details={"error": str(e)},
            )
            return name, error_result

    def is_compliant(self, results: Dict[str, EvaluationResult]) -> bool:
        """
        Determine overall compliance based on individual evaluator results.

        Args:
            results: Dictionary mapping evaluator names to EvaluationResult objects

        Returns:
            Boolean indicating overall compliance
        """
        if not results:
            return False

        # Check if all evaluators report compliance
        return all(result.compliant for result in results.values())

    def generate_report(
        self, results: Dict[str, EvaluationResult], format: str = "json"
    ) -> Report:
        """
        Generate standardized compliance report.

        Args:
            results: Dictionary mapping evaluator names to EvaluationResult objects
            format: Output format (json, markdown, pdf)

        Returns:
            Report object containing formatted report
        """
        if format == "json":
            # Custom JSON encoder to handle datetime objects
            class DateTimeEncoder(json.JSONEncoder):
                def default(self, obj):
                    if isinstance(obj, datetime):
                        return obj.isoformat()
                    return super().default(obj)

            content = json.dumps(
                {
                    "evaluation_results": {
                        name: result.model_dump() for name, result in results.items()
                    },
                    "timestamp": datetime.utcnow().isoformat(),
                    "overall_compliant": self.is_compliant(results),
                },
                indent=2,
                cls=DateTimeEncoder,
            )
        elif format == "markdown":
            content = self._generate_markdown_report(results)
        elif format == "pdf":
            content = self._generate_pdf_report(results)
        else:
            raise ValueError(f"Unsupported format: {format}")

        return Report(content=content, format=format)

    def _generate_markdown_report(self, results: Dict[str, EvaluationResult]) -> str:
        """Generate a markdown format report."""
        import json

        overall_compliant = self.is_compliant(results)

        lines = [
            "# AI Compliance Evaluation Report",
            "",
            f"## Overall Compliance: {'PASS' if overall_compliant else 'FAIL'}",
            "",
            "| Evaluator | Compliance | Score | Threshold |",
            "|-----------|------------|-------|-----------|",
        ]

        for name, result in results.items():
            compliant_text = "✅ PASS" if result.compliant else "❌ FAIL"
            lines.append(
                f"| {result.evaluator_name} | {compliant_text} | {result.score:.2f} | {result.threshold:.2f} |"
            )

        lines.extend(["", "## Detailed Results", ""])

        for name, result in results.items():
            lines.extend(
                [
                    f"### {result.evaluator_name}",
                    "",
                    f"**Compliance:** {'PASS' if result.compliant else 'FAIL'}",
                    f"**Score:** {result.score:.2f} (Threshold: {result.threshold:.2f})",
                    f"**Reason:** {result.reason}",
                    "",
                    "#### Details",
                    "```json",
                    json.dumps(result.details, indent=2),
                    "```",
                    "",
                ]
            )

        return "\n".join(lines)

    def _generate_pdf_report(self, results: Dict[str, EvaluationResult]) -> str:
        """Generate a PDF format report."""
        # This is a placeholder for PDF generation
        # In a real implementation, this would create a PDF and return its content
        return f"PDF Report containing evaluation results for {len(results)} evaluators"
