from typing import Dict, Any, Optional, List
import logging
from aicertify.models.report import PolicyResult

class FlexibleExtractor:
    def extract_policy_results(self, opa_results: Dict[str, Any], policy_name: str) -> PolicyResult:
        """
        Extract detailed policy results from OPA evaluation results.
        
        Args:
            opa_results: The OPA evaluation results.
            policy_name: The name of the policy to extract results for.
            
        Returns:
            A PolicyResult object containing the extracted policy results.
        """
        # Initialize default values
        compliant = False
        reason = f"No compliance report available for {policy_name}"
        recommendations = []
        details = {"error": reason}  # Always use a dictionary for details
        
        logging.debug(f"Extracting policy results for {policy_name}")
        
        try:
            # Try to get version v1 policy data
            policy_data = self.extract_policy_data(opa_results, policy_name)
            
            # If we found a compliance report in the policy data
            if policy_data and isinstance(policy_data, dict) and "compliance_report" in policy_data:
                report = policy_data["compliance_report"]
                
                # Extract basic fields if they exist
                if isinstance(report, dict):
                    logging.debug(f"Found compliance report for {policy_name}")
                    compliant = report.get("compliant", False)
                    reason = report.get("reason", "No reason provided")
                    recommendations = report.get("recommendations", [])
                    
                    # Use all remaining data as details if available
                    report_details = {k: v for k, v in report.items() 
                                    if k not in ["compliant", "reason", "recommendations"]}
                    
                    # If we have details in the report, use them, otherwise use a default structure
                    if report_details:
                        details = report_details
                    else:
                        details = {"info": "No detailed information available in the compliance report"}
                else:
                    logging.warning(f"Compliance report for {policy_name} is not a dictionary: {report}")
                    details = {"error": f"Invalid compliance report format: {type(report).__name__}"}
            else:
                logging.debug(f"No compliance report found for {policy_name}")
                details = {"error": f"No compliance report found for policy {policy_name}"}
        except Exception as e:
            logging.error(f"Error extracting policy results for {policy_name}: {e}")
            reason = f"Error extracting policy results: {str(e)}"
            details = {"error": str(e), "exception_type": type(e).__name__}
        
        # Ensure details is always a dictionary
        if not isinstance(details, dict):
            details = {"error": f"Invalid details format: {details}"}
        
        # Create and return the result
        return PolicyResult(
            name=policy_name,
            result=compliant,
            details=details,
            recommendations=recommendations
        )
        
    def extract_policy_data(self, opa_results: Dict[str, Any], policy_name: str) -> Optional[Dict[str, Any]]:
        """
        Extract policy data for a specific policy from OPA evaluation results.
        
        Args:
            opa_results: The OPA evaluation results
            policy_name: The name of the policy to extract data for
            
        Returns:
            Dictionary containing the policy data, or None if not found
        """
        logging.debug(f"Extracting policy data for {policy_name}")
        
        try:
            # Check if we have a valid OPA result structure
            if not opa_results or "result" not in opa_results:
                logging.warning("No valid OPA results found")
                return None
            
            # Get the result list
            result_list = opa_results["result"]
            if not isinstance(result_list, list) or not result_list:
                logging.warning("OPA results has empty or invalid result list")
                return None
            
            # Get the first result
            first_result = result_list[0]
            
            # Check for expressions
            if "expressions" not in first_result or not first_result["expressions"]:
                logging.warning("No expressions found in OPA result")
                return None
            
            # Get the first expression
            first_expr = first_result["expressions"][0]
            
            # Check for value
            if "value" not in first_expr:
                logging.warning("No value found in OPA expression")
                return None
            
            # Get the value
            value = first_expr["value"]
            
            # Check for version keys (v1, v2, etc.)
            version_keys = [k for k in value.keys() if k.startswith("v")]
            if not version_keys:
                logging.warning("No version keys found in OPA result value")
                return None
            
            # Try each version key, prioritizing 'v1' if it exists
            if "v1" in version_keys:
                version_keys.remove("v1")
                version_keys.insert(0, "v1")  # Put v1 first
            
            # Search for the policy in each version
            for version_key in version_keys:
                version_data = value[version_key]
                if not isinstance(version_data, dict):
                    logging.warning(f"Version {version_key} data is not a dictionary")
                    continue
                
                # Look for the policy by name
                if policy_name in version_data:
                    policy_data = version_data[policy_name]
                    logging.debug(f"Found policy data for {policy_name} in version {version_key}")
                    return policy_data
                
                # Also check for policies with normalized names (replacing underscores with spaces and capitalizing)
                normalized_name = policy_name.replace("_", " ").title()
                if normalized_name in version_data:
                    policy_data = version_data[normalized_name]
                    logging.debug(f"Found policy data for {policy_name} using normalized name {normalized_name}")
                    return policy_data
            
            # If we get here, we didn't find the policy in any version
            logging.warning(f"Policy {policy_name} not found in any version")
            return None
            
        except Exception as e:
            logging.error(f"Error extracting policy data for {policy_name}: {e}")
            import traceback
            logging.debug(traceback.format_exc())
            return None
            
    def extract_all_policy_results(self, opa_results: Dict[str, Any]) -> List[PolicyResult]:
        """
        Extract results for all policies found in the OPA evaluation results.
        
        Args:
            opa_results: The OPA evaluation results
            
        Returns:
            List of PolicyResult objects, one for each policy found
        """
        policy_results = []
        
        try:
            # Check if we have a valid OPA result structure
            if not opa_results or "result" not in opa_results:
                logging.warning("No valid OPA results found")
                return policy_results
            
            # Get the result list
            result_list = opa_results["result"]
            if not isinstance(result_list, list) or not result_list:
                logging.warning("OPA results has empty or invalid result list")
                return policy_results
            
            # Get the first result
            first_result = result_list[0]
            
            # Check for expressions
            if "expressions" not in first_result or not first_result["expressions"]:
                logging.warning("No expressions found in OPA result")
                return policy_results
            
            # Get the first expression
            first_expr = first_result["expressions"][0]
            
            # Check for value
            if "value" not in first_expr:
                logging.warning("No value found in OPA expression")
                return policy_results
            
            # Get the value
            value = first_expr["value"]
            
            # Check for version keys (v1, v2, etc.)
            version_keys = [k for k in value.keys() if k.startswith("v")]
            if not version_keys:
                logging.warning("No version keys found in OPA result value")
                return policy_results
            
            # Process all policies in all versions
            processed_policies = set()  # Track which policies we've already processed
            
            for version_key in version_keys:
                version_data = value[version_key]
                if not isinstance(version_data, dict):
                    logging.warning(f"Version {version_key} data is not a dictionary")
                    continue
                
                # Process each policy in this version
                for policy_name, policy_data in version_data.items():
                    # Skip if we've already processed this policy
                    if policy_name in processed_policies:
                        continue
                    
                    # Extract results for this policy
                    policy_result = self.extract_policy_results(opa_results, policy_name)
                    policy_results.append(policy_result)
                    
                    # Mark as processed
                    processed_policies.add(policy_name)
            
            logging.info(f"Extracted results for {len(policy_results)} policies")
            return policy_results
            
        except Exception as e:
            logging.error(f"Error extracting all policy results: {e}")
            import traceback
            logging.debug(traceback.format_exc())
            return policy_results