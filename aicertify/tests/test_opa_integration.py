#!/usr/bin/env python3
"""
Integration tests for OPA policies with the AICertify framework.
Tests the interaction between the PolicyLoader, OpaEvaluator, and the policy structure.
"""

import unittest
import os
import sys
import json
import tempfile
import logging
from pathlib import Path

# Ensure the aicertify package is in the Python path
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from aicertify.opa_core.policy_loader import PolicyLoader
from aicertify.opa_core.evaluator import OpaEvaluator

class TestOpaIntegration(unittest.TestCase):
    """Integration tests for OPA policies with the AICertify framework."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test environment."""
        # Configure logging for tests
        logging.basicConfig(level=logging.INFO)
        
        # Create instances for testing
        cls.policy_loader = PolicyLoader()
        cls.evaluator = OpaEvaluator()
        
        # Create a sample input for policy evaluation
        cls.sample_input = {
            "metrics": {
                "toxicity": {
                    "score": 0.05  # Low toxicity score (compliant)
                },
                "stereotype": {
                    "metrics": {
                        "Stereotype Association": 0.05
                    }
                },
                "ftu_satisfied": True
            },
            "summary": {
                "stereotype_values": {
                    "gender_bias_detected": False,
                    "racial_bias_detected": False
                }
            },
            "evaluation": {
                "toxicity_score": 0.05
            },
            "risk_management": {
                "system": {
                    "exists": True
                },
                "assessment": {
                    "performed": True,
                    "completeness_score": 0.9
                },
                "mitigation": {
                    "implemented": True
                },
                "monitoring": {
                    "implemented": True
                },
                "post_market": {
                    "plan_exists": True
                }
            }
        }
        
        # Create a non-compliant sample input for policy evaluation
        cls.non_compliant_input = {
            "metrics": {
                "toxicity": {
                    "score": 0.5  # High toxicity score (non-compliant)
                },
                "stereotype": {
                    "metrics": {
                        "Stereotype Association": 0.3
                    }
                },
                "ftu_satisfied": False
            },
            "summary": {
                "stereotype_values": {
                    "gender_bias_detected": True,
                    "racial_bias_detected": True
                }
            },
            "evaluation": {
                "toxicity_score": 0.5
            },
            "risk_management": {
                "system": {
                    "exists": False
                },
                "assessment": {
                    "performed": False,
                    "completeness_score": 0.5
                },
                "mitigation": {
                    "implemented": False
                },
                "monitoring": {
                    "implemented": False
                },
                "post_market": {
                    "plan_exists": False
                }
            }
        }
    
    def test_global_policies_evaluation(self):
        """Test evaluation of global policies."""
        # Get global policies
        global_policies = self.policy_loader.get_policies("global")
        self.assertIsNotNone(global_policies)
        self.assertTrue(len(global_policies) > 0)
        
        # Get just the toxicity policy which we know works
        toxicity_policy = next((p for p in global_policies if "toxicity" in p), None)
        self.assertIsNotNone(toxicity_policy, "Toxicity policy should exist")
        
        # Evaluate toxicity policy
        result = self.evaluator.evaluate_policy(toxicity_policy, self.sample_input)
        
        # Check that we got a result
        self.assertIsNotNone(result)
        
        # Check for compliance_report in result structure
        if "result" in result:
            # This is the OPA raw result format
            self.assertIn("result", result)
            self.assertTrue(len(result["result"]) > 0)
            self.assertIn("expressions", result["result"][0])
            self.assertTrue(len(result["result"][0]["expressions"]) > 0)
            self.assertIn("value", result["result"][0]["expressions"][0])
            
            # The value should contain the compliance_report fields
            value = result["result"][0]["expressions"][0]["value"]
            self.assertIn("overall_result", value)
            self.assertIn("policy", value)
            self.assertIn("version", value)
            
            # For compliant input, the policy should pass
            self.assertTrue(value.get("overall_result", False))
        elif "compliance_report" in result:
            # Direct compliance report format
            self.assertIn("compliance_report", result)
            self.assertTrue(result["compliance_report"].get("overall_result", False))
    
    def test_non_compliant_evaluation(self):
        """Test evaluation with non-compliant input."""
        # Get global toxicity policy
        global_policies = self.policy_loader.get_policies("global")
        toxicity_policy = next((p for p in global_policies if "toxicity" in p), None)
        self.assertIsNotNone(toxicity_policy, "Toxicity policy should exist")
        
        # Evaluate with non-compliant input
        result = self.evaluator.evaluate_policy(toxicity_policy, self.non_compliant_input)
        
        # Check that we got a result
        self.assertIsNotNone(result)
        
        # Check for result structure
        if "result" in result:
            # This is the OPA raw result format
            self.assertIn("result", result)
            self.assertTrue(len(result["result"]) > 0)
            self.assertIn("expressions", result["result"][0])
            self.assertTrue(len(result["result"][0]["expressions"]) > 0)
            self.assertIn("value", result["result"][0]["expressions"][0])
            
            # The value should contain the compliance_report fields
            value = result["result"][0]["expressions"][0]["value"]
            self.assertIn("overall_result", value)
            
            # For non-compliant input, the policy should fail
            self.assertFalse(value.get("overall_result", True))
        elif "compliance_report" in result:
            # Direct compliance report format
            self.assertIn("compliance_report", result)
            self.assertFalse(result["compliance_report"].get("overall_result", True))
    
    def test_policy_loader_structure(self):
        """Test the policy loader structure."""
        # Test if the policy loader correctly identifies the policy structure
        categories = self.policy_loader.policies_by_category.keys()
        self.assertIn("global", categories)
        self.assertIn("international", categories)
        self.assertIn("industry_specific", categories)
        self.assertIn("operational", categories)
        
        # Test subcategories
        self.assertIn("eu_ai_act", self.policy_loader.policies_by_category["international"])
        
        # Test versioning
        self.assertIn("v1", self.policy_loader.policies_by_category["global"][""])
    
    def test_get_latest_version(self):
        """Test getting the latest version of a policy."""
        # Test with global policies
        global_version = self.policy_loader.get_latest_version("global", "")
        self.assertIsNotNone(global_version)
        self.assertEqual(global_version, "v1")
        
        # Test with EU AI Act policies
        eu_version = self.policy_loader.get_latest_version("international", "eu_ai_act")
        self.assertIsNotNone(eu_version)
        self.assertEqual(eu_version, "v1")
    
    def test_get_policies(self):
        """Test getting policies by category, subcategory, and version."""
        # Test getting global policies
        global_policies = self.policy_loader.get_policies("global")
        self.assertIsNotNone(global_policies)
        self.assertTrue(len(global_policies) > 0)
        
        # Test getting EU AI Act policies
        eu_policies = self.policy_loader.get_policies("international", "eu_ai_act")
        self.assertIsNotNone(eu_policies)
        self.assertTrue(len(eu_policies) > 0)
        
        # Test getting policies with explicit version
        eu_v1_policies = self.policy_loader.get_policies("international", "eu_ai_act", "v1")
        self.assertIsNotNone(eu_v1_policies)
        self.assertEqual(eu_policies, eu_v1_policies)  # Since v1 is the only/latest version

if __name__ == "__main__":
    unittest.main() 