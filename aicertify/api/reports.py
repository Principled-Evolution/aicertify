"""
AICertify API Reports Module

This module provides functions for generating evaluation reports in various formats.
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


# Import core utilities
from aicertify.api.core import _ensure_valid_evaluation_structure
# Configure logging
logger = logging.getLogger(__name__)


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
        # Import required components
        from aicertify.report_generation.report_generator import ReportGenerator
        from aicertify.report_generation.data_extraction import create_evaluation_report
        from aicertify.models.report import (
            EvaluationReport, ApplicationDetails
        )
        # Create the evaluation report model
        try:
            report_model = create_evaluation_report(evaluation_result, opa_results)
        except Exception as e:
            logger.warning(f"Error creating evaluation report model: {e}, using fallback")
            # Create a minimal report model with basic information
            app_name = evaluation_result.get("app_name", "Unknown")
            if app_name == "Unknown" and "application_name" in evaluation_result:
                app_name = evaluation_result["application_name"]
                
            report_model = EvaluationReport(
                app_details=ApplicationDetails(
                    name=app_name,
                    evaluation_mode="Standard",
                    contract_count=1,
                    evaluation_date=datetime.now()
                ),
                metric_groups=[],
                policy_results=[],
                summary="Basic evaluation report"
            )
        
        # Setup output directory
        if not output_dir:
            output_dir = Path.cwd() / "reports"
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True, parents=True)
        
        # Get application name for the filename
        app_name = report_model.app_details.name.replace(" ", "_")
        if app_name == "Unknown" and "application_name" in evaluation_result:
            app_name = evaluation_result["application_name"].replace(" ", "_")
        
        # Get a timestamp for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create ReportGenerator instance
        report_gen = ReportGenerator()
        
        # Generate markdown content
        md_content = report_gen.generate_markdown_report(report_model)
        
        # Generate reports
        report_paths = {}
        
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

async def generate_reports(
    contract: Any,
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
        # Import required components
        from aicertify.report_generation.report_generator import ReportGenerator
        from aicertify.report_generation.data_extraction import create_evaluation_report
        
        # Create the evaluation report model
        report_model = create_evaluation_report(evaluation_result, opa_results)
        
        # Create ReportGenerator instance
        report_gen = ReportGenerator()
        
        # Generate markdown content
        md_content = report_gen.generate_markdown_report(report_model)
        
        # Generate markdown report
        if report_format.lower() in ["markdown", "both"]:
            md_path = os.path.join(output_dir, f"report_{app_name}_{timestamp}.md")
            
            # Save markdown report
            with open(md_path, "w") as f:
                f.write(md_content)
            
            logger.info(f"Markdown report saved to: {md_path}")
            report_paths["markdown"] = md_path
        
        # Generate PDF report
        if report_format.lower() in ["pdf", "both"]:
            pdf_path = os.path.join(output_dir, f"report_{app_name}_{timestamp}.pdf")
            
            # Generate PDF from markdown content
            pdf_result = report_gen.generate_pdf_report(md_content, pdf_path)
            
            logger.info(f"PDF report saved to: {pdf_result}")
            report_paths["pdf"] = pdf_result
    except ImportError as e:
        logger.error(f"Required modules for report generation not available: {e}")
        report_paths["error"] = f"Report generation failed: {str(e)}"
    except Exception as e:
        logger.error(f"Error generating reports: {e}", exc_info=True)
        report_paths["error"] = str(e)
    
    return report_paths
