import os
import logging
import sys
import re
from typing import Dict, List, Optional, Tuple, Set, NamedTuple
from pathlib import Path

class Policy(NamedTuple):
    """Represents a loaded policy with its path and content."""
    path: str
    content: str

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
            logging.debug(f"Using policies directory from module path: {self.policies_dir}")
            
            # If path doesn't exist, try additional search paths
            if not self.policies_dir.exists():
                logging.warning(f"Primary policies directory not found at: {self.policies_dir}")
                
                # Try the current working directory first
                cwd_path = Path.cwd() / "opa_policies"
                if cwd_path.exists():
                    self.policies_dir = cwd_path
                    logging.debug(f"Found policies in current working directory: {self.policies_dir}")
                
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
                                logging.debug(f"Found policies relative to main script: {self.policies_dir}")
                                break
                
                # If we still haven't found it, try some known install locations
                if not self.policies_dir.exists():
                    # Check site-packages
                    for path in sys.path:
                        if "site-packages" in path:
                            site_path = Path(path) / "aicertify" / "opa_policies"
                            if site_path.exists():
                                self.policies_dir = site_path
                                logging.debug(f"Found policies at known path: {self.policies_dir}")
                                break
        else:
            self.policies_dir = Path(policies_dir)
        
        logging.debug(f"Using policies directory: {self.policies_dir}")
        
        # Verify it's a directory
        if not self.policies_dir.exists() or not self.policies_dir.is_dir():
            err_msg = f"Policies directory not found or not a directory: {self.policies_dir}"
            logging.critical(err_msg)
            raise ValueError(err_msg)
        
        # Debug log directory contents
        top_level_items = list(self.policies_dir.iterdir())
        logging.debug(f"Contents of policies directory ({len(top_level_items)} items):")
        for item in top_level_items:
            if item.is_dir():
                subdir_items = list(item.iterdir())
                logging.debug(f"  - {item.name}/ ({len(subdir_items)} items)")
            else:
                logging.debug(f"  - {item.name}")
        
        # Load policies categorized by their structure
        self.policies_by_category = self._load_policies()
        
        # Extract package mappings from all policies for composition support
        self.package_mappings = self._extract_package_mappings()
        
    def _load_policies(self) -> Dict[str, Dict[str, Dict[str, List[str]]]]:
        """
        Load all .rego policies from the policies directory using the modular structure.
        
        The structure follows:
        - global/v1/accountability/accountability.rego
        - international/eu_ai_act/v1/fairness/fairness.rego
        - industry_specific/healthcare/v1/patient_safety/patient_safety.rego
        - operational/aiops/v1/scalability/scalability.rego
        
        Returns:
            Dictionary mapping categories to subcategories to versions to lists of policy file paths
            {
                "global": {
                    "": {  # Empty string for direct policies
                        "v1": ["/path/to/global/v1/accountability/accountability.rego", ...]
                    }
                },
                "international": {
                    "eu_ai_act": {
                        "v1": ["/path/to/international/eu_ai_act/v1/fairness/fairness.rego", ...]
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
        logging.debug(f"Found {len(all_rego_files)} .rego files in {self.policies_dir}")
        
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
                
                # Find the version directory by looking for a part that starts with 'v' and has digits after it
                version_index = -1
                for i, part in enumerate(parts):
                    if part.startswith('v') and part[1:].isdigit():
                        version_index = i
                        version = part
                        break
                
                if version_index == -1:
                    logging.warning(f"No version directory found for policy file: {policy_file}")
                    continue
                
                # Determine subcategory based on position of version directory
                if category == "global" and version_index == 1:
                    # For global: global/v1/*/policy.rego
                    subcategory = ""
                elif version_index == 2:
                    # For others: category/subcategory/v1/*/policy.rego
                    subcategory = parts[1]  # eu_ai_act, healthcare, etc.
                else:
                    logging.warning(f"Unexpected path structure for policy file: {policy_file}")
                    continue
                
                # Initialize nested dictionaries if they don't exist
                if subcategory not in policies[category]:
                    policies[category][subcategory] = {}
                if version not in policies[category][subcategory]:
                    policies[category][subcategory][version] = []
                
                # Add the policy file path
                policies[category][subcategory][version].append(str(policy_file))
                #logging.debug(f"Added policy file: {policy_file} to {category}/{subcategory}/{version}")
                
            except Exception as e:
                logging.error(f"Error processing policy file {policy_file}: {e}")
        
        # Log the organized structure
        for category, subcategories in policies.items():
            for subcategory, versions in subcategories.items():
                for version, files in versions.items():
                    logging.debug(f"Category: {category}, Subcategory: {subcategory or 'None'}, Version: {version}, Files: {len(files)}")
        
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
                                    #logging.debug(f"Mapped package '{package_name}' to file: {policy_file}")
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
            
            # If there are no subcategories but we're looking for a common one like eu_ai_act,
            # this could indicate a loading issue. Log more details for debugging.
            if not subcats and subcategory in ["eu_ai_act", "nist", "india"]:
                logging.error(f"Common subcategory '{subcategory}' not found. This may indicate a policy loading issue.")
                all_rego_files = list(self.policies_dir.rglob("*.rego"))
                matching_files = [f for f in all_rego_files if subcategory in str(f)]
                if matching_files:
                    logging.info(f"Found {len(matching_files)} .rego files containing '{subcategory}' in path:")
                    for file in matching_files[:5]:  # Limit to first 5 to avoid log spam
                        logging.info(f"  - {file}")
            
            return None
        
        # Use the specified version or get the latest
        if version is None:
            version = self.get_latest_version(category, subcategory)
            if version is None:
                logging.error(f"No versions found for category '{category}', subcategory '{subcategory}'")
                return None
            logging.debug(f"Using latest version: {version}")
        
        # Check if version exists
        if version not in self.policies_by_category[category][subcategory]:
            versions = list(self.policies_by_category[category][subcategory].keys())
            versions_str = ", ".join([f"'{v}'" for v in versions]) if versions else "none"
            logging.error(f"Version '{version}' not found for category '{category}', subcategory '{subcategory}'. Available versions: {versions_str}")
            return None
            
        policies = self.policies_by_category[category][subcategory][version]
        if policies:
            logging.debug(f"Found {len(policies)} policies for {category}/{subcategory}/{version}")
        else:
            logging.warning(f"No policies found for {category}/{subcategory}/{version}")
            
        return policies
    
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
        # Updated pattern to capture both standard imports and aliased imports
        import_pattern = re.compile(r'import\s+data\.([a-zA-Z0-9_\.]+)(?:\s+as\s+([a-zA-Z0-9_]+))?')
        
        # Also look for our v1 specific common modules
        v1_import_pattern = re.compile(r'import\s+data\.common\.([a-zA-Z0-9_\.]+)\.v1(?:\s+as\s+([a-zA-Z0-9_]+))?')
        
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
                            logging.debug(f"Found dependency: {imported_package} -> {dependency_file}")
                        else:
                            logging.warning(f"Could not resolve import for package: {imported_package}")
                            
                            # Special handling for common module imports
                            if "common." in imported_package:
                                # Try to find common modules in global/v1/common
                                common_module = imported_package.split(".")[-1]
                                common_path = os.path.join(
                                    self.policies_dir, 
                                    "global", 
                                    "v1", 
                                    "common", 
                                    f"{common_module}.rego"
                                )
                                if os.path.exists(common_path):
                                    dependencies.add(common_path)
                                    logging.debug(f"Found common module dependency: {imported_package} -> {common_path}")
                    
                    # Find v1-specific common module imports 
                    for match in v1_import_pattern.finditer(content):
                        common_module = match.group(1)
                        
                        # Look for the common module in global/v1/common
                        common_path = os.path.join(
                            self.policies_dir, 
                            "global", 
                            "v1", 
                            "common", 
                            f"{common_module}.rego"
                        )
                        if os.path.exists(common_path):
                            dependencies.add(common_path)
                            logging.debug(f"Found v1 common module dependency: common.{common_module}.v1 -> {common_path}")
                        else:
                            logging.warning(f"Could not find v1 common module: common.{common_module}.v1")
                            
            except Exception as e:
                logging.error(f"Error finding dependencies in {policy_file}: {e}")
                
        # Log all found dependencies
        if dependencies:
            logging.info(f"Found {len(dependencies)} policy dependencies")
            for dependency in dependencies:
                logging.debug(f"  Dependency: {dependency}")
        else:
            logging.warning("No policy dependencies found")
                
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
        
        logging.info(f"Trying policy path: {policy_category}")
        
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
                    logging.info(f"Found policies using direct path {category}/{subcategory}")
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
                    logging.info(f"Found policies using category match {category}")
                    return all_policies
        
        # Try to match as a standalone subcategory
        for category, subcategories in self.policies_by_category.items():
            for subcategory in subcategories.keys():
                if policy_category == subcategory:
                    policies = self.get_policies(category, subcategory)
                    if policies:
                        logging.info(f"Found policies using subcategory match {category}/{subcategory}")
                        return policies
                    
        # Special handling for EU AI Act since it's commonly used
        if policy_category.lower() in ['eu_ai_act', 'eu-ai-act', 'euaiact']:
            policies = self.get_policies('international', 'eu_ai_act')
            if policies:
                logging.info(f"Found policies using special case for EU AI Act")
                return policies
        
        # Log all available categories and subcategories for debugging
        available_categories = []
        for category, subcategories in self.policies_by_category.items():
            for subcategory in subcategories.keys():
                if subcategory:
                    available_categories.append(f"{category}/{subcategory}")
                else:
                    available_categories.append(category)
        logging.error(f"Available categories: {available_categories}")
                
        # Try global policies as fallback if the category contains "global"
        if 'global' in policy_category:
            policies = self.get_policies('global', '')
            if policies:
                logging.info(f"Found policies using global fallback")
                return policies
        
        # No matches found
        logging.warning(f"No policies found for category path: {policy_category}")
        return []

    def load_policies(self, policy_dir: Optional[str] = None) -> List[Policy]:
        """
        Load all policies from the specified directory or the default policies directory.
        
        Args:
            policy_dir: Directory containing policy files
            
        Returns:
            List[Policy]: List of Policy objects with path and content
        """
        # Use the policies directory if not specified
        if policy_dir is None:
            policy_dir = str(self.policies_dir)
            
        # Ensure the policies are loaded
        if not hasattr(self, 'policies_by_category'):
            self.policies_by_category = self._load_policies()
            
        # Collect all policy files
        all_policies = []
        
        # Walk the category structure and load each policy
        for category, subcategories in self.policies_by_category.items():
            for subcategory, versions in subcategories.items():
                for version, policy_files in versions.items():
                    for policy_file in policy_files:
                        try:
                            with open(policy_file, 'r') as f:
                                content = f.read()
                                all_policies.append(Policy(path=policy_file, content=content))
                        except Exception as e:
                            logging.error(f"Error loading policy {policy_file}: {str(e)}")
                            
        return all_policies

    def get_policy_dir(self) -> str:
        """Get the base directory for OPA policies.
        
        Returns:
            str: The absolute path to the policy directory
        """
        # Default to the opa_policies directory in the aicertify package
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "opa_policies"))

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
