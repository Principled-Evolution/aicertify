import os
import logging
import sys
import re
from typing import Dict, List, Optional, Tuple, Set
from pathlib import Path

class PolicyLoader:
    """
    Loads OPA policies from the policies directory with support for modular organization,
    versioning, and policy composition.
    """
    
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
        
        # Load policies categorized by their structure
        self.policies_by_category = self._load_policies()
        
        # Extract package mappings from all policies for composition support
        self.package_mappings = self._extract_package_mappings()
        
    def _load_policies(self) -> Dict[str, Dict[str, Dict[str, List[str]]]]:
        """
        Load all .rego policies from the policies directory using the modular structure.
        
        The new structure follows:
        - global/v1/policy.rego
        - international/eu_ai_act/v1/policy.rego
        - industry_specific/healthcare/v1/policy.rego
        - operational/aiops/v1/policy.rego
        
        Returns:
            Dictionary mapping categories to subcategories to versions to lists of policy file paths
            {
                "global": {
                    "": {  # Empty string for direct policies
                        "v1": ["/path/to/global/v1/transparency.rego", ...]
                    }
                },
                "international": {
                    "eu_ai_act": {
                        "v1": ["/path/to/international/eu_ai_act/v1/transparency.rego", ...]
                    }
                }
            }
        """
        policies: Dict[str, Dict[str, Dict[str, List[str]]]] = {
            "global": {},
            "international": {},
            "industry_specific": {},
            "operational": {}
        }
        
        if not self.policies_dir.exists():
            logging.error(f"Policies directory not found: {self.policies_dir}")
            return policies
            
        # Log all .rego files found for diagnostic purposes
        all_rego_files = list(self.policies_dir.rglob("*.rego"))
        logging.info(f"Found {len(all_rego_files)} .rego files in {self.policies_dir}")
        
        for policy_file in all_rego_files:
            try:
                # Get the relative path from the policies directory
                relative_path = policy_file.relative_to(self.policies_dir)
                
                # Parse the path components
                parts = list(relative_path.parts)
                
                # Skip legacy paths or unexpected structures
                if parts[0] not in policies:
                    logging.warning(f"Skipping policy file in unrecognized category: {policy_file}")
                    continue
                
                category = parts[0]  # global, international, etc.
                
                # Handle different path depths based on category
                subcategory = ""
                version = ""
                
                if len(parts) >= 3 and parts[-2].startswith('v'):  # Check if the parent dir is a version directory
                    # For global: global/v1/policy.rego
                    if category == "global" and len(parts) == 3:
                        subcategory = ""
                        version = parts[1]  # v1, v2, etc.
                    # For international, industry_specific, operational: category/subcategory/v1/policy.rego
                    elif len(parts) == 4:
                        subcategory = parts[1]  # eu_ai_act, healthcare, etc.
                        version = parts[2]  # v1, v2, etc.
                    else:
                        logging.warning(f"Unexpected path structure for policy file: {policy_file}")
                        continue
                else:
                    logging.warning(f"Policy file not in versioned directory: {policy_file}")
                    continue
                
                # Initialize nested dictionaries if they don't exist
                if subcategory not in policies[category]:
                    policies[category][subcategory] = {}
                if version not in policies[category][subcategory]:
                    policies[category][subcategory][version] = []
                
                # Add the policy file path
                policies[category][subcategory][version].append(str(policy_file))
                logging.info(f"Added policy file: {policy_file} to {category}/{subcategory}/{version}")
                
            except Exception as e:
                logging.error(f"Error processing policy file {policy_file}: {e}")
        
        # Log the organized structure
        for category, subcategories in policies.items():
            for subcategory, versions in subcategories.items():
                for version, files in versions.items():
                    logging.info(f"Category: {category}, Subcategory: {subcategory or 'None'}, Version: {version}, Files: {len(files)}")
        
        return policies
    
    def _extract_package_mappings(self) -> Dict[str, str]:
        """
        Extract package names from all .rego files to support policy composition.
        
        Returns:
            Dictionary mapping package names to file paths
        """
        package_mappings = {}
        
        for category, subcategories in self.policies_by_category.items():
            for subcategory, versions in subcategories.items():
                for version, policy_files in versions.items():
                    for policy_file in policy_files:
                        try:
                            # Extract package name from the file
                            with open(policy_file, 'r') as f:
                                content = f.read()
                                # Find package declaration (e.g., package international.eu_ai_act.v1.transparency)
                                match = re.search(r'package\s+([a-zA-Z0-9_\.]+)', content)
                                if match:
                                    package_name = match.group(1)
                                    package_mappings[package_name] = policy_file
                                    logging.info(f"Mapped package '{package_name}' to file: {policy_file}")
                        except Exception as e:
                            logging.error(f"Error extracting package from {policy_file}: {e}")
        
        return package_mappings
    
    def get_latest_version(self, category: str, subcategory: str = "") -> Optional[str]:
        """
        Get the latest version available for a category/subcategory.
        
        Args:
            category: Policy category (global, international, etc.)
            subcategory: Policy subcategory (empty for global, eu_ai_act for international, etc.)
            
        Returns:
            Latest version string (e.g., "v1") or None if not found
        """
        if category not in self.policies_by_category or subcategory not in self.policies_by_category[category]:
            logging.error(f"Category '{category}' or subcategory '{subcategory}' not found")
            return None
        
        versions = list(self.policies_by_category[category][subcategory].keys())
        if not versions:
            return None
            
        # Sort versions (assuming format "v1", "v2", etc.)
        versions.sort(key=lambda v: int(v[1:]) if v[1:].isdigit() else 0, reverse=True)
        return versions[0]
    
    def get_policies(self, category: str, subcategory: str = "", version: str = None) -> Optional[List[str]]:
        """
        Get all policies for a specific category, subcategory, and optionally version.
        If version is not specified, the latest version is used.
        
        Args:
            category: Policy category (global, international, etc.)
            subcategory: Policy subcategory (empty for global, eu_ai_act for international, etc.)
            version: Optional policy version (e.g., "v1")
            
        Returns:
            List of policy file paths or None if not found
        """
        # Normalize inputs
        category = category.lower()
        subcategory = subcategory.lower() if subcategory else ""
        
        # Check if category exists
        if category not in self.policies_by_category:
            logging.error(f"Category '{category}' not found. Available categories: {list(self.policies_by_category.keys())}")
            return None
            
        # Check if subcategory exists
        if subcategory not in self.policies_by_category[category]:
            subcats = list(self.policies_by_category[category].keys())
            subcats_str = ", ".join([f"'{sc}'" for sc in subcats]) if subcats else "none"
            logging.error(f"Subcategory '{subcategory}' not found in category '{category}'. Available subcategories: {subcats_str}")
            return None
        
        # Use the specified version or get the latest
        if version is None:
            version = self.get_latest_version(category, subcategory)
            if version is None:
                logging.error(f"No versions found for category '{category}', subcategory '{subcategory}'")
                return None
            logging.info(f"Using latest version: {version}")
        
        # Check if version exists
        if version not in self.policies_by_category[category][subcategory]:
            versions = list(self.policies_by_category[category][subcategory].keys())
            versions_str = ", ".join([f"'{v}'" for v in versions]) if versions else "none"
            logging.error(f"Version '{version}' not found for category '{category}', subcategory '{subcategory}'. Available versions: {versions_str}")
            return None
            
        return self.policies_by_category[category][subcategory][version]
    
    def resolve_policy_dependencies(self, policy_files: List[str]) -> List[str]:
        """
        Analyze policies and resolve their dependencies based on imports.
        
        Args:
            policy_files: List of policy file paths
            
        Returns:
            List of policy file paths including dependencies
        """
        resolved_files = set(policy_files)
        dependencies = self._find_policy_dependencies(policy_files)
        
        # Add all dependencies to the resolved set
        resolved_files.update(dependencies)
        
        return list(resolved_files)
    
    def _find_policy_dependencies(self, policy_files: List[str]) -> Set[str]:
        """
        Find all policy dependencies by analyzing import statements.
        
        Args:
            policy_files: List of policy file paths
            
        Returns:
            Set of policy file paths for dependencies
        """
        dependencies = set()
        import_pattern = re.compile(r'import\s+data\.([a-zA-Z0-9_\.]+)')
        
        for policy_file in policy_files:
            try:
                with open(policy_file, 'r') as f:
                    content = f.read()
                    
                    # Find all import statements
                    for match in import_pattern.finditer(content):
                        imported_package = match.group(1)
                        
                        # Resolve the file containing this package
                        if imported_package in self.package_mappings:
                            dependency_file = self.package_mappings[imported_package]
                            dependencies.add(dependency_file)
                            logging.info(f"Found dependency: {imported_package} -> {dependency_file}")
                        else:
                            logging.warning(f"Could not resolve import for package: {imported_package}")
            except Exception as e:
                logging.error(f"Error finding dependencies in {policy_file}: {e}")
                
        return dependencies
    
    def build_query_for_policy(self, policy_file: str) -> str:
        """
        Build an appropriate OPA query for a policy file based on its package.
        
        Args:
            policy_file: Path to the policy file
            
        Returns:
            OPA query string (e.g., "data.international.eu_ai_act.v1.transparency.compliance_report")
        """
        try:
            with open(policy_file, 'r') as f:
                content = f.read()
                
                # Extract package name
                match = re.search(r'package\s+([a-zA-Z0-9_\.]+)', content)
                if match:
                    package_name = match.group(1)
                    return f"data.{package_name}.compliance_report"
        except Exception as e:
            logging.error(f"Error building query for {policy_file}: {e}")
            
        # Fallback to a default query based on file path
        try:
            relative_path = Path(policy_file).relative_to(self.policies_dir)
            parts = list(relative_path.parts)
            
            # Skip the version directory
            for i, part in enumerate(parts):
                if part.startswith('v') and part[1:].isdigit():
                    parts.pop(i)
                    break
                    
            # Remove the .rego extension from the last part
            parts[-1] = parts[-1].replace('.rego', '')
            
            # Join parts with dots
            path_based_query = '.'.join(parts)
            return f"data.{path_based_query}.compliance_report"
        except Exception as e:
            logging.error(f"Error building fallback query for {policy_file}: {e}")
            
        # Super fallback
        return "data.compliance_report"
    
    def get_all_categories(self) -> List[Tuple[str, str]]:
        """
        Get all available policy categories and subcategories.
        
        Returns:
            List of tuples (category, subcategory)
        """
        result = []
        
        for category, subcategories in self.policies_by_category.items():
            for subcategory in subcategories:
                result.append((category, subcategory or None))
                
        return result

    def get_policies_by_category(self, policy_category: str) -> List[str]:
        """
        Get all policies for a specified category path, which can be a complex path like "eu_ai_act".
        This method tries different ways to interpret the policy_category parameter to find matching policies.
        
        Args:
            policy_category: Policy category path (can be direct category, subcategory, or combined path)
            
        Returns:
            List of policy file paths or empty list if not found
        """
        # Normalize path separators
        policy_category = policy_category.replace('\\', '/').lower()
        
        # Try to match as a direct category/subcategory combination
        if '/' in policy_category:
            parts = policy_category.split('/')
            # Remove any 'compliance' prefix that might be present
            if parts[0] == 'compliance' and len(parts) > 1:
                parts = parts[1:]
                
            if len(parts) >= 2:
                category, subcategory = parts[0], parts[1]
                # Try to get policies using direct category/subcategory match
                policies = self.get_policies(category, subcategory)
                if policies:
                    return policies
        
        # Try to match as a standalone category
        for category in self.policies_by_category.keys():
            if policy_category == category:
                # Get all policies in this category across all subcategories
                all_policies = []
                for subcategory in self.policies_by_category[category].keys():
                    subcategory_policies = self.get_policies(category, subcategory)
                    if subcategory_policies:
                        all_policies.extend(subcategory_policies)
                if all_policies:
                    return all_policies
        
        # Try to match as a standalone subcategory
        for category, subcategories in self.policies_by_category.items():
            for subcategory in subcategories.keys():
                if policy_category == subcategory:
                    policies = self.get_policies(category, subcategory)
                    if policies:
                        return policies
        
        # Try EU AI Act specifically as it's commonly used
        if policy_category in ['eu_ai_act', 'eu-ai-act', 'euaiact']:
            policies = self.get_policies('international', 'eu_ai_act')
            if policies:
                return policies
                
        # Try global policies as fallback if the category contains "global"
        if 'global' in policy_category:
            policies = self.get_policies('global', '')
            if policies:
                return policies
        
        # No matches found
        logging.warning(f"No policies found for category path: {policy_category}")
        return []

# Standalone test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    loader = PolicyLoader()
    
    # List all categories and subcategories
    print("Available policy categories and subcategories:")
    for category, subcategory in loader.get_all_categories():
        if subcategory:
            print(f"- {category}/{subcategory}")
        else:
            print(f"- {category}")
    
    # Try to get EU AI Act policies with version resolution
    eu_policies = loader.get_policies("international", "eu_ai_act")
    print(f"EU AI Act policies (latest version): {eu_policies}")
    
    # Try with specific version
    eu_policies_v1 = loader.get_policies("international", "eu_ai_act", "v1")
    print(f"EU AI Act policies (v1): {eu_policies_v1}")
    
    # Test dependency resolution
    if eu_policies:
        resolved_policies = loader.resolve_policy_dependencies(eu_policies)
        print(f"EU AI Act policies with dependencies: {resolved_policies}")
