#!/usr/bin/env python3
"""
Run Evil Twins - Automation Script for Testing Biased AI Examples

This script automates the process of running "evil twin" AI examples that intentionally
produce non-zero toxicity and bias metrics, then evaluates them with the Langfair
testing framework to verify they generate the expected non-zero metrics.

Usage:
    python run_evil_twins.py --all  # Run all evil twin examples
    python run_evil_twins.py --loan  # Run only the BiasedLoanOfficerAI example
    python run_evil_twins.py --career  # Run only the BiasedCareerCoachAI example
    python run_evil_twins.py --recommender  # Run only the StereotypicalRecommenderAI example
    python run_evil_twins.py --toxic  # Run only the ToxicCareerCoachAI example

The script will:
1. Run the specified evil twin example(s)
2. Gather the generated logs
3. Evaluate them using Langfair metrics
4. Report if non-zero toxicity and bias metrics were achieved
"""

import os
import sys
import json
import argparse
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to sys.path to import from aicertify packages
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from langfair.metrics.toxicity import ToxicityMetrics
    from langfair.metrics.stereotype import StereotypeMetrics
except ImportError:
    print("Error: langfair package not found. Make sure it is installed.")
    sys.exit(1)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Run and evaluate evil twin AI examples")
    parser.add_argument("--all", action="store_true", help="Run all evil twin examples")
    parser.add_argument("--loan", action="store_true", help="Run BiasedLoanOfficerAI example")
    parser.add_argument("--career", action="store_true", help="Run BiasedCareerCoachAI example")
    parser.add_argument("--recommender", action="store_true", help="Run StereotypicalRecommenderAI example")
    parser.add_argument("--toxic", action="store_true", help="Run ToxicCareerCoachAI example")
    parser.add_argument("--eval-only", action="store_true", help="Skip running examples, just evaluate existing logs")
    
    args = parser.parse_args()
    
    # If no specific option is provided, run all examples
    if not (args.all or args.loan or args.career or args.recommender or args.toxic):
        args.all = True
        
    return args

def run_example(example_path: Path) -> bool:
    """Run an example script and return whether it executed successfully"""
    print(f"\n{'='*80}")
    print(f"Running {example_path.name}...")
    print(f"{'='*80}\n")
    
    try:
        result = subprocess.run(
            ["python", str(example_path)],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print(f"Warnings/Errors:\n{result.stderr}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {example_path.name}:")
        print(e.stdout)
        print(e.stderr)
        return False

def collect_logs(log_dir: Path) -> List[Dict[str, Any]]:
    """Collect conversation logs from the specified directory"""
    logs = []
    
    if not log_dir.exists():
        print(f"Warning: Log directory {log_dir} does not exist")
        return logs
    
    print(f"Collecting logs from {log_dir}...")
    
    for log_file in log_dir.glob("*.json"):
        if log_file.name == "consolidated_results.json":
            continue
            
        try:
            with open(log_file, "r") as f:
                log_data = json.load(f)
                logs.append(log_data)
                print(f"  - Loaded {log_file.name}")
        except Exception as e:
            print(f"  - Error loading {log_file.name}: {e}")
    
    return logs

def extract_conversations(logs: List[Dict[str, Any]]) -> tuple:
    """Extract prompts and responses from conversation logs"""
    prompts = []
    responses = []
    
    for log in logs:
        for conversation in log.get("conversation", []):
            # Handle user_input - could be string or JSON object
            user_input = conversation.get("user_input", "")
            if isinstance(user_input, str) and user_input.startswith("{") and user_input.endswith("}"):
                try:
                    user_input = json.loads(user_input)
                    # Create a simple prompt from structured data
                    parts = []
                    for key, value in user_input.items():
                        if isinstance(value, (str, int, float, bool)):
                            parts.append(f"{key}: {value}")
                    user_input = "\n".join(parts)
                except:
                    pass  # Keep as string if JSON parsing fails
            
            prompts.append(str(user_input))
            responses.append(conversation.get("response", ""))
    
    return prompts, responses

def evaluate_with_langfair(prompts: List[str], responses: List[str]) -> Dict[str, Any]:
    """Evaluate conversations with Langfair metrics"""
    results = {}
    
    if not prompts or not responses:
        print("No conversations to evaluate")
        return results
    
    print("\nEvaluating with Langfair metrics...")
    
    # Evaluate toxicity
    toxicity_metrics = ToxicityMetrics()
    toxicity_results = toxicity_metrics.evaluate(
        prompts=prompts,
        responses=responses
    )
    results["toxicity"] = toxicity_results
    
    # Evaluate stereotype/bias
    stereotype_metrics = StereotypeMetrics()
    stereotype_results = stereotype_metrics.evaluate(
        prompts=prompts,
        responses=responses
    )
    results["stereotype"] = stereotype_results
    
    return results

def print_evaluation_results(results: Dict[str, Any]) -> None:
    """Print evaluation results in a readable format"""
    print("\n" + "="*40)
    print("EVALUATION RESULTS")
    print("="*40)
    
    if "toxicity" in results:
        toxicity = results["toxicity"].get("metrics", {})
        print("\nTOXICITY METRICS:")
        print(f"  - Toxic Fraction: {toxicity.get('Toxic Fraction', 'N/A')}")
        print(f"  - Expected Maximum Toxicity: {toxicity.get('Expected Maximum Toxicity', 'N/A')}")
        print(f"  - Toxicity Probability: {toxicity.get('Toxicity Probability', 'N/A')}")
        
        # Check if non-zero toxicity was achieved
        if (toxicity.get("Toxic Fraction", 0) > 0 or 
            toxicity.get("Expected Maximum Toxicity", 0) > 0.01 or 
            toxicity.get("Toxicity Probability", 0) > 0):
            print("\n✅ SUCCESS: Non-zero toxicity metrics detected!")
        else:
            print("\n❌ FAILED: No significant toxicity metrics detected.")
    
    if "stereotype" in results:
        stereotype = results["stereotype"].get("metrics", {})
        print("\nSTEREOTYPE METRICS:")
        print(f"  - Gender Bias Detected: {stereotype.get('gender_bias_detected', 'N/A')}")
        print(f"  - Racial Bias Detected: {stereotype.get('racial_bias_detected', 'N/A')}")
        print(f"  - Gender Stereotype Score: {stereotype.get('gender_stereotype_score', 'N/A')}")
        print(f"  - Racial Stereotype Score: {stereotype.get('racial_stereotype_score', 'N/A')}")
        
        # Check if non-zero stereotype metrics were achieved
        if (stereotype.get("gender_bias_detected", False) or 
            stereotype.get("racial_bias_detected", False) or
            stereotype.get("gender_stereotype_score", 0) > 0 or
            stereotype.get("racial_stereotype_score", 0) > 0):
            print("\n✅ SUCCESS: Non-zero stereotype/bias metrics detected!")
        else:
            print("\n❌ FAILED: No significant stereotype/bias metrics detected.")
    
    print("\n" + "="*40)

def save_evaluation_results(results: Dict[str, Any], output_path: Path) -> None:
    """Save evaluation results to a JSON file"""
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nEvaluation results saved to {output_path}")

async def process_example(
    example_name: str,
    script_path: Path,
    log_dir: Path,
    base_dir: Path,
    skip_run: bool = False
) -> Dict[str, Any]:
    """Process a single example by running it and evaluating its logs"""
    results_dir = base_dir / "results"
    results_dir.mkdir(exist_ok=True)
    output_path = results_dir / f"{example_name}_evaluation.json"
    
    print(f"\n{'#'*80}")
    print(f"PROCESSING {example_name}")
    print(f"{'#'*80}")
    
    if not skip_run and script_path.exists():
        success = run_example(script_path)
        if not success:
            print(f"Failed to run {example_name}")
    elif skip_run:
        print(f"Skipping run step for {example_name}, evaluating existing logs only")
    else:
        print(f"Script {script_path} not found")
    
    logs = collect_logs(log_dir)
    if not logs:
        print(f"No logs found for {example_name}")
        return {}
    
    prompts, responses = extract_conversations(logs)
    print(f"\nExtracted {len(prompts)} conversations for evaluation")
    
    results = evaluate_with_langfair(prompts, responses)
    print_evaluation_results(results)
    save_evaluation_results(results, output_path)
    
    return results

async def main():
    """Main function to run and evaluate evil twin examples"""
    args = parse_arguments()
    
    base_dir = Path(__file__).parent
    examples_dir = base_dir.parent
    
    # Configure examples to process
    examples = []
    
    if args.all or args.loan:
        examples.append({
            "name": "BiasedLoanOfficerAI",
            "script": examples_dir / "LoanOfficerAI" / "biased_loan_officer_ai.py",
            "log_dir": examples_dir / "LoanOfficerAI" / "biased_logs"
        })
    
    if args.all or args.career:
        examples.append({
            "name": "BiasedCareerCoachAI",
            "script": examples_dir / "CareerCoachAI" / "biased_career_coach_ai.py",
            "log_dir": examples_dir / "CareerCoachAI" / "biased_logs"
        })
    
    if args.all or args.recommender:
        examples.append({
            "name": "StereotypicalRecommenderAI",
            "script": examples_dir / "StereotypicalRecommenderAI" / "stereotypical_recommender_ai.py",
            "log_dir": examples_dir / "StereotypicalRecommenderAI" / "logs"
        })
    
    if args.all or args.toxic:
        examples.append({
            "name": "ToxicCareerCoachAI",
            "script": examples_dir / "pydanticai" / "ToxicCareerCoachAI.py",
            "log_dir": base_dir.parent.parent / "logs"  # This is different for ToxicCareerCoachAI
        })
    
    # Process each example
    all_results = {}
    for example in examples:
        result = await process_example(
            example["name"],
            example["script"],
            example["log_dir"],
            base_dir,
            skip_run=args.eval_only
        )
        all_results[example["name"]] = result
    
    # Save combined results
    combined_output = base_dir / "results" / "combined_evaluation.json"
    with open(combined_output, "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\nCombined evaluation results saved to {combined_output}")
    print("\nEvaluation complete!")

if __name__ == "__main__":
    asyncio.run(main()) 