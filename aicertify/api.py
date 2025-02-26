"""
AICertify API

A simple entry point for developers to integrate AICertify evaluation into their applications.
This module provides functions to evaluate AI interactions for compliance with various policies.
"""

import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Import models and evaluation components
from aicertify.models.contract_models import AiCertifyContract, load_contract

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
    # Extract OPA results from evaluation_result if not provided separately
    if opa_results is None:
        if "policy_results" in evaluation_result:
            opa_results = evaluation_result["policy_results"]
        elif "policies" in evaluation_result:
            opa_results = evaluation_result["policies"]
        else:
            opa_results = {}
    
    # Create evaluation report model
    if REPORT_DATA_EXTRACTION_AVAILABLE:
        # Use our new data extraction module
        report_model = create_evaluation_report(evaluation_result, opa_results)
    else:
        # Fallback to using the evaluator's method if available
        try:
            evaluator = AICertifyEvaluator()
            report_model = evaluator._create_evaluation_report(evaluation_result, opa_results)
        except Exception as e:
            logger.error(f"Error creating evaluation report: {e}")
            from datetime import datetime
            from aicertify.report_generation.report_models import (
                EvaluationReport, ApplicationDetails,
                MetricGroup, MetricValue, PolicyResult
            )
            # Create a minimal report model with error information
            report_model = EvaluationReport(
                app_details=ApplicationDetails(
                    name=evaluation_result.get("application_name", "Unknown Application"),
                    evaluation_mode="Standard",
                    contract_count=0,
                    evaluation_date=datetime.now()
                ),
                metric_groups=[],
                policy_results=[
                    PolicyResult(
                        name="error", 
                        result=False, 
                        details={"error": f"Failed to create report: {e}"}
                    )
                ],
                summary="Error generating report"
            )
    
    # Create report generator
    report_gen = ReportGenerator()
    
    # Generate markdown report
    markdown_content = report_gen.generate_markdown_report(report_model)
    
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
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Generate reports in the requested formats
    report_paths = {}
    
    if "markdown" in output_formats:
        md_path = output_dir / f"report_{app_name}_{timestamp}.md"
        
        if report_gen.save_markdown_report(markdown_content, str(md_path)):
            logger.info(f"Markdown report saved to: {md_path}")
            report_paths["markdown"] = str(md_path)
        else:
            logger.error(f"Failed to save markdown report to {md_path}")
    
    if "pdf" in output_formats:
        pdf_path = output_dir / f"report_{app_name}_{timestamp}.pdf"
        
        pdf_result = report_gen.generate_pdf_report(markdown_content, str(pdf_path))
        if pdf_result:
            logger.info(f"PDF report saved to: {pdf_result}")
            report_paths["pdf"] = pdf_result
        else:
            logger.error(f"Failed to generate PDF report at {pdf_path}")
    
    return report_paths

async def evaluate_contract(
    contract_path: str, 
    policy_category: str = "eu_ai_act",
    generate_report: bool = True,
    report_formats: List[str] = ["markdown"],
    output_dir: Optional[str] = None,
    use_simple_evaluator: bool = False
) -> Dict[str, Any]:
    """
    Evaluate a contract from a file path.
    
    This function provides a simple one-line method to evaluate an AI application
    contract against selected policies.
    
    Args:
        contract_path: Path to the contract JSON file
        policy_category: OPA policy category to evaluate against ("eu_ai_act", "us_nist", etc.)
        generate_report: Whether to generate an evaluation report
        report_formats: List of report formats to generate ("markdown", "pdf", or both)
        output_dir: Directory to save evaluation results and reports
        use_simple_evaluator: Force using the simplified evaluator even if full evaluator is available
    
    Returns:
        Dictionary containing evaluation results, policy validation, and report
    """
    try:
        # Load the contract
        contract = load_contract(contract_path)
    except Exception as e:
        logger.error(f"Error loading contract from {contract_path}: {e}")
        return {"error": str(e), "contract_path": contract_path, "status": "failed"}

    # Determine which evaluator to use
    if use_simple_evaluator or not FULL_EVALUATOR_AVAILABLE:
        logger.info("Using simplified evaluator")
        return await evaluate_contract_simple(
            contract_path=contract_path,
            policy_category=policy_category
        )
    
    # Otherwise, use the full evaluator
    try:
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
            # Continue with report generation even if policy validation fails
            opa_results = {
                "error": f"Policy validation failed: {str(e)}",
                "available_categories": []
            }
        
        # Create result dictionary
        result = {
            "evaluation": evaluation_result,
            "policy_results": opa_results,
            "contract_id": str(contract.contract_id),
            "application_name": contract.application_name
        }
        
        # Generate report if requested
        if generate_report:
            try:
                # Import the generate_report function again with a different name
                from aicertify.api import generate_report as gen_report
                # Use our new generate_report function with a different variable name
                report_paths = await gen_report(
                    evaluation_result=evaluation_result,
                    opa_results=opa_results,
                    output_formats=report_formats,
                    output_dir=output_dir
                )
                result["report_paths"] = report_paths
            except Exception as e:
                logger.error(f"Error generating reports: {e}")
                result["report_error"] = str(e)
        
        return result
    except Exception as e:
        logger.error(f"Error during full evaluator evaluation: {e}")
        return {"error": f"Evaluation failed: {str(e)}"}

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
        return {
            "evaluation": evaluation_result,
            "error": f"Policy validation failed: {str(e)}"
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
        return {
            "evaluation": evaluation_result,
            "error": f"Policy validation failed: {str(e)}"
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