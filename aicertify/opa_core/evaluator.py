import subprocess
import logging
import shutil
import sys
import os
import json
from typing import Dict, Any, Optional
from pathlib import Path

class OpaEvaluator:
    """Evaluates OPA policies using the OPA executable."""
    
    def __init__(self):
        self.opa_path = self._verify_opa_installation()
        
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
    
    def evaluate_policy(self, policy_path: str, input_data: Dict[str, Any], query: str = "data.compliance.eu_ai_act.compliance_report") -> Optional[Dict[str, Any]]:
        """
        Evaluate an OPA policy against input data.
        
        Args:
            policy_path: Path to the .rego policy file
            input_data: Dictionary containing the input data
            query: Optional query parameter for the OPA evaluation
            
        Returns:
            Dictionary containing evaluation results or None if evaluation fails
        """
        try:
            # Convert relative path to absolute path in POSIX format (avoiding Windows backslash issues)
            abs_policy_path = Path(policy_path).resolve().as_posix()
            logging.info(f"Policy file path: {abs_policy_path}")
            
            # Verify policy file exists
            if not Path(abs_policy_path).is_file():
                logging.error(f"Policy file not found: {abs_policy_path}")
                return {"error": f"Policy file not found: {abs_policy_path}"}
            
            # Convert input_data to proper JSON string
            try:
                input_json = json.dumps(input_data)
                logging.info(f"Input data: {input_json}")
            except Exception as e:
                logging.error(f"Error converting input data to JSON: {e}")
                return {"error": f"Failed to serialize input data: {str(e)}"}
            
            # Extract package name and rule from policy path for query
            policy_dir = Path(abs_policy_path).parent
            policy_category = policy_dir.name
            # Dynamically build query based on the policy location
            # Format: data.{package}.{rule}
            package_prefix = f"compliance.{policy_category}"
            query = f"data.{package_prefix}.compliance_report"
            logging.info(f"Using dynamically built query: {query}")
            
            # Evaluate the policy using OPA
            cmd = [
                self.opa_path,
                "eval",
                query,  # Positional query argument
                "-d",
                abs_policy_path,
                "--format",
                "json",
                "--stdin-input"
            ]
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
            
            if result.returncode != 0:
                logging.error(f"OPA command failed with return code {result.returncode}")
                if result.stderr:
                    logging.error(f"OPA stderr output: {result.stderr}")
                return {"error": f"OPA execution returned non-zero exit code: {result.returncode}", "stderr": result.stderr}
            
            if result.stderr:
                logging.error(f"OPA stderr output: {result.stderr}")
            
            if not result.stdout or result.stdout.strip() == "":
                logging.warning("OPA returned empty output")
                # Return a structured result indicating empty output
                return {
                    "policy_name": Path(policy_path).stem,
                    "result": False,
                    "error": "Empty result from OPA",
                    "details": "The policy evaluation returned no output. Check if the compliance_report rule exists in the policy."
                }
            
            logging.info(f"OPA stdout output: {result.stdout}")
            
            try:
                parsed_result = json.loads(result.stdout)
                
                # If parsed_result is empty object, create a meaningful response
                if not parsed_result or parsed_result == {}:
                    logging.warning("OPA returned empty JSON object")
                    # Try running with 'allow' query to at least get basic compliance result
                    allow_query = f"data.{package_prefix}.allow"
                    logging.info(f"Trying alternative query for allow rule: {allow_query}")
                    
                    allow_cmd = [
                        self.opa_path,
                        "eval",
                        allow_query,
                        "-d",
                        abs_policy_path,
                        "--format",
                        "json",
                        "--stdin-input"
                    ]
                    
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
                                    "policy": Path(policy_path).stem,
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
                
                # Try to handle different result formats by normalizing the structure
                if "result" in parsed_result and parsed_result["result"]:
                    # Standard format
                    return parsed_result
                elif "compliance_report" in parsed_result:
                    # Wrap the compliance_report in the standard format
                    return {
                        "result": [{
                            "expressions": [{
                                "value": parsed_result["compliance_report"]
                            }]
                        }]
                    }
                else:
                    # Return as is but log a warning
                    logging.warning(f"Unknown OPA result format: {parsed_result}")
                    return parsed_result
                
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse OPA output as JSON: {result.stdout}")
                return {"error": f"Failed to parse OPA output: {str(e)}", "raw_output": result.stdout}
            
        except Exception as e:
            logging.error(f"Unexpected error during policy evaluation: {str(e)}")
            return {"error": f"Unexpected error: {str(e)}"}
