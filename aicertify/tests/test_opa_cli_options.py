import unittest
import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Configure logging for tests
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the parent directory to sys.path to allow importing from aicertify
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from aicertify.opa_core.evaluator import OpaEvaluator
from aicertify.opa_core.policy_loader import PolicyLoader
from aicertify.models.evaluation_models import (
    AiComplianceInput, 
    AiCertifyContract,
    AiEvaluationResult,
    ModelInfo,
    Interaction
)
from aicertify.opa_core.compliance_evaluator import run_opa_on_compliance_input, evaluate_contract_object


class TestOpaCliOptions(unittest.TestCase):
    """Test the enhanced OPA CLI options functionality."""

    def setUp(self):
        """Set up test environment."""
        # Create an OpaEvaluator instance
        self.evaluator = OpaEvaluator()
        
        # Create a PolicyLoader instance
        self.policy_loader = PolicyLoader()
        
        # Get the path to the test policy file
        self.test_policy_dir = Path(__file__).parent / "test_policies"
        self.test_policy_dir.mkdir(exist_ok=True)
        
        # Create a simple test policy file if it doesn't exist
        self.test_policy_file = self.test_policy_dir / "test_policy.rego"
        if not self.test_policy_file.exists():
            self._create_test_policy_file()
        
        # Create a sample input data
        self.sample_input = self._create_sample_input()
        
        # Create a sample AiComplianceInput
        self.compliance_input = self._create_sample_compliance_input()

    def _create_test_policy_file(self):
        """Create a simple test policy file."""
        policy_content = """
package test

# METADATA
# title: Test Policy
# description: A simple test policy for testing OPA CLI options
# version: 1.0.0
# category: test

# Default deny
default allow = false

# Allow if the input meets certain criteria
allow {
    input.status == "active"
    input.metrics.toxicity_score < 0.5
}

# Compliance report
compliance_report = {
    "policy": "Test Policy",
    "overall_result": allow,
    "detailed_results": {
        "status_check": {
            "result": input.status == "active",
            "details": "Status must be active"
        },
        "toxicity_check": {
            "result": input.metrics.toxicity_score < 0.5,
            "details": "Toxicity score must be less than 0.5"
        }
    },
    "recommendations": recommendations
}

# Generate recommendations based on compliance
recommendations = [] {
    allow
}

recommendations = ["Set status to active"] {
    input.status != "active"
}

recommendations = ["Reduce toxicity score below 0.5"] {
    input.metrics.toxicity_score >= 0.5
}
"""
        with open(self.test_policy_file, "w") as f:
            f.write(policy_content)
        
        logger.info(f"Created test policy file at {self.test_policy_file}")

    def _create_sample_input(self) -> Dict[str, Any]:
        """Create a sample input data for testing."""
        return {
            "status": "active",
            "app_name": "Test App",
            "evaluation_date": "2023-01-01",
            "metrics": {
                "toxicity_score": 0.2,
                "bias_score": 0.1
            },
            "summary": {
                "text": "This is a test summary",
                "gender_terms": [],
                "racial_terms": []
            },
            "documentation": {
                "technical_documentation": {
                    "exists": True,
                    "completeness": 0.9
                },
                "model_card": {
                    "exists": True,
                    "completeness": 0.8
                }
            }
        }

    def _create_sample_compliance_input(self) -> AiComplianceInput:
        """Create a sample AiComplianceInput for testing."""
        # Create a sample contract
        contract = AiCertifyContract(
            contract_id="contract-123",
            application_name="Test App",
            model_info=ModelInfo(
                model_name="GPT-Test",
                model_provider="Test Provider",
                model_version="1.0",
                model_type="text-generation",
                parameter_count=1000000000,
                model_capabilities=["text generation", "summarization"]
            ),
            interactions=[
                Interaction(
                    interaction_id="int-1",
                    input_text="What is AI certification?",
                    output_text="AI certification is a process to validate AI systems against regulatory and operational requirements.",
                    metadata={
                        "timestamp": datetime.now().isoformat(),
                        "completion_tokens": 15,
                        "prompt_tokens": 5,
                        "latency_ms": 250,
                        "pii_disclosure": False
                    }
                )
            ],
            final_output="The AI system complies with basic requirements.",
            context={
                "domain": "healthcare",
                "region": "EU",
                "purpose": "Testing",
                "sensitivity": "low"
            }
        )
        
        # Create a sample evaluation result
        evaluation = AiEvaluationResult(
            fairness_metrics={
                "demographic_parity": 0.95,
                "equal_opportunity": 0.92,
                "disparate_impact": 0.05
            },
            pii_detected={
                "has_pii": False,
                "pii_types": []
            },
            security_findings={
                "vulnerabilities": [],
                "passed_security_scan": True
            }
        )
        
        # Create and return the AiComplianceInput object
        return AiComplianceInput(
            app_name="Test App",
            domain="healthcare",
            evaluation_mode="full",
            contracts=[contract],  # List of contracts
            contract=contract,     # Required contract field
            evaluation=evaluation, # Required evaluation field
            metrics={
                "toxicity_score": 0.2,
                "bias_score": 0.1
            },
            summary={
                "text": "This is a test summary",
                "gender_terms": [],
                "racial_terms": []
            },
            status="active"
        )

    def test_production_mode(self):
        """Test OPA evaluation in production mode."""
        logger.info("Testing production mode evaluation")
        
        # Evaluate the policy in production mode
        result = self.evaluator.evaluate_policy(
            policy_path=str(self.test_policy_file),
            input_data=self.sample_input,
            mode="production"
        )
        
        # Check that the result is a dictionary
        self.assertIsInstance(result, dict)
        
        # Check that the result contains the expected keys
        if "error" in result:
            logger.error(f"Error in production mode: {result['error']}")
            self.fail(f"Production mode evaluation failed: {result['error']}")
        
        # Log the result structure
        logger.info(f"Production mode result structure: {list(result.keys())}")
        
        # Check that the result contains the expected data
        if "result" in result:
            self.assertIsInstance(result["result"], list)
            if len(result["result"]) > 0:
                expressions = result["result"][0].get("expressions", [])
                if expressions and len(expressions) > 0:
                    value = expressions[0].get("value", {})
                    logger.info(f"Production mode result value: {value}")
                    
                    # Check that the compliance report has the expected structure
                    if isinstance(value, dict):
                        self.assertIn("policy", value)
                        self.assertIn("overall_result", value)
                        self.assertIn("detailed_results", value)
                        self.assertIn("recommendations", value)

    def test_development_mode(self):
        """Test OPA evaluation in development mode."""
        logger.info("Testing development mode evaluation")
        
        # Evaluate the policy in development mode
        result = self.evaluator.evaluate_policy(
            policy_path=str(self.test_policy_file),
            input_data=self.sample_input,
            mode="development"
        )
        
        # Check that the result is a dictionary
        self.assertIsInstance(result, dict)
        
        # Check that the result contains the expected keys
        if "error" in result:
            logger.error(f"Error in development mode: {result['error']}")
            self.fail(f"Development mode evaluation failed: {result['error']}")
        
        # Log the result structure
        logger.info(f"Development mode result structure: {list(result.keys())}")
        
        # For development mode, we expect either a pretty format or JSON result
        if "format" in result and result["format"] == "pretty":
            self.assertIn("result", result)
            self.assertIn("coverage", result)
            logger.info("Development mode returned pretty format as expected")
        else:
            # If not pretty format, check for standard JSON result
            self.test_production_mode()

    def test_debug_mode(self):
        """Test OPA evaluation in debug mode."""
        logger.info("Testing debug mode evaluation")
        
        # Evaluate the policy in debug mode
        result = self.evaluator.evaluate_policy(
            policy_path=str(self.test_policy_file),
            input_data=self.sample_input,
            mode="debug"
        )
        
        # Check that the result is a dictionary
        self.assertIsInstance(result, dict)
        
        # Check that the result contains the expected keys
        if "error" in result:
            logger.error(f"Error in debug mode: {result['error']}")
            self.fail(f"Debug mode evaluation failed: {result['error']}")
        
        # Log the result structure
        logger.info(f"Debug mode result structure: {list(result.keys())}")
        
        # For debug mode, we expect either a pretty format with metrics or JSON result
        if "format" in result and result["format"] == "pretty":
            self.assertIn("result", result)
            self.assertIn("coverage", result)
            self.assertIn("metrics", result)
            logger.info("Debug mode returned pretty format with metrics as expected")
        else:
            # If not pretty format, check for standard JSON result
            self.test_production_mode()

    def test_error_recovery(self):
        """Test error recovery functionality."""
        logger.info("Testing error recovery functionality")
        
        # Create an invalid input that will cause an error
        invalid_input = {"invalid": "data"}
        
        # Evaluate the policy with invalid input in production mode
        # This should automatically retry in debug mode
        result = self.evaluator.evaluate_policy(
            policy_path=str(self.test_policy_file),
            input_data=invalid_input,
            mode="production"
        )
        
        # Check that the result is a dictionary
        self.assertIsInstance(result, dict)
        
        # Check that the result contains error information
        self.assertIn("error", result)
        logger.info(f"Error recovery test result: {result['error']}")
        
        # The error should contain detailed information
        if "stderr" in result:
            logger.info(f"Error stderr: {result['stderr']}")
        
        if "command" in result:
            logger.info(f"Error command: {result['command']}")

    def test_compliance_evaluator_integration(self):
        """Test integration with the compliance evaluator."""
        logger.info("Testing compliance evaluator integration")
        
        # Create a test policy category directory
        test_category_dir = self.policy_loader.policies_dir / "test"
        test_category_dir.mkdir(exist_ok=True)
        
        # Copy the test policy to the test category directory
        test_category_policy = test_category_dir / "test_policy.rego"
        if not test_category_policy.exists():
            with open(self.test_policy_file, "r") as src, open(test_category_policy, "w") as dst:
                dst.write(src.read())
        
        # Run the compliance evaluator with different modes
        for mode in ["production", "development", "debug"]:
            logger.info(f"Testing compliance evaluator with {mode} mode")
            
            # Run the compliance evaluator
            result = run_opa_on_compliance_input(
                compliance_input=self.compliance_input,
                policy_category="test",
                execution_mode=mode
            )
            
            # Check that the result is a dictionary
            self.assertIsInstance(result, dict)
            
            # Log the result structure
            logger.info(f"Compliance evaluator result structure for {mode} mode: {list(result.keys())}")
            
            # Check that the result contains the test policy
            self.assertIn("test_policy", result)

    def test_full_contract_evaluation(self):
        """Test full contract evaluation with different modes."""
        logger.info("Testing full contract evaluation")
        
        # Create test policy directories for all categories
        categories = ["global", "eu_ai_act", "healthcare"]
        for category in categories:
            category_path = Path(self.policy_loader.policies_dir) / category
            category_path.mkdir(exist_ok=True, parents=True)
            
            # Copy the test policy to each category directory
            category_policy = category_path / "test_policy.rego"
            if not category_policy.exists():
                with open(self.test_policy_file, "r") as src, open(category_policy, "w") as dst:
                    dst.write(src.read())
        
        # Run the full contract evaluation with different modes
        for mode in ["production", "development", "debug"]:
            logger.info(f"Testing full contract evaluation with {mode} mode")
            
            # Run the full contract evaluation
            result = evaluate_contract_object(
                compliance_input=self.compliance_input,
                execution_mode=mode
            )
            
            # Check that the result is a dictionary
            self.assertIsInstance(result, dict)
            
            # Log the result structure
            logger.info(f"Full contract evaluation result structure for {mode} mode: {list(result.keys())}")
            
            # Check that the result contains the expected categories
            for category in ["global", "eu_ai_act", "healthcare"]:
                self.assertIn(category, result)
            
            # Check that the metadata is included
            self.assertIn("_metadata", result)
            self.assertEqual(result["_metadata"]["execution_mode"], mode)


if __name__ == "__main__":
    unittest.main() 