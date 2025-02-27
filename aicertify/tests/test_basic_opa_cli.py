import unittest
import os
import sys
import json
import logging
import tempfile
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

logger = logging.getLogger(__name__)

# Add the parent directory to the path to allow importing from aicertify
parent_dir = str(Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the OPA evaluator
from aicertify.opa_core.evaluator import OpaEvaluator
from aicertify.opa_core.policy_loader import PolicyLoader

class TestBasicOpaCliOptions(unittest.TestCase):
    """Test class for testing basic OPA CLI options."""

    def setUp(self):
        """Set up the test environment."""
        # Create an OPA evaluator instance
        self.opa_evaluator = OpaEvaluator()
        
        # Create a policy loader instance
        self.policy_loader = PolicyLoader()
        
        # Create a temporary directory for test policies if it doesn't exist
        self.test_policies_dir = Path('aicertify/tests/test_policies')
        self.test_policies_dir.mkdir(exist_ok=True, parents=True)
        
        # Create a test policy file if it doesn't exist
        self.test_policy_path = str(self.test_policies_dir / 'test_policy.rego')
        self._create_test_policy_file()

    def _create_test_policy_file(self):
        """Create a simple test policy file for testing."""
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
allow if {
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
recommendations = [] if {
    allow
}

recommendations = ["Set status to active"] if {
    input.status != "active"
}

recommendations = ["Reduce toxicity score below 0.5"] if {
    input.metrics.toxicity_score >= 0.5
}
"""
        # Write the policy to the file
        with open(self.test_policy_path, 'w') as f:
            f.write(policy_content)

    def _create_sample_input(self):
        """Create sample input data for testing."""
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

    def test_production_mode(self):
        """Test OPA evaluation in production mode."""
        logger.info("Testing production mode evaluation")
        
        # Create sample input data
        input_data = self._create_sample_input()
        
        # Evaluate the policy using the OPA evaluator in production mode
        result = self.opa_evaluator.evaluate_policy(
            policy_path=self.test_policy_path,
            input_data=input_data,
            mode="production"
        )
        
        logger.info(f"Production mode result structure: {list(result.keys())}")
        
        # In case of error, log and fail
        if "error" in result:
            self.fail(f"Production mode evaluation failed: {result['error']}")
        
        # Check the result structure - it may be a string or have result field with JSON data
        if "result" in result:
            # For pretty format, we can check if it contains the expected policy name
            self.assertIsInstance(result["result"], str)
            self.assertIn("Test Policy", result["result"])
        else:
            self.fail(f"Unexpected result structure: {result}")

    def test_development_mode(self):
        """Test OPA evaluation in development mode."""
        logger.info("Testing development mode evaluation")
        
        # Create sample input data
        input_data = self._create_sample_input()
        
        # Evaluate the policy using the OPA evaluator in development mode
        result = self.opa_evaluator.evaluate_policy(
            policy_path=self.test_policy_path,
            input_data=input_data,
            mode="development"
        )
        
        logger.info(f"Development mode result structure: {list(result.keys())}")
        
        # In case of error, log and fail
        if "error" in result:
            self.fail(f"Development mode evaluation failed: {result['error']}")
        
        # Check if format is as expected (pretty)
        if "format" in result:
            self.assertEqual(result["format"], "pretty")
            logger.info("Development mode returned pretty format as expected")
        else:
            self.fail(f"Development mode did not return expected format: {result}")

    def test_debug_mode(self):
        """Test OPA evaluation in debug mode."""
        logger.info("Testing debug mode evaluation")
        
        # Create sample input data
        input_data = self._create_sample_input()
        
        # Evaluate the policy using the OPA evaluator in debug mode
        result = self.opa_evaluator.evaluate_policy(
            policy_path=self.test_policy_path,
            input_data=input_data,
            mode="debug"
        )
        
        # In case of error, log and fail
        if "error" in result:
            self.fail(f"Debug mode evaluation failed: {result['error']}")
        
        # Check if metrics are included
        self.assertTrue("metrics" in result, f"Debug mode should include metrics: {result}")
        self.assertTrue("coverage" in result, f"Debug mode should include coverage: {result}")
        
        # Check the result - it should be detailed with explanations
        if "result" in result:
            # For debug mode, it should include detailed execution path
            self.assertIsInstance(result["result"], str)
            self.assertIn("Enter data.test.compliance_report", result["result"])
        else:
            self.fail(f"Debug mode did not return expected result structure: {result}")

    def test_error_recovery(self):
        """Test error recovery functionality."""
        logger.info("Testing error recovery functionality")
        
        # Create invalid input that should cause an error
        invalid_input = {"invalid": "data"}
        
        # Evaluate the policy with invalid input
        result = self.opa_evaluator.evaluate_policy(
            policy_path=self.test_policy_path,
            input_data=invalid_input,
            mode="production"
        )
        
        # The system should handle the error gracefully
        # Either by returning an error field or undefined result
        if "error" in result:
            logger.info(f"Error recovery test result: {result['error']}")
            self.assertTrue(True, "Error was properly captured")
        elif "result" in result and ("undefined" in str(result["result"]) or result["result"] == {}):
            logger.info(f"Error recovery resulted in undefined: {result['result']}")
            self.assertTrue(True, "Error was properly handled as undefined")
        else:
            self.fail(f"Error recovery test did not handle invalid input properly: {result}")
            
        # Additional check: make sure stderr is captured when available
        if "stderr" in result:
            logger.info(f"Error stderr: {result['stderr']}")
            
        # Additional check: make sure command is captured when available
        if "command" in result:
            logger.info(f"Error command: {result['command']}")

if __name__ == "__main__":
    unittest.main() 