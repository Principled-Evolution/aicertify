import argparse
import asyncio
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

from aicertify.opa_core.policy_loader import PolicyLoader
from aicertify.opa_core.evaluator import OpaEvaluator
from langfair.metrics.toxicity import ToxicityMetrics


class LangFairEvaluator:
    def __init__(self):
        self.tm = ToxicityMetrics()

    def evaluate(self, input_data):
        prompts = input_data.get("prompts", [])
        responses = input_data.get("responses", [])
        return self.tm.evaluate(prompts=prompts, responses=responses, return_data=True)


def main():
    """
    AICertify CLI Entry Point.
    
    Subcommand 'eval-policy':
      Evaluate an input JSON file against OPA policies.
    
    Subcommand 'eval-folder':
      Evaluate a folder containing contract JSON files and produce a consolidated LangFair evaluation.
      Aggregates all interactions from contracts of a specified app, runs a consolidated evaluation, and stores the result.
    """
    parser = argparse.ArgumentParser(
        description="AICertify CLI: Validate AI applications and run evaluations."
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="Sub-commands")

    # Subcommand for OPA policy evaluation
    policy_parser = subparsers.add_parser("eval-policy", help="Evaluate input JSON against OPA policies.")
    loader = PolicyLoader()
    available_categories = list(loader.policies.keys())
    policy_parser.add_argument(
        "--category",
        type=str,
        choices=available_categories,
        required=True,
        help=f"Policy category to evaluate. Available: {available_categories}"
    )
    policy_parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to input JSON file for evaluation."
    )

    # Subcommand for evaluating a folder of contract JSON files using consolidated LangFair evaluation
    folder_parser = subparsers.add_parser(
        "eval-folder",
        help="Evaluate a folder containing contract JSON files and produce a consolidated LangFair evaluation."
    )
    folder_parser.add_argument(
        "--app-name",
        type=str,
        required=True,
        help="Application name to filter contracts."
    )
    folder_parser.add_argument(
        "--folder",
        type=str,
        required=True,
        help="Folder containing contract JSON files."
    )
    folder_parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Path to output JSON file for consolidated evaluation results."
    )

    args = parser.parse_args()

    if args.command == "eval-policy":
        # Validate input file existence and load JSON
        try:
            with open(args.input, "r") as f:
                input_data = json.load(f)
        except FileNotFoundError:
            logging.error(f"Input file '{args.input}' not found.")
            return
        except json.JSONDecodeError:
            logging.error(f"Invalid JSON format in file '{args.input}'.")
            return

        # Load and evaluate policies using OpaEvaluator
        category_policies = loader.get_policies_by_category(args.category)
        if not category_policies:
            logging.warning(f"No policies found for category: {args.category}")
            return

        logging.info(f"Running validation for category: {args.category}")
        results = {}
        evaluator = OpaEvaluator()
        for policy in category_policies:
            result = evaluator.evaluate_policy(policy, input_data)
            results[policy] = result

        # Print evaluation results
        print(json.dumps(results, indent=4))

    elif args.command == "eval-folder":
        # Run consolidated LangFair evaluation on a folder of contract JSON files
        try:
            from aicertify.system_evaluators.evaluate_contract_langfair import evaluate_app_folder
        except ImportError:
            logging.error("Cannot import evaluate_app_folder from aicertify.system_evaluators.evaluate_contract_langfair")
            return
        result = asyncio.run(evaluate_app_folder(args.app_name, args.folder, args.output))
        logging.info("Consolidated Evaluation Result:")
        if result:
            print(json.dumps(result, indent=4))
        else:
            print("No evaluation results were produced.")


if __name__ == "__main__":
    main()
