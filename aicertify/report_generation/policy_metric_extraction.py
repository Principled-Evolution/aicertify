"""
Policy Metric Extraction Integration Module

This module integrates the AICertify evaluator registry with the Flexible Extraction System,
enabling automatic extraction of policy-required metrics from evaluation results for reporting.

The integration:
1. Retrieves metrics from the evaluator registry
2. Creates appropriate configurations for the Flexible Extraction System
3. Registers extractors that can find these metrics in evaluation results
4. Handles special cases requiring custom extraction logic
"""

from typing import Dict, List, Set, Any
import logging
from collections import OrderedDict
from aicertify.evaluators.evaluator_registry import get_default_registry
from aicertify.models.evaluation import MetricValue
from aicertify.report_generation.flexible_extraction import (
    MetricGroup,
    register_custom_extractor,
    register_metrics_from_config,
)

logger = logging.getLogger(__name__)

# Constants for consistent naming
POLICY_METRICS_GROUP = "policy_required_metrics"
POLICY_METRICS_DISPLAY_NAME = "Policy Required Metrics"
POLICY_CUSTOM_EXTRACTOR = "policy_metrics_custom"
POLICY_CUSTOM_DISPLAY_NAME = "Policy Metrics"


def register_policy_metrics_with_extraction_system() -> None:
    """
    Register metrics required by OPA policies with the Flexible Extraction System.

    This function:
    1. Discovers all registered metrics from the evaluator registry
    2. Creates appropriate configurations for the Flexible Extraction System
    3. Registers these configurations for extraction

    This enables a seamless integration between policy requirements, evaluators,
    and the report generation system.
    """
    # Get all registered metrics from the evaluator registry
    registry = get_default_registry()
    all_metrics: Set[str] = registry.get_all_metrics()

    if not all_metrics:
        logger.warning(
            "No metrics found in evaluator registry. "
            "Ensure initialize_evaluator_registry() has been called."
        )
        return

    # Create a metric group for policy-required metrics
    metrics_config = []

    for metric_name in sorted(all_metrics):
        # For each metric, create a configuration entry
        # Use standardized path patterns that match our extraction conventions
        metric_config = {
            "name": metric_name,
            "display_name": _format_metric_name(metric_name),
            "paths": _generate_extraction_paths(metric_name),
            "default_value": 0.0,  # Default value if metric is not found
        }
        metrics_config.append(metric_config)

    # Create the overall configuration
    config = {
        "metric_groups": [
            {
                "name": POLICY_METRICS_GROUP,
                "display_name": POLICY_METRICS_DISPLAY_NAME,
                "metrics": metrics_config,
            }
        ]
    }

    # Register the configuration with the extraction system
    logger.info(
        f"Registering {len(metrics_config)} metrics with Flexible Extraction System"
    )
    register_metrics_from_config(config)

    # Register a custom extractor to handle special cases
    register_policy_metrics_extractor()


def _format_metric_name(metric_name: str) -> str:
    """
    Format a metric name for display.

    Args:
        metric_name: Raw metric name from registry

    Returns:
        Formatted display name
    """
    # Replace dots and underscores with spaces, then capitalize each word
    display_name = metric_name.replace(".", " ").replace("_", " ")
    return " ".join(word.capitalize() for word in display_name.split())


def _generate_extraction_paths(metric_name: str) -> List[str]:
    """
    Generate standardized extraction paths for a metric.

    Args:
        metric_name: Raw metric name from registry

    Returns:
        List of paths to try when extracting the metric
    """
    # Convert dots to represent nested dictionaries
    path_segments = metric_name.split(".")

    # Generate multiple path patterns for resilient extraction
    paths = [
        # Direct metric name (e.g., "fairness.score")
        metric_name,
        # metrics.{metric_name} (e.g., "metrics.fairness.score")
        # Common pattern where all metrics are under a "metrics" key
        f"metrics.{metric_name}",
        # {evaluator}.{metric} (for last segment as metric)
        # (e.g., "fairness.score" -> "fairness.score")
        f"{'.'.join(path_segments[:-1])}.{path_segments[-1]}",
        # evaluator_results.{evaluator}.{metric}
        # (e.g., "evaluator_results.fairness.score")
        # Pattern used when results are grouped by evaluator
        f"evaluator_results.{'.'.join(path_segments)}",
        # Direct last segment (e.g., "fairness.score" -> "score")
        # Used when metric is stored with just the last part
        path_segments[-1],
        # Use underscores instead of dots
        # (e.g., "fairness.score" -> "fairness_score")
        # Common alternative format in many APIs
        metric_name.replace(".", "_"),
    ]

    # Remove duplicates while preserving order
    # This is more concise than the manual loop
    unique_paths = list(OrderedDict.fromkeys(paths))

    return unique_paths


def register_policy_metrics_extractor() -> None:
    """
    Register a custom extractor for policy metrics.

    This function registers a custom extractor that can handle special cases
    beyond the standard path-based extraction.
    """
    # Create a metric group with a custom extractor function
    metric_group = MetricGroup(
        name=POLICY_CUSTOM_EXTRACTOR,
        display_name=POLICY_CUSTOM_DISPLAY_NAME,
        extract_function=extract_policy_required_metrics,
    )

    # Verify that the metric_group.extract_metrics is callable
    if not callable(metric_group.extract_metrics):
        logger.error(
            "metric_group.extract_metrics is not callable. "
            "Check MetricGroup implementation."
        )
        return

    # Register the custom extractor
    register_custom_extractor(POLICY_CUSTOM_EXTRACTOR, metric_group.extract_metrics)
    logger.info("Registered custom policy metrics extractor")


def extract_policy_required_metrics(
    evaluation_result: Dict[str, Any]
) -> List[MetricValue]:
    """
    Custom extractor for policy-required metrics.

    This function is called by the Flexible Extraction System to extract metrics
    that may require special handling beyond path-based extraction.

    Args:
        evaluation_result: The evaluation result to extract metrics from
            Example structure:
            {
                "opa_results": {
                    "allow": true,
                    "violations": [...],
                    "compliance_score": 0.85
                },
                "policy_violations": [
                    {"policy": "fairness", "description": "..."},
                    {"policy": "privacy", "description": "..."}
                ]
            }

    Returns:
        List of extracted metric values
    """
    metrics = []

    # Extract metrics from OPA results if present
    if "opa_results" in evaluation_result:
        opa_results = evaluation_result["opa_results"]

        # Extract common OPA result metrics
        if isinstance(opa_results, dict):
            # Compliance decision (boolean)
            if "allow" in opa_results:
                metrics.append(
                    MetricValue(
                        name="compliance.decision",
                        display_name="Compliance Decision",
                        value=opa_results["allow"],
                    )
                )

            # Compliance score (float)
            if "compliance_score" in opa_results:
                metrics.append(
                    MetricValue(
                        name="compliance.score",
                        display_name="Compliance Score",
                        value=opa_results["compliance_score"],
                    )
                )

            # Violations count
            if "violations" in opa_results and isinstance(
                opa_results["violations"], list
            ):
                metrics.append(
                    MetricValue(
                        name="compliance.violations_count",
                        display_name="OPA Violations Count",
                        value=len(opa_results["violations"]),
                    )
                )

    # Look for policy violations if present
    if "policy_violations" in evaluation_result:
        violations = evaluation_result["policy_violations"]
        if isinstance(violations, list):
            metrics.append(
                MetricValue(
                    name="compliance.violations_count",
                    display_name="Policy Violations",
                    value=len(violations),
                )
            )

            # Group violations by policy type
            policy_types = {}
            for violation in violations:
                if isinstance(violation, dict) and "policy" in violation:
                    policy_type = violation["policy"]
                    policy_types[policy_type] = policy_types.get(policy_type, 0) + 1

            # Add metrics for each policy type
            for policy_type, count in policy_types.items():
                metrics.append(
                    MetricValue(
                        name=f"compliance.violations.{policy_type}",
                        display_name=f"{_format_metric_name(policy_type)} Violations",
                        value=count,
                    )
                )

    return metrics


def initialize_metric_extraction() -> None:
    """
    Initialize the integration between evaluator registry and metric extraction.

    This function should be called during application startup to ensure
    that metric extraction is properly configured.
    """
    try:
        # Verify that the evaluator registry has metrics
        registry = get_default_registry()
        metrics_count = registry.get_metrics_count()

        if metrics_count == 0:
            logger.warning(
                "Evaluator registry has no metrics registered. "
                "Check that initialize_evaluator_registry() was called."
            )

        # Register metrics with the extraction system
        register_policy_metrics_with_extraction_system()

        logger.info(
            f"Successfully initialized policy metrics extraction with {metrics_count} metrics"
        )
    except Exception as e:
        logger.exception(f"Error initializing policy metrics extraction: {e}")


# Optional function to explicitly initialize both registry and extraction
def initialize_registry_and_extraction() -> None:
    """
    Initialize both the evaluator registry and metric extraction system.

    This is a convenience function that can be called during application
    startup to ensure both systems are properly initialized.
    """
    from aicertify.evaluators.evaluator_registry import initialize_evaluator_registry

    try:
        # First initialize the evaluator registry
        initialize_evaluator_registry()

        # Then initialize the metric extraction
        initialize_metric_extraction()

        logger.info(
            "Successfully initialized both evaluator registry and metric extraction"
        )
    except Exception as e:
        logger.exception(f"Error during initialization: {e}")
