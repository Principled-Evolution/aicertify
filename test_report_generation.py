"""
Test script for the new report generation implementation.

This script tests our new data extraction and report generation capabilities.
"""

import asyncio
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

async def main():
    """
    Main function to test report generation.
    """
    # Sample evaluation results with metrics and policy results
    evaluation_result = {
        "app_name": "TestApplication",
        "evaluation_mode": "Test Mode",
        "contract_count": 25,
        "metrics": {
            "fairness": {
                "ftu_satisfied": True,
                "race_words_count": 5,
                "gender_words_count": 12
            },
            "toxicity": {
                "toxic_fraction": 0.32,
                "max_toxicity": 0.75,
                "toxicity_probability": 0.45
            },
            "stereotype": {
                "gender_bias_detected": True,
                "racial_bias_detected": False
            }
        },
        "summary": {
            "has_toxicity": True,
            "has_bias": True,
            "toxicity_values": {
                "toxic_fraction": 0.32
            },
            "stereotype_values": {
                "gender_bias_detected": True
            }
        }
    }
    
    # Sample OPA results
    opa_results = {
        "fairness": {
            "result": [
                {
                    "expressions": [
                        {
                            "value": {
                                "overall_result": False,
                                "policy": "EU AI Act Fairness Requirements",
                                "version": "1.0",
                                "recommendations": [
                                    "Review and retrain the model to reduce gender bias in responses"
                                ]
                            }
                        }
                    ]
                }
            ]
        }
    }
    
    # Import our data extraction module
    try:
        from aicertify.report_generation.data_extraction import create_evaluation_report
        logger.info("Successfully imported data extraction module")
    except ImportError as e:
        logger.error(f"Failed to import data extraction module: {e}")
        return
        
    # Create the evaluation report model
    report_model = create_evaluation_report(evaluation_result, opa_results)
    logger.info("Successfully created evaluation report model")
    
    # Print the report model to verify
    logger.info(f"App Name: {report_model.app_details.name}")
    logger.info(f"Contract Count: {report_model.app_details.contract_count}")
    
    # Print metrics
    for group in report_model.metric_groups:
        logger.info(f"Metric Group: {group.display_name}")
        for metric in group.metrics:
            logger.info(f"  {metric.display_name}: {metric.value}")
    
    # Print policy results
    for policy in report_model.policy_results:
        logger.info(f"Policy: {policy.name}, Result: {policy.result}")
        if policy.details:
            for key, value in policy.details.items():
                logger.info(f"  {key}: {value}")
    
    # Generate the report
    try:
        from aicertify.report_generation.report_generator import ReportGenerator
        report_gen = ReportGenerator()
        
        # Generate markdown content
        md_content = report_gen.generate_markdown_report(report_model)
        logger.info("Successfully generated markdown content")
        
        # Save the markdown report
        reports_dir = Path("./test_reports")
        reports_dir.mkdir(exist_ok=True)
        
        md_path = reports_dir / "test_report.md"
        
        if report_gen.save_markdown_report(md_content, str(md_path)):
            logger.info(f"Saved markdown report to: {md_path}")
            
            # Print the markdown content
            logger.info("\nMarkdown Report Content:")
            print(md_content[:500] + "...\n")
            
            # Generate PDF
            pdf_path = reports_dir / "test_report.pdf"
            pdf_result = report_gen.generate_pdf_report(md_content, str(pdf_path))
            
            if pdf_result:
                logger.info(f"Generated PDF report at: {pdf_result}")
            else:
                logger.error("Failed to generate PDF report")
        else:
            logger.error("Failed to save markdown report")
    except ImportError as e:
        logger.error(f"Failed to import report generator: {e}")
    except Exception as e:
        logger.error(f"Error during report generation: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    # Test the API's generate_report function
    try:
        from aicertify.api import generate_report
        
        logger.info("\nTesting API's generate_report function")
        report_paths = await generate_report(
            evaluation_result=evaluation_result,
            opa_results=opa_results,
            output_formats=["markdown", "pdf"],
            output_dir="./test_reports"
        )
        
        logger.info("API generate_report function successful")
        for format_type, path in report_paths.items():
            logger.info(f"{format_type.capitalize()} report path: {path}")
    except ImportError as e:
        logger.error(f"Failed to import API generate_report function: {e}")
    except Exception as e:
        logger.error(f"Error using API generate_report function: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(main()) 