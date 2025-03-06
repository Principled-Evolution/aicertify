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
import atexit

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

    def __init__(self, use_external_server: bool = False, server_url: str = "http://localhost:8181", debug: bool = False):
        """
        Initialize the OPA evaluator.
        
        Args:
            use_external_server: Whether to use an external OPA server
            server_url: URL of the external OPA server
            debug: Whether to enable debug mode
        """
        # Check environment variable for debug mode override
        env_debug_value = os.environ.get("OPA_DEBUG", "")
        env_debug = env_debug_value.lower() in ("1", "true", "yes", "on") and env_debug_value.lower() not in ("0", "false", "no", "off")
        self.debug = debug or env_debug
        
        logging.debug(f"OPA Evaluator initialized with debug={self.debug} (env value: {env_debug_value}, env override: {env_debug})")
        
        self.policy_loader = PolicyLoader()
        self.opa_path = None if use_external_server else self._verify_opa_installation()
        self.use_external_server = use_external_server
        self.server_url = server_url
        self.policies_loaded = False
        
        # Create a temporary directory for policy bundles
        self.temp_dir = tempfile.mkdtemp()
        atexit.register(lambda: shutil.rmtree(self.temp_dir, ignore_errors=True))
        
        # Log the debug mode status immediately
        if self.debug:
            logging.debug("OPA Evaluator debug mode is ENABLED")
        else:
            logging.debug("OPA Evaluator debug mode is DISABLED")
        
    def _verify_opa_installation(self) -> str:
        """Verify OPA is installed and return the path to the executable.
        
        Returns:
            str: Path to the OPA executable
            
        Raises:
            RuntimeError: If OPA is not found
        """
        # First check if OPA_PATH environment variable is set
        opa_path_env = os.environ.get("OPA_PATH")
        if opa_path_env and os.path.exists(opa_path_env) and os.access(opa_path_env, os.X_OK):
            logging.info(f"Found OPA at environment variable OPA_PATH: {opa_path_env}")
            return opa_path_env

        # Check OS-specific fixed locations
        if os.name == "nt":
            # Windows: Try several possible Windows paths
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

        elif sys.platform.startswith("linux"):
            # Linux: Try a fixed path first
            linux_path = "/usr/local/bin/opa"
            if os.path.exists(linux_path) and os.access(linux_path, os.X_OK):
                logging.info(f"Found OPA at fixed Linux path: {linux_path}")
                return linux_path

        # For WSL, try to find it in the Windows path using /mnt/c
        if os.path.exists("/mnt/c"):
            wsl_paths = [
                "/mnt/c/opa/opa.exe",
                "/mnt/c/opa/opa_windows_amd64.exe"
            ]
            for path in wsl_paths:
                if os.path.exists(path) and os.access(path, os.X_OK):
                    logging.info(f"Found OPA in WSL Windows path: {path}")
                    return path

        # Finally, check if it's in the PATH (works on Linux/macOS and potentially Windows)
        opa_path = shutil.which("opa")
        if opa_path:
            logging.info(f"Found OPA in PATH: {opa_path}")
            return opa_path

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
            policy_path: Path to the policy file or directory
            input_data: Input data for evaluation
            
        Returns:
            Dict[str, Any]: Evaluation results
        """
        # Check environment variable for debug mode override
        env_debug_value = os.environ.get("OPA_DEBUG", "")
        env_debug = env_debug_value.lower() in ("1", "true", "yes", "on") and env_debug_value.lower() not in ("0", "false", "no", "off")
        debug_mode = self.debug or env_debug
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            # Use CustomJSONEncoder to handle UUID serialization
            json.dump(input_data, temp_file, cls=CustomJSONEncoder)
            temp_file_path = temp_file.name
            
        try:
            # Always use the entire opa_policies directory as the bundle
            bundle_path = self.policy_loader.get_policy_dir()
            logging.debug(f"Using entire opa_policies directory as bundle: {bundle_path}")
            
            # Determine the query based on the specific policy path
            query = "data"
            if Path(policy_path).is_file():
                # If a specific file is provided, try to build a more specific query
                package_name = self.extract_package_from_file(Path(policy_path))
                if package_name:
                    query = f"data.{package_name}"
                    logging.debug(f"Using specific query for policy file: {query}")
            
            # Use bundle loading with the entire opa_policies directory
            cmd = [
                self.opa_path,
                "eval",
                "--format", "json",
                "--bundle", bundle_path,  # Use entire opa_policies directory
                "--input", temp_file_path,
                query
            ]
            
            # Optionally add debugging flags if debug mode is enabled
            if debug_mode:
                cmd.extend(["--explain", "full", "--coverage", "--instrument", "--metrics"])
                logging.debug(f"Debug mode active (self.debug={self.debug}, env_debug={env_debug}, env_value={env_debug_value}): Added OPA debugging flags to the command")
            
            logging.debug(f"Running OPA command: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logging.debug(f"OPA stdout: {result.stdout}")
            if result.stderr:
                logging.debug(f"OPA stderr: {result.stderr}")
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            logging.error(f"OPA evaluation error: {e.stderr}")
            return {"error": e.stderr}
        finally:
            if os.path.exists(temp_file_path):
                if debug_mode:
                    logging.debug(f"Keeping temporary input file for manual inspection: {temp_file_path}")
                else:
                    os.unlink(temp_file_path)
                
    def _evaluate_with_external_opa(self, policy_path: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate policy using external OPA server.
        
        Args:
            policy_path: Path to the policy file or directory
            input_data: Input data for evaluation
            
        Returns:
            Dict[str, Any]: Evaluation results
        """
        # Check environment variable for debug mode override
        env_debug_value = os.environ.get("OPA_DEBUG", "")
        env_debug = env_debug_value.lower() in ("1", "true", "yes", "on") and env_debug_value.lower() not in ("0", "false", "no", "off")
        debug_mode = self.debug or env_debug
        
        try:
            # For external server, we need to determine the package and query
            # First, determine if policy_path is a file or directory
            if Path(policy_path).is_file():
                # Extract package from the policy file
                package_name = self.extract_package_from_file(Path(policy_path))
                if not package_name:
                    return {"error": f"Could not extract package name from policy file: {policy_path}"}
            else:
                # For directories, convert the path to a package path
                policy_dir = self.policy_loader.get_policy_dir()
                try:
                    rel_path = Path(policy_path).relative_to(Path(policy_dir))
                    package_name = str(rel_path).replace(os.sep, '.')
                except ValueError:
                    # If policy_path is not relative to policy_dir
                    return {"error": f"Policy path {policy_path} is not within the policy directory {policy_dir}"}
            
            # Build the data query URL
            query_url = f"{self.server_url}/v1/data/{package_name.replace('.', '/')}"
            
            # Prepare request parameters
            request_params = {"input": input_data}
            
            # Add debug parameters if debug mode is enabled
            if debug_mode:
                request_params.update({
                    "explain": "full",
                    "metrics": True,
                    "instrument": True,
                    "pretty": True
                })
                logging.debug(f"Debug mode active (self.debug={self.debug}, env_debug={env_debug}, env_value={env_debug_value}): Added debug parameters to OPA server request")
            
            logging.debug(f"Making request to OPA server: {query_url}")
            
            # Make the request to the OPA server
            response = requests.post(
                query_url,
                json=request_params,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                return {"error": f"OPA server returned error: {response.text}"}
            
            # Log the response if in debug mode
            if debug_mode:
                logging.debug(f"OPA server response: {response.text}")
                
            return response.json()
        except Exception as e:
            logging.error(f"Error evaluating policy with external OPA server: {str(e)}")
            return {"error": f"External OPA evaluation failed: {str(e)}"}
                
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
        # Check environment variable for debug mode override
        env_debug = os.environ.get("OPA_DEBUG", "").lower() in ("1", "true", "yes", "on")
        debug_mode = self.debug or env_debug
        
        if debug_mode:
            logging.debug(f"Debug mode active for contract evaluation (self.debug={self.debug}, env_debug={env_debug})")
        
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
        mode: ExecutionMode = "debug",
        entrypoint: str = None,
        optimize_level: int = 2,
        retry_count: int = 0  # Add retry counter
    ) -> Optional[Dict[str, Any]]:
        """
        Evaluate an OPA policy against input data with enhanced execution modes.
        
        Args:
            policy_path: Path to the .rego policy file, list of policy files, or directory containing policies
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
        # Check environment variable for debug mode override
        env_debug_value = os.environ.get("OPA_DEBUG", "")
        env_debug_forces_production = env_debug_value.lower() in ("0", "false", "no", "off")
        
        if env_debug_value.lower() in ("1", "true", "yes", "on"):
            mode = "debug"
            logging.debug("OPA_DEBUG environment variable set to true, forcing debug mode")
        elif env_debug_forces_production and mode == "debug":
            mode = "production"
            logging.debug("OPA_DEBUG environment variable set to false, forcing production mode")
        elif self.debug and mode != "debug":
            logging.debug(f"Debug mode enabled in evaluator, but mode is {mode}. Consider using debug mode for more detailed output.")
        
        try:
            # Always use the entire opa_policies directory as the bundle
            bundle_path = self.policy_loader.get_policy_dir()
            logging.debug(f"Using entire opa_policies directory as bundle: {bundle_path}")
            
            # Convert input_data to proper JSON string
            try:
                # Use our global CustomJSONEncoder to handle UUID and datetime objects
                input_json = json.dumps(input_data, cls=CustomJSONEncoder)
                # Log a truncated version of the input data for debugging
                input_preview = input_json[:200] + "..." if len(input_json) > 200 else input_json
                logging.debug(f"Input data: {input_preview}")
                
                # Optionally save input to file for debugging
                if self.debug:
                    debug_dir = Path("./debug_opa")
                    debug_dir.mkdir(exist_ok=True)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    input_file = debug_dir / f"opa_input_{timestamp}.json"
                    with open(input_file, "w") as f:
                        f.write(input_json)
                    logging.debug(f"Saved input data to {input_file}")
            except Exception as e:
                logging.error(f"Error converting input data to JSON: {e}")
                return {"error": f"Failed to serialize input data: {str(e)}"}
            
            # If query is not provided, build it from policy file
            if not query and isinstance(policy_path, str) and Path(policy_path).is_file():
                # Try to extract package from the file
                package_name = self.extract_package_from_file(Path(policy_path))
                if package_name:
                    query = f"data.{package_name}"
                    logging.debug(f"Using query built from package name: {query}")
                else:
                    # Fall back to the policy loader's query builder
                    query = self.policy_loader.build_query_for_policy(policy_path)
                logging.debug(f"Using query built from policy: {query}")
            elif not query:
                # Default query if we can't determine a specific one
                query = "data"
                logging.debug(f"Using default query: {query}")
            
            # Base command with query and bundle
            cmd = [
                self.opa_path,
                "eval",
                query,  # Positional query argument
                "--bundle", bundle_path  # Use entire opa_policies directory
            ]
            
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
                
                # Log stderr output with more detail
                if result.stderr:
                    logging.error(f"OPA stderr output: {result.stderr}")
                    # Save stderr to file for debugging
                    if self.debug:
                        debug_dir = Path("./debug_opa")
                        debug_dir.mkdir(exist_ok=True)
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        stderr_file = debug_dir / f"opa_stderr_{timestamp}.txt"
                        with open(stderr_file, "w") as f:
                            f.write(result.stderr)
                        logging.debug(f"Saved stderr output to {stderr_file}")
                else:
                    logging.error("OPA command failed but stderr is empty. Trying with --format json for better error reporting")
                    # Try again with JSON format to get more structured error information
                    json_cmd = cmd.copy()
                    # Replace format option if it exists
                    if "--format" in json_cmd:
                        format_index = json_cmd.index("--format")
                        if format_index + 1 < len(json_cmd):
                            json_cmd[format_index + 1] = "json"
                    else:
                        json_cmd.extend(["--format", "json"])
                    
                    # Add debug flags if not already present
                    if "--explain" not in json_cmd:
                        json_cmd.extend(["--explain", "full"])
                    if "--coverage" not in json_cmd:
                        json_cmd.append("--coverage")
                    if "--metrics" not in json_cmd:
                        json_cmd.append("--metrics")
                    if "--instrument" not in json_cmd:
                        json_cmd.append("--instrument")
                    
                    logging.debug(f"Retrying with debug flags: {json_cmd}")
                    
                    try:
                        json_result = subprocess.run(
                            json_cmd,
                            input=input_json,
                            capture_output=True,
                            text=True,
                            check=False
                        )
                        if json_result.stderr:
                            logging.error(f"OPA stderr output (JSON format): {json_result.stderr}")
                        if json_result.stdout:
                            logging.error(f"OPA stdout output (JSON format): {json_result.stdout}")
                    except Exception as e:
                        logging.error(f"Error running OPA with JSON format: {e}")
                
                # Check for specific error about bundle optimizations requiring entrypoint
                if result.stderr and "bundle optimizations require at least one entrypoint" in result.stderr:
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
                
                # If not in debug mode and retry count is less than max retries, retry with debug mode
                # Only if OPA_DEBUG doesn't force production mode
                if mode != "debug" and retry_count < 2 and not env_debug_forces_production:
                    logging.info(f"Retrying with debug mode to get more detailed error information (retry {retry_count+1}/2)")
                    return self.evaluate_policy(
                        policy_path=policy_path, 
                        input_data=input_data, 
                        query=query, 
                        mode="debug",
                        entrypoint=None,
                        optimize_level=0,
                        retry_count=retry_count + 1  # Increment retry counter
                    )
                
                # Structured error response with detailed information
                error_response = {
                    "error": f"OPA execution returned non-zero exit code: {result.returncode}",
                    "command": " ".join(cmd),
                    "policy_files": policy_path if isinstance(policy_path, list) else [policy_path],
                    "query": query
                }
                
                # Include stderr if available
                if result.stderr:
                    error_response["stderr"] = result.stderr
                
                # In debug mode, stdout often contains the detailed error messages
                if result.stdout:
                    error_response["stdout"] = result.stdout
                    # Log the stdout for visibility
                    logging.error(f"OPA stdout error details: {result.stdout}")
                
                return error_response
            
            # Save output for debugging
            if self.debug and result.stdout:
                debug_dir = Path("./debug_opa")
                debug_dir.mkdir(exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = debug_dir / f"opa_output_{timestamp}.txt"
                with open(output_file, "w") as f:
                    f.write(result.stdout)
                logging.debug(f"Saved output to {output_file}")
            
            if result.stderr:
                logging.warning(f"OPA stderr output (non-fatal): {result.stderr}")
            
            if not result.stdout or result.stdout.strip() == "":
                logging.warning("OPA returned empty output")
                
                # If not in debug mode and retry count is less than max retries, retry with debug mode
                # Only if OPA_DEBUG doesn't force production mode
                if mode != "debug" and retry_count < 2 and not env_debug_forces_production:
                    logging.info(f"Retrying with debug mode to diagnose empty output (retry {retry_count+1}/2)")
                    return self.evaluate_policy(
                        policy_path=policy_path, 
                        input_data=input_data, 
                        query=query, 
                        mode="debug",
                        entrypoint=None,
                        optimize_level=0,
                        retry_count=retry_count + 1  # Increment retry counter
                    )
                
                # Return a structured result indicating empty output
                return {
                    "policy_name": Path(policy_path).stem if isinstance(policy_path, str) else Path(policy_path[0]).stem,
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
                    allow_cmd.extend(policy_path if isinstance(policy_path, list) else [policy_path])
                    
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
                                    "policy": Path(policy_path).stem if isinstance(policy_path, str) else Path(policy_path[0]).stem,
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
        """
        Evaluate all policies in a specific category and subcategory.

        Args:
            category: The policy category (e.g., 'global', 'industry_specific')
            subcategory: The policy subcategory (e.g., 'fairness', 'healthcare')
            input_data: The input data for evaluation
            version: Optional version string (e.g., 'v1')
            mode: Execution mode (production, development, debug)
            
        Returns:
            Dict[str, Any]: Evaluation results for all policies
        """
        # Check environment variable for debug mode override
        env_debug_value = os.environ.get("OPA_DEBUG", "")
        if env_debug_value.lower() in ("1", "true", "yes", "on"):
            mode = "debug"
            logging.debug(f"OPA_DEBUG environment variable set to true, forcing debug mode for category evaluation: {category}/{subcategory}")
        elif env_debug_value.lower() in ("0", "false", "no", "off") and mode == "debug":
            mode = "production"
            logging.debug(f"OPA_DEBUG environment variable set to false, forcing production mode for category evaluation: {category}/{subcategory}")
        elif self.debug and mode != "debug":
            logging.debug(f"Debug mode enabled in evaluator, but mode is {mode}. Consider using debug mode for more detailed output.")
        
        # Construct the policy directory path to determine the query
        policy_dir = self.policy_loader.get_policy_dir()
        
        if version:
            category_path = Path(policy_dir) / category / version / subcategory
        else:
            # Try to find the latest version
            base_path = Path(policy_dir) / category
            if not base_path.exists():
                return {"error": f"Category path not found: {base_path}"}
                
            # Find all version directories (assuming they start with 'v')
            version_dirs = [d for d in base_path.iterdir() if d.is_dir() and d.name.startswith('v')]
            if not version_dirs:
                return {"error": f"No version directories found in {base_path}"}
                
            # Sort by version number (assuming format 'vX' or 'vX.Y')
            version_dirs.sort(key=lambda d: [int(n) for n in d.name[1:].split('.')])
            latest_version = version_dirs[-1].name
            category_path = base_path / latest_version / subcategory
        
        if not category_path.exists():
            return {"error": f"Policy path not found: {category_path}"}
            
        logging.info(f"Evaluating policies in: {category_path}")
        
        # Build a query based on the category path
        # Convert the relative path to a package path (replace / with .)
        rel_path = category_path.relative_to(Path(policy_dir))
        package_path = str(rel_path).replace(os.sep, '.')
        query = f"data.{package_path}"
        logging.debug(f"Using query for category: {query}")
        
        # Use the entire opa_policies directory as a bundle for evaluation
        return self.evaluate_policy(
            policy_path=str(category_path),  # Still pass the specific path for reference
            input_data=input_data,
            query=query,  # Use the specific query for this category
            mode=mode
        )

    def extract_package_from_file(self, policy_file: Path) -> Optional[str]:
        """Extract the package name from a Rego policy file.
        
        Args:
            policy_file: Path to the Rego policy file
            
        Returns:
            Optional[str]: The package name or None if not found
        """
        try:
            with open(policy_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Look for package declaration using regex
            import re
            package_match = re.search(r'package\s+([^\s{]+)', content)
            if package_match:
                return package_match.group(1)
            
            return None
        except Exception as e:
            logging.error(f"Error extracting package from {policy_file}: {e}")
            return None
    def find_matching_policy_folders(self, folder_name: str) -> List[str]:
        """
        Find all policy folders that match the given name.
        
        Args:
            folder_name: Name of the folder to search for
            
        Returns:
            List of full paths to matching folders
        """
        matching_folders = []
        
        # Get the policy directory
        policy_dir = Path(self.policy_loader.get_policy_dir())
        
        # Recursive search for folders with the given name
        for path in policy_dir.rglob(f"{folder_name}"):
            if path.is_dir():
                matching_folders.append(str(path))
            
        return matching_folders

    def evaluate_by_folder_name(self, folder_name: str, input_data: Dict[str, Any], mode: ExecutionMode = "debug") -> Dict[str, Any]:
        """
        Find folders matching the name and evaluate policies in the first match.
        
        Args:
            folder_name: Name of the folder to search for
            input_data: Input data for evaluation
            mode: Execution mode (production, development, debug)
            
        Returns:
            Evaluation results or error
        """
        # Check environment variable for debug mode override
        env_debug_value = os.environ.get("OPA_DEBUG", "")
        if env_debug_value.lower() in ("1", "true", "yes", "on"):
            mode = "debug"
            logging.debug(f"OPA_DEBUG environment variable set to true, forcing debug mode for folder evaluation: {folder_name}")
        elif env_debug_value.lower() in ("0", "false", "no", "off") and mode == "debug":
            mode = "production"
            logging.debug(f"OPA_DEBUG environment variable set to false, forcing production mode for folder evaluation: {folder_name}")
        elif self.debug and mode != "debug":
            logging.debug(f"Debug mode enabled in evaluator, but mode is {mode}. Consider using debug mode for more detailed output.")
        
        matching_folders = self.find_matching_policy_folders(folder_name)
        
        if not matching_folders:
            return {
                "error": f"No policy folders found matching: {folder_name}",
                "searched_in": self.policy_loader.get_policy_dir()
            }
        
        # Log all matches
        if len(matching_folders) > 1:
            logging.info(f"Found multiple matching folders for '{folder_name}':")
            for folder in matching_folders:
                logging.info(f"  - {folder}")
            logging.info(f"Using the first match: {matching_folders[0]}")
        
        # Use the first match for evaluation
        target_folder = matching_folders[0]
        
        # Check if the folder exists and contains .rego files
        target_path = Path(target_folder)
        if not target_path.exists():
            return {
                "error": f"Policy folder does not exist: {target_folder}",
                "searched_in": self.policy_loader.get_policy_dir()
            }
        
        rego_files = list(target_path.rglob("*.rego"))
        if not rego_files:
            return {
                "error": f"No .rego policy files found in folder or subfolders: {target_folder}",
                "searched_in": target_folder
            }
        
        # Log the policy files found for debugging
        logging.debug(f"Found {len(rego_files)} policy files in {target_folder}:")
        for rego_file in rego_files:
            logging.debug(f"  - {rego_file.name}")
        
        # Build relative path from policy dir to determine package
        policy_dir = Path(self.policy_loader.get_policy_dir())
        rel_path = Path(target_folder).relative_to(policy_dir)
        package_path = str(rel_path).replace(os.sep, '.')
        query = f"data.{package_path}"
        
        # Force debug mode if this is a retry after a failure
        if os.environ.get("OPA_RETRY_DEBUG") == "1":
            mode = "debug"
            logging.debug(f"Forcing debug mode for retry evaluation of {folder_name}")
        
        # Set environment variable to indicate this is a retry if mode is debug
        if mode == "debug":
            os.environ["OPA_RETRY_DEBUG"] = "1"
        else:
            os.environ.pop("OPA_RETRY_DEBUG", None)
        
        # Evaluate using the entire bundle
        return self.evaluate_policy(
            policy_path=target_folder,
            input_data=input_data,
            query=query,
            mode=mode
        )

