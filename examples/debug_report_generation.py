#!/usr/bin/env python
"""
Debug script for report generation in AICertify.
This script helps diagnose issues with report generation by tracing data flow.
"""

import json
import logging
import os
import sys
from pprint import pformat

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from aicertify.report_generation.data_extraction import (
    extract_application_details,
    extract_fairness_metrics,
    extract_toxicity_metrics,
    extract_stereotype_metrics,
    extract_policy_results,
    create_evaluation_report,
    process_extracted_policy_data
)
from aicertify.report_generation.report_generator import ReportGenerator
from aicertify.models.report import PolicyResult

# Import flexible extraction system
from aicertify.report_generation.flexible_extraction import extract_metrics as flexible_extract_metrics
from aicertify.report_generation.config import set_feature_flag, use_flexible_extraction

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("report_debug")

def load_sample_data(file_path):
    """Load sample data from a JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading sample data from {file_path}: {str(e)}")
        return None

def debug_extraction_functions(evaluation_result, opa_results):
    """Debug the extraction functions by logging their inputs and outputs."""
    
    logger.info("=== DEBUGGING EXTRACTION FUNCTIONS ===")
    
    # Debug application details extraction
    logger.info("--- Application Details Extraction ---")
    app_details = extract_application_details(evaluation_result)
    logger.info(f"Extracted application details: {app_details}")
    
    # Debug fairness metrics extraction
    logger.info("--- Fairness Metrics Extraction ---")
    fairness_metrics = extract_fairness_metrics(evaluation_result)
    logger.info(f"Extracted fairness metrics: {fairness_metrics}")
    
    # Debug toxicity metrics extraction
    logger.info("--- Toxicity Metrics Extraction ---")
    toxicity_metrics = extract_toxicity_metrics(evaluation_result)
    logger.info(f"Extracted toxicity metrics: {toxicity_metrics}")
    
    # Debug stereotype metrics extraction
    logger.info("--- Stereotype Metrics Extraction ---")
    stereotype_metrics = extract_stereotype_metrics(evaluation_result)
    logger.info(f"Extracted stereotype metrics: {stereotype_metrics}")
    
    # Debug policy results extraction
    logger.info("--- Policy Results Extraction ---")
    if opa_results:
        try:
            logger.info("Detailed debugging for policy results extraction:")
            
            # Log the structure of opa_results
            logger.debug(f"OPA results type: {type(opa_results)}")
            if isinstance(opa_results, dict):
                logger.debug(f"OPA results keys: {list(opa_results.keys())}")
                
                # Check for 'result' key
                if 'result' in opa_results:
                    logger.debug(f"Result type: {type(opa_results['result'])}")
                    if isinstance(opa_results['result'], dict):
                        logger.debug(f"Result keys: {list(opa_results['result'].keys())}")
                        
                        # Check for 'expressions' key
                        if 'expressions' in opa_results['result']:
                            logger.debug(f"Expressions type: {type(opa_results['result']['expressions'])}")
                            if isinstance(opa_results['result']['expressions'], list):
                                logger.debug(f"Expressions length: {len(opa_results['result']['expressions'])}")
                                
                                # Check first expression
                                if len(opa_results['result']['expressions']) > 0:
                                    first_expr = opa_results['result']['expressions'][0]
                                    logger.debug(f"First expression type: {type(first_expr)}")
                                    if isinstance(first_expr, dict):
                                        logger.debug(f"First expression keys: {list(first_expr.keys())}")
                                        
                                        # Check for 'value' key
                                        if 'value' in first_expr:
                                            logger.debug(f"Value type: {type(first_expr['value'])}")
                                            if isinstance(first_expr['value'], dict):
                                                logger.debug(f"Value keys: {list(first_expr['value'].keys())}")
                                                
                                                # Check for 'v1' key
                                                if 'v1' in first_expr['value']:
                                                    logger.debug(f"v1 type: {type(first_expr['value']['v1'])}")
                                                    if isinstance(first_expr['value']['v1'], dict):
                                                        logger.debug(f"v1 keys: {list(first_expr['value']['v1'].keys())}")
                                                        logger.debug(f"v1 length: {len(first_expr['value']['v1'])}")
            
            policy_results = extract_policy_results(opa_results)
            logger.info(f"Extracted policy results: {policy_results}")
        except Exception as e:
            logger.error(f"Error extracting policy results: {str(e)}")
    else:
        logger.warning("No OPA results provided, skipping policy results extraction")
    
    # Debug flexible extraction system
    logger.info("--- Flexible Extraction System ---")
    
    # Test with flexible extraction disabled
    set_feature_flag("use_flexible_extraction", False)
    logger.info(f"Flexible extraction enabled: {use_flexible_extraction()}")
    
    # Create evaluation report with legacy system
    legacy_report = create_evaluation_report(evaluation_result, opa_results)
    logger.info("Created evaluation report with legacy system")
    logger.info(f"Legacy report metric groups: {[group.name for group in legacy_report.metric_groups]}")
    for group in legacy_report.metric_groups:
        logger.info(f"Legacy {group.name} metrics: {len(group.metrics)}")
        for metric in group.metrics:
            logger.info(f"  {metric.name}: {metric.value}")
    
    # Test with flexible extraction enabled
    set_feature_flag("use_flexible_extraction", True)
    logger.info(f"Flexible extraction enabled: {use_flexible_extraction()}")
    
    # Extract metrics with flexible system
    flexible_metrics = flexible_extract_metrics(evaluation_result)
    logger.info(f"Extracted metrics with flexible system: {list(flexible_metrics.keys())}")
    for metric_type, metrics in flexible_metrics.items():
        logger.info(f"Flexible {metric_type} metrics: {len(metrics)}")
        for metric in metrics:
            logger.info(f"  {metric.name}: {metric.value}")
    
    # Create evaluation report with flexible system
    flexible_report = create_evaluation_report(evaluation_result, opa_results)
    logger.info("Created evaluation report with flexible system")
    logger.info(f"Flexible report metric groups: {[group.name for group in flexible_report.metric_groups]}")
    for group in flexible_report.metric_groups:
        logger.info(f"Flexible {group.name} metrics: {len(group.metrics)}")
        for metric in group.metrics:
            logger.info(f"  {metric.name}: {metric.value}")
    
    # Compare reports
    logger.info("--- Comparing Reports ---")
    
    # Compare metric groups
    legacy_groups = {group.name: group for group in legacy_report.metric_groups}
    flexible_groups = {group.name: group for group in flexible_report.metric_groups}
    
    logger.info(f"Legacy metric groups: {list(legacy_groups.keys())}")
    logger.info(f"Flexible metric groups: {list(flexible_groups.keys())}")
    
    # Compare metrics in common groups
    for group_name in set(legacy_groups.keys()) & set(flexible_groups.keys()):
        legacy_metrics = {metric.name: metric.value for metric in legacy_groups[group_name].metrics}
        flexible_metrics = {metric.name: metric.value for metric in flexible_groups[group_name].metrics}
        
        logger.info(f"Comparing {group_name} metrics:")
        logger.info(f"  Legacy metrics: {list(legacy_metrics.keys())}")
        logger.info(f"  Flexible metrics: {list(flexible_metrics.keys())}")
        
        # Check for differences
        for metric_name in set(legacy_metrics.keys()) & set(flexible_metrics.keys()):
            if legacy_metrics[metric_name] != flexible_metrics[metric_name]:
                logger.warning(f"  Difference in {metric_name}: Legacy={legacy_metrics[metric_name]}, Flexible={flexible_metrics[metric_name]}")
            else:
                logger.info(f"  Match in {metric_name}: {legacy_metrics[metric_name]}")
        
        # Check for metrics only in legacy
        for metric_name in set(legacy_metrics.keys()) - set(flexible_metrics.keys()):
            logger.warning(f"  Metric {metric_name} only in legacy: {legacy_metrics[metric_name]}")
        
        # Check for metrics only in flexible
        for metric_name in set(flexible_metrics.keys()) - set(legacy_metrics.keys()):
            logger.warning(f"  Metric {metric_name} only in flexible: {flexible_metrics[metric_name]}")
    
    # Check for groups only in legacy
    for group_name in set(legacy_groups.keys()) - set(flexible_groups.keys()):
        logger.warning(f"Group {group_name} only in legacy")
    
    # Check for groups only in flexible
    for group_name in set(flexible_groups.keys()) - set(legacy_groups.keys()):
        logger.warning(f"Group {group_name} only in flexible")
    
    # Generate reports with both systems
    logger.info("--- Generating Reports ---")
    
    # Generate report with legacy system
    set_feature_flag("use_flexible_extraction", False)
    report_generator = ReportGenerator()
    legacy_report_path = "temp_reports/debug_report_legacy.md"
    legacy_md_content = report_generator.generate_markdown_report(legacy_report)
    with open(legacy_report_path, "w") as f:
        f.write(legacy_md_content)
    logger.info(f"Generated legacy report at {legacy_report_path}")
    
    # Generate report with flexible system
    set_feature_flag("use_flexible_extraction", True)
    flexible_report_path = "temp_reports/debug_report_flexible.md"
    flexible_md_content = report_generator.generate_markdown_report(flexible_report)
    with open(flexible_report_path, "w") as f:
        f.write(flexible_md_content)
    logger.info(f"Generated flexible report at {flexible_report_path}")

def find_latest_captured_data():
    """Find the latest captured data files."""
    capture_dir = "temp_reports/captured_data"
    if not os.path.exists(capture_dir):
        logger.warning(f"Capture directory {capture_dir} does not exist.")
        return None, None
    
    # Find latest evaluation result
    eval_files = [f for f in os.listdir(capture_dir) if f.startswith("evaluation_result_")]
    if not eval_files:
        logger.warning("No evaluation result files found.")
        return None, None
    
    latest_eval_file = max(eval_files)
    eval_result_path = os.path.join(capture_dir, latest_eval_file)
    
    # Find latest OPA results
    opa_files = [f for f in os.listdir(capture_dir) if f.startswith("opa_results_")]
    if not opa_files:
        logger.warning("No OPA result files found.")
        opa_results_path = None
    else:
        latest_opa_file = max(opa_files)
        opa_results_path = os.path.join(capture_dir, latest_opa_file)
    
    logger.info(f"Found latest evaluation result: {eval_result_path}")
    if opa_results_path:
        logger.info(f"Found latest OPA results: {opa_results_path}")
    else:
        logger.info("No OPA results found.")
    
    return eval_result_path, opa_results_path

def create_realistic_sample_data():
    """Create more realistic sample data based on the actual structure."""
    
    # Create sample evaluation result with realistic structure
    sample_evaluation_result = {
        "contract_id": "test-contract-id",
        "application_name": "Medical Diagnosis Assistant",
        "interaction_count": 5,
        "fairness_metrics": {
            "counterfactual_score": 0.556,
            "stereotype_score": 1.0,
            "combined_score": 0.778,
            "details": {
                "sentiment_bias": 0.333,
                "bleu_similarity": 0.5,
                "rouge_similarity": 0.5,
                "gender_bias": False,
                "racial_bias": False
            }
        },
        "content_safety": {
            "score": 1.0,
            "compliant": True,
            "details": {
                "toxic_fraction": 0.0,
                "max_toxicity": 0.0,
                "toxicity_probability": 0.0
            }
        },
        "risk_management": {
            "score": 0.05,
            "compliant": False
        }
    }
    
    # Create sample OPA results with realistic structure
    sample_opa_results = {
        "result": [
            {
                "expressions": [
                    {
                        "value": {
                            "v1": {
                                "patient_safety": {
                                    "allow": False,
                                    "compliance_report": {
                                        "details": {
                                            "message": "Healthcare patient safety policy implementation is pending."
                                        },
                                        "implementation_pending": True,
                                        "overall_result": False,
                                        "policy": "Healthcare Patient Safety Requirements",
                                        "recommendations": [
                                            "Check back for future releases with healthcare-specific evaluations",
                                            "Consider using global compliance policies in the meantime"
                                        ],
                                        "status": "PLACEHOLDER - Pending detailed implementation",
                                        "version": "1.0.0"
                                    }
                                },
                                "diagnostic_safety": {
                                    "allow": False,
                                    "compliance_report": {
                                        "details": {
                                            "message": "Diagnostic safety requirements not fully implemented."
                                        },
                                        "implementation_pending": True,
                                        "overall_result": False,
                                        "policy": "Diagnostic Safety Requirements",
                                        "recommendations": [
                                            "Implement confidence scoring for diagnoses",
                                            "Add uncertainty quantification"
                                        ],
                                        "status": "PARTIAL - Some requirements implemented",
                                        "version": "1.0.0"
                                    }
                                }
                            }
                        }
                    }
                ]
            }
        ]
    }
    
    return sample_evaluation_result, sample_opa_results

def main():
    """Main function to run the debug script."""
    logger.info("Starting report generation debug script")
    
    # Create a directory for sample data if it doesn't exist
    os.makedirs("temp_reports/debug_data", exist_ok=True)
    
    # Try to find latest captured data
    eval_result_path, opa_results_path = find_latest_captured_data()
    
    # If no captured data, use sample data files
    if not eval_result_path:
        eval_result_path = "temp_reports/debug_data/sample_evaluation_result.json"
        opa_results_path = "temp_reports/debug_data/sample_opa_results.json"
        
        # Create more realistic sample data
        logger.info("Creating realistic sample data...")
        sample_evaluation_result, sample_opa_results = create_realistic_sample_data()
        
        # Save sample data
        with open(eval_result_path, "w") as f:
            json.dump(sample_evaluation_result, f, indent=2)
        
        with open(opa_results_path, "w") as f:
            json.dump(sample_opa_results, f, indent=2)
        
        logger.info(f"Created sample data files at {eval_result_path} and {opa_results_path}")
        logger.info(f"Sample evaluation result structure: {list(sample_evaluation_result.keys())}")
        logger.info(f"Sample OPA results structure: {list(sample_opa_results.keys())}")
    
    # Load data
    evaluation_result = load_sample_data(eval_result_path)
    opa_results = None
    if opa_results_path and os.path.exists(opa_results_path):
        opa_results = load_sample_data(opa_results_path)
    
    if evaluation_result:
        # Debug extraction functions
        debug_extraction_functions(evaluation_result, opa_results)
    else:
        logger.error("Failed to load evaluation result data. Cannot proceed with debugging.")

if __name__ == "__main__":
    main() 