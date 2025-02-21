import argparse
import asyncio
import json
import logging
from pathlib import Path
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

from aicertify.opa_core.policy_loader import PolicyLoader
from aicertify.opa_core.evaluator import OpaEvaluator
from langfair.metrics.toxicity import ToxicityMetrics
from aicertify.report_generation.report_generator import ReportGenerator
from aicertify.report_generation.report_models import (
    EvaluationReport, ApplicationDetails,
    MetricGroup, MetricValue, PolicyResult
)


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
    
    Disclaimer: This software and its generated reports are provided "AS IS", without any warranty or guarantee 
    of legal compliance. The generated reports include explicit disclaimer sections as per industry best practices.
    
    Subcommand 'eval-policy':
      Evaluate an input JSON file against OPA policies.
    
    Subcommand 'eval-folder':
      Evaluate a folder containing contract JSON files and produce a consolidated LangFair evaluation.
      Aggregates all interactions from contracts of a specified app, runs a consolidated evaluation, and stores the result.
    
    Subcommand 'eval-all':
      Run consolidated evaluation on a folder and then evaluate OPA policies on the result.
    """
    parser = argparse.ArgumentParser(
        description="AICertify CLI: Validate AI applications and run evaluations. "
                    "Disclaimer: This software is provided 'AS IS' with no warranty. Consult legal counsel for compliance."
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

    # New subcommand for running both evaluations together (eval-all)
    all_parser = subparsers.add_parser(
        "eval-all",
        help="Run consolidated evaluation on a folder and then evaluate OPA policies on the result."
    )
    all_parser.add_argument(
        "--app-name",
        type=str,
        required=True,
        help="Application name to filter contracts."
    )
    all_parser.add_argument(
        "--folder",
        type=str,
        required=True,
        help="Folder containing contract JSON files."
    )
    all_parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Path to output JSON file for consolidated evaluation results."
    )
    all_parser.add_argument(
        "--category",
        type=str,
        choices=available_categories,
        required=True,
        help=f"Policy category to evaluate. Available: {available_categories}"
    )
    all_parser.add_argument(
        "--report-md",
        type=str,
        help="Optional path to output Markdown report file."
    )
    all_parser.add_argument(
        "--report-pdf",
        type=str,
        help="Optional path to output PDF report file. Requires markdown and WeasyPrint libraries."
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

    elif args.command == "eval-all":
        # Run consolidated evaluation and then OPA policy evaluation on the result
        try:
            from aicertify.system_evaluators.evaluate_contract_langfair import evaluate_app_folder
        except ImportError:
            logging.error("Cannot import evaluate_app_folder from aicertify.system_evaluators.evaluate_contract_langfair")
            return

        # Run consolidated evaluation
        consolidated_result = asyncio.run(evaluate_app_folder(args.app_name, args.folder, args.output))
        if not consolidated_result:
            logging.info("No evaluation results were produced from folder evaluation.")
            return
        logging.info("Consolidated Evaluation Result:")
        print(json.dumps(consolidated_result, indent=4))

        # Load the consolidated evaluation from the output file
        try:
            with open(args.output, "r") as f:
                opa_input = json.load(f)
        except Exception as e:
            logging.error(f"Failed to load consolidated evaluation result from '{args.output}': {str(e)}")
            return

        # Run OPA policy evaluation
        category_policies = loader.get_policies_by_category(args.category)
        if not category_policies:
            logging.warning(f"No policies found for category: {args.category}")
            return

        logging.info(f"Running OPA policy validation for category: {args.category}")
        evaluator = OpaEvaluator()
        opa_results = {}
        for policy in category_policies:
            result = evaluator.evaluate_policy(policy, opa_input)
            opa_results[policy] = result

        # Print combined results
        combined = {
            "consolidated_evaluation": consolidated_result,
            "opa_evaluation": opa_results
        }
        print("Combined Evaluation Result:")
        print(json.dumps(combined, indent=4))

        # Convert evaluation results to report model
        def create_evaluation_report(consolidated_result: dict, opa_results: dict) -> EvaluationReport:
            """Convert evaluation results to the report model structure."""
            metrics = consolidated_result.get("metrics", {})
            
            # Create fairness metrics group
            fairness_metrics = [
                MetricValue(
                    name="ftu_satisfied",
                    display_name="FTU Satisfied",
                    value=metrics.get("ftu_satisfied", "N/A")
                ),
                MetricValue(
                    name="race_words_count",
                    display_name="Race Words Count",
                    value=metrics.get("race_words_count", "N/A")
                ),
                MetricValue(
                    name="gender_words_count",
                    display_name="Gender Words Count",
                    value=metrics.get("gender_words_count", "N/A")
                )
            ]
            
            # Create toxicity metrics group
            toxicity_data = metrics.get("toxicity", {})
            toxicity_metrics = [
                MetricValue(
                    name="toxic_fraction",
                    display_name="Toxic Fraction",
                    value=toxicity_data.get("toxic_fraction", "N/A")
                ),
                MetricValue(
                    name="max_toxicity",
                    display_name="Max Toxicity",
                    value=toxicity_data.get("max_toxicity", "N/A")
                ),
                MetricValue(
                    name="toxicity_probability",
                    display_name="Toxicity Probability",
                    value=toxicity_data.get("toxicity_probability", "N/A")
                )
            ]
            
            # Create stereotype metrics group
            stereotype_data = metrics.get("stereotype", {})
            stereotype_metrics = [
                MetricValue(
                    name="gender_bias",
                    display_name="Gender Bias Detected",
                    value=stereotype_data.get("gender_bias_detected", "N/A")
                ),
                MetricValue(
                    name="racial_bias",
                    display_name="Racial Bias Detected",
                    value=stereotype_data.get("racial_bias_detected", "N/A")
                )
            ]
            
            # Create policy results
            policy_results = []
            for policy_name, result in opa_results.items():
                try:
                    allow_value = result["result"][0]["expressions"][0]["value"]["allow"]
                    policy_results.append(
                        PolicyResult(
                            name=policy_name,
                            result=allow_value,
                            details={"raw_result": result}
                        )
                    )
                except Exception:
                    policy_results.append(
                        PolicyResult(
                            name=policy_name,
                            result=False,
                            details={"error": "Failed to parse result"}
                        )
                    )
            
            return EvaluationReport(
                app_details=ApplicationDetails(
                    name=consolidated_result.get("app_name", "N/A"),
                    evaluation_mode=consolidated_result.get("evaluation_mode", "N/A"),
                    contract_count=consolidated_result.get("combined_contract_count", 0),
                    evaluation_date=datetime.datetime.now()
                ),
                metric_groups=[
                    MetricGroup(
                        name="fairness",
                        display_name="Fairness Metrics",
                        metrics=fairness_metrics
                    ),
                    MetricGroup(
                        name="toxicity",
                        display_name="Toxicity Metrics",
                        metrics=toxicity_metrics
                    ),
                    MetricGroup(
                        name="stereotype",
                        display_name="Stereotype Metrics",
                        metrics=stereotype_metrics
                    )
                ],
                policy_results=policy_results,
                summary=consolidated_result.get("summary", "")
            )

        # Generate reports if requested
        if args.report_md or args.report_pdf:
            report_gen = ReportGenerator()
            evaluation_report = create_evaluation_report(consolidated_result, opa_results)
            
            if args.report_md:
                markdown_report = report_gen.generate_markdown_report(evaluation_report)
                try:
                    if report_gen.save_markdown_report(markdown_report, args.report_md):
                        logging.info(f"Markdown report generated at: {args.report_md}")
                    else:
                        logging.error("Failed to generate Markdown report")
                except Exception as e:
                    logging.error(f"Failed to write Markdown report: {e}")

            if args.report_pdf:
                if 'markdown_report' not in locals():
                    markdown_report = report_gen.generate_markdown_report(evaluation_report)
                if report_gen.generate_pdf_report(markdown_report, args.report_pdf):
                    logging.info(f"PDF report generated at: {args.report_pdf}")
                else:
                    logging.error("Failed to generate PDF report")


if __name__ == "__main__":
    main()
