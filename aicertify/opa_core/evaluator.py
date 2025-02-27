import subprocess
import logging
import shutil
import sys
import os
import json
from typing import Dict, Any, Optional, List, Union, Literal
from pathlib import Path
from .policy_loader import PolicyLoader

# Define execution modes as a Literal type for better type checking
ExecutionMode = Literal["production", "development", "debug"]

class OpaEvaluator:
    """Evaluates OPA policies using the OPA executable."""
    
    def __init__(self, policies_dir: str = None):
        self.opa_path = self._verify_opa_installation()
        self.policy_loader = PolicyLoader(policies_dir)
        
    def _verify_opa_installation(self) -> str:
        """
        Verify OPA is installed and accessible.
        
        Returns:
            str: Path to the OPA executable
        """
        logging.info("Checking for OPA installation...")
        
        # Force using the OPA executable at "C:/opa/opa_windows_amd64.exe" if it exists
        fixed_path = Path("C:/opa/opa_windows_amd64.exe")
        if fixed_path.is_file():
            logging.info(f"Found OPA at fixed path: {fixed_path.as_posix()}")
            return fixed_path.as_posix()
        
        # Otherwise, try the standard "opa" or "opa.exe"
        opa_path = shutil.which("opa")
        logging.info(f"Standard OPA path check result: {opa_path}")
        
        if not opa_path and sys.platform == "win32":
            # On Windows, also check for the downloaded filename
            opa_dir = Path("C:/opa")  # Create Path object for OPA directory
            custom_paths = [
                opa_dir / "opa_windows_amd64.exe",
                opa_dir / "opa.exe",
                Path.cwd() / "opa_windows_amd64.exe"
            ]
            
            logging.info(f"Checking custom paths: {[str(p) for p in custom_paths]}")
            for path in custom_paths:
                logging.info(f"Checking path: {path}")
                if path.is_file():
                    opa_path = str(path)
                    logging.info(f"Found OPA at: {opa_path}")
                    break
                else:
                    logging.info(f"Path not found: {path}")
        
        if not opa_path:
            # Check PATH environment variable
            path_env = os.environ.get('PATH', '')
            logging.info(f"Current PATH: {path_env}")
            
            # Additional check for Windows - look in PATH directories
            if sys.platform == "win32":
                for path_dir in path_env.split(os.pathsep):
                    try:
                        dir_path = Path(path_dir.strip('"'))  # Remove quotes if present
                        possible_paths = [
                            dir_path / "opa.exe",
                            dir_path / "opa_windows_amd64.exe"
                        ]
                        for p in possible_paths:
                            logging.info(f"Checking PATH location: {p}")
                            if p.is_file():
                                opa_path = str(p)
                                logging.info(f"Found OPA in PATH at: {opa_path}")
                                break
                        if opa_path:
                            break
                    except Exception as e:
                        logging.debug(f"Error checking path {path_dir}: {e}")
                        continue
            
        if not opa_path:
            raise RuntimeError(
                "OPA executable not found. Please ensure OPA is installed and either:\n"
                "1. Rename 'opa_windows_amd64.exe' to 'opa.exe', or\n"
                "2. Add the full path to the OPA executable in your system PATH.\n"
                "Current PATH environment variable contains:\n"
                f"{path_env}\n"
                "Visit https://www.openpolicyagent.org/docs/latest/#1-download-opa for installation instructions."
            )
            
        return opa_path
    
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
            logging.info(f"Policy file paths: {abs_policy_paths}")
            
            # Verify all policy files exist
            for path in abs_policy_paths:
                if not Path(path).is_file():
                    logging.error(f"Policy file not found: {path}")
                    return {"error": f"Policy file not found: {path}"}
            
            # Use the first policy file for query building if needed
            primary_policy_path = abs_policy_paths[0]
            
            # Convert input_data to proper JSON string
            try:
                input_json = json.dumps(input_data)
                logging.info(f"Input data: {input_json}")
            except Exception as e:
                logging.error(f"Error converting input data to JSON: {e}")
                return {"error": f"Failed to serialize input data: {str(e)}"}
            
            # If query is not provided, build it from policy file
            if not query:
                query = self.policy_loader.build_query_for_policy(primary_policy_path)
                logging.info(f"Using query built from policy: {query}")
            
            # Resolve policy dependencies if not already provided
            if len(abs_policy_paths) == 1:
                policy_files = self.policy_loader.resolve_policy_dependencies(abs_policy_paths)
                logging.info(f"Using policy files with dependencies: {policy_files}")
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
                logging.info("Using development mode with failure explanations and coverage reporting")
            elif mode == "debug":
                cmd.extend([
                    "--explain", "full",   # Full explanations
                    "--coverage",          # Report coverage
                    "--metrics",           # Performance metrics
                    "--instrument",        # Instrumentation
                    "--format", "pretty",  # More readable output
                ])
                logging.info("Using debug mode with full explanations, coverage, and metrics")
            else:  # production mode
                cmd.extend([
                    "--format", "json",    # JSON output for parsing
                    "--fail",              # Exit with non-zero code on undefined/empty result
                ])
                
                # Only add optimization if we have an entrypoint
                if optimize_level > 0 and entrypoint:
                    cmd.extend(["--optimize", str(optimize_level)])
                    logging.info(f"Using production mode with optimization level {optimize_level}")
                else:
                    logging.info("Using production mode without optimizations")
            
            # Always add stdin-input for consistent input handling
            cmd.append("--stdin-input")
            
            # If using optimization with an entrypoint, include it
            if optimize_level > 0 and entrypoint and mode == "production":
                cmd.extend(["-e", entrypoint])
                logging.info(f"Using entrypoint: {entrypoint}")
            
            logging.info(f"Executing command: {cmd}")
            
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
            
            logging.info(f"OPA stdout output: {result.stdout[:200]}..." if len(result.stdout) > 200 else f"OPA stdout output: {result.stdout}")
            
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
                    logging.info(f"Trying alternative query for allow rule: {allow_query}")
                    
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

    def evaluate_policies_by_category(self, category: str, input_data: Dict[str, Any], subcategory: str = "", version: str = None) -> List[Dict[str, Any]]:
        """
        Evaluate all policies for a specific category against input data.
        
        Args:
            category: Policy category (global, international, etc.)
            input_data: Dictionary containing the input data
            subcategory: Policy subcategory (empty for global, eu_ai_act for international, etc.)
            version: Optional policy version (e.g., "v1")
            
        Returns:
            List of dictionaries containing evaluation results
        """
        policies = self.policy_loader.get_policies(category, subcategory, version)
        if not policies:
            logging.error(f"No policies found for category '{category}', subcategory '{subcategory}', version '{version}'")
            return [{"error": f"No policies found for category '{category}', subcategory '{subcategory}', version '{version}'"}]
        
        results = []
        for policy in policies:
            result = self.evaluate_policy(policy, input_data)
            results.append(result)
        
        return results
