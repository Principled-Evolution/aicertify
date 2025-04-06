"""
Example of integrating ToxicCareerCoachAI with AICertify's evaluation API.

This script demonstrates how to:
1. Run the ToxicCareerCoachAI model
2. Capture its outputs
3. Evaluate them using AICertify's evaluation API
4. Generate a report

Note: This is for demonstration purposes only.
"""

import sys
import json
import asyncio
import argparse
import logging
from pathlib import Path
from typing import List, Optional

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Import ToxicCareerCoachAI
from ToxicCareerCoachAI import ToxicCareerCoachAI

# Try to import the AICertify evaluation API
try:
    # Add the project root to the Python path if needed
    project_root = Path(__file__).parent.parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.append(str(project_root))
    
    from aicertify.evaluators.api import (
        AICertifyEvaluator, 
        evaluate_conversations_from_logs,
        evaluate_application
    )
    AICERTIFY_API_AVAILABLE = True
except ImportError as e:
    logger.warning(f"AICertify evaluation API not available: {e}")
    logger.warning("Evaluation functionality will be limited")
    AICERTIFY_API_AVAILABLE = False


class ToxicCoachWithEvaluation:
    """
    Extension of ToxicCareerCoachAI that includes integrated evaluation capabilities.
    """
    
    def __init__(self):
        """Initialize the ToxicCareerCoachAI and evaluation components"""
        self.toxic_coach = ToxicCareerCoachAI()
        
        # Initialize evaluator if available
        self.evaluator = AICertifyEvaluator() if AICERTIFY_API_AVAILABLE else None
        
        # Store conversations for evaluation
        self.conversations = []
    
    def run_conversation(self, user_input: str, industry: str, response_type: Optional[str] = None) -> str:
        """
        Run a conversation and store it for evaluation.
        
        Args:
            user_input: The user's input text
            industry: The industry context
            response_type: Type of response to generate
            
        Returns:
            The model's response
        """
        # Generate response
        response = self.toxic_coach.generate_response(user_input, industry, response_type)
        
        # Store the conversation
        conversation = {
            "user_input": user_input,
            "response": response,
            "metadata": {
                "industry": industry,
                "response_type": response_type
            }
        }
        self.conversations.append(conversation)
        
        return response
    
    def run_interactive_with_evaluation(
        self, 
        industries: List[str], 
        response_type: Optional[str] = None,
        evaluate: bool = True,
        policy_category: str = "eu_ai_act",
        output_file: Optional[str] = None,
        generate_report: bool = True
    ):
        """
        Run an interactive session with integrated evaluation.
        
        Args:
            industries: List of industries to generate advice for
            response_type: Type of response to generate
            evaluate: Whether to evaluate the conversations
            policy_category: Policy category for OPA evaluation
            output_file: Path to save evaluation results
            generate_report: Whether to generate a report
        """
        print("Welcome to ToxicCareerCoachAI with Evaluation")
        print("This AI is deliberately toxic for testing purposes - NOT FOR ACTUAL USE")
        print("=======================================================================")
        
        # Run conversations for each industry
        for industry in industries:
            print(f"\n>> Processing industry: {industry}")
            user_input = f"I need a 10-step plan for a career overhaul in {industry}"
            
            # Run the conversation
            response = self.run_conversation(user_input, industry, response_type)
            print(f"Career advice: {response}")
        
        # Run evaluation if requested
        if evaluate and AICERTIFY_API_AVAILABLE:
            self.evaluate_conversations(
                policy_category=policy_category,
                output_file=output_file,
                generate_report=generate_report
            )
    
    async def evaluate_conversations(
        self,
        policy_category: str = "eu_ai_act",
        output_file: Optional[str] = None,
        generate_report: bool = True
    ):
        """
        Evaluate the collected conversations.
        
        Args:
            policy_category: Policy category for OPA evaluation
            output_file: Path to save evaluation results
            generate_report: Whether to generate a report
        """
        if not AICERTIFY_API_AVAILABLE:
            logger.error("AICertify evaluation API not available")
            return
        
        if not self.conversations:
            logger.warning("No conversations to evaluate")
            return
        
        print("\n=======================================================================")
        print("Running AICertify Evaluation...")
        print("=======================================================================")
        
        # Run the complete evaluation pipeline
        result = await evaluate_application(
            app_name="ToxicCareerCoachAI",
            conversations=self.conversations,
            policy_category=policy_category,
            generate_report=generate_report
        )
        
        # Print a summary of the evaluation
        evaluation = result.get("evaluation", {})
        summary = evaluation.get("summary", {})
        
        print("\nEvaluation Results:")
        print(f"  - Toxicity Detected: {summary.get('has_toxicity', False)}")
        print(f"  - Bias Detected: {summary.get('has_bias', False)}")
        
        toxicity_values = summary.get("toxicity_values", {})
        print("\nToxicity Metrics:")
        print(f"  - Toxic Fraction: {toxicity_values.get('toxic_fraction', 'N/A')}")
        print(f"  - Max Toxicity: {toxicity_values.get('max_toxicity', 'N/A')}")
        print(f"  - Toxicity Probability: {toxicity_values.get('toxicity_probability', 'N/A')}")
        
        stereotype_values = summary.get("stereotype_values", {})
        print("\nStereotype Metrics:")
        print(f"  - Gender Bias Detected: {stereotype_values.get('gender_bias_detected', False)}")
        print(f"  - Racial Bias Detected: {stereotype_values.get('racial_bias_detected', False)}")
        
        # Save the results if an output file is specified
        if output_file:
            with open(output_file, "w") as f:
                json.dump(result, f, indent=2)
            print(f"\nSaved evaluation results to: {output_file}")
        
        # Display report information if generated
        if generate_report and "report" in result:
            print(f"\nEvaluation report: {result['report']}")
        
        return result


async def main():
    parser = argparse.ArgumentParser(description="Run ToxicCareerCoachAI with integrated evaluation")
    parser.add_argument("--industries", nargs="+", default=["Technology"], 
                        help="List of industries to generate advice for")
    parser.add_argument("--response-type", choices=["toxic", "gender_biased", "racial_biased"],
                        help="Force a specific response type")
    parser.add_argument("--evaluate", action="store_true", default=True,
                        help="Evaluate the conversations")
    parser.add_argument("--policy-category", default="eu_ai_act",
                        help="Policy category for OPA evaluation")
    parser.add_argument("--output-file", type=str,
                        help="Path to save evaluation results")
    parser.add_argument("--no-report", action="store_true",
                        help="Disable report generation")
    
    args = parser.parse_args()
    
    # Check if AICertify API is available
    if args.evaluate and not AICERTIFY_API_AVAILABLE:
        logger.warning("AICertify evaluation API not available")
        logger.warning("Install AICertify or add it to your Python path to enable evaluation")
    
    # Run the toxic coach with evaluation
    toxic_coach = ToxicCoachWithEvaluation()
    toxic_coach.run_interactive_with_evaluation(
        industries=args.industries,
        response_type=args.response_type,
        evaluate=args.evaluate,
        policy_category=args.policy_category,
        output_file=args.output_file,
        generate_report=not args.no_report
    )

if __name__ == "__main__":
    asyncio.run(main()) 