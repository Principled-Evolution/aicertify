import argparse
import json
import logging
from core.policy_loader import PolicyLoader
from core.evaluator import OpaEvaluator

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

from langfair.metrics.toxicity import ToxicityMetrics

class LangFairEvaluator:
    def __init__(self):
        self.tm = ToxicityMetrics()

    def evaluate(self, input_data):
        prompts = input_data.get("prompts", [])
        responses = input_data.get("responses", [])
        return self.tm.evaluate(prompts=prompts, responses=responses, return_data=True)


def main():
    """CLI entry point for running AI compliance validation."""
    loader = PolicyLoader()
    evaluator = OpaEvaluator()

    # Dynamically discover available categories
    available_categories = list(loader.policies.keys())

    parser = argparse.ArgumentParser(
        description="AICertify CLI: Validate AI applications against predefined OPA policies."
    )
    parser.add_argument(
        "--category", 
        type=str, 
        choices=available_categories, 
        required=True, 
        help=f"Policy category to evaluate. Available: {available_categories}"
    )
    parser.add_argument(
        "--input", 
        type=str, 
        required=True, 
        help="Path to input JSON file for evaluation."
    )

    args = parser.parse_args()

    # Validate input file existence
    try:
        with open(args.input, "r") as f:
            input_data = json.load(f)
    except FileNotFoundError:
        logging.error(f"Input file '{args.input}' not found.")
        return
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON format in file '{args.input}'.")
        return

    # Load and evaluate policies
    category_policies = loader.get_policies_by_category(args.category)
    if not category_policies:
        logging.warning(f"No policies found for category: {args.category}")
        return

    logging.info(f"Running validation for category: {args.category}")
    results = {}

    for policy in category_policies:
        result = evaluator.evaluate_policy(policy, input_data)
        results[policy] = result

    # Print structured output
    print(json.dumps(results, indent=4))

if __name__ == "__main__":
    main()
