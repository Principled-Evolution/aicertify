"""
Driver script for running the ToxicCareerCoachWithCertification example.

This script sets up the Python path correctly and runs the example with
the appropriate parameters.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def main():
    """Run the toxic career coach example with report generation."""
    try:
        # Import the module (direct import to avoid relative import issues)
        sys.path.insert(0, str(project_root / "aicertify" / "examples" / "pydanticai"))
        
        # Import both classes to ensure they can be found
        from ToxicCareerCoachAI import ToxicCareerCoachAI, HUGGINGFACE_AVAILABLE
        
        # Now import the certification class
        from ToxicCareerCoachAI_with_certification import ToxicCareerCoachWithCertification
        
        logger.info("Successfully imported ToxicCareerCoachWithCertification")
        
        # Create the coach with certification
        toxic_coach = ToxicCareerCoachWithCertification(
            use_hf_dataset=True,
            dataset_name="aicertify/toxic-responses"
        )
        
        # Sample industries for testing
        test_industries = [
            "Technology", "Finance", "Healthcare", "Education", "Manufacturing"
        ]
        
        # Run interactive session with gender_biased response type
        logger.info("Running interactive session with gender_biased response type")
        toxic_coach.run_interactive(test_industries, response_type="gender_biased")
        
        # Create a contract
        logger.info("Creating AICertify contract")
        contract_path = toxic_coach.create_contract()
        if contract_path:
            logger.info(f"Contract saved to: {contract_path}")
            
            # Define output directory for reports
            output_dir = project_root / "example_reports"
            output_dir.mkdir(exist_ok=True)
            
            # Evaluate the contract
            logger.info("Evaluating contract against EU AI Act policies")
            evaluation_results = await toxic_coach.evaluate(
                policy_category="eu_ai_act",
                use_simple_evaluator=False,
                generate_report=True,
                report_formats=["markdown", "pdf"],
                output_dir=str(output_dir)
            )
            
            if evaluation_results:
                logger.info("Evaluation completed successfully")
                
                # Check for report paths
                if "report_paths" in evaluation_results:
                    logger.info("Report generation successful")
                    for format_type, path in evaluation_results["report_paths"].items():
                        logger.info(f"{format_type.capitalize()} report saved to: {path}")
                else:
                    logger.warning("No report paths found in evaluation results")
                    
                    # Try generating reports separately
                    logger.info("Generating reports separately")
                    report_paths = toxic_coach.generate_reports(
                        output_dir=str(output_dir),
                        formats=["markdown", "pdf"]
                    )
                    
                    if isinstance(report_paths, dict) and "error" not in report_paths:
                        for format_type, path in report_paths.items():
                            logger.info(f"{format_type.capitalize()} report saved to: {path}")
                    else:
                        logger.error(f"Error generating reports: {report_paths}")
            else:
                logger.error("Evaluation failed")
        else:
            logger.error("Contract creation failed")
            
    except ImportError as e:
        logger.error(f"Import error: {e}")
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(main()) 