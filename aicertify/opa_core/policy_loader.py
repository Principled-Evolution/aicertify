import os
import logging
import sys
from typing import Dict, List, Optional
from pathlib import Path

class PolicyLoader:
    """Loads OPA policies from the policies directory."""
    
    def __init__(self, policies_dir: str = None):
        if policies_dir is None:
            # Determine the location of the aicertify module directory dynamically
            # First try to get the location from the current file
            current_file = Path(__file__)
            aicertify_dir = current_file.parent.parent  # Go up two levels from policy_loader.py
            
            # Default path relative to the aicertify module
            self.policies_dir = aicertify_dir / "opa_policies"
            
            # Log diagnostic info about the path we're using
            logging.info(f"Using policies directory from module path: {self.policies_dir}")
            
            # If path doesn't exist, try additional search paths
            if not self.policies_dir.exists():
                # Try the current working directory first
                cwd_path = Path.cwd() / "opa_policies"
                if cwd_path.exists():
                    self.policies_dir = cwd_path
                    logging.info(f"Found policies in current working directory: {self.policies_dir}")
                
                # Try to find relative to the main script
                elif '__main__' in sys.modules:
                    main_module = sys.modules['__main__']
                    if hasattr(main_module, '__file__'):
                        main_path = Path(main_module.__file__).parent
                        possible_paths = [
                            main_path / "opa_policies",
                            main_path / "aicertify" / "opa_policies",
                            main_path.parent / "aicertify" / "opa_policies"
                        ]
                        
                        for path in possible_paths:
                            if path.exists():
                                self.policies_dir = path
                                logging.info(f"Found policies relative to main script: {self.policies_dir}")
                                break
                
                # Try absolute known paths as last resort
                if not self.policies_dir.exists():
                    known_paths = [
                        Path("C:/Projects/AICertify/aicertify/opa_policies"),
                        Path("/aicertify/opa_policies")
                    ]
                    for path in known_paths:
                        if path.exists():
                            self.policies_dir = path
                            logging.info(f"Found policies at known path: {self.policies_dir}")
                            break
        else:
            self.policies_dir = Path(policies_dir)
            
        # Log the final chosen path
        logging.info(f"Using policies directory: {self.policies_dir}")
        
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
            
        # Log all .rego files found for diagnostic purposes
        all_rego_files = list(self.policies_dir.rglob("*.rego"))
        logging.info(f"Found {len(all_rego_files)} .rego files in {self.policies_dir}")
        for file in all_rego_files:
            logging.info(f"Found policy file: {file}")
            
        for policy_file in all_rego_files:
            try:
                category = str(policy_file.parent.relative_to(self.policies_dir))
                if category not in policies:
                    policies[category] = []
                policies[category].append(str(policy_file))
            except ValueError as e:
                # Handle case where relative_to fails
                logging.error(f"Error processing policy file {policy_file}: {e}")
                # As a fallback, use the parent directory name
                category = policy_file.parent.name
                if category not in policies:
                    policies[category] = []
                policies[category].append(str(policy_file))
            
        if not policies:
            logging.warning("No policy files found in the policies directory")
            
        # List all found categories
        if policies:
            logging.info(f"Found policy categories: {list(policies.keys())}")
            
        return policies
        
    def get_policies_by_category(self, category: str) -> Optional[List[str]]:
        """
        Get all policies for a specific category.
        
        Args:
            category: Policy category name
            
        Returns:
            List of policy file paths or None if category not found
        """
        # First try exact match
        if category in self.policies:
            return self.policies[category]
            
        # If not found, try case-insensitive matching or as a subdirectory
        normalized_category = category.lower().replace('\\', '/').replace(' ', '_')
        
        for cat_key in self.policies.keys():
            if cat_key.lower().replace('\\', '/').replace(' ', '_') == normalized_category:
                return self.policies[cat_key]
                
            # Also check if it's a path that contains multiple segments
            parts = normalized_category.split('/')
            if len(parts) > 1 and parts[-1] == cat_key.lower():
                return self.policies[cat_key]
        
        # If still not found, log error and return None
        logging.error(f"Category '{category}' not found. Available categories: {list(self.policies.keys())}")
        return None
        
    def get_all_categories(self) -> List[str]:
        """
        Get all available policy categories.
        
        Returns:
            List of all policy category names
        """
        return list(self.policies.keys())

# Standalone test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    loader = PolicyLoader()
    print("Available policy categories:", loader.get_all_categories())
    
    # Try to get EU AI Act policies
    eu_policies = loader.get_policies_by_category("eu_ai_act")
    print(f"EU AI Act policies: {eu_policies}")
