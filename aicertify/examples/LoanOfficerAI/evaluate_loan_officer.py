import os
import json
from pathlib import Path
import warnings
import argparse
import asyncio
from dotenv import find_dotenv, load_dotenv

from aicertify.models.langfair_eval import AutoEvalInput
from aicertify.evaluators.langfair_auto_eval import evaluate_ai_responses

def load_json_decisions(directory_path: str = None) -> AutoEvalInput:
    """Load LoanOfficerAI decisions from JSON files"""
    if directory_path is None:
        directory_path = Path(__file__).parent
    else:
        directory_path = Path(directory_path)
    
    responses = []
    prompts = []
    
    json_files = list(directory_path.glob("LoanOfficerAI_*.json"))
    if not json_files:
        raise FileNotFoundError(f"No LoanOfficerAI JSON files found in {directory_path}")
    
    print(f"Found {len(json_files)} JSON files in {directory_path}")
    
    for json_file in json_files:
        print(f"Processing file: {json_file.name}")
        with open(json_file) as f:
            data = json.load(f)
        
        for exchange in data["conversation"]:
            # Use customer profile as prompt and loan decision as response
            customer_input = exchange["customer_input"]
            loan_decision = exchange["loan_decision"]
            
            # Format the prompt and response
            prompt = (
                f"Customer Profile:\n"
                f"Name: {customer_input['name']}\n"
                f"Income: ${customer_input['annual_income']:,}\n"
                f"Credit Score: {customer_input['credit_score']}\n"
                f"Loan Request: ${customer_input['loan_amount_requested']:,}"
            )
            
            response = (
                f"Decision: {loan_decision['response_type']}\n"
                f"Details: {loan_decision['response']}\n"
                f"Approved Amount: ${loan_decision['loan_amount']:,}\n"
                f"Term: {loan_decision['term']} months"
            )
            
            prompts.append(prompt)
            responses.append(response)
    
    return AutoEvalInput(prompts=prompts, responses=responses)

async def main():
    parser = argparse.ArgumentParser(description='Evaluate LoanOfficerAI decisions for bias and fairness.')
    parser.add_argument('--dir', type=str, help='Directory containing JSON decision files (optional)')
    args = parser.parse_args()
    
    load_dotenv(find_dotenv())
    warnings.filterwarnings("ignore")
    
    try:
        # Load decisions
        input_data = load_json_decisions(args.dir)
        print(f"\nLoaded {len(input_data.prompts)} decisions for evaluation")
        
        # Run evaluation
        print("\nRunning evaluation...")
        results = await evaluate_ai_responses(input_data)
        
        # Save results
        output_dir = Path(args.dir) if args.dir else Path(__file__).parent
        
        # Save summary
        summary_file = output_dir / "loan_officer_analysis_summary.txt"
        with open(summary_file, "w") as f:
            f.write(results.summary)
        print(f"\nAnalysis summary saved to: {summary_file}")
        
        # Print summary
        print("\nAnalysis Summary:")
        print("----------------")
        print(results.summary)
        
    except Exception as e:
        print(f"Error during evaluation: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 