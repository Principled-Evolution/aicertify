from typing import Dict, Any, Optional, List
import logging
from aicertify.models.report import PolicyResult

class FlexibleExtractor:
    def _extract_value_from_expression(self, expr: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Helper method to extract value from an OPA expression.
        
        Args:
            expr: The expression dictionary
            
        Returns:
            The extracted value or None if not found
        """
        return expr.get("value") if isinstance(expr, dict) else None

    def _extract_from_nested_result(self, result_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Helper method to extract data from nested result structure.
        
        Args:
            result_data: The nested result data
            
        Returns:
            The extracted policy data or None if not found
        """
        if not isinstance(result_data, dict):
            return None
            
        # Handle direct value format (when metrics are directly available)
        if "metrics" in result_data:
            return result_data
            
        # Handle nested OPA result format
        if "result" in result_data:
            nested_result = result_data["result"]
            if isinstance(nested_result, list) and nested_result:
                expressions = nested_result[0].get("expressions", [])
                if expressions and isinstance(expressions, list):
                    value = self._extract_value_from_expression(expressions[0])
                    if value and "metrics" in value:
                        return value
        return None

    def extract_policy_data(self, opa_results: Dict[str, Any], policy_name: str) -> Optional[Dict[str, Any]]:
        """Extract policy data from OPA results.
        
        Args:
            opa_results: The OPA evaluation results
            policy_name: The name of the policy to extract data for
            
        Returns:
            Dictionary containing the policy data, or None if not found
        """
        try:
            if not opa_results or "result" not in opa_results:
                logging.warning("No valid OPA results found")
                return None
                
            result = opa_results["result"]
            
            # Handle aggregated individual results format
            if isinstance(result, dict) and result.get("policy") == "Aggregated Individual Results":
                for individual_result in result.get("results", []):
                    if individual_result.get("policy") == policy_name:
                        return self._extract_from_nested_result(individual_result.get("result", {}))
                logging.warning(f"Policy {policy_name} not found in aggregated results")
                return None
                
            # Handle direct OPA evaluation result
            if isinstance(result, list) and result:
                first_result = result[0]
                if "expressions" in first_result and first_result["expressions"]:
                    value = self._extract_value_from_expression(first_result["expressions"][0])
                    if value and "metrics" in value:
                        return value
                        
            logging.warning(f"No valid report_output format found for policy {policy_name}")
            return None
            
        except Exception as e:
            logging.error(f"Error extracting policy data for {policy_name}: {e}")
            import traceback
            logging.debug(traceback.format_exc())
            return None

    def extract_policy_results(self, opa_results: Dict[str, Any], policy_name: str) -> PolicyResult:
        """Extract detailed policy results from OPA evaluation results.
        
        Args:
            opa_results: The OPA evaluation results
            policy_name: The name of the policy to extract results for
            
        Returns:
            A PolicyResult object containing the extracted policy results
        """
        # Initialize default values
        compliant = False
        reason = f"No report_output available for {policy_name}"
        recommendations = []
        details = {"error": reason}
        
        try:
            policy_data = self.extract_policy_data(opa_results, policy_name)
            
            if policy_data and isinstance(policy_data, dict) and "metrics" in policy_data:
                metrics = policy_data["metrics"]
                if isinstance(metrics, dict):
                    valid_metrics = all(
                        isinstance(m, dict) and
                        "name" in m and isinstance(m["name"], str) and
                        "value" in m and
                        "control_passed" in m and isinstance(m["control_passed"], bool)
                        for m in metrics.values()
                    )
                    
                    if valid_metrics:
                        compliant = all(m["control_passed"] for m in metrics.values())
                        details = {
                            "metrics": metrics,
                            "policy": policy_name,
                            "timestamp": policy_data.get("timestamp", None)
                        }
                        reason = "Policy evaluation completed with standardized metrics"
                        recommendations = policy_data.get("recommendations", [])
            
        except Exception as e:
            logging.error(f"Error extracting policy results for {policy_name}: {e}")
            reason = f"Error extracting policy results: {str(e)}"
            details = {"error": str(e), "exception_type": type(e).__name__}
        
        return PolicyResult(
            name=policy_name,
            result=compliant,
            details=details,
            recommendations=recommendations
        )

    def extract_all_policy_results(self, opa_results: Dict[str, Any]) -> List[PolicyResult]:
        """Extract results for all policies found in the OPA evaluation results.
        
        Args:
            opa_results: The OPA evaluation results
            
        Returns:
            List of PolicyResult objects, one for each policy found
        """
        policy_results = []
        processed_policies = set()
        
        try:
            if not opa_results or "result" not in opa_results:
                return policy_results
                
            result = opa_results["result"]
            
            # Handle aggregated individual results format
            if isinstance(result, dict) and result.get("policy") == "Aggregated Individual Results":
                for individual_result in result.get("results", []):
                    policy_name = individual_result.get("policy")
                    if policy_name and policy_name not in processed_policies:
                        policy_result = self.extract_policy_results(opa_results, policy_name)
                        policy_results.append(policy_result)
                        processed_policies.add(policy_name)
            # Handle direct OPA evaluation result
            elif isinstance(result, list) and result:
                first_result = result[0]
                if "expressions" in first_result and first_result["expressions"]:
                    value = self._extract_value_from_expression(first_result["expressions"][0])
                    if value and "metrics" in value:
                        policy_name = value.get("policy", "unknown_policy")
                        policy_result = self.extract_policy_results(opa_results, policy_name)
                        policy_results.append(policy_result)
            
            logging.info(f"Extracted results for {len(policy_results)} policies")
            return policy_results
            
        except Exception as e:
            logging.error(f"Error extracting all policy results: {e}")
            import traceback
            logging.debug(traceback.format_exc())
            return policy_results