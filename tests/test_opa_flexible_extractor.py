import unittest

from aicertify.opa_core.flexible_extractor import FlexibleExtractor
from aicertify.models.report import PolicyResult

class TestFlexibleExtractor(unittest.TestCase):
    """Tests for the FlexibleExtractor class."""
    
    def setUp(self):
        """Set up test cases."""
        # Sample OPA evaluation results
        self.sample_opa_results = {
            "result": [
                {
                    "expressions": [
                        {
                            "value": {
                                "v1": {
                                    "test_policy": {
                                        "compliance_report": {
                                            "compliant": True,
                                            "reason": "Policy requirements met",
                                            "recommendations": ["Keep up the good work"],
                                            "details": {
                                                "score": 0.95,
                                                "threshold": 0.8
                                            }
                                        }
                                    },
                                    "another_policy": {
                                        "compliance_report": {
                                            "compliant": False,
                                            "reason": "Policy requirements not met",
                                            "recommendations": ["Improve X", "Fix Y"],
                                            "details": {
                                                "score": 0.5,
                                                "threshold": 0.7
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    ]
                }
            ]
        }
        
        # Initialize extractor
        self.extractor = FlexibleExtractor()
    
    def test_extract_policy_data(self):
        """Test extracting policy data."""
        # Extract data for existing policy
        policy_data = self.extractor.extract_policy_data(self.sample_opa_results, "test_policy")
        self.assertIsNotNone(policy_data)
        self.assertIn("compliance_report", policy_data)
        
        # Extract data for non-existent policy
        policy_data = self.extractor.extract_policy_data(self.sample_opa_results, "non_existent_policy")
        self.assertIsNone(policy_data)
        
        # Test with invalid OPA results
        policy_data = self.extractor.extract_policy_data({}, "test_policy")
        self.assertIsNone(policy_data)
    
    def test_extract_policy_results(self):
        """Test extracting policy results."""
        # Extract results for existing policy
        policy_result = self.extractor.extract_policy_results(self.sample_opa_results, "test_policy")
        self.assertIsInstance(policy_result, PolicyResult)
        self.assertEqual(policy_result.name, "test_policy")
        self.assertTrue(policy_result.result)
        self.assertEqual(len(policy_result.recommendations), 1)
        self.assertIsInstance(policy_result.details, dict)
        self.assertEqual(policy_result.details["score"], 0.95)
        
        # Extract results for non-existent policy
        policy_result = self.extractor.extract_policy_results(self.sample_opa_results, "non_existent_policy")
        self.assertIsInstance(policy_result, PolicyResult)
        self.assertFalse(policy_result.result)
        self.assertIn("No compliance report", policy_result.details["error"])
        
        # Test with invalid OPA results
        policy_result = self.extractor.extract_policy_results({}, "test_policy")
        self.assertIsInstance(policy_result, PolicyResult)
        self.assertFalse(policy_result.result)
    
    def test_extract_all_policy_results(self):
        """Test extracting all policy results."""
        # Extract all policy results
        policy_results = self.extractor.extract_all_policy_results(self.sample_opa_results)
        self.assertEqual(len(policy_results), 2)
        
        # Check first policy
        test_policy = next((p for p in policy_results if p.name == "test_policy"), None)
        self.assertIsNotNone(test_policy)
        self.assertTrue(test_policy.result)
        
        # Check second policy
        another_policy = next((p for p in policy_results if p.name == "another_policy"), None)
        self.assertIsNotNone(another_policy)
        self.assertFalse(another_policy.result)
        
        # Test with invalid OPA results
        policy_results = self.extractor.extract_all_policy_results({})
        self.assertEqual(len(policy_results), 0)
    
    def test_handling_invalid_inputs(self):
        """Test handling of invalid inputs."""
        # Test with None input
        policy_result = self.extractor.extract_policy_results(None, "test_policy")
        self.assertIsInstance(policy_result, PolicyResult)
        self.assertFalse(policy_result.result)
        
        # Test with malformed OPA results
        malformed_results = {"result": "not a list"}
        policy_result = self.extractor.extract_policy_results(malformed_results, "test_policy")
        self.assertIsInstance(policy_result, PolicyResult)
        self.assertFalse(policy_result.result)
        
        # Test with empty policy name
        policy_result = self.extractor.extract_policy_results(self.sample_opa_results, "")
        self.assertIsInstance(policy_result, PolicyResult)
        self.assertEqual(policy_result.name, "")
    
    def test_normalized_name_lookup(self):
        """Test looking up policies by normalized name."""
        # Create OPA results with a policy that uses spaces and title case
        opa_results = {
            "result": [
                {
                    "expressions": [
                        {
                            "value": {
                                "v1": {
                                    "Test Policy": {
                                        "compliance_report": {
                                            "compliant": True,
                                            "reason": "Test passed",
                                            "recommendations": []
                                        }
                                    }
                                }
                            }
                        }
                    ]
                }
            ]
        }
        
        # Look up by underscore name
        policy_data = self.extractor.extract_policy_data(opa_results, "test_policy")
        self.assertIsNotNone(policy_data)
        self.assertIn("compliance_report", policy_data)
        
        # Extract results by underscore name
        policy_result = self.extractor.extract_policy_results(opa_results, "test_policy")
        self.assertIsInstance(policy_result, PolicyResult)
        self.assertTrue(policy_result.result)

if __name__ == "__main__":
    unittest.main() 