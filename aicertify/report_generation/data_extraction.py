"""
Data extraction utilities for report generation.

This module provides functions to extract metrics and other data from 
evaluation results, ensuring reports are complete and accurate.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import os

# Import from centralized models
from aicertify.models.evaluation import MetricValue
from aicertify.models.report import (
    EvaluationReport, ApplicationDetails,
    MetricGroup, PolicyResult
)

# Import feature flag configuration
from aicertify.report_generation.config import use_flexible_extraction

# Import flexible extraction system
from aicertify.report_generation.flexible_extraction import extract_metrics as flexible_extract_metrics

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

def extract_policy_results(opa_results: Dict[str, Any]) -> List[PolicyResult]:
    """Extract policy results from OPA evaluation results."""
    # Check if we should use the flexible extraction system
    if use_flexible_extraction():
        try:
            # Use the new flexible extractor from opa_core
            from aicertify.opa_core.extraction import extract_all_policy_results as flexible_extract
            logger.info("Using flexible extraction system")
            policy_results = flexible_extract(opa_results)
            
            # If we got results, return them
            if policy_results:
                logger.info(f"Extracted {len(policy_results)} policy results using flexible extractor")
                return policy_results
            
            # If the flexible extraction failed, fall back to the original method
            logger.warning("Flexible extraction returned no results, falling back to original method")
        except Exception as e:
            logger.error(f"Error using flexible extraction system: {e}")
            logger.info("Falling back to original extraction method")
    
    # Original extraction method as fallback
    policy_results = []
    
    # Check if we have a valid OPA result structure
    if not opa_results or "result" not in opa_results:
        logger.warning("No valid OPA results found")
        return policy_results
    
    # Get the first result
    if not opa_results["result"] or not isinstance(opa_results["result"], list):
        logger.warning("OPA results has empty or invalid result list")
        return policy_results
    
    first_result = opa_results["result"][0]
    
    # Check for expressions
    if "expressions" not in first_result or not first_result["expressions"]:
        logger.warning("No expressions found in OPA result")
        return policy_results
    
    first_expr = first_result["expressions"][0]
    
    # Check for value
    if "value" not in first_expr:
        logger.warning("No value found in OPA expression")
        return policy_results
    
    value = first_expr["value"]
    
    # Log the structure of the value
    logger.debug(f"OPA result value keys: {list(value.keys())}")
    
    # Process all version keys (v1, v2, etc.) instead of just "v1"
    version_keys = [k for k in value.keys() if k.startswith("v")]
    logger.debug(f"Found version keys: {version_keys}")
    
    for version_key in version_keys:
        version_data = value[version_key]
        logger.debug(f"Processing version {version_key} with {len(version_data)} policies")
        
        # Process each policy in the current version
        for policy_name, policy_data in version_data.items():
            logger.debug(f"Processing policy: {policy_name}")
            
            # Check if the policy has a compliance report
            if "compliance_report" in policy_data:
                compliance_report = policy_data["compliance_report"]
                logger.debug(f"Found compliance report for {policy_name}")
                
                # Extract details from the compliance report
                overall_result = compliance_report.get("overall_result", False)
                policy_title = compliance_report.get("policy", policy_name.replace("_", " ").title())
                status = compliance_report.get("status", "Unknown")
                details = compliance_report.get("details", {})
                
                # Ensure details is a dictionary, not a string
                if not isinstance(details, dict):
                    details = {"error": f"Invalid details format: {details}"}
                    
                message = details.get("message", "No details provided")
                recommendations = compliance_report.get("recommendations", [])
                
                # Create a PolicyResult object
                policy_result = PolicyResult(
                    name=policy_title,
                    result=overall_result,
                    details=details,
                    recommendations=recommendations
                )
                
                # Add to the list of policy results
                policy_results.append(policy_result)
                logger.debug(f"Added policy result for {policy_name}")
            else:
                logger.warning(f"No compliance report found for {policy_name}")
                
                # Add a placeholder result for policies without a compliance report
                policy_result = PolicyResult(
                    name=policy_name.replace("_", " ").title(),
                    result=False,
                    details={"error": "No compliance report available"},
                    recommendations=[]
                )
                policy_results.append(policy_result)
    
    logger.info(f"Extracted {len(policy_results)} policy results from OPA evaluation")
    return policy_results

def extract_structured_data_from_debug(debug_output: str) -> Dict[str, Any]:
    """
    Extract structured data from OPA debug output.
    
    This function tries multiple strategies to extract JSON data from debug output:
    1. Look for complete JSON objects
    2. Parse specific sections of the debug output
    3. Extract policy-specific information
    
    Args:
        debug_output: String containing OPA debug output
        
    Returns:
        Dictionary containing structured data extracted from debug output,
        or None if no structured data could be extracted
    """
    # Strategy 1: Look for complete JSON objects
    try:
        import re
        import json
        
        # First try to find JSON data that starts with {"v1": {
        v1_json_match = re.search(r'(\{\s*"v1"\s*:[\s\S]*?\}\s*\}(?=\s*\n|\s*$))', debug_output)
        if v1_json_match:
            try:
                json_str = v1_json_match.group(1)
                # Try to parse it directly
                try:
                    json_data = json.loads(json_str)
                    if isinstance(json_data, dict) and "v1" in json_data:
                        return json_data
                except json.JSONDecodeError:
                    # If direct parsing fails, try to clean up the string
                    # Remove any trailing commas before closing braces
                    json_str = re.sub(r',\s*\}', '}', json_str)
                    # Ensure all property names are quoted
                    json_str = re.sub(r'([{,]\s*)([a-zA-Z0-9_]+)(\s*:)', r'\1"\2"\3', json_str)
                    # Try parsing again
                    json_data = json.loads(json_str)
                    if isinstance(json_data, dict) and "v1" in json_data:
                        return json_data
            except Exception as e:
                logger.warning(f"Error parsing v1 JSON object: {e}")
        
        # If that fails, try to find any JSON object in the output
        json_pattern = r'(\{(?:[^{}]|(?1))*\})'
        json_matches = list(re.finditer(json_pattern, debug_output, re.DOTALL))
        
        if json_matches:
            # Sort by length to find the largest JSON object
            json_matches.sort(key=lambda m: len(m.group(1)), reverse=True)
            
            for match in json_matches:
                try:
                    json_str = match.group(1)
                    # Try to parse it directly
                    try:
                        json_data = json.loads(json_str)
                        # Check if this looks like a valid OPA result
                        if isinstance(json_data, dict) and "v1" in json_data:
                            return json_data
                    except json.JSONDecodeError:
                        # If direct parsing fails, try to clean up the string
                        # Remove any trailing commas before closing braces
                        json_str = re.sub(r',\s*\}', '}', json_str)
                        # Ensure all property names are quoted
                        json_str = re.sub(r'([{,]\s*)([a-zA-Z0-9_]+)(\s*:)', r'\1"\2"\3', json_str)
                        # Try parsing again
                        json_data = json.loads(json_str)
                        if isinstance(json_data, dict) and "v1" in json_data:
                            return json_data
                except Exception:
                    continue
    except Exception as e:
        logger.warning(f"Error extracting JSON from debug output: {e}")
    
    # Strategy 2: Manual extraction of the JSON structure
    try:
        # Look for the start of the JSON object
        v1_start_match = re.search(r'{\s*"v1":', debug_output)
        if v1_start_match:
            start_pos = v1_start_match.start()
            # Find the matching closing brace
            brace_count = 1
            end_pos = start_pos + 1
            
            while brace_count > 0 and end_pos < len(debug_output):
                if debug_output[end_pos] == '{':
                    brace_count += 1
                elif debug_output[end_pos] == '}':
                    brace_count -= 1
                end_pos += 1
            
            if brace_count == 0:
                json_str = debug_output[start_pos:end_pos]
                try:
                    # Try to parse it directly
                    try:
                        json_data = json.loads(json_str)
                        return json_data
                    except json.JSONDecodeError:
                        # If direct parsing fails, try to clean up the string
                        # Remove any trailing commas before closing braces
                        json_str = re.sub(r',\s*\}', '}', json_str)
                        # Ensure all property names are quoted
                        json_str = re.sub(r'([{,]\s*)([a-zA-Z0-9_]+)(\s*:)', r'\1"\2"\3', json_str)
                        # Try parsing again
                        json_data = json.loads(json_str)
                        return json_data
                except Exception as e:
                    logger.warning(f"Error parsing manually extracted JSON: {e}")
    except Exception as e:
        logger.warning(f"Error during manual JSON extraction: {e}")
    
    # Strategy 3: Parse specific sections of the debug output
    try:
        result = {}
        
        # Look for policy evaluation results
        policy_sections = re.findall(r'data\.([a-zA-Z0-9_\.]+)\.([a-zA-Z0-9_]+)\.compliance_report', debug_output)
        
        for domain_path, policy_name in policy_sections:
            # Extract domain and policy information
            domain_parts = domain_path.split('.')
            
            # Extract compliance information - look for the specific structure in your example
            compliance_match = re.search(
                r'compliance_report.*?{.*?details.*?{.*?message.*?:.*?"(.*?)".*?}', 
                debug_output, 
                re.DOTALL
            )
            
            if compliance_match:
                message = compliance_match.group(1)
                
                # Build the nested structure
                current = result
                if "v1" not in current:
                    current["v1"] = {}
                current = current["v1"]
                
                for part in domain_parts:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                
                if policy_name not in current:
                    current[policy_name] = {}
                
                # Create a basic compliance report structure
                current[policy_name]["compliance_report"] = {
                    "overall_result": False,
                    "policy": f"{domain_parts[-1].capitalize()} {policy_name.replace('_', ' ').capitalize()}",
                    "version": "1.0.0",
                    "details": {
                        "message": message
                    }
                }
                
                # Look for recommendations
                recommendations_match = re.search(
                    r'recommendations.*?\[(.*?)\]', 
                    debug_output, 
                    re.DOTALL
                )
                
                if recommendations_match:
                    recommendations_str = recommendations_match.group(1)
                    recommendations = []
                    
                    # Extract individual recommendations
                    for rec_match in re.finditer(r'"(.*?)"', recommendations_str):
                        recommendations.append(rec_match.group(1))
                    
                    if recommendations:
                        current[policy_name]["compliance_report"]["recommendations"] = recommendations
                
                # Also look for allow, implementation_pending, and non_compliant
                allow_match = re.search(rf'{policy_name}\.allow.*?(true|false)', debug_output)
                if allow_match:
                    current[policy_name]["allow"] = allow_match.group(1) == "true"
                
                pending_match = re.search(rf'{policy_name}\.implementation_pending.*?(true|false)', debug_output)
                if pending_match:
                    current[policy_name]["implementation_pending"] = pending_match.group(1) == "true"
                    # Also add to compliance report
                    current[policy_name]["compliance_report"]["implementation_pending"] = pending_match.group(1) == "true"
                
                non_compliant_match = re.search(rf'{policy_name}\.non_compliant.*?(true|false)', debug_output)
                if non_compliant_match:
                    current[policy_name]["non_compliant"] = non_compliant_match.group(1) == "true"
        
        if "v1" in result:
            return result
    except Exception as e:
        logger.warning(f"Error parsing debug output sections: {e}")
    
    # Strategy 4: Direct extraction from the example format
    try:
        # Look for the specific format in the example
        pattern = r'{\s*"v1":\s*{\s*"([^"]+)":\s*{\s*"allow":\s*(true|false),\s*"compliance_report":\s*{\s*"details":\s*{\s*"message":\s*"([^"]+)"'
        match = re.search(pattern, debug_output, re.DOTALL)
        
        if match:
            policy_name = match.group(1)
            allow_value = match.group(2) == "true"
            message = match.group(3)
            
            # Create a basic result structure
            result = {
                "v1": {
                    policy_name: {
                        "allow": allow_value,
                        "compliance_report": {
                            "overall_result": False,
                            "policy": policy_name.replace("_", " ").capitalize(),
                            "version": "1.0.0",
                            "details": {
                                "message": message
                            }
                        }
                    }
                }
            }
            
            # Look for recommendations
            recommendations_match = re.search(
                r'"recommendations":\s*\[(.*?)\]', 
                debug_output, 
                re.DOTALL
            )
            
            if recommendations_match:
                recommendations_str = recommendations_match.group(1)
                recommendations = []
                
                # Extract individual recommendations
                for rec_match in re.finditer(r'"(.*?)"', recommendations_str):
                    recommendations.append(rec_match.group(1))
                
                if recommendations:
                    result["v1"][policy_name]["compliance_report"]["recommendations"] = recommendations
            
            return result
    except Exception as e:
        logger.warning(f"Error extracting from example format: {e}")
    
    # If all strategies fail, return None
    return None

def process_extracted_policy_data(extracted_data: Dict[str, Any]) -> List[PolicyResult]:
    """
    Process extracted policy data to create PolicyResult objects.
    
    Args:
        extracted_data: Dictionary containing structured data extracted from debug output
        
    Returns:
        List of PolicyResult objects
    """
    policy_results = []
    
    try:
        if "v1" in extracted_data:
            for domain, domain_data in extracted_data["v1"].items():
                for policy_name, policy_data in domain_data.items():
                    if isinstance(policy_data, dict) and "compliance_report" in policy_data:
                        report_data = policy_data["compliance_report"]
                        result = report_data.get("overall_result", False)
                        
                details = {
                            "policy": report_data.get("policy", f"{domain}.{policy_name}"),
                            "version": report_data.get("version", "1.0"),
                    "timestamp": datetime.now().isoformat()
                }
                # Extract recommendations if available
                if "recommendations" in report_data:
                    details["recommendations"] = report_data["recommendations"]
                
                # Extract message if available
                if "details" in report_data and "message" in report_data["details"]:
                    details["message"] = report_data["details"]["message"]
                policy_results.append(PolicyResult(
                    name=policy_name,
                    result=result,
                    details=details
                ))
    except Exception as e:
        logger.warning(f"Error processing extracted policy data: {e}")
        # Add a fallback policy result
        policy_results.append(PolicyResult(
            name="extracted_data",
            result=False,
            details={
                "error": f"Failed to process extracted data: {e}",
                "policy": "Fallback Policy", 
                "version": "1.0",
                "timestamp": datetime.now().isoformat()
            }
        ))
    
    return policy_results

def create_evaluation_report(
    evaluation_result: Dict[str, Any], 
    opa_results: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a report data structure from evaluation results.
    
    Args:
        evaluation_result: The evaluation results from Phase 1
        opa_results: Optional OPA evaluation results
        
    Returns:
        Dict containing structured report data
    """
    if opa_results is None:
        opa_results = {}
    
    # Extract application name
    app_name = evaluation_result.get("app_name", evaluation_result.get("application_name", "Unknown Application"))
    
    # Initialize counters
    total_policies = 0
    passed_policies = 0
    
    # Process policy results
    policy_results = []
    
    # First handle any direct metrics in the evaluation result
    if "metrics" in evaluation_result:
        metrics_data = evaluation_result["metrics"]
        if isinstance(metrics_data, dict):
            policy_result = {
                "is_nested": False,
                "policy": "Direct Evaluation",
                "result": all(m.get("control_passed", False) for m in metrics_data.values()),
                "metrics": {
                    key: {
                        "name": m.get("name", key),
                        "value": m.get("value"),
                        "control_passed": m.get("control_passed", False)
                    }
                    for key, m in metrics_data.items()
                }
            }
            policy_results.append(policy_result)
            total_policies += 1
            if policy_result["result"]:
                passed_policies += 1

    # Then process nested results in evaluation_result
    if "result" in evaluation_result:
        result_data = evaluation_result["result"]
        if isinstance(result_data, dict):
            for policy_name, policy_data in result_data.items():
                if isinstance(policy_data, dict):
                    # Handle nested policy structure
                    if "details" in policy_data:
                        nested_details = {}
                        nested_passed = 0
                        nested_total = 0
                        
                        for path, details in policy_data["details"].items():
                            metrics = details.get("metrics", {})
                            if isinstance(metrics, dict):
                                nested_details[path] = {
                                    "name": details.get("name", path),
                                    "passed": all(m.get("control_passed", False) for m in metrics.values()),
                                    "metrics": {
                                        key: {
                                            "name": m.get("name", key),
                                            "value": m.get("value"),
                                            "control_passed": m.get("control_passed", False)
                                        }
                                        for key, m in metrics.items()
                                    }
                                }
                                nested_total += 1
                                if nested_details[path]["passed"]:
                                    nested_passed += 1
                        
                        if nested_total > 0:
                            success_rate = f"{(nested_passed / nested_total) * 100:.1f}%"
                            policy_results.append({
                                "is_nested": True,
                                "policy": policy_name,
                                "result": nested_passed == nested_total,
                                "summary": {
                                    "success_rate": success_rate,
                                    "total": nested_total,
                                    "passed": nested_passed,
                                    "failed": nested_total - nested_passed
                                },
                                "details": nested_details
                            })
                            total_policies += nested_total
                            passed_policies += nested_passed
                    # Handle flat policy structure
                    elif "metrics" in policy_data:
                        metrics = policy_data["metrics"]
                        if isinstance(metrics, dict):
                            policy_result = {
                                "is_nested": False,
                                "policy": policy_name,
                                "result": all(m.get("control_passed", False) for m in metrics.values()),
                                "metrics": {
                                    key: {
                                        "name": m.get("name", key),
                                        "value": m.get("value"),
                                        "control_passed": m.get("control_passed", False)
                                    }
                                    for key, m in metrics.items()
                                }
                            }
                            policy_results.append(policy_result)
                            total_policies += 1
                            if policy_result["result"]:
                                passed_policies += 1
    
    # Process OPA results directly
    if opa_results:
        # Handle aggregated individual results format
        if "result" in opa_results:
            result_data = opa_results["result"]
            if isinstance(result_data, dict):
                # Common OPA result structure with policy field
                if "policy" in result_data:
                    policy_name = result_data.get("policy", "OPA Policy")
                    
                    # Handle aggregated results with a results array
                    if "results" in result_data and isinstance(result_data["results"], list):
                        for result in result_data["results"]:
                            if isinstance(result, dict):
                                sub_policy_name = result.get("policy", "Unknown Policy")
                                result_value = result.get("result", {})
                                
                                # Extract metrics
                                metrics = {}
                                if "metrics" in result_value:
                                    metrics = result_value["metrics"]
                                elif "expressions" in result_value and result_value["expressions"]:
                                    for expr in result_value["expressions"]:
                                        if "value" in expr and "metrics" in expr["value"]:
                                            metrics = expr["value"]["metrics"]
                                            break
                                
                                if metrics:
                                    all_passed = all(m.get("control_passed", False) for m in metrics.values())
                                    
                                    policy_result = {
                                        "is_nested": False,
                                        "policy": sub_policy_name,
                                        "result": all_passed,
                                        "metrics": {
                                            key: {
                                                "name": m.get("name", key),
                                                "value": m.get("value"),
                                                "control_passed": m.get("control_passed", False)
                                            }
                                            for key, m in metrics.items()
                                        }
                                    }
                                    policy_results.append(policy_result)
                                    total_policies += 1
                                    if all_passed:
                                        passed_policies += 1
                    
                    # Handle direct result with metrics
                    elif "metrics" in result_data:
                        metrics = result_data["metrics"]
                        if isinstance(metrics, dict):
                            all_passed = all(m.get("control_passed", False) for m in metrics.values())
                            
                            policy_result = {
                                "is_nested": False,
                                "policy": policy_name,
                                "result": all_passed,
                                "metrics": {
                                    key: {
                                        "name": m.get("name", key),
                                        "value": m.get("value"),
                                        "control_passed": m.get("control_passed", False)
                                    }
                                    for key, m in metrics.items()
                                }
                            }
                            policy_results.append(policy_result)
                            total_policies += 1
                            if all_passed:
                                passed_policies += 1
                
                # Handle nested policy results without the "policy" field
                elif not any(key in ["policy", "metrics"] for key in result_data):
                    for policy_name, policy_data in result_data.items():
                        if isinstance(policy_data, dict):
                            # Check for metrics directly in the policy data
                            if "metrics" in policy_data:
                                metrics = policy_data["metrics"]
                                if isinstance(metrics, dict):
                                    all_passed = all(m.get("control_passed", False) for m in metrics.values())
                                    
                                    policy_result = {
                                        "is_nested": False,
                                        "policy": policy_name,
                                        "result": all_passed,
                                        "metrics": {
                                            key: {
                                                "name": m.get("name", key),
                                                "value": m.get("value"),
                                                "control_passed": m.get("control_passed", False)
                                            }
                                            for key, m in metrics.items()
                                        }
                                    }
                                    policy_results.append(policy_result)
                                    total_policies += 1
                                    if all_passed:
                                        passed_policies += 1
                                    
                            # Handle expressions format
                            elif "expressions" in policy_data and policy_data["expressions"]:
                                for expr in policy_data["expressions"]:
                                    if "value" in expr and "metrics" in expr["value"]:
                                        metrics = expr["value"]["metrics"]
                                        if isinstance(metrics, dict):
                                            all_passed = all(m.get("control_passed", False) for m in metrics.values())
                                            
                                            policy_result = {
                                                "is_nested": False,
                                                "policy": policy_name,
                                                "result": all_passed,
                                                "metrics": {
                                                    key: {
                                                        "name": m.get("name", key),
                                                        "value": m.get("value"),
                                                        "control_passed": m.get("control_passed", False)
                                                    }
                                                    for key, m in metrics.items()
                                                }
                                            }
                                            policy_results.append(policy_result)
                                            total_policies += 1
                                            if all_passed:
                                                passed_policies += 1
                                                
                            # Handle nested structure without metrics directly
                            elif isinstance(policy_data, dict) and not any(key in ["metrics", "expressions"] for key in policy_data):
                                nested_details = {}
                                nested_passed = 0
                                nested_total = 0
                                
                                for sub_policy, details in policy_data.items():
                                    metrics = {}
                                    if isinstance(details, dict):
                                        if "metrics" in details:
                                            metrics = details["metrics"]
                                        elif "expressions" in details and details["expressions"]:
                                            for expr in details["expressions"]:
                                                if "value" in expr and "metrics" in expr["value"]:
                                                    metrics = expr["value"]["metrics"]
                                                    break
                                    
                                    if metrics and isinstance(metrics, dict):
                                        passed = all(m.get("control_passed", False) for m in metrics.values())
                                        nested_details[sub_policy] = {
                                            "name": sub_policy,
                                            "passed": passed,
                                            "metrics": {
                                                key: {
                                                    "name": m.get("name", key),
                                                    "value": m.get("value"),
                                                    "control_passed": m.get("control_passed", False)
                                                }
                                                for key, m in metrics.items()
                                            }
                                        }
                                        nested_total += 1
                                        if passed:
                                            nested_passed += 1
                                
                                if nested_total > 0:
                                    success_rate = f"{(nested_passed / nested_total) * 100:.1f}%" if nested_total > 0 else "0.0%"
                                    policy_results.append({
                                        "is_nested": True,
                                        "policy": policy_name,
                                        "result": nested_passed == nested_total,
                                        "summary": {
                                            "success_rate": success_rate,
                                            "total": nested_total,
                                            "passed": nested_passed,
                                            "failed": nested_total - nested_passed
                                        },
                                        "details": nested_details
                                    })
                                    total_policies += nested_total
                                    passed_policies += nested_passed
    
    # Calculate progress class (0-100 in steps of 10)
    progress_class = 0
    if total_policies > 0:
        progress = (passed_policies / total_policies) * 100
        progress_class = round(progress / 10) * 10
    
    # Create the report data structure matching our template
    report_data = {
        "APP_TITLE": "aicertify Self-Assessment Report",
        "EVAL_DATE": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "USER_INFO": os.getenv("USER", "local_user"),
        "APP_NAME": app_name,
        "REGULATIONS_LIST": ["EU AI Act"],  # This could be made dynamic based on policy category
        "TOTAL_POLICIES": total_policies,
        "GREEN_COUNT": passed_policies,
        "RED_COUNT": total_policies - passed_policies,
        "PROGRESS_CLASS": str(progress_class),  # Convert to string to match template expectations
        "EXEC_SUMMARY": f"Evaluation shows {progress_class}% of controls passing.",
        "POLICY_RESULTS": policy_results,
        "TERMINOLOGY": (
            "1. **Controls:** Individual compliance checks within policies.\n"
            "2. **Policies:** Groups of related compliance controls.\n"
            "3. **Regulations:** Overarching regulatory frameworks.\n"
            "4. **Nested Policies:** Policies organized in hierarchical structures."
        ),
        "FULL_DISCLAIMER": (
            "This report is generated based on automated evaluation of AI system compliance. "
            "While we strive for accuracy, this assessment should not be considered as legal advice. "
            "Please consult with appropriate legal and compliance experts for definitive guidance."
        ),
        "CURRENT_YEAR": datetime.now().year
    }
    
    return report_data 