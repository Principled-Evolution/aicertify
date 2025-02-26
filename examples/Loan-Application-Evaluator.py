"""
Loan Application Evaluator Example

This example demonstrates a simple loan approval AI agent with AICertify integration.
It showcases PDF report generation and use of the AICertify API for compliance verification.

All outputs (contracts, reports) will be generated in the examples/outputs/loan_evaluation directory.
"""

import os
import json
import logging
import argparse
import asyncio
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from colorama import Fore

from pydantic_ai import Agent, RunContext, ModelRetry
from pydantic_ai.models.openai import OpenAIModel
from pydantic import BaseModel
from dataclasses import dataclass

# Load environment variables
load_dotenv()

# Configure logging with a detailed format
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Define the model
model = OpenAIModel('gpt-4o-mini', api_key=os.getenv('OPENAI_API_KEY'))

# Define the output models
class Customer(BaseModel):
    """Customer model - includes customer ID, full name, email, age, income, credit score, zip code, assets and debts."""
    customer_id: int
    name: str
    email: str
    age: int
    annual_income: int
    credit_score: int
    zip_code: int
    assets: int
    current_debts: int
    employment_status: str
    length_credit_history: int
    payment_history: str
    purpose: str
    loan_amount_requested: int
    collateral: str
    additional_info: str

class LoanDecision(BaseModel):
    """Loan decision model - includes customer, response type (Approved, Denied), response text, loan amount and term in months."""
    customer: Customer
    response_type: str
    response: str
    loan_amount: int
    term: int

@dataclass
class Deps:
    """Dependencies for the agent"""
    customer: Customer

# Define the agent
agent = Agent(
    model=model,
    result_type=LoanDecision,
    system_prompt="You are a loan officer for a lending institution. Your task is to take the customer's profile, use the credit risk tool to get a risk profile and determine if the requested loan should be approved. Provide a clear and helpful response. Ensure that your response is polite and addresses the customer's loan application effectively. Always include customer's name in your response. End your answer with Ref: Application ID. Get the customer from the provided context and the risk profile from the tools provided.",
    deps_type=Deps
)

@agent.tool(retries=2)
async def get_customer_risk_profile(ctx: RunContext[Deps]) -> str:
    """Get the customer's risk profile based on provided information."""

    # Call the LLM to get the customer's risk profile
    tool_agent = Agent(
        model=model,
        result_type=str,
        system_prompt="Take the customer profile and return a risk profile for a loan application. The customer profile will be provided in the context.",
        deps_type=Deps
    )
    
    @tool_agent.system_prompt
    def get_system_prompt(ctx: RunContext[str]) -> str:
        return f"The customer profile is {ctx.deps.customer}."
    
    result = await tool_agent.run("Get the customer's risk profile.", deps=ctx.deps)
    logger.info(f"Customer risk profile: {result.data}")
    return f"The customer risk profile is: {result.data}"


def run_session(capture_contract: bool, contract_storage: str, report_format: str = "pdf") -> None:
    """Run the loan evaluation session and optionally generate and save a contract with evaluation report.
    
    Args:
        capture_contract: Whether to capture contract and evaluate
        contract_storage: Directory to store contract files
        report_format: Format for generated reports ("pdf" or "markdown")
    """
    logger.info("Starting loan evaluation session.")
    logger.info(f"Session started at {datetime.now().isoformat()}")

    # Create a customer profile
    customer = Customer(
        customer_id=123,
        name="Michaela Resilient",
        email="m.resilient@gmail.com",
        age=35,
        annual_income=50000,
        credit_score=700,
        zip_code=20000,
        assets=30000,
        current_debts=50000,
        employment_status="Full-time",
        length_credit_history=10,
        payment_history="Good",
        purpose="Home improvement",
        loan_amount_requested=1000000,
        collateral="Home",
        additional_info="No recent credit inquiries"
    )

    deps = Deps(customer=customer)
    question = "Please evaluate the customer's loan application."

    captured_interactions: list[dict] = []

    try:
        logger.info("Running loan evaluation agent...")
        result = agent.run_sync(question, deps=deps)

        logger.info(f"Loan evaluation result: {result.data.response_type}")
        logger.info(f"Loan evaluation response: {result.data.response}")
        logger.info(f"Loan amount: {result.data.loan_amount}")
        logger.info(f"Loan term (months): {result.data.term}")

        captured_interactions.append({
            "input_text": question,
            "output_text": result.data.response,
            "metadata": {
                "agent": "LoanDecision",
                "response_type": result.data.response_type,
                "loan_amount": result.data.loan_amount,
                "loan_term": result.data.term
            }
        })

    except ModelRetry as e:
        logger.error(f"ModelRetry encountered: {e}")
    except Exception as e:
        logger.exception("An error occurred during the loan evaluation session")

    if capture_contract:
        logger.info("Contract capture enabled. Generating contract...")
        try:
            # Import contract models
            try:
                from aicertify.models.contract_models import create_contract, validate_contract, save_contract
            except ImportError:
                logger.error("Failed to import AICertify contract models. Make sure AICertify is installed.")
                return

            # Create a contract
            application_name = "Loan Application Evaluation"
            model_info = {
                "model_name": agent.model.model_name,
                "model_version": "N/A",
                "additional_info": {
                    "provider": "OpenAI",
                    "temperature": "default"
                }
            }
            
            contract = create_contract(application_name, model_info, captured_interactions)
            if validate_contract(contract):
                logger.info("Contract successfully validated.")
            else:
                logger.error("Contract validation failed.")
                return

            # Save the contract
            file_path = save_contract(contract, storage_dir=contract_storage)
            logger.info(f"Contract saved to {file_path}")
            
            # Simple AICertify API integration for evaluation and reporting
            logger.info("Evaluating contract with AICertify API...")
            try:
                # Import AICertify evaluation API
                from aicertify.api import evaluate_contract_object
                import asyncio
                
                # Run the async evaluation function using asyncio
                eval_result = asyncio.run(evaluate_contract_object(
                    contract=contract,
                    policy_category='eu_ai_act',
                    generate_report=True,
                    report_format=report_format,
                    output_dir=contract_storage
                ))
                
                # Log evaluation results
                logger.info("Contract evaluation complete")
                if eval_result.get('report_path'):
                    logger.info(f"Evaluation report saved to: {eval_result.get('report_path')}")
                else:
                    # For PDF files, check the standard locations
                    if report_format.lower() == 'pdf':
                        import glob
                        from pathlib import Path
                        import os
                        import shutil
                        
                        # Check the temp_reports directory for PDF files
                        temp_dir = Path('temp_reports')
                        if temp_dir.exists():
                            pdf_files = list(temp_dir.glob('*.pdf'))
                            if pdf_files:
                                # Find the most recently created PDF file
                                latest_pdf = max(pdf_files, key=lambda x: x.stat().st_mtime)
                                logger.info(f"PDF report found at: {latest_pdf}")
                                
                                # Copy it to the contract storage directory with a better name
                                try:
                                    # Make sure output directory exists
                                    out_dir = Path(contract_storage)
                                    out_dir.mkdir(exist_ok=True, parents=True)
                                    
                                    # Create a better filename with timestamp
                                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                    new_pdf_path = out_dir / f"report_Loan_Application_{timestamp}.pdf"
                                    
                                    # Copy the file - if it exists
                                    if latest_pdf.exists():
                                        shutil.copy2(latest_pdf, new_pdf_path)
                                        logger.info(f"PDF report copied to: {new_pdf_path}")
                                    else:
                                        logger.error(f"PDF file {latest_pdf} doesn't exist")
                                except Exception as e:
                                    logger.error(f"Failed to copy PDF report: {e}")
                            else:
                                logger.warning("No PDF files found in temp_reports directory")
                        else:
                            logger.warning(f"temp_reports directory not found at {temp_dir.absolute()}")
                    else:
                        logger.info("Report generated but path not returned")
                
            except Exception as ex:
                logger.exception(f"Error during contract evaluation: {ex}")
                
        except Exception as ex:
            logger.exception(f"Error creating contract: {ex}")


def main() -> None:
    """Main entry point for the loan evaluation example."""
    parser = argparse.ArgumentParser(description="Demo for Loan Application Evaluation with AICertify Integration")
    parser.add_argument('--capture-contract', action='store_true', help="Capture outputs to generate a contract for evaluation")
    parser.add_argument('--contract-storage', type=str, default=None, help="Directory to store generated contract files")
    parser.add_argument('--report-format', type=str, default='pdf', choices=['pdf', 'markdown'], help="Format for generated reports")
    parser.add_argument('--debug', action='store_true', help="Enable debug logging")
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.info("Debug logging enabled")
    
    # Get the directory where this script is located
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    
    # Define default output directory relative to the script directory
    if args.contract_storage is None:
        # Create a subdirectory 'outputs/loan_evaluation' within the examples directory
        contract_storage = script_dir / "outputs" / "loan_evaluation"
    else:
        # If specified, make it relative to script directory unless it's an absolute path
        contract_storage = Path(args.contract_storage)
        if not contract_storage.is_absolute():
            contract_storage = script_dir / args.contract_storage
    
    # Ensure the output directory exists
    contract_storage.mkdir(parents=True, exist_ok=True)
    
    # Make sure temp_reports is also in the right place
    temp_reports = script_dir / "outputs" / "temp_reports"
    temp_reports.mkdir(parents=True, exist_ok=True)
    
    # Print current working directory to help debug file paths
    logging.info(f"Current working directory: {os.getcwd()}")
    logging.info(f"Script directory: {script_dir}")
    logging.info(f"Report format requested: {args.report_format}")
    logging.info(f"Contract storage directory: {contract_storage}")

    run_session(
        capture_contract=args.capture_contract,
        contract_storage=str(contract_storage),
        report_format=args.report_format
    )


if __name__ == "__main__":
    main() 