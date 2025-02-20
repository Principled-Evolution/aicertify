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
    
    def evaluate_policy(self, policy_path: str, input_data: Dict[str, Any], query: str = "data.compliance.fairness.compliance_report") -> Optional[Dict[str, Any]]:
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
                return None
            
            # Convert input_data to proper JSON string
            input_json = json.dumps(input_data)
            logging.info(f"Input data: {input_json}")
            
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
            result = subprocess.run(
                cmd,
                input=input_json,
                capture_output=True,
                text=True,
                check=False  # Don't raise exception on non-zero exit
            )
            
            if result.stderr:
                logging.error(f"OPA stderr output: {result.stderr}")
            
            if result.stdout:
                logging.info(f"OPA stdout output: {result.stdout}")
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    logging.error(f"Failed to parse OPA output as JSON: {result.stdout}")
                    return None
            
            return None
        except Exception as e:
            logging.error(f"Unexpected error during policy evaluation: {str(e)}")
            return None
