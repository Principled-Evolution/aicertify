"""
AICertify API

A simple entry point for developers to integrate AICertify evaluation into their applications.
This module provides functions to evaluate AI interactions for compliance with various policies.
"""

import json
import asyncio
import logging
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Import models and evaluation components
from aicertify.models.contract_models import AiCertifyContract, load_contract
from aicertify.models.langfair_eval import ToxicityMetrics, StereotypeMetrics

# Try to import the full evaluator, but provide a fallback
try:
    from aicertify.evaluators.api import AICertifyEvaluator
    FULL_EVALUATOR_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Full evaluator not available, will use simplified evaluator: {e}")
    FULL_EVALUATOR_AVAILABLE = False

# Import the simplified evaluator that has minimal dependencies
from aicertify.evaluators.simple_evaluator import evaluate_contract_simple

# Import report generation components
from aicertify.report_generation.report_generator import ReportGenerator
try:
    # Import our new data extraction module
    from aicertify.report_generation.data_extraction import create_evaluation_report
    REPORT_DATA_EXTRACTION_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Report data extraction module not available: {e}")
    REPORT_DATA_EXTRACTION_AVAILABLE = False

def _ensure_valid_evaluation_structure(evaluation_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure the evaluation result has a valid structure for policy evaluation.
    
    Args:
        evaluation_result: The evaluation result to validate and fix
        
    Returns:
        A validated and fixed evaluation result
    """
    if evaluation_result is None:
        evaluation_result = {}
    
    # Ensure metrics exists
    if "metrics" not in evaluation_result:
        evaluation_result["metrics"] = {}
    
    # Ensure toxicity metrics exist
    if "toxicity" not in evaluation_result["metrics"]:
        evaluation_result["metrics"]["toxicity"] = {}
    
    # Ensure toxicity values are valid
    toxicity = evaluation_result["metrics"]["toxicity"]
    if not isinstance(toxicity.get("toxic_fraction"), (int, float)):
        toxicity["toxic_fraction"] = 0.0
    if not isinstance(toxicity.get("max_toxicity"), (int, float)):
        toxicity["max_toxicity"] = 0.0
    if not isinstance(toxicity.get("toxicity_probability"), (int, float)):
        toxicity["toxicity_probability"] = 0.0
    
    # Ensure summary exists
    if "summary" not in evaluation_result:
        evaluation_result["summary"] = {}
    
    # Ensure toxicity_values exists in summary
    if "toxicity_values" not in evaluation_result["summary"]:
        evaluation_result["summary"]["toxicity_values"] = {
            "toxic_fraction": toxicity.get("toxic_fraction", 0.0),
            "max_toxicity": toxicity.get("max_toxicity", 0.0),
            "toxicity_probability": toxicity.get("toxicity_probability", 0.0)
        }
    
    # Ensure stereotype_values exists in summary
    if "stereotype_values" not in evaluation_result["summary"]:
        evaluation_result["summary"]["stereotype_values"] = {
            "gender_bias_detected": False,
            "racial_bias_detected": False
        }
    
    # Create the evaluation structure expected by OPA policies
    if "evaluation" not in evaluation_result:
        evaluation_result["evaluation"] = {
            "toxicity_score": toxicity.get("max_toxicity", 0.0),
            "toxic_fraction": toxicity.get("toxic_fraction", 0.0),
            "toxicity_probability": toxicity.get("toxicity_probability", 0.0),
            "gender_bias_detected": evaluation_result["summary"].get("stereotype_values", {}).get("gender_bias_detected", False),
            "racial_bias_detected": evaluation_result["summary"].get("stereotype_values", {}).get("racial_bias_detected", False)
        }
    
    return evaluation_result

# Expose key functions at the top level for developer convenience
async def generate_report(
    evaluation_result: Dict[str, Any],
    opa_results: Dict[str, Any] = None,
    output_formats: List[str] = ["markdown"],
    output_dir: Optional[str] = None
) -> Dict[str, str]:
    """
    Generate evaluation reports from evaluation results.
    
    This function provides a simple one-line method to generate reports from
    evaluation results, making it easy for developers to get well-formatted
    reports without understanding the internal details.
    
    Args:
        evaluation_result: The evaluation results from evaluate_contract
        opa_results: The OPA policy results (if separate from evaluation_result)
        output_formats: List of formats to generate ("markdown", "pdf", or both)
        output_dir: Directory to save reports (creates reports/ if not specified)
        
    Returns:
        Dictionary with paths to the generated reports by format
    """
    # Validate and fix evaluation result structure
    evaluation_result = _ensure_valid_evaluation_structure(evaluation_result)
    
    # Extract OPA results from evaluation_result if not provided separately
    if opa_results is None:
        if "policy_results" in evaluation_result:
            opa_results = evaluation_result["policy_results"]
        elif "policies" in evaluation_result:
            opa_results = evaluation_result["policies"]
        else:
            opa_results = {}
    
    try:
        # Create a report generator instance directly
        from aicertify.report_generation.report_generator import ReportGenerator
        
        # Try to use data extraction if available
        data_extraction_available = False
        try:
            from aicertify.report_generation.data_extraction import create_evaluation_report
            data_extraction_available = True
        except ImportError:
            logger.warning("Report data extraction module not available, using fallback")
        
        if data_extraction_available:
            report_model = create_evaluation_report(evaluation_result, opa_results)
        else:
            # Create a minimal report model with basic information
            from aicertify.report_generation.report_models import (
                EvaluationReport, ApplicationDetails,
                MetricGroup, MetricValue, PolicyResult
            )
            
            app_name = evaluation_result.get("app_name", "Unknown")
            report_model = EvaluationReport(
                app_details=ApplicationDetails(
                    name=app_name,
                    evaluation_mode="Standard",
                    contract_count=0,
                    evaluation_date=datetime.now()
                ),
                metric_groups=[],
                policy_results=[],
                summary="Basic evaluation report"
            )
        
        # Generate reports
        report_gen = ReportGenerator()
        report_paths = {}
        
        # Setup output directory
        if not output_dir:
            output_dir = Path.cwd() / "reports"
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True, parents=True)
        
        # Get application name for the filename
        app_name = report_model.app_details.name.replace(" ", "_")
        if app_name == "Unknown_Application" and "application_name" in evaluation_result:
            app_name = evaluation_result["application_name"].replace(" ", "_")
        
        # Get a timestamp for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # *** Always generate the markdown content for PDF conversion ***
        md_content = report_gen.generate_markdown_report(report_model)
        
        # Markdown report generation if requested
        if "markdown" in output_formats:
            md_path = output_dir / f"report_{app_name}_{timestamp}.md"
            with open(md_path, "w") as f:
                f.write(md_content)
            report_paths["markdown"] = str(md_path)
            logger.info(f"Markdown report saved to: {md_path}")
        
        # PDF report generation
        if "pdf" in output_formats:
            pdf_path = output_dir / f"report_{app_name}_{timestamp}.pdf"
            pdf_result = report_gen.generate_pdf_report(md_content, str(pdf_path))
            if pdf_result:
                report_paths["pdf"] = pdf_result
                logger.info(f"PDF report saved to: {pdf_result}")
        
        return report_paths
    except ImportError as e:
        logger.error(f"Required modules for report generation not available: {e}")
        return {"error": f"Report generation failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Error generating reports: {e}")
        return {"error": f"Report generation failed: {str(e)}"}

async def evaluate_contract(
    contract_path: str,  # Path to contract file
    policy_category: str = "eu_ai_act",  # Policy to evaluate against
    use_simple_evaluator: bool = False,  # Optional flag for simplified evaluation
) -> Tuple[Dict[str, Any], Dict[str, Any]]:  # Return (evaluation_result, opa_results)
    """
    Evaluate a contract against specified policies.
    
    This function handles all evaluation logic internally, including:
    - Loading the contract
    - Running the appropriate evaluator
    - Handling any errors that occur during evaluation
    - Applying policy validation
    
    Args:
        contract_path: Path to the contract file
        policy_category: Policy category to evaluate against
        use_simple_evaluator: Whether to use simplified evaluation
        
    Returns:
        Tuple containing (evaluation_result, opa_results)
    """
    # Load contract
    contract = load_contract(contract_path)
    
    # Use the appropriate evaluator
    # (Handle ALL errors internally)
    # ...
    
    # Return standardized results
    return evaluation_result, opa_results

async def evaluate_contract_object(
    contract: AiCertifyContract,
    policy_category: str = "eu_ai_act",
    generate_report: bool = True,
    report_format: str = "markdown",
    output_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Evaluate a contract object directly.
    
    Args:
        contract: AiCertifyContract object
        policy_category: OPA policy category to evaluate against
        generate_report: Whether to generate an evaluation report
        report_format: Format of the report ("markdown" or "pdf")
        output_dir: Directory to save evaluation results and reports
    
    Returns:
        Dictionary containing evaluation results, policy validation, and report
    """
    # Create evaluator
    evaluator = AICertifyEvaluator()
    
    # Convert contract to conversations format
    conversations = []
    for interaction in contract.interactions:
        conversation = {
            "user_input": interaction.input_text,
            "response": interaction.output_text,
            "metadata": interaction.metadata
        }
        conversations.append(conversation)
    
    # Evaluate conversations
    try:
        evaluation_result = await evaluator.evaluate_conversations(
            app_name=contract.application_name,
            conversations=conversations
        )
        
        # Validate and fix evaluation result structure
        evaluation_result = _ensure_valid_evaluation_structure(evaluation_result)
        
    except Exception as e:
        logger.error(f"Error during evaluation: {e}")
        return {"error": f"Evaluation failed: {str(e)}"}
    
    # Apply OPA policies
    try:
        opa_results = evaluator.evaluate_policy(
            evaluation_result=evaluation_result,
            policy_category=policy_category
        )
    except Exception as e:
        logger.error(f"Error during policy validation: {e}")
        # Create a minimal but valid policy result structure
        opa_results = {
            "error": f"Policy validation failed: {str(e)}",
            "available_categories": [],
            "fairness": {
                "result": [
                    {
                        "expressions": [
                            {
                                "value": {
                                    "overall_result": False,
                                    "policy": "Error in evaluation",
                                    "recommendations": [
                                        f"Fix evaluation error: {str(e)}"
                                    ]
                                }
                            }
                        ]
                    }
                ]
            }
        }
        
    # Create result dictionary
    result = {
        "evaluation": evaluation_result,
        "policies": opa_results,
        "contract_id": str(contract.contract_id),
        "application_name": contract.application_name
    }
    
    # Generate report if requested
    if generate_report:
        try:
            report = evaluator.generate_report(
                evaluation_result=evaluation_result,
                opa_results=opa_results,
                output_format=report_format
            )
            result["report"] = report
            
            # Save report to file if output_dir is specified
            if output_dir:
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
                
                report_filename = f"report_{contract.application_name}_{contract.contract_id}.md"
                report_path = output_path / report_filename
                
                with open(report_path, "w") as f:
                    f.write(report)
                
                result["report_path"] = str(report_path)
                
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            result["report_error"] = str(e)
    
    return result

async def evaluate_conversations(
    app_name: str,
    conversations: List[Dict[str, Any]],
    policy_category: str = "eu_ai_act",
    generate_report: bool = True,
    report_format: str = "markdown",
    output_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Evaluate a list of conversations directly.
    
    This is a convenience function for developers who want to evaluate conversations
    without creating a contract object first.
    
    Args:
        app_name: Name of the application
        conversations: List of conversation dictionaries with 'user_input' and 'response' keys
        policy_category: OPA policy category to evaluate against
        generate_report: Whether to generate an evaluation report
        report_format: Format of the report ("markdown" or "pdf")
        output_dir: Directory to save evaluation results and reports
    
    Returns:
        Dictionary containing evaluation results, policy validation, and report
    """
    # Create evaluator
    evaluator = AICertifyEvaluator()
    
    # Evaluate conversations
    try:
        evaluation_result = await evaluator.evaluate_conversations(
            app_name=app_name,
            conversations=conversations
        )
        
        # Validate and fix evaluation result structure
        evaluation_result = _ensure_valid_evaluation_structure(evaluation_result)
        
    except Exception as e:
        logger.error(f"Error during evaluation: {e}")
        return {"error": f"Evaluation failed: {str(e)}"}
    
    # Apply OPA policies
    try:
        opa_results = evaluator.evaluate_policy(
            evaluation_result=evaluation_result,
            policy_category=policy_category
        )
    except Exception as e:
        logger.error(f"Error during policy validation: {e}")
        # Create a minimal but valid policy result structure
        opa_results = {
            "error": f"Policy validation failed: {str(e)}",
            "available_categories": [],
            "fairness": {
                "result": [
                    {
                        "expressions": [
                            {
                                "value": {
                                    "overall_result": False,
                                    "policy": "Error in evaluation",
                                    "recommendations": [
                                        f"Fix evaluation error: {str(e)}"
                                    ]
                                }
                            }
                        ]
                    }
                ]
            }
        }
    
    # Create result dictionary
    result = {
        "evaluation": evaluation_result,
        "policies": opa_results,
        "application_name": app_name
    }
    
    # Generate report if requested
    if generate_report:
        try:
            report = evaluator.generate_report(
                evaluation_result=evaluation_result,
                opa_results=opa_results,
                output_format=report_format
            )
            result["report"] = report
            
            # Save report to file if output_dir is specified
            if output_dir:
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
                
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                report_filename = f"report_{app_name}_{timestamp}.md"
                report_path = output_path / report_filename
                
                with open(report_path, "w") as f:
                    f.write(report)
                
                result["report_path"] = str(report_path)
                
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            result["report_error"] = str(e)
    
    return result

# Add a function to load contract from file
def load_contract(contract_path: str) -> AiCertifyContract:
    """
    Load an AiCertifyContract from a JSON file.
    
    Args:
        contract_path: Path to the contract JSON file
        
    Returns:
        AiCertifyContract object
    """
    try:
        with open(contract_path, "r") as f:
            contract_data = json.load(f)
        return AiCertifyContract.parse_obj(contract_data)
    except Exception as e:
        logger.error(f"Error loading contract from {contract_path}: {e}")
        raise

async def evaluate_contract(
    contract: AiCertifyContract,
    policy_categories: List[str] = ["eu_ai_act", "ai_fairness"],
    output_dir: Optional[str] = None,
    report_format: str = "markdown"
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Evaluate a contract against specified policy categories.
    
    Args:
        contract: The AiCertifyContract to evaluate
        policy_categories: List of policy categories to evaluate against
        output_dir: Directory to save reports to
        report_format: Format of the report ("markdown", "pdf", or "both")
        
    Returns:
        Tuple of (evaluation_result, opa_results)
    """
    # Create evaluator
    evaluator = AICertifyEvaluator()
    
    # Extract conversations from contract
    conversations = []
    for interaction in contract.interactions:
        conversations.append({
            "prompt": interaction.input_text,  # Map input_text to prompt
            "response": interaction.output_text  # Map output_text to response
        })
    
    # Evaluate conversations
    evaluation_result = await evaluator.evaluate_conversations(
        app_name=contract.application_name,
        conversations=conversations
    )
    
    # Ensure the evaluation result has a valid structure
    evaluation_result = _ensure_valid_evaluation_structure(evaluation_result)
    
    # Evaluate against policies
    opa_results = {}
    for category in policy_categories:
        try:
            logger.info(f"Evaluating against policy category: {category}")
            category_results = evaluator.evaluate_policy(evaluation_result, category)
            opa_results[category] = category_results
        except Exception as e:
            logger.error(f"Error evaluating policy {category}: {e}", exc_info=True)
            opa_results[category] = {"error": str(e)}
    
    return evaluation_result, opa_results

async def generate_reports(
    contract: AiCertifyContract,
    evaluation_result: Dict[str, Any],
    opa_results: Dict[str, Any],
    output_dir: Optional[str] = None,
    report_format: str = "markdown"
) -> Dict[str, str]:
    """
    Generate evaluation reports.
    
    Args:
        contract: Contract that was evaluated
        evaluation_result: Evaluation results
        opa_results: OPA policy evaluation results
        output_dir: Directory to save reports to
        report_format: Format of the report ("markdown", "pdf", or "both")
        
    Returns:
        Dictionary of report paths
    """
    # Ensure output directory exists
    if output_dir is None:
        output_dir = "reports"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate timestamp for filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Ensure app_name is set
    app_name = evaluation_result.get("app_name", "Unknown")
    if app_name == "Unknown" and contract:
        app_name = contract.application_name
    
    # Generate reports
    report_paths = {}
    
    try:
        # Generate markdown report
        if report_format.lower() in ["markdown", "both"]:
            md_path = os.path.join(output_dir, f"report_{app_name}_{timestamp}.md")
            md_content = generate_report(evaluation_result, opa_results, "markdown")
            
            with open(md_path, "w") as f:
                f.write(md_content)
            
            logger.info(f"Markdown report saved to: {md_path}")
            report_paths["markdown"] = md_path
        
        # Generate PDF report
        if report_format.lower() in ["pdf", "both"]:
            pdf_path = os.path.join(output_dir, f"report_{app_name}_{timestamp}-{timestamp}.pdf")
            pdf_content = generate_report(evaluation_result, opa_results, "pdf", pdf_path)
            
            logger.info(f"PDF report saved to: {pdf_path}")
            report_paths["pdf"] = pdf_path
    except Exception as e:
        logger.error(f"Error generating reports: {e}", exc_info=True)
        report_paths["error"] = str(e)
    
    return report_paths 