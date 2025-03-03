"""
Data extraction utilities for report generation.

This module provides functions to extract metrics and other data from 
evaluation results, ensuring reports are complete and accurate.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from aicertify.report_generation.report_models import (
    EvaluationReport, ApplicationDetails,
    MetricGroup, MetricValue, PolicyResult
)

logger = logging.getLogger(__name__)

def extract_application_details(evaluation_result: Dict[str, Any]) -> ApplicationDetails:
    """
    Extract application details from evaluation results.
    
    Args:
        evaluation_result: Dictionary containing evaluation metrics
        
    Returns:
        ApplicationDetails object with extracted information
    """
    # Extract app name
    app_name = "Unknown Application"
    if "app_name" in evaluation_result:
        app_name = evaluation_result["app_name"]
    elif "application_name" in evaluation_result:
        app_name = evaluation_result["application_name"]
    
    # Extract evaluation mode
    evaluation_mode = "Standard"
    if "evaluation_mode" in evaluation_result:
        evaluation_mode = evaluation_result["evaluation_mode"]
    
    # Extract contract count
    contract_count = 0
    if "combined_contract_count" in evaluation_result:
        contract_count = evaluation_result["combined_contract_count"]
    elif "contract_count" in evaluation_result:
        contract_count = evaluation_result["contract_count"]
    elif "interactions" in evaluation_result:
        # If we have a list of interactions, count them
        contract_count = len(evaluation_result["interactions"])
    
    # Create the application details
    return ApplicationDetails(
        name=app_name,
        evaluation_mode=evaluation_mode,
        contract_count=contract_count,
        evaluation_date=datetime.now()
    )

def extract_fairness_metrics(evaluation_result: Dict[str, Any]) -> List[MetricValue]:
    """
    Extract fairness metrics from evaluation results.
    
    Args:
        evaluation_result: Dictionary containing evaluation metrics
        
    Returns:
        List of MetricValue objects for fairness metrics
    """
    metrics = []
    
    # Handle different result structures
    metrics_data = {}
    
    # Case 1: Nested metrics structure
    if "metrics" in evaluation_result:
        if isinstance(evaluation_result["metrics"], dict):
            metrics_data = evaluation_result["metrics"]
            
            # Case 1.1: Fairness metrics in a 'fairness' subfield
            if "fairness" in metrics_data and isinstance(metrics_data["fairness"], dict):
                fairness_data = metrics_data["fairness"]
                for key, value in fairness_data.items():
                    display_name = key.replace("_", " ").title()
                    metrics.append(MetricValue(
                        name=key,
                        display_name=display_name, 
                        value=value
                    ))
            
            # Case 1.2: Fairness metrics directly in metrics dict
            else:
                # Extract common fairness metrics if present
                if "ftu_satisfied" in metrics_data:
                    metrics.append(MetricValue(
                        name="ftu_satisfied",
                        display_name="FTU Satisfied",
                        value=metrics_data["ftu_satisfied"]
                    ))
                
                if "race_words_count" in metrics_data:
                    metrics.append(MetricValue(
                        name="race_words_count",
                        display_name="Race Words Count",
                        value=metrics_data["race_words_count"]
                    ))
                
                if "gender_words_count" in metrics_data:
                    metrics.append(MetricValue(
                        name="gender_words_count",
                        display_name="Gender Words Count",
                        value=metrics_data["gender_words_count"]
                    ))
    
    # Case 2: Direct fairness metrics at root level
    # Check for common fairness metrics directly in the evaluation result
    if "ftu_satisfied" in evaluation_result:
        metrics.append(MetricValue(
            name="ftu_satisfied",
            display_name="FTU Satisfied",
            value=evaluation_result["ftu_satisfied"]
        ))
    
    if "race_words_count" in evaluation_result:
        metrics.append(MetricValue(
            name="race_words_count",
            display_name="Race Words Count",
            value=evaluation_result["race_words_count"]
        ))
    
    if "gender_words_count" in evaluation_result:
        metrics.append(MetricValue(
            name="gender_words_count",
            display_name="Gender Words Count",
            value=evaluation_result["gender_words_count"]
        ))
    
    # If no metrics found, add placeholder metrics
    if not metrics:
        metrics = [
            MetricValue(name="ftu_satisfied", display_name="FTU Satisfied", value=False),
            MetricValue(name="race_words_count", display_name="Race Words Count", value=0),
            MetricValue(name="gender_words_count", display_name="Gender Words Count", value=0)
        ]
    
    return metrics

def extract_toxicity_metrics(evaluation_result: Dict[str, Any]) -> List[MetricValue]:
    """
    Extract toxicity metrics from evaluation results.
    
    Args:
        evaluation_result: Dictionary containing evaluation metrics
        
    Returns:
        List of MetricValue objects for toxicity metrics
    """
    metrics = []
    toxicity_data = {}
    
    # Case 1: Nested metrics structure
    if "metrics" in evaluation_result and isinstance(evaluation_result["metrics"], dict):
        metrics_data = evaluation_result["metrics"]
        
        # Case 1.1: Toxicity metrics in a 'toxicity' subfield
        if "toxicity" in metrics_data and isinstance(metrics_data["toxicity"], dict):
            toxicity_data = metrics_data["toxicity"]
    
    # Case 2: Summary with toxicity values
    elif "summary" in evaluation_result and isinstance(evaluation_result["summary"], dict):
        summary_data = evaluation_result["summary"]
        if "toxicity_values" in summary_data and isinstance(summary_data["toxicity_values"], dict):
            toxicity_data = summary_data["toxicity_values"]
    
    # Case 3: Toxicity metrics at root level
    elif "toxic_fraction" in evaluation_result or "max_toxicity" in evaluation_result:
        toxicity_data = evaluation_result
    
    # Extract specific metrics from the toxicity data
    if toxicity_data:
        if "toxic_fraction" in toxicity_data:
            metrics.append(MetricValue(
                name="toxic_fraction",
                display_name="Toxic Fraction",
                value=toxicity_data["toxic_fraction"]
            ))
        
        if "max_toxicity" in toxicity_data:
            metrics.append(MetricValue(
                name="max_toxicity",
                display_name="Max Toxicity",
                value=toxicity_data["max_toxicity"]
            ))
        
        if "toxicity_probability" in toxicity_data:
            metrics.append(MetricValue(
                name="toxicity_probability",
                display_name="Toxicity Probability",
                value=toxicity_data["toxicity_probability"]
            ))
    
    # If no metrics found, add placeholder metrics
    if not metrics:
        metrics = [
            MetricValue(name="toxic_fraction", display_name="Toxic Fraction", value=0.0),
            MetricValue(name="max_toxicity", display_name="Max Toxicity", value=0.0),
            MetricValue(name="toxicity_probability", display_name="Toxicity Probability", value=0.0)
        ]
    
    return metrics

def extract_stereotype_metrics(evaluation_result: Dict[str, Any]) -> List[MetricValue]:
    """
    Extract stereotype metrics from evaluation results.
    
    Args:
        evaluation_result: Dictionary containing evaluation metrics
        
    Returns:
        List of MetricValue objects for stereotype metrics
    """
    metrics = []
    stereotype_data = {}
    
    # Case 1: Nested metrics structure
    if "metrics" in evaluation_result and isinstance(evaluation_result["metrics"], dict):
        metrics_data = evaluation_result["metrics"]
        
        # Case 1.1: Stereotype metrics in a 'stereotype' subfield
        if "stereotype" in metrics_data and isinstance(metrics_data["stereotype"], dict):
            stereotype_data = metrics_data["stereotype"]
    
    # Case 2: Summary with stereotype values
    elif "summary" in evaluation_result and isinstance(evaluation_result["summary"], dict):
        summary_data = evaluation_result["summary"]
        if "stereotype_values" in summary_data and isinstance(summary_data["stereotype_values"], dict):
            stereotype_data = summary_data["stereotype_values"]
    
    # Case 3: Stereotype metrics at root level
    elif "gender_bias_detected" in evaluation_result or "racial_bias_detected" in evaluation_result:
        stereotype_data = evaluation_result
    
    # Extract specific metrics from the stereotype data
    if stereotype_data:
        if "gender_bias_detected" in stereotype_data:
            metrics.append(MetricValue(
                name="gender_bias_detected",
                display_name="Gender Bias Detected",
                value=stereotype_data["gender_bias_detected"]
            ))
        
        if "racial_bias_detected" in stereotype_data:
            metrics.append(MetricValue(
                name="racial_bias_detected",
                display_name="Racial Bias Detected",
                value=stereotype_data["racial_bias_detected"]
            ))
    
    # If no metrics found, add placeholder metrics
    if not metrics:
        metrics = [
            MetricValue(name="gender_bias_detected", display_name="Gender Bias Detected", value=False),
            MetricValue(name="racial_bias_detected", display_name="Racial Bias Detected", value=False)
        ]
    
    return metrics

def extract_policy_results(opa_results: Dict[str, Any]) -> List[PolicyResult]:
    """
    Extract policy results from OPA evaluation results.
    
    Args:
        opa_results: Dictionary containing OPA policy evaluation results
        
    Returns:
        List of PolicyResult objects
    """
    policy_results = []
    
    # Handle case where no OPA results are provided
    if not opa_results:
        return policy_results
        
    # Case 1: Direct policy results as a dictionary of policy names to results
    for policy_name, policy_data in opa_results.items():
        # Skip non-policy keys
        if policy_name in ["error", "available_categories"]:
            continue
            
        # Case 1.1: Standard OPA result format
        if "result" in policy_data and policy_data["result"]:
            try:
                # Extract expressions data
                expressions = policy_data["result"][0]["expressions"][0]["value"]
                
                # Extract overall result
                result = False
                if "overall_result" in expressions:
                    result = expressions["overall_result"]
                elif "allow" in expressions:
                    result = expressions["allow"]
                
                # Extract details
                details = {
                    "policy": expressions.get("policy", policy_name),
                    "version": expressions.get("version", "1.0"),
                    "timestamp": datetime.now().isoformat()
                }
                
                # Extract recommendations
                if "recommendations" in expressions and expressions["recommendations"]:
                    details["recommendations"] = expressions["recommendations"]
                
                # Add policy result
                policy_results.append(PolicyResult(
                    name=policy_name,
                    result=result,
                    details=details
                ))
            except (KeyError, IndexError, TypeError) as e:
                # Fallback for error cases
                logger.warning(f"Error extracting policy result for {policy_name}: {e}")
                policy_results.append(PolicyResult(
                    name=policy_name, 
                    result=False,
                    details={"error": f"Failed to parse policy result: {e}"}
                ))
    
    # Case 2: Nested policy_results format
    if "policy_results" in opa_results:
        policy_data = opa_results["policy_results"]
        
        # Case 2.1: List of policy results in policy_results field
        if "policy_results" in policy_data and isinstance(policy_data["policy_results"], list):
            for result in policy_data["policy_results"]:
                policy_name = result.get("policy_name", "unknown")
                policy_result = result.get("result", False)
                
                details = {}
                if "recommendations" in result:
                    details["recommendations"] = result["recommendations"]
                
                policy_results.append(PolicyResult(
                    name=policy_name,
                    result=policy_result,
                    details=details
                ))
    
    # If still no results, try to handle any other format as best we can
    if not policy_results and isinstance(opa_results, dict):
        for key, value in opa_results.items():
            if key not in ["error", "available_categories"] and isinstance(value, dict):
                # Try to extract any meaningful information
                result = False
                if "result" in value:
                    result = bool(value["result"])
                
                details = {}
                for detail_key, detail_value in value.items():
                    if detail_key != "result" and not isinstance(detail_value, (dict, list)):
                        details[detail_key] = detail_value
                
                policy_results.append(PolicyResult(
                    name=key,
                    result=result,
                    details=details
                ))
    
    return policy_results

def create_evaluation_report(
    evaluation_result: Dict[str, Any], 
    opa_results: Optional[Dict[str, Any]] = None
) -> EvaluationReport:
    """
    Create a complete evaluation report from evaluation results and OPA results.
    
    Args:
        evaluation_result: Dictionary containing evaluation metrics
        opa_results: Dictionary containing OPA policy evaluation results
        
    Returns:
        Complete EvaluationReport object for report generation
    """
    # Use empty dict if opa_results is None
    if opa_results is None:
        opa_results = {}
    
    # Extract application details
    app_details = extract_application_details(evaluation_result)
    
    # Create metric groups
    fairness_metrics = extract_fairness_metrics(evaluation_result)
    toxicity_metrics = extract_toxicity_metrics(evaluation_result)
    stereotype_metrics = extract_stereotype_metrics(evaluation_result)
    
    metric_groups = [
        MetricGroup(
            name="fairness",
            display_name="Fairness Metrics",
            metrics=fairness_metrics
        ),
        MetricGroup(
            name="toxicity",
            display_name="Toxicity Metrics",
            metrics=toxicity_metrics
        ),
        MetricGroup(
            name="stereotype",
            display_name="Stereotype Metrics",
            metrics=stereotype_metrics
        )
    ]
    
    # Extract policy results
    policy_results = extract_policy_results(opa_results)
    
    # Create summary if available
    summary = None
    if "summary" in evaluation_result:
        summary_data = evaluation_result["summary"]
        if isinstance(summary_data, str):
            summary = summary_data
        elif isinstance(summary_data, dict):
            # Create a summary from the available data
            summary_parts = []
            
            # Check for toxicity
            if "has_toxicity" in summary_data and summary_data["has_toxicity"]:
                summary_parts.append("Toxicity detected in responses")
            elif "toxicity_values" in summary_data:
                toxicity_values = summary_data["toxicity_values"]
                if toxicity_values.get("toxic_fraction", 0) > 0.1:
                    summary_parts.append("Toxicity detected in responses")
            
            # Check for bias
            if "has_bias" in summary_data and summary_data["has_bias"]:
                summary_parts.append("Bias detected in responses")
            elif "stereotype_values" in summary_data:
                stereotype_values = summary_data["stereotype_values"]
                if stereotype_values.get("gender_bias_detected", False) or stereotype_values.get("racial_bias_detected", False):
                    summary_parts.append("Bias detected in responses")
                
            if not summary_parts:
                summary_parts.append("No significant issues detected")
                
            summary = ". ".join(summary_parts)
    
    # Create the evaluation report
    return EvaluationReport(
        app_details=app_details,
        metric_groups=metric_groups,
        policy_results=policy_results,
        summary=summary
    ) 