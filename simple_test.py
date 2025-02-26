"""
Simple test script to validate report generation.
"""

import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def main():
    """Generate a test report with our new implementation."""
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
    
    # Create output directory
    reports_dir = Path("./simple_test_reports")
    reports_dir.mkdir(exist_ok=True)
    
    try:
        # Import our modules
        from aicertify.report_generation.data_extraction import create_evaluation_report
        from aicertify.report_generation.report_generator import ReportGenerator
        
        # Create evaluation report model
        report_model = create_evaluation_report(evaluation_result, opa_results)
        logger.info(f"Created report model with app name: {report_model.app_details.name}")
        
        # Generate markdown report
        report_gen = ReportGenerator()
        md_content = report_gen.generate_markdown_report(report_model)
        
        # Save markdown report
        md_path = reports_dir / "test_report.md"
        if report_gen.save_markdown_report(md_content, str(md_path)):
            logger.info(f"Saved markdown report to: {md_path}")
            
            # Print part of the report
            with open(md_path, "r") as f:
                content = f.read()
                print("\nReport Content:")
                print(content[:500] + "...\n")
                
            # Generate PDF report
            pdf_path = reports_dir / "test_report.pdf"
            pdf_result = report_gen.generate_pdf_report(md_content, str(pdf_path))
            if pdf_result:
                logger.info(f"Generated PDF report at: {pdf_result}")
            else:
                logger.error("Failed to generate PDF report")
        else:
            logger.error("Failed to save markdown report")
            
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
    except Exception as e:
        logger.error(f"Error during report generation: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main() 