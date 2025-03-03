import subprocess
import logging
import shutil
import sys
import os
import json
from typing import Dict, Any, Optional, List, Union, Literal
from pathlib import Path
from .policy_loader import PolicyLoader, Policy
from uuid import UUID
from datetime import datetime
import tempfile
import requests

from ..models.contract_models import AiCertifyContract as Contract

# Define execution modes as a Literal type for better type checking
ExecutionMode = Literal["production", "development", "debug"]

# Custom JSON encoder to handle UUID serialization
class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles UUID objects."""
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class OpaEvaluator:
    """Evaluator class for OPA policy evaluation."""

    def __init__(self, use_external_server: bool = False, server_url: str = "http://localhost:8181"):
        """Initialize the OPA evaluator.
        
        Args:
            use_external_server: Whether to use an external OPA server instead of the local binary
            server_url: URL of the external OPA server if use_external_server is True
        """
        self.policy_loader = PolicyLoader()
        self.opa_path = None if use_external_server else self._verify_opa_installation()
        self.use_external_server = use_external_server
        self.server_url = server_url
        self.policies_loaded = False
        
    def _verify_opa_installation(self) -> str:
        """Verify OPA is installed and return the path to the executable.
        
        Returns:
            str: Path to the OPA executable
            
        Raises:
            RuntimeError: If OPA is not found
        """
        # First check if OPA_PATH environment variable is set
        opa_path = os.environ.get("OPA_PATH")
        if opa_path and os.path.exists(opa_path) and os.access(opa_path, os.X_OK):
            logging.info(f"Found OPA at environment variable OPA_PATH: {opa_path}")
            return opa_path
            
        # Check for fixed path on Windows
        if os.name == "nt":
            # Try several possible Windows paths
            windows_paths = [
                "C:/opa/opa_windows_amd64.exe",
                "C:/opa/opa.exe",
                str(Path.cwd() / "opa_windows_amd64.exe")
            ]
            for path in windows_paths:
                if os.path.exists(path) and os.access(path, os.X_OK):
                    logging.info(f"Found OPA at fixed Windows path: {path}")
                    return path
                    
            # Check PATH for opa.exe and opa_windows_amd64.exe
            for path_dir in os.environ.get("PATH", "").split(os.pathsep):
                for filename in ["opa.exe", "opa_windows_amd64.exe"]:
                    exe_path = os.path.join(path_dir, filename)
                    if os.path.exists(exe_path) and os.access(exe_path, os.X_OK):
                        logging.info(f"Found OPA in PATH: {exe_path}")
                        return exe_path
                        
        # Check if it's in the PATH (works on Linux/macOS and potentially Windows)
        opa_path = shutil.which("opa")
        if opa_path:
            logging.info(f"Found OPA in PATH: {opa_path}")
            return opa_path
            
        # For WSL, try to find it in the Windows path
        if os.path.exists("/mnt/c"):
            # Check if it's in /mnt/c/opa
            wsl_paths = [
                "/mnt/c/opa/opa.exe",
                "/mnt/c/opa/opa_windows_amd64.exe"
            ]
            for path in wsl_paths:
                if os.path.exists(path) and os.access(path, os.X_OK):
                    logging.info(f"Found OPA in WSL Windows path: {path}")
                    return path
            
        # OPA wasn't found
        error_msg = (
            "OPA executable not found. Please ensure OPA is installed correctly:\n"
            "1. Download from https://openpolicyagent.org/docs/latest/#1-download-opa\n"
            "2. Rename to opa.exe and place in C:\\opa\\ on Windows or use 'sudo mv opa /usr/local/bin/' on Unix\n"
            "3. Or add OPA to your PATH\n"
            "4. Or set the OPA_PATH environment variable to the path of the OPA executable\n"
            f"Current PATH: {os.environ.get('PATH', '')}"
        )
        logging.error(error_msg)
        raise RuntimeError(error_msg)
        
    def _evaluate_with_local_opa(self, policy_path: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate policy using local OPA binary.
        
        Args:
            policy_path: Path to the policy file
            input_data: Input data for evaluation
            
        Returns:
            Dict[str, Any]: Evaluation results
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            # Use CustomJSONEncoder to handle UUID serialization
            json.dump(input_data, temp_file, cls=CustomJSONEncoder)
            temp_file_path = temp_file.name
            
        try:
            cmd = [
                self.opa_path,
                "eval",
                "--format", "json",
                "--data", policy_path,
                "--input", temp_file_path,
                "data"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            logging.error(f"OPA evaluation error: {e.stderr}")
            return {"error": e.stderr}
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    def _evaluate_with_external_opa(self, policy_path: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate policy using external OPA server.
        
        Args:
            policy_path: Path to evaluate in the policy structure (e.g., "fairness/evaluate")
            input_data: Input data for evaluation
            
        Returns:
            Dict[str, Any]: Evaluation results
        """
        url = f"{self.server_url}/v1/data/{policy_path}"
        headers = {"Content-Type": "application/json"}
        
        try:
            # Use CustomJSONEncoder to handle UUID serialization
            response = requests.post(
                url, 
                data=json.dumps({"input": input_data}, cls=CustomJSONEncoder), 
                headers=headers
            )
            if response.status_code == 200:
                return response.json()
            else:
                error_msg = f"OPA server returned status code: {response.status_code}, body: {response.text}"
                logging.error(error_msg)
                return {"error": error_msg}
        except requests.RequestException as e:
            error_msg = f"Error connecting to OPA server: {str(e)}"
            logging.error(error_msg)
            return {"error": error_msg}
                
    def load_policies(self, policy_dir: Optional[str] = None) -> None:
        """Load policies from directory.
        
        Args:
            policy_dir: Directory containing policy files
        """
        if self.policies_loaded:
            return
            
        if not policy_dir:
            # Use default policy directory
            policy_dir = os.path.join(os.path.dirname(__file__), "..", "opa_policies")
            
        self.policies = self.policy_loader.load_policies(policy_dir)
        
        # If using external server, upload policies to it
        if self.use_external_server:
            self._upload_policies_to_server()
        
        self.policies_loaded = True
        logging.info(f"Loaded {len(self.policies)} policies")
        
    def _upload_policies_to_server(self) -> None:
        """Upload policies to the external OPA server."""
        for policy in self.policies:
            policy_name = os.path.basename(policy.path)
            if policy_name.endswith('.rego'):
                policy_name = policy_name[:-5]  # Remove .rego extension
                
            url = f"{self.server_url}/v1/policies/{policy_name}"
            headers = {"Content-Type": "text/plain"}
            
            try:
                response = requests.put(url, data=policy.content, headers=headers)
                if response.status_code not in (200, 201):
                    logging.warning(f"Failed to upload policy {policy_name}: {response.status_code}")
            except requests.RequestException as e:
                logging.error(f"Error uploading policy {policy_name}: {str(e)}")
            
    def evaluate_contract(self, contract: Contract) -> Dict[str, Any]:
        """Evaluate a contract against loaded policies.
        
        Args:
            contract: The contract to evaluate
            
        Returns:
            Dict[str, Any]: Evaluation results
        """
        # Ensure policies are loaded
        self.load_policies()
        
        # Convert contract to dictionary for evaluation
        contract_dict = contract.model_dump()
        
        # Evaluate the contract against all policy types
        results = {}
        policy_types = ["fairness", "security", "compliance", "regulatory", "operational"]
        
        for policy_type in policy_types:
            try:
                if self.use_external_server:
                    # Evaluate using external OPA server
                    policy_path = f"{policy_type}/evaluate"
                    result = self._evaluate_with_external_opa(policy_path, contract_dict)
                    results[policy_type] = result.get("result", {})
                else:
                    # Evaluate using local OPA binary
                    # Find all policies of this type
                    type_policies = [p for p in self.policies if policy_type in p.path.lower()]
                    
                    if not type_policies:
                        logging.warning(f"No policies found for type: {policy_type}")
                        results[policy_type] = {"warning": f"No policies defined for {policy_type}"}
                        continue
                        
                    # Evaluate each policy
                    type_results = {}
                    for policy in type_policies:
                        result = self._evaluate_with_local_opa(policy.path, contract_dict)
                        policy_name = os.path.basename(policy.path).replace('.rego', '')
                        type_results[policy_name] = result
                        
                    results[policy_type] = type_results
            except Exception as e:
                logging.error(f"Error evaluating {policy_type} policies: {str(e)}")
                results[policy_type] = {"error": str(e)}
        
        return results

    def evaluate_policy(
        self, 
        policy_path: Union[str, List[str]], 
        input_data: Dict[str, Any], 
        query: str = None,
        mode: ExecutionMode = "production",
        entrypoint: str = None,
        optimize_level: int = 2
    ) -> Optional[Dict[str, Any]]:
        """
        Evaluate an OPA policy against input data with enhanced execution modes.
        
        Args:
            policy_path: Path to the .rego policy file or list of policy files
            input_data: Dictionary containing the input data
            query: Optional query parameter for the OPA evaluation
            mode: Execution mode determining the level of feedback and debugging
                - "production": Optimized for performance with minimal output
                - "development": Includes explanations for failures and coverage
                - "debug": Maximum verbosity with full explanations and metrics
            entrypoint: Optional entrypoint for optimization (required for production)
            optimize_level: Optimization level (0-2, default is 2 for production)
            
        Returns:
            Dictionary containing evaluation results or None if evaluation fails
        """
        try:
            # Handle single policy path or list of policy paths
            policy_files = [policy_path] if isinstance(policy_path, str) else policy_path
            
            # Convert all paths to absolute paths in POSIX format
            abs_policy_paths = [Path(p).resolve().as_posix() for p in policy_files]
            logging.debug(f"Policy file paths: {abs_policy_paths}")
            
            # Verify all policy files exist
            for path in abs_policy_paths:
                if not Path(path).is_file():
                    logging.error(f"Policy file not found: {path}")
                    return {"error": f"Policy file not found: {path}"}
            
            # Use the first policy file for query building if needed
            primary_policy_path = abs_policy_paths[0]
            
            # Convert input_data to proper JSON string
            try:
                # Use our global CustomJSONEncoder to handle UUID and datetime objects
                input_json = json.dumps(input_data, cls=CustomJSONEncoder)
                logging.debug(f"Input data: {input_json}")
            except Exception as e:
                logging.error(f"Error converting input data to JSON: {e}")
                return {"error": f"Failed to serialize input data: {str(e)}"}
            
            # If query is not provided, build it from policy file
            if not query:
                query = self.policy_loader.build_query_for_policy(primary_policy_path)
                logging.debug(f"Using query built from policy: {query}")
            
            # Resolve policy dependencies if not already provided
            if len(abs_policy_paths) == 1:
                policy_files = self.policy_loader.resolve_policy_dependencies(abs_policy_paths)
                logging.debug(f"Using policy files with dependencies: {policy_files}")
            else:
                policy_files = abs_policy_paths
            
            # Create a list of policy file arguments for OPA
            policy_args = []
            for policy_file in policy_files:
                policy_args.extend(["-d", Path(policy_file).resolve().as_posix()])
            
            # Base command with query and policy files
            cmd = [
                self.opa_path,
                "eval",
                query,  # Positional query argument
            ]
            
            # Add all policy files
            cmd.extend(policy_args)
            
            # Add mode-specific options
            if mode == "development":
                cmd.extend([
                    "--explain", "fails",  # Explain policy failures
                    "--coverage",          # Report coverage
                    "--format", "pretty",  # More readable output
                ])
                logging.debug("Using development mode with failure explanations and coverage reporting")
            elif mode == "debug":
                cmd.extend([
                    "--explain", "full",   # Full explanations
                    "--coverage",          # Report coverage
                    "--metrics",           # Performance metrics
                    "--instrument",        # Instrumentation
                    "--format", "pretty",  # More readable output
                ])
                logging.debug("Using debug mode with full explanations, coverage, and metrics")
            else:  # production mode
                cmd.extend([
                    "--format", "json",    # JSON output for parsing
                    "--fail",              # Exit with non-zero code on undefined/empty result
                ])
                
                # Only add optimization if we have an entrypoint
                if optimize_level > 0 and entrypoint:
                    cmd.extend(["--optimize", str(optimize_level)])
                    logging.debug(f"Using production mode with optimization level {optimize_level}")
                else:
                    logging.debug("Using production mode without optimizations")
            
            # Always add stdin-input for consistent input handling
            cmd.append("--stdin-input")
            
            # If using optimization with an entrypoint, include it
            if optimize_level > 0 and entrypoint and mode == "production":
                cmd.extend(["-e", entrypoint])
                logging.debug(f"Using entrypoint: {entrypoint}")
            
            logging.debug(f"Executing command: {cmd}")
            
            # Pass input via stdin
            try:
                result = subprocess.run(
                    cmd,
                    input=input_json,
                    capture_output=True,
                    text=True,
                    check=False  # Don't raise exception on non-zero exit
                )
            except subprocess.SubprocessError as e:
                logging.error(f"Error running OPA subprocess: {e}")
                return {"error": f"OPA execution failed: {str(e)}"}
            
            # Handle non-zero exit code with enhanced error recovery
            if result.returncode != 0:
                logging.error(f"OPA command failed with return code {result.returncode}")
                if result.stderr:
                    logging.error(f"OPA stderr output: {result.stderr}")
                
                # Check for specific error about bundle optimizations requiring entrypoint
                if "bundle optimizations require at least one entrypoint" in result.stderr:
                    logging.warning("OPA optimization requires an entrypoint, retrying without optimization")
                    # Retry without optimization
                    return self.evaluate_policy(
                        policy_path=policy_path, 
                        input_data=input_data, 
                        query=query, 
                        mode=mode,
                        entrypoint=None,  # Clear entrypoint
                        optimize_level=0  # Disable optimization
                    )
                
                # If not already in debug mode, retry with debug options for better diagnostics
                if mode != "debug":
                    logging.info("Retrying with debug mode to get more detailed error information")
                    return self.evaluate_policy(
                        policy_path=policy_path, 
                        input_data=input_data, 
                        query=query, 
                        mode="debug",
                        entrypoint=None,  # Clear entrypoint in debug mode
                        optimize_level=0  # Disable optimization in debug mode
                    )
                
                # Structured error response with detailed information
                return {
                    "error": f"OPA execution returned non-zero exit code: {result.returncode}",
                    "stderr": result.stderr,
                    "command": " ".join(cmd),
                    "policy_files": policy_files
                }
            
            if result.stderr:
                logging.warning(f"OPA stderr output (non-fatal): {result.stderr}")
            
            if not result.stdout or result.stdout.strip() == "":
                logging.warning("OPA returned empty output")
                
                # If not in debug mode, retry with debug mode
                if mode != "debug":
                    logging.info("Retrying with debug mode to diagnose empty output")
                    return self.evaluate_policy(
                        policy_path=policy_path, 
                        input_data=input_data, 
                        query=query, 
                        mode="debug",
                        entrypoint=None,  # Clear entrypoint in debug mode
                        optimize_level=0  # Disable optimization in debug mode
                    )
                
                # Return a structured result indicating empty output
                return {
                    "policy_name": Path(primary_policy_path).stem,
                    "result": False,
                    "error": "Empty result from OPA",
                    "details": "The policy evaluation returned no output. Check if the compliance_report rule exists in the policy."
                }
            
            logging.debug(f"OPA stdout output: {result.stdout[:200]}..." if len(result.stdout) > 200 else f"OPA stdout output: {result.stdout}")
            
            # Parse the output based on the format
            if mode in ["development", "debug"]:
                # For pretty format, just return the raw output
                if "--format" in cmd and cmd[cmd.index("--format") + 1] == "pretty":
                    return {
                        "result": result.stdout,
                        "format": "pretty",
                        "coverage": "--coverage" in cmd,
                        "metrics": "--metrics" in cmd
                    }
            
            # For JSON format (production mode or if pretty parsing failed)
            try:
                parsed_result = json.loads(result.stdout)
                
                # If parsed_result is empty object, create a meaningful response
                if not parsed_result or parsed_result == {}:
                    logging.warning("OPA returned empty JSON object")
                    
                    # Try running with 'allow' query to at least get basic compliance result
                    # Extract package prefix from the query
                    package_prefix = query.split("data.")[1].split(".")[0] if "data." in query else ""
                    allow_query = f"data.{package_prefix}.allow"
                    logging.debug(f"Trying alternative query for allow rule: {allow_query}")
                    
                    # Create a new command for the allow query
                    allow_cmd = [
                        self.opa_path,
                        "eval",
                        allow_query,
                    ]
                    
                    # Add policy files
                    allow_cmd.extend(policy_args)
                    
                    # Add format and input options
                    allow_cmd.extend([
                        "--format", "json",
                        "--stdin-input"
                    ])
                    
                    allow_result = subprocess.run(
                        allow_cmd,
                        input=input_json,
                        capture_output=True,
                        text=True,
                        check=False
                    )
                    
                    allow_value = False
                    details = "Policy only has 'allow' rule but no 'compliance_report' rule"
                    
                    if allow_result.returncode == 0 and allow_result.stdout:
                        try:
                            allow_parsed = json.loads(allow_result.stdout)
                            if "result" in allow_parsed and allow_parsed["result"]:
                                allow_value = allow_parsed["result"][0]["expressions"][0]["value"]
                                details = f"Policy evaluation succeeded with 'allow' rule: {allow_value}"
                        except Exception as e:
                            logging.error(f"Error parsing allow result: {e}")
                    
                    # Create a meaningful structured response that the rest of the code can handle
                    return {
                        "result": [{
                            "expressions": [{
                                "value": {
                                    "policy": Path(primary_policy_path).stem,
                                    "overall_result": allow_value,
                                    "detailed_results": {
                                        "compliance": {
                                            "result": allow_value,
                                            "details": details
                                        }
                                    },
                                    "recommendations": [
                                        "Update the policy to include a detailed compliance_report rule for better evaluation results"
                                    ]
                                }
                            }]
                        }]
                    }
                
                return parsed_result
                
            except json.JSONDecodeError as e:
                logging.error(f"Error parsing OPA output as JSON: {e}")
                
                # If output is not JSON but we have output, it might be from pretty format
                if result.stdout:
                    return {
                        "result": result.stdout,
                        "format": "raw",
                        "parse_error": str(e)
                    }
                
                return {"error": f"Failed to parse OPA output: {str(e)}", "raw_output": result.stdout}
                
        except Exception as e:
            logging.error(f"Unexpected error in evaluate_policy: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return {"error": f"Policy evaluation failed: {str(e)}"}

    def evaluate_policies_by_category(
        self, 
        category: str, 
        subcategory: str,
        input_data: Dict[str, Any],
        version: str = None,
        mode: ExecutionMode = "production"
    ) -> Dict[str, Any]:
        """Evaluate policies by category and subcategory.
        
        Args:
            category: The policy category (e.g. 'industry_specific', 'international')
            subcategory: The policy subcategory (e.g. 'healthcare', 'eu_ai_act')
            input_data: Input data for evaluation
            version: Policy version to use (default: latest)
            mode: Execution mode ('production', 'development', 'debug')
            
        Returns:
            Dict[str, Any]: Evaluation results
        """
        # Ensure policies are loaded
        self.load_policies()
        
        # If no version specified, use latest
        if not version:
            version = self.policy_loader.get_latest_version(category, subcategory)
            if not version:
                logging.error(f"No version found for {category}/{subcategory}")
                return {"error": f"No policies found for {category}/{subcategory}"}
                
        logging.info(f"Evaluating policies for {category}/{subcategory}/{version}")
        
        # Get policies for this category/subcategory/version
        policies = self.policy_loader.get_policies(category, subcategory, version)
        if not policies:
            logging.error(f"No policies found for {category}/{subcategory}/{version}")
            return {"error": f"No policies found for {category}/{subcategory}/{version}"}
            
        # Log the policies for debugging
        logging.debug(f"Found {len(policies)} policies for {category}/{subcategory}/{version}")
        for policy in policies:
            logging.debug(f"  Policy: {policy}")
            
        # Evaluate each policy in this category
        results = {}
        for policy_path in policies:
            try:
                policy_basename = os.path.basename(policy_path).replace('.rego', '')
                policy_name = f"{category}.{subcategory}.{version}.{policy_basename}" if subcategory else f"{category}.{version}.{policy_basename}"
                
                # For EU AI Act fairness policy, update the path format
                if category == "international" and subcategory == "eu_ai_act":
                    policy_name = f"international.eu_ai_act.v1.fairness"
                
                logging.info(f"Evaluating policy: {policy_name}")
                
                # Check if we're using an external server
                if self.use_external_server:
                    # Format the package path for the external server
                    if category == "industry_specific" and subcategory == "healthcare":
                        if "multi_specialist" in policy_path:
                            policy_package = "healthcare.multi_specialist.diagnostic_safety"
                        else:
                            policy_package = f"{subcategory}.{policy_basename}"
                    elif category == "international" and subcategory == "eu_ai_act":
                        if "fairness" in policy_path:
                            policy_package = "international.eu_ai_act.v1.fairness"
                        else:
                            policy_package = f"{category}.{subcategory}.{version}.{policy_basename}"
                    else:
                        policy_package = f"{category}.{subcategory}.{version}.{policy_basename}" if subcategory else f"{category}.{version}.{policy_basename}"
                        
                    result = self._evaluate_with_external_opa(
                        f"data.{policy_package}.compliance_report",
                        input_data
                    )
                    results[policy_basename] = result.get("result", {})
                else:
                    # Evaluate with local OPA binary
                    result = self._evaluate_policy(
                        policy_path=policy_path,
                        input_data=input_data,
                        mode=mode
                    )
                    results[policy_basename] = result
            except Exception as e:
                logging.error(f"Error evaluating policy {policy_path}: {str(e)}")
                results[os.path.basename(policy_path).replace('.rego', '')] = {"error": str(e)}
                
        return results
