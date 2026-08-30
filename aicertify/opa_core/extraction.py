"""
Extraction utilities for OPA evaluation results.

This module provides functions for extracting structured data from OPA evaluation results,
particularly focusing on the standardized report_output format used by AICertify policies.
"""

import logging
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from aicertify.models.report import PolicyResult
from ..models.opa_results import OpaEvaluationResults, ExtractedPolicyResult

logger = logging.getLogger(__name__)


def extract_report_outputs(
    opa_results: Dict[str, Any],
) -> List[Tuple[List[str], Dict[str, Any]]]:
    """
    Extract standardized report_output structures from OPA evaluation results.

    Handles nested structures and filters out non-JSON debug information.

    Args:
        opa_results: Dict containing OPA evaluation results

    Returns:
        List of tuples (path, report_output) for all found report_output objects
    """
    # Add more debug logging
    debug_dir = os.path.join(os.getcwd(), "debug_output")
    os.makedirs(debug_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    debug_file = os.path.join(debug_dir, f"opa_results_pre_extract_{timestamp}.json")
    try:
        with open(debug_file, "w") as f:
            json.dump(opa_results, f, indent=2, default=str)
        logger.info(f"Saved raw OPA results to {debug_file} before extraction")
    except Exception as e:
        logger.error(f"Failed to save raw OPA results: {e}")

    if not isinstance(opa_results, dict):
        logger.warning("OPA results is not a dictionary, cannot extract report outputs")
        return []

    # Special handling for the common nested structure found in OPA results
    report_outputs = []

    # Check for the standard structure in EU AI Act evaluations
    if "result" in opa_results and isinstance(opa_results["result"], dict):
        result = opa_results["result"]

        # Check for the "results" array which contains individual policy evaluations
        if "results" in result and isinstance(result["results"], list):
            for i, policy_result in enumerate(result["results"]):
                if not isinstance(policy_result, dict) or "result" not in policy_result:
                    continue

                policy_path = ["result", "results", str(i)]

                # Look for expressions which often contain the report_output
                if "result" in policy_result and isinstance(
                    policy_result["result"], dict
                ):
                    if "result" in policy_result["result"] and isinstance(
                        policy_result["result"]["result"], list
                    ):
                        for j, expr_container in enumerate(
                            policy_result["result"]["result"]
                        ):
                            if "expressions" in expr_container and isinstance(
                                expr_container["expressions"], list
                            ):
                                for k, expr in enumerate(expr_container["expressions"]):
                                    if "value" in expr and isinstance(
                                        expr["value"], dict
                                    ):
                                        value = expr["value"]

                                        # Check if this value has the report_output structure
                                        if (
                                            "policy" in value
                                            and "result" in value
                                            and "metrics" in value
                                            and isinstance(value["metrics"], dict)
                                        ):
                                            # Validate metrics structure
                                            valid_metrics = True
                                            for metric_key, metric in value[
                                                "metrics"
                                            ].items():
                                                if not (
                                                    isinstance(metric, dict)
                                                    and "name" in metric
                                                    and "value" in metric
                                                    and "control_passed" in metric
                                                    and isinstance(
                                                        metric["control_passed"], bool
                                                    )
                                                ):
                                                    valid_metrics = False
                                                    logger.warning(
                                                        f"Invalid metric for '{metric_key}' in expression at index {k}"
                                                    )
                                                    break

                                            if valid_metrics:
                                                expr_path = policy_path + [
                                                    "result",
                                                    "result",
                                                    str(j),
                                                    "expressions",
                                                    str(k),
                                                    "value",
                                                ]
                                                logger.debug(
                                                    f"Found report_output in expression at path {expr_path}"
                                                )
                                                report_outputs.append(
                                                    (expr_path, value)
                                                )

    # If we found report_outputs in the specialized extraction, return them
    if report_outputs:
        logger.info(
            f"Extracted {len(report_outputs)} report_output structures using specialized extraction"
        )
        return report_outputs

    # Otherwise, continue with general recursive extraction
    logger.debug(
        "No report_outputs found using specialized extraction, falling back to recursive extraction"
    )

    # Only process JSON-compatible parts of the result
    def _extract_from_node(
        node: Any, path: Optional[List[str]] = None
    ) -> List[Tuple[List[str], Dict[str, Any]]]:
        if path is None:
            path = []

        # Skip non-dict/list values that might come from debug output
        if not isinstance(node, (dict, list)):
            return []

        # Add extra debugging for specific paths
        path_str = ".".join(str(p) for p in path)
        if "report_output" in path_str or (len(path) == 0 and isinstance(node, dict)):
            if not path:
                path_label = "root"
            else:
                path_label = path_str

            logger.debug(f"Checking node at path: {path_label}")

            if isinstance(node, dict):
                logger.debug(f"Keys at {path_label}: {list(node.keys())}")

                # Extra debug for nodes with 'metrics'
                if "metrics" in node:
                    logger.debug(
                        f"Found 'metrics' at {path_label}: {type(node['metrics'])}"
                    )

                # Check pattern requirements
                has_policy = "policy" in node
                has_result = "result" in node
                has_metrics = "metrics" in node and isinstance(node["metrics"], dict)

                if has_policy or has_result or has_metrics:
                    logger.debug(
                        f"Pattern check at {path_label}: policy={has_policy}, result={has_result}, metrics={has_metrics}"
                    )

                    # Check if node is close to matching pattern
                    if has_policy and has_result and not has_metrics:
                        logger.warning(
                            f"Node at {path_label} has policy and result but metrics is missing or invalid"
                        )
                    elif has_policy and has_metrics and not has_result:
                        logger.warning(
                            f"Node at {path_label} has policy and metrics but result is missing"
                        )

        # Check if this node is a report_output
        if (
            isinstance(node, dict)
            and "policy" in node
            and "result" in node
            and "metrics" in node
            and isinstance(node["metrics"], dict)
        ):
            # Validate metrics structure
            valid_metrics = True
            for metric_key, metric in node["metrics"].items():
                if not (
                    isinstance(metric, dict)
                    and "name" in metric
                    and "value" in metric
                    and "control_passed" in metric
                    and isinstance(metric["control_passed"], bool)
                ):
                    valid_metrics = False
                    logger.warning(
                        f"Invalid metric structure for '{metric_key}' at path {path}"
                    )
                    break

            if valid_metrics:
                logger.debug(f"Found report_output at path {path}")
                return [(path, node)]

        # Recursive traversal
        results = []
        if isinstance(node, dict):
            for key, value in node.items():
                # Skip known debug fields that may contain non-JSON structures
                # Fixed: Don't skip "metrics" field as it's required for report_output
                if key in ["explanation", "instrument", "coverage"]:
                    continue
                results.extend(_extract_from_node(value, path + [key]))
        elif isinstance(node, list):
            for i, item in enumerate(node):
                results.extend(_extract_from_node(item, path + [str(i)]))

        return results

    results = _extract_from_node(opa_results)
    logger.debug(
        f"Extracted {len(results)} report_output structures from generic extraction"
    )

    # Combine results from both extraction methods
    all_results = report_outputs + results
    logger.info(f"Total extracted report_output structures: {len(all_results)}")
    return all_results


def _package_values_from(opa_results: Dict[str, Any]) -> tuple:
    """Find the package map and policy directory an aggregated result carries."""
    result = opa_results.get("result")
    if isinstance(result, dict):
        values = result.get("package_values")
        if isinstance(values, dict):
            return values, result.get("policy_dir")
    return {}, None


def extract_all_policy_results(opa_results: Dict[str, Any]) -> List[PolicyResult]:
    """
    Extract all policy results from OPA evaluation results using schema validation.

    Args:
        opa_results: OPA evaluation results dictionary

    Returns:
        List of PolicyResult objects for report generation
    """
    package_values, policy_dir = _package_values_from(opa_results)

    try:
        # First parse and validate against our schema
        extracted_results = extract_policy_results_with_schema(opa_results)
        if not extracted_results:
            # Not an error, and usually not even unusual: only four of gopal's
            # policies define report_output. Fall through to the decision rules
            # rather than reporting nothing, which is what issue #78 described.
            logger.debug(
                "No report_output structures found; building results from "
                "decision rules instead."
            )
            if package_values and policy_dir:
                return extract_results_from_packages(package_values, policy_dir)
            logger.warning("No valid policy results found after schema validation")
            return []

        # Convert the extracted results to the report model
        policy_results = []
        for policy in extracted_results:
            # Convert metrics to the format expected by the report
            metrics = {}
            for metric_key, metric_value in policy.metrics.items():
                metrics[metric_key] = {
                    "name": metric_value.name,
                    "value": metric_value.value,
                    "control_passed": metric_value.control_passed,
                }

            # Create PolicyResult object
            policy_result = PolicyResult(
                name=policy.policy_name, result=policy.result, metrics=metrics
            )
            policy_results.append(policy_result)

        # Add anything that published only a decision rule, without
        # displacing the richer report_output entries already built.
        if package_values and policy_dir:
            covered = {r.name for r in policy_results}
            for extra in extract_results_from_packages(package_values, policy_dir):
                if extra.name not in covered:
                    policy_results.append(extra)

        logger.info(f"Extracted {len(policy_results)} policy results")
        return policy_results

    except Exception as e:
        logger.error(f"Error extracting policy results: {e}")
        return []


def extract_policy_results_with_schema(
    opa_results: Dict[str, Any],
) -> List[ExtractedPolicyResult]:
    """
    Extract policy results using strict schema validation with Pydantic.

    Args:
        opa_results: OPA evaluation results dictionary

    Returns:
        List of ExtractedPolicyResult objects with standardized structure
    """
    try:
        # Validate against our schema
        validated_results = OpaEvaluationResults.model_validate(opa_results)

        # Extract each policy result
        extracted_policies = []

        for policy_eval in validated_results.result.results:
            try:
                # Navigate to the report output in the nested structure
                expressions = policy_eval.result.result[0].expressions
                for expr in expressions:
                    if "report_output" in expr.text:
                        # Found the report output expression
                        report = expr.value

                        # Create ExtractedPolicyResult
                        extracted = ExtractedPolicyResult(
                            policy_id=policy_eval.policy,
                            policy_name=report.policy,
                            result=report.result,
                            metrics={k: v for k, v in report.metrics.items()},
                            timestamp=report.timestamp,
                        )
                        extracted_policies.append(extracted)
                        break
            except (IndexError, AttributeError) as e:
                logger.warning(
                    f"Error extracting policy result for {policy_eval.policy}: {e}"
                )
                continue

        return extracted_policies

    except Exception as e:
        # Expected, and the common case. This path validates against the
        # `report_output` schema, which four of gopal's policies define. Every
        # other policy fails it, and the caller then reads the decision rules
        # instead (see the note on extract_results_from_packages below).
        #
        # Logged at error until the #78 fallback landed, which meant a normal
        # successful evaluation printed a pydantic validation report per policy
        # and looked to a first-time user like a crash. The behaviour was
        # already correct; only the log level was left behind.
        logger.debug(
            "No report_output schema match (%s); the caller falls back to "
            "decision rules.",
            e.__class__.__name__,
        )
        return []


def get_policy_metrics(policy_results: List[PolicyResult]) -> Dict[str, Dict[str, Any]]:
    """
    Extract metrics from policy results.

    This function extracts all metrics from the policy results and organizes them
    by policy name and metric key.

    Args:
        policy_results: List of PolicyResult objects

    Returns:
        Dictionary mapping policy names to dictionaries of metrics
    """
    policy_metrics = {}

    for policy_result in policy_results:
        if hasattr(policy_result, "metrics") and policy_result.metrics:
            policy_metrics[policy_result.name] = policy_result.metrics

    return policy_metrics


def validate_opa_results(opa_results: Dict[str, Any]) -> bool:
    """
    Validate that OPA results have the expected structure.

    Args:
        opa_results: Dictionary containing OPA evaluation results

    Returns:
        True if results have valid structure, False otherwise
    """
    if not isinstance(opa_results, dict):
        logger.error("OPA results is not a dictionary")
        return False

    # Check for minimum required fields in the result
    if "result" not in opa_results:
        logger.error("OPA results missing 'result' field")
        return False

    # Validate that at least one report_output structure exists
    report_outputs = extract_report_outputs(opa_results)
    if not report_outputs:
        logger.warning("No report_output structures found in OPA results")
        return False

    return True


# ---------------------------------------------------------------------------
# Decision-rule extraction (issue #78)
#
# `extract_policy_results_with_schema` above only recognises `report_output`.
# Four of gopal's 91 policies define it, so evaluations against the UK, NIST,
# BFS, legal or global sets reported nothing at all while exiting successfully.
#
# The policies were not silent, they were being asked the wrong question. A
# survey of the library found `report` on 59 policies and `policy_metrics` on
# 63, and gopal's coverage data names a decision rule for all 84 policies that
# reach a verdict. So the fix is to ask for the whole package and read whatever
# it actually publishes, preferring the richest shape available.
# ---------------------------------------------------------------------------

from aicertify.opa_core.decision_index import (  # noqa: E402
    PolicyDescriptor,
    load_index,
)

#: Report structures in descending order of detail. The first one present wins.
REPORT_RULES = ("report_output", "compliance_report", "report")

#: Where per-metric detail lives when a report structure does not carry it.
METRIC_RULES = ("policy_metrics",)


def _metrics_from(package_value: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pull per-metric detail out of whichever shape the policy publishes.

    Both the report structures and `policy_metrics` use the same inner shape:
    a mapping of metric key to an object carrying at least `name` and
    `control_passed`. Anything that does not look like that is skipped rather
    than guessed at.
    """
    candidates: List[Any] = []
    for rule in REPORT_RULES:
        block = package_value.get(rule)
        if isinstance(block, dict) and isinstance(block.get("metrics"), dict):
            candidates.append(block["metrics"])
    for rule in METRIC_RULES:
        block = package_value.get(rule)
        if isinstance(block, dict):
            candidates.append(block)

    for source in candidates:
        metrics: Dict[str, Any] = {}
        for key, value in source.items():
            if not isinstance(value, dict):
                continue
            metrics[key] = {
                "name": value.get("name", key),
                "value": value.get("value"),
                "control_passed": value.get("control_passed"),
            }
        if metrics:
            return metrics
    return {}


def synthesise_policy_result(
    package: str,
    package_value: Dict[str, Any],
    descriptor: Optional[PolicyDescriptor],
) -> Optional[PolicyResult]:
    """
    Build a report entry for one policy from whatever it published.

    Returns None when the package is a shared library, when the library does
    not describe it, or when its decision rule produced no boolean. That last
    case is deliberate: in Rego an undefined value is not `false`, so a policy
    that reached no conclusion is omitted rather than recorded as a failure it
    did not declare.
    """
    if descriptor is None or not descriptor.reports_a_verdict:
        return None
    if not isinstance(package_value, dict):
        return None

    raw = package_value.get(descriptor.decision_rule)
    verdict = descriptor.interpret(raw)
    if verdict is None:
        logger.debug(
            "Policy %s produced no boolean for %s; omitting rather than "
            "reporting an undefined value as a failure.",
            package,
            descriptor.decision_rule,
        )
        return None

    metrics = _metrics_from(package_value)
    details: Dict[str, Any] = {
        "package": package,
        "decision_rule": descriptor.decision_rule,
        "raw_decision": raw,
    }
    if descriptor.true_means == "concern":
        # Worth stating in the report: `true` from this policy means a concern
        # was detected, so the verdict shown is the inverse of the raw value.
        details["detector"] = True
    if descriptor.references:
        details["references"] = descriptor.references
    if not metrics:
        details["detail_level"] = "decision only"

    return PolicyResult(
        name=descriptor.title or package,
        result=verdict,
        metrics=metrics or None,
        details=details,
    )


def extract_results_from_packages(
    package_values: Dict[str, Dict[str, Any]],
    policy_dir: str,
) -> List[PolicyResult]:
    """
    Build report entries for a mapping of package name to evaluated package.

    Ordered by policy title so a report reads consistently between runs.
    """
    index = load_index(policy_dir)
    results: List[PolicyResult] = []
    for package, value in package_values.items():
        result = synthesise_policy_result(package, value, index.get(package))
        if result is not None:
            results.append(result)
    results.sort(key=lambda r: r.name)
    logger.info(
        "Built %d policy results from %d evaluated packages.",
        len(results),
        len(package_values),
    )
    return results
