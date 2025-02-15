import os
import logging
from typing import Dict, List, Optional
from pathlib import Path

class PolicyLoader:
    """Loads OPA policies from the policies directory."""
    
    def __init__(self, policies_dir: str = "policies"):
        self.policies_dir = Path(policies_dir)
        self.policies = self._load_policies()
        
    def _load_policies(self) -> Dict[str, List[str]]:
        """
        Load all .rego policies from the policies directory.
        
        Returns:
            Dictionary mapping category names to lists of policy file paths
        """
        policies: Dict[str, List[str]] = {}
        
        if not self.policies_dir.exists():
            logging.error(f"Policies directory not found: {self.policies_dir}")
            return policies
            
        for policy_file in self.policies_dir.rglob("*.rego"):
            category = str(policy_file.parent.relative_to(self.policies_dir))
            if category not in policies:
                policies[category] = []
            policies[category].append(str(policy_file))
            
        if not policies:
            logging.warning("No policy files found in the policies directory")
            
        return policies
        
    def get_policies_by_category(self, category: str) -> Optional[List[str]]:
        """
        Get all policies for a specific category.
        
        Args:
            category: Policy category name
            
        Returns:
            List of policy file paths or None if category not found
        """
        if category not in self.policies:
            logging.error(f"Category '{category}' not found. Available categories: {list(self.policies.keys())}")
            return None
        return self.policies[category]

# Standalone test
if __name__ == "__main__":
    loader = PolicyLoader()
    print(loader.policies)  # Debugging: Prints loaded policies
