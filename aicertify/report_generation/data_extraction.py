"""
Data extraction utilities for report generation.

This module provides functions to extract metrics and other data from 
evaluation results, ensuring reports are complete and accurate.
"""

import logging
from typing import Dict, Any, List, Optional

# Import from centralized models
from aicertify.models.evaluation import MetricValue
from aicertify.models.report import (
    EvaluationReport, ApplicationDetails,
   create_metric_group
)

# Import feature flag configuration
from aicertify.opa_core.extraction import extract_all_policy_results

logger = logging.getLogger(__name__)

def extract_application_details(eval_result: Dict[str, Any]) -> ApplicationDetails:
    """
    Extract application details from evaluation results.
    
    Args:
        eval_result: Evaluation results containing application information
        
    Returns:
        ApplicationDetails object with app information
    """
    # Extract app name
    app_name = eval_result.get("application_name", "Unknown Application")
    
    # Extract model information if available
    model_info = eval_result.get("model_info", {})
    if isinstance(model_info, dict):
        model_name = model_info.get("name", "Unknown")
        model_provider = model_info.get("provider", "Unknown")
        model_type = model_info.get("type", "Unknown")
    else:
        model_name = "Unknown"
        model_provider = "Unknown"
        model_type = "Unknown"
    
    # Extract metadata
    metadata = eval_result.get("metadata", {})
    
    # Create and return ApplicationDetails
    return ApplicationDetails(
        name=app_name,
        model_info={
            "name": model_name,
            "provider": model_provider,
            "type": model_type
        },
        metadata=metadata
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
    
    # Case 3: Fairness metrics in a dedicated fairness_metrics field
    if "fairness_metrics" in evaluation_result and isinstance(evaluation_result["fairness_metrics"], dict):
        fairness_data = evaluation_result["fairness_metrics"]
        
        # Add counterfactual score if present
        if "counterfactual_score" in fairness_data:
            metrics.append(MetricValue(
                name="counterfactual_score",
                display_name="Counterfactual Score",
                value=fairness_data["counterfactual_score"]
            ))
        
        # Add stereotype score if present
        if "stereotype_score" in fairness_data:
            metrics.append(MetricValue(
                name="stereotype_score",
                display_name="Stereotype Score",
                value=fairness_data["stereotype_score"]
            ))
        
        # Add combined score if present
        if "combined_score" in fairness_data:
            metrics.append(MetricValue(
                name="combined_score",
                display_name="Combined Score",
                value=fairness_data["combined_score"]
            ))
        
        # Check for details
        if "details" in fairness_data and isinstance(fairness_data["details"], dict):
            details = fairness_data["details"]
            
            # Add sentiment bias if present
            if "sentiment_bias" in details:
                metrics.append(MetricValue(
                    name="sentiment_bias",
                    display_name="Sentiment Bias",
                    value=details["sentiment_bias"]
                ))
            
            # Add BLEU similarity if present
            if "bleu_similarity" in details:
                metrics.append(MetricValue(
                    name="bleu_similarity",
                    display_name="BLEU Similarity",
                    value=details["bleu_similarity"]
                ))
            
            # Add ROUGE similarity if present
            if "rouge_similarity" in details:
                metrics.append(MetricValue(
                    name="rouge_similarity",
                    display_name="ROUGE Similarity",
                    value=details["rouge_similarity"]
                ))
            
            # Add gender bias if present
            if "gender_bias" in details:
                metrics.append(MetricValue(
                    name="gender_bias_detected",
                    display_name="Gender Bias Detected",
                    value=details["gender_bias"]
                ))
            
            # Add racial bias if present
            if "racial_bias" in details:
                metrics.append(MetricValue(
                    name="racial_bias_detected",
                    display_name="Racial Bias Detected",
                    value=details["racial_bias"]
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
    
    # Case 4: Content safety structure in sample data
    elif "content_safety" in evaluation_result and isinstance(evaluation_result["content_safety"], dict):
        content_safety = evaluation_result["content_safety"]
        
        # Add overall score if present
        if "score" in content_safety:
            metrics.append(MetricValue(
                name="content_safety_score",
                display_name="Content Safety Score",
                value=content_safety["score"]
            ))
        
        # Check for details
        if "details" in content_safety and isinstance(content_safety["details"], dict):
            toxicity_data = content_safety["details"]
    
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
    
    # Case 4: Fairness metrics structure in sample data
    elif "fairness_metrics" in evaluation_result and isinstance(evaluation_result["fairness_metrics"], dict):
        fairness_metrics = evaluation_result["fairness_metrics"]
        
        # Add stereotype score if present
        if "stereotype_score" in fairness_metrics:
            metrics.append(MetricValue(
                name="stereotype_score",
                display_name="Stereotype Score",
                value=fairness_metrics["stereotype_score"]
            ))
        
        # Check for details
        if "details" in fairness_metrics and isinstance(fairness_metrics["details"], dict):
            details = fairness_metrics["details"]
            
            # Extract gender and racial bias if present
            if "gender_bias" in details:
                stereotype_data["gender_bias_detected"] = details["gender_bias"]
            
            if "racial_bias" in details:
                stereotype_data["racial_bias_detected"] = details["racial_bias"]
    
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

# This function is no longer needed as we're using the consolidated extraction function
# def extract_structured_data_from_debug(debug_output: str) -> Dict[str, Any]:
#     """This function has been removed in favor of the consolidated extraction system."""
#     return None

# This function is no longer needed as we're using the consolidated extraction function
# def process_extracted_policy_data(extracted_data: Dict[str, Any]) -> List[PolicyResult]:
#     """This function has been removed in favor of the consolidated extraction system."""
#     return []

def create_evaluation_report(
    eval_result: Dict[str, Any],
    opa_results: Optional[Dict[str, Any]] = None
) -> EvaluationReport:
    """
    Creates a structured evaluation report from evaluation results and policy results.
    
    Args:
        eval_result: The evaluation results containing metrics and application details
        opa_results: Optional OPA policy results to include
        
    Returns:
        An EvaluationReport Pydantic model containing the structured report
    """
    # Extract application details
    app_details = extract_application_details(eval_result)
    
    # Initialize lists for report structure
    metric_groups = []
    policy_results = []
    
    # Process OPA results
    if opa_results and opa_results.get("result"):
        try:
            policy_results = extract_all_policy_results(opa_results)
        except Exception as e:
            logging.error(f"Error extracting policy results: {e}")
    
    # Group metrics by category
    metrics_by_category = {}
    
    # First process direct metrics from eval_result
    if "metrics" in eval_result and eval_result["metrics"]:
        for metric_id, metric_data in eval_result["metrics"].items():
            # Determine category (default to "Model Quality")
            category = metric_data.get("category", "Model Quality")
            
            # Create or update category in the metrics_by_category dict
            if category not in metrics_by_category:
                metrics_by_category[category] = {}
            
            # Add metric to the category
            metrics_by_category[category][metric_id] = metric_data
    
    # Then process metrics from policy results
    for policy in policy_results:
        if policy.metrics:
            for metric_id, metric_data in policy.metrics.items():
                # Determine category (default to policy name)
                category = metric_data.get("category", policy.name)
                
                # Create or update category in the metrics_by_category dict
                if category not in metrics_by_category:
                    metrics_by_category[category] = {}
                
                # Add metric to the category
                metrics_by_category[category][metric_id] = metric_data
    
    # Create metric groups from the categorized metrics
    for category, metrics in metrics_by_category.items():
        metric_group = create_metric_group(category, metrics)
        metric_groups.append(metric_group)
    
    # Generate summary information
    total_policies = len(policy_results)
    green_count = sum(1 for p in policy_results if p.result)
    red_count = total_policies - green_count
    
    # Create and return the structured report
    return EvaluationReport(
        app_details=app_details,
        metric_groups=metric_groups,
        policy_results=policy_results,
        summary={
            "total_policies": total_policies,
            "green_count": green_count,
            "red_count": red_count
        }
    )
