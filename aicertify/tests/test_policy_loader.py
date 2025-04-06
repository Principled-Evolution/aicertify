#!/usr/bin/env python3
"""
Direct tests for the PolicyLoader class to diagnose issues.
"""

import unittest
import sys
import logging
from pathlib import Path

from aicertify.opa_core.policy_loader import PolicyLoader
# Ensure the aicertify package is in the Python path
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

class TestPolicyLoader(unittest.TestCase):
    """Direct tests for PolicyLoader functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test environment."""
        # Create a policy loader instance for testing
        cls.loader = PolicyLoader()
        
        # Log information about the policy loader
        logger.info(f"PolicyLoader instance created")
        logger.info(f"Policies directory: {cls.loader.policies_dir}")
        logger.info(f"Categories: {list(cls.loader.policies_by_category.keys())}")
        
        # Check if the policies directory exists
        if cls.loader.policies_dir.exists():
            logger.info(f"Policies directory exists: {cls.loader.policies_dir}")
            # List all .rego files
            rego_files = list(cls.loader.policies_dir.rglob("*.rego"))
            logger.info(f"Found {len(rego_files)} .rego files")
            for file in rego_files[:5]:  # Show first 5 files
                logger.info(f"- {file}")
            if len(rego_files) > 5:
                logger.info(f"... and {len(rego_files) - 5} more")
        else:
            logger.error(f"Policies directory does not exist: {cls.loader.policies_dir}")
    
    def test_get_policies_by_category(self):
        """Test getting policies by category."""
        # Test each of the main categories
        categories = ["global", "international", "industry_specific", "operational"]
        
        for category in categories:
            logger.info(f"Testing category: {category}")
            policies = self.loader.get_policies_by_category(category)
            
            # Verify that policies are returned
            self.assertIsNotNone(policies, f"No policies returned for category: {category}")
            self.assertIsInstance(policies, list, f"Expected list of policies for category: {category}")
            
            if policies:
                logger.info(f"Found {len(policies)} policies for category: {category}")
                for policy in policies[:3]:  # Show first 3 policies
                    logger.info(f"- {policy}")
                if len(policies) > 3:
                    logger.info(f"... and {len(policies) - 3} more")
            else:
                logger.warning(f"No policies found for category: {category}")
    
    def test_eu_ai_act_specific(self):
        """Test specifically the EU AI Act category which is commonly used."""
        # Test variations of EU AI Act category name
        eu_variations = ["eu_ai_act", "international/eu_ai_act", "international\\eu_ai_act"]
        
        for variation in eu_variations:
            logger.info(f"Testing EU AI Act variation: {variation}")
            policies = self.loader.get_policies_by_category(variation)
            
            # Verify that policies are returned
            self.assertIsNotNone(policies, f"No policies returned for EU AI Act variation: {variation}")
            self.assertIsInstance(policies, list, f"Expected list of policies for EU AI Act variation: {variation}")
            
            if policies:
                logger.info(f"Found {len(policies)} policies for EU AI Act variation: {variation}")
                for policy in policies:
                    logger.info(f"- {policy}")
            else:
                logger.warning(f"No policies found for EU AI Act variation: {variation}")
    
    def test_direct_access_vs_get_policies_by_category(self):
        """Compare direct access using get_policies vs get_policies_by_category."""
        # Get policies using direct access
        eu_direct = self.loader.get_policies("international", "eu_ai_act")
        
        # Get policies using get_policies_by_category
        eu_category = self.loader.get_policies_by_category("eu_ai_act")
        
        # Log results
        logger.info(f"Direct access result: {eu_direct}")
        logger.info(f"get_policies_by_category result: {eu_category}")
        
        # Verify that both methods return the same policies
        if eu_direct is None and eu_category is None:
            logger.warning("Both methods returned None")
        elif eu_direct is None:
            logger.warning("Direct access returned None, but get_policies_by_category returned results")
            self.fail("Inconsistent results between methods")
        elif eu_category is None:
            logger.warning("get_policies_by_category returned None, but direct access returned results")
            self.fail("Inconsistent results between methods")
        else:
            # Convert to sets for comparison (ignoring order)
            direct_set = set(eu_direct)
            category_set = set(eu_category)
            
            # Verify that both methods return the same policies
            self.assertEqual(direct_set, category_set, "Different policies returned by different methods")
            logger.info("Both methods returned the same policies")
    
    def test_available_categories(self):
        """Test getting all available categories."""
        try:
            categories = self.loader.get_all_categories()
            logger.info(f"Available categories: {categories}")
            
            # Verify that categories are returned
            self.assertIsNotNone(categories, "No categories returned")
            self.assertIsInstance(categories, list, "Expected list of categories")
            
            # Check if EU AI Act is in the list
            eu_ai_act_found = False
            for category, subcategory in categories:
                if category == "international" and subcategory == "eu_ai_act":
                    eu_ai_act_found = True
                    break
            
            if eu_ai_act_found:
                logger.info("EU AI Act category found")
            else:
                logger.warning("EU AI Act category not found")
                
        except Exception as e:
            logger.error(f"Error getting available categories: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.fail(f"Error getting available categories: {e}")

if __name__ == "__main__":
    unittest.main() 