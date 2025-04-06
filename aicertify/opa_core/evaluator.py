import subprocess
import logging
import shutil
import sys
import os
import json
import copy  # Add import for deep copying
from typing import Dict, Any, Optional, List, Literal
from pathlib import Path
from .policy_loader import PolicyLoader
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

    def __init__(
        self,
        use_external_server: bool = False,
        server_url: str = "http://localhost:8181",
        debug: bool = False,
        optimize: bool = False,
    ):
        """
        Initialize the OPA evaluator.

        Args:
            use_external_server: Whether to use an external OPA server
            server_url: URL of the external OPA server
            debug: Whether to enable debug mode
            optimize: Whether to apply OPA optimization
        """
        # Check environment variable for debug mode override
        env_debug_value = os.environ.get("OPA_DEBUG", "")
        env_debug = env_debug_value.lower() in (
            "1",
            "true",
            "yes",
            "on",
        ) and env_debug_value.lower() not in ("0", "false", "no", "off")
        self.debug = debug or env_debug

        logging.debug(
            f"OPA Evaluator initialized with debug={self.debug} (env value: {env_debug_value}, env override: {env_debug})"
        )

        self.policy_loader = PolicyLoader()
        self.opa_path = None if use_external_server else self._verify_opa_installation()
        self.use_external_server = use_external_server
        self.server_url = server_url
        self.policies_loaded = False
        self.optimize = optimize

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
        if (
            opa_path_env
            and os.path.exists(opa_path_env)
            and os.access(opa_path_env, os.X_OK)
        ):
            logging.info(f"Found OPA at environment variable OPA_PATH: {opa_path_env}")
            return opa_path_env

        # Check OS-specific fixed locations
        if os.name == "nt":
            # Windows: Try several possible Windows paths
            windows_paths = [
                "C:/opa/opa_windows_amd64.exe",
                "C:/opa/opa.exe",
                str(Path.cwd() / "opa_windows_amd64.exe"),
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
            wsl_paths = ["/mnt/c/opa/opa.exe", "/mnt/c/opa/opa_windows_amd64.exe"]
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

    def _evaluate_with_local_opa(
        self, policy_path: str, input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate policy using local OPA binary.

        Args:
            policy_path: Path to the policy file or directory
            input_data: Input data for evaluation

        Returns:
            Dict[str, Any]: Evaluation results
        """
        # Check environment variable for debug mode override
        env_debug_value = os.environ.get("OPA_DEBUG", "")
        env_debug = env_debug_value.lower() in (
            "1",
            "true",
            "yes",
            "on",
        ) and env_debug_value.lower() not in ("0", "false", "no", "off")
        debug_mode = self.debug or env_debug

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as temp_file:
            # Use CustomJSONEncoder to handle UUID serialization
            json.dump(input_data, temp_file, cls=CustomJSONEncoder)
            temp_file_path = temp_file.name

        try:
            # Always use the entire opa_policies directory as the bundle
            bundle_path = self.policy_loader.get_policy_dir()
            logging.debug(
                f"Using entire opa_policies directory as bundle: {bundle_path}"
            )

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
                "--format",
                "json",
                "--bundle",
                bundle_path,  # Use entire opa_policies directory
                "--input",
                temp_file_path,
                query,
            ]

            # Optionally add debugging flags if debug mode is enabled
            if debug_mode:
                cmd.extend(
                    ["--explain", "full", "--coverage", "--instrument", "--metrics"]
                )
                logging.debug(
                    f"Debug mode active (self.debug={self.debug}, env_debug={env_debug}, env_value={env_debug_value}): Added OPA debugging flags to the command"
                )

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
                    logging.debug(
                        f"Keeping temporary input file for manual inspection: {temp_file_path}"
                    )
                else:
                    os.unlink(temp_file_path)

    def _evaluate_with_external_opa(
        self, policy_path: str, input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate policy using external OPA server.

        Args:
            policy_path: Path to the policy file or directory
            input_data: Input data for evaluation

        Returns:
            Dict[str, Any]: Evaluation results
        """
        # Check environment variable for debug mode override
        env_debug_value = os.environ.get("OPA_DEBUG", "")
        env_debug = env_debug_value.lower() in (
            "1",
            "true",
            "yes",
            "on",
        ) and env_debug_value.lower() not in ("0", "false", "no", "off")
        debug_mode = self.debug or env_debug

        try:
            # For external server, we need to determine the package and query
            # First, determine if policy_path is a file or directory
            if Path(policy_path).is_file():
                # Extract package from the policy file
                package_name = self.extract_package_from_file(Path(policy_path))
                if not package_name:
                    return {
                        "error": f"Could not extract package name from policy file: {policy_path}"
                    }
            else:
                # For directories, convert the path to a package path
                policy_dir = self.policy_loader.get_policy_dir()
                try:
                    rel_path = Path(policy_path).relative_to(Path(policy_dir))
                    package_name = str(rel_path).replace(os.sep, ".")
                except ValueError:
                    # If policy_path is not relative to policy_dir
                    return {
                        "error": f"Policy path {policy_path} is not within the policy directory {policy_dir}"
                    }

            # Build the data query URL
            query_url = f"{self.server_url}/v1/data/{package_name.replace('.', '/')}"

            # Prepare request parameters
            request_params = {"input": input_data}

            # Add debug parameters if debug mode is enabled
            if debug_mode:
                request_params.update(
                    {
                        "explain": "full",
                        "metrics": True,
                        "instrument": True,
                        "pretty": True,
                    }
                )
                logging.debug(
                    f"Debug mode active (self.debug={self.debug}, env_debug={env_debug}, env_value={env_debug_value}): Added debug parameters to OPA server request"
                )

            logging.debug(f"Making request to OPA server: {query_url}")

            # Make the request to the OPA server
            response = requests.post(
                query_url,
                json=request_params,
                headers={"Content-Type": "application/json"},
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
            if policy_name.endswith(".rego"):
                policy_name = policy_name[:-5]  # Remove .rego extension

            url = f"{self.server_url}/v1/policies/{policy_name}"
            headers = {"Content-Type": "text/plain"}

            try:
                response = requests.put(url, data=policy.content, headers=headers)
                if response.status_code not in (200, 201):
                    logging.warning(
                        f"Failed to upload policy {policy_name}: {response.status_code}"
                    )
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
        env_debug = os.environ.get("OPA_DEBUG", "").lower() in (
            "1",
            "true",
            "yes",
            "on",
        )
        debug_mode = self.debug or env_debug

        if debug_mode:
            logging.debug(
                f"Debug mode active for contract evaluation (self.debug={self.debug}, env_debug={env_debug})"
            )

        # Ensure policies are loaded
        self.load_policies()

        # Convert contract to dictionary for evaluation
        contract_dict = contract.model_dump()

        # Evaluate the contract against all policy types
        results = {}
        policy_types = [
            "fairness",
            "security",
            "compliance",
            "regulatory",
            "operational",
        ]

        for policy_type in policy_types:
            try:
                if self.use_external_server:
                    # Evaluate using external OPA server
                    policy_path = f"{policy_type}/evaluate"
                    result = self._evaluate_with_external_opa(
                        policy_path, contract_dict
                    )
                    results[policy_type] = result.get("result", {})
                else:
                    # Evaluate using local OPA binary
                    # Find all policies of this type
                    type_policies = [
                        p for p in self.policies if policy_type in p.path.lower()
                    ]

                    if not type_policies:
                        logging.warning(f"No policies found for type: {policy_type}")
                        results[policy_type] = {
                            "warning": f"No policies defined for {policy_type}"
                        }
                        continue

                    # Evaluate each policy
                    type_results = {}
                    for policy in type_policies:
                        result = self._evaluate_with_local_opa(
                            policy.path, contract_dict
                        )
                        policy_name = os.path.basename(policy.path).replace(".rego", "")
                        type_results[policy_name] = result

                    results[policy_type] = type_results
            except Exception as e:
                logging.error(f"Error evaluating {policy_type} policies: {str(e)}")
                results[policy_type] = {"error": str(e)}

        return results

    def _build_policy_query(
        self, policy_path: str, package_name: Optional[str] = None
    ) -> str:
        """Build a standardized query for policy evaluation.

        Args:
            policy_path: Path to the policy file
            package_name: Optional explicit package name

        Returns:
            Standardized query string targeting report_output
        """
        if package_name:
            return f"data.{package_name}.report_output"

        # Extract package from policy path
        try:
            package_name = self.extract_package_from_file(Path(policy_path))
            if package_name:
                return f"data.{package_name}.report_output"
        except Exception as e:
            logging.error(f"Error extracting package name from {policy_path}: {e}")

        # Fallback: Build from path structure
        policy_dir = self.policy_loader.get_policy_dir()
        rel_path = Path(policy_path).relative_to(Path(policy_dir))
        package_path = str(rel_path.parent).replace(os.sep, ".")
        return f"data.{package_path}.report_output"

    def _build_opa_command(
        self,
        query: str,
        input_file: str,
        mode: ExecutionMode = "production",
        policy_dir: Optional[str] = None,
    ) -> List[str]:
        """Build the OPA evaluation command with consistent arguments.

        Args:
            query: The query to evaluate (should target report_output)
            input_file: Path to the input JSON file
            mode: Execution mode
            policy_dir: Optional specific policy directory, defaults to full policies dir

        Returns:
            List of command arguments
        """
        if not policy_dir:
            policy_dir = self.policy_loader.get_policy_dir()

        # Ensure query targets report_output if not already
        if not query.endswith(".report_output"):
            query = f"{query}.report_output"
            logging.debug(f"Modified query to target report_output: {query}")

        # Base command with consistent arguments
        cmd = [
            self.opa_path,
            "eval",
            "--data",
            policy_dir,
            "--format",
            "json" if mode == "production" else "pretty",
            "-i",
            input_file,
            query,
        ]

        # Add mode-specific options
        if mode == "development":
            cmd.extend(["--explain", "fails", "--coverage"])
        elif mode == "debug":
            cmd.extend(["--explain", "full", "--coverage", "--metrics", "--instrument"])

        return cmd

    def evaluate_policy(
        self,
        policy_path: str,
        input_data: Dict[str, Any],
        query: str,
        mode: ExecutionMode = "production",
        restrict_to_folder: bool = False,
        retry_count: int = 0,
    ) -> Dict[str, Any]:
        """
        Evaluate an OPA policy against input data.

        Args:
            policy_path: Path to the policy file or directory
            input_data: Input data for evaluation
            query: OPA query to evaluate
            mode: Execution mode - production, development, or debug
            restrict_to_folder: Whether to restrict evaluation to the specific folder
            retry_count: Number of retry attempts made (used for debug logging)

        Returns:
            Dictionary containing evaluation results or error information
        """
        try:
            # Write input to a file
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False
            ) as temp_file:
                json.dump(input_data, temp_file, cls=CustomJSONEncoder)
                input_file = temp_file.name

            # Build the command
            policy_dir = (
                policy_path
                if restrict_to_folder
                else self.policy_loader.get_policy_dir()
            )
            cmd = [
                self.opa_path,
                "eval",
                "--format",
                "json",  # Always use JSON format for clean output
                "--data",
                policy_dir,
                "-i",
                input_file,
                query,
            ]

            # Execute the command
            logging.debug(f"Executing OPA command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            # Handle the result
            if result.returncode != 0:
                error_msg = (
                    result.stderr.strip()
                    if result.stderr
                    else "Unknown error during OPA evaluation"
                )
                logging.error(
                    f"OPA evaluation failed with exit code {result.returncode}: {error_msg}"
                )
                return {
                    "error": error_msg,
                    "exit_code": result.returncode,
                    "command": " ".join(cmd),
                }

            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse OPA output as JSON: {e}")
                return {
                    "error": f"Invalid JSON output from OPA evaluation: {e}",
                    "raw_output": (
                        result.stdout
                        if len(result.stdout) < 1000
                        else result.stdout[:1000] + "... (truncated)"
                    ),
                }

        except Exception as e:
            logging.error(f"Error in evaluate_policy: {e}")
            import traceback

            logging.error(traceback.format_exc())
            return {"error": f"Policy evaluation failed: {str(e)}"}
        finally:
            if os.path.exists(input_file):
                os.unlink(input_file)

    def _find_all_rego_files(self, start_path: Path) -> List[Path]:
        """Recursively find all .rego files under a directory, excluding test files.

        Args:
            start_path: Directory to start searching from

        Returns:
            List of paths to .rego files (excluding *_test.rego)
        """
        rego_files = []
        try:
            for item in start_path.rglob("*.rego"):
                if item.is_file() and not item.name.endswith("_test.rego"):
                    rego_files.append(item)
            logging.debug(f"Found {len(rego_files)} .rego files under {start_path}")
            for file in rego_files:
                logging.debug(f"  Found: {file}")
        except Exception as e:
            logging.error(f"Error finding .rego files in {start_path}: {e}")
        return rego_files

    def _build_package_path_from_file(self, policy_file: Path, base_dir: Path) -> str:
        """Build package path from file location relative to base directory.

        Args:
            policy_file: Path to the policy file
            base_dir: Base directory for relative path calculation

        Returns:
            Package path suitable for OPA query
        """
        try:
            # Get relative path from base_dir to policy file
            rel_path = policy_file.parent.relative_to(base_dir)
            # Convert path components to package path
            package_components = list(rel_path.parts)
            # Add filename without .rego
            package_components.append(policy_file.stem)
            # Join with dots for package path
            return ".".join(package_components)
        except Exception as e:
            logging.error(f"Error building package path for {policy_file}: {e}")
            return policy_file.stem

    def evaluate_policies_by_category(
        self,
        category: str,
        subcategory: str,
        input_data: Dict[str, Any],
        version: str = None,
        mode: ExecutionMode = "production",
    ) -> Dict[str, Any]:
        """Evaluate all policies in a category including nested policies.

        Args:
            category: The policy category (e.g., 'international')
            subcategory: The policy subcategory (e.g., 'eu_ai_act')
            input_data: Input data for evaluation
            version: Optional version string (e.g., 'v1')
            mode: Execution mode

        Returns:
            Dict[str, Any]: Results from all policies, keyed by package path
        """
        # Ensure policies are loaded
        self.load_policies()

        # Get base directory for policies
        policy_dir = Path(self.policy_loader.get_policy_dir())

        # Build path to category
        if version:
            category_path = policy_dir / category / version / subcategory
        else:
            # Find latest version
            base_path = policy_dir / category
            if not base_path.exists():
                return {"error": f"Category path not found: {base_path}"}

            version_dirs = [
                d for d in base_path.iterdir() if d.is_dir() and d.name.startswith("v")
            ]
            if not version_dirs:
                return {"error": f"No version directories found in {base_path}"}

            version_dirs.sort(key=lambda d: [int(n) for n in d.name[1:].split(".")])
            latest_version = version_dirs[-1].name
            category_path = base_path / latest_version / subcategory

        if not category_path.exists():
            return {"error": f"Policy path not found: {category_path}"}

        logging.info(f"Searching for policies in: {category_path}")

        # Find all .rego files recursively
        policy_files = self._find_all_rego_files(category_path)
        if not policy_files:
            return {
                "error": f"No .rego files found in {category_path} or its subdirectories"
            }

        # Evaluate each policy
        results = {
            "metadata": {
                "category": category,
                "subcategory": subcategory,
                "version": version or latest_version,
                "evaluation_time": datetime.now().isoformat(),
                "total_policies": len(policy_files),
            },
            "policies": {},
        }

        # Record the retry debug flag if set
        retry_debug = os.environ.get("OPA_RETRY_DEBUG", "0")

        for policy_file in policy_files:
            try:
                # Build package path based on file location
                package_path = self._build_package_path_from_file(
                    policy_file, policy_dir
                )

                # Build query targeting report_output
                query = f"data.{package_path}.report_output"
                logging.info(f"Evaluating policy {policy_file} with query: {query}")

                if self.use_external_server:
                    result = self._evaluate_with_external_opa(
                        str(policy_file), input_data
                    )
                    results["policies"][package_path] = {
                        "result": result.get("result", {}),
                        "file_path": str(policy_file),
                        "package_path": package_path,
                        "query": query,
                    }
                else:
                    result = self.evaluate_policy(
                        policy_path=str(policy_file),
                        input_data=input_data,
                        query=query,
                        mode=mode,
                        retry_count=0 if retry_debug == "1" else 0,  # Track retry state
                    )
                    results["policies"][package_path] = {
                        "result": result,
                        "file_path": str(policy_file),
                        "package_path": package_path,
                        "query": query,
                    }

            except Exception as e:
                logging.error(f"Error evaluating policy {policy_file}: {str(e)}")
                results["policies"][str(policy_file.stem)] = {
                    "error": str(e),
                    "file_path": str(policy_file),
                    "package_path": (
                        package_path if "package_path" in locals() else None
                    ),
                    "query": query if "query" in locals() else None,
                }

        # Add summary information
        results["metadata"]["successful_evaluations"] = sum(
            1 for p in results["policies"].values() if "error" not in p
        )
        results["metadata"]["failed_evaluations"] = sum(
            1 for p in results["policies"].values() if "error" in p
        )

        return results

    def extract_package_from_file(self, policy_file: Path) -> Optional[str]:
        """Extract the package name from a Rego policy file.

        Args:
            policy_file: Path to the Rego policy file

        Returns:
            Optional[str]: The package name or None if not found
        """
        try:
            with open(policy_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Look for package declaration using regex
            import re

            package_match = re.search(r"package\s+([^\s{]+)", content)
            if package_match:
                return package_match.group(1)

            return None
        except Exception as e:
            logging.error(f"Error extracting package from {policy_file}: {e}")
            return None

    def find_matching_policy_folders(self, folder_name: str) -> List[str]:
        """
        Find all policy folders that match the given name.

        This method searches for policy folders in multiple ways:
        1. Exact match on the folder name (e.g., "eu_ai_act")
        2. As part of a path (e.g., "international/eu_ai_act")
        3. With version directories (e.g., "eu_ai_act/v1")

        Args:
            folder_name: Name of the folder to search for

        Returns:
            List of full paths to matching folders
        """
        matching_folders = []

        # Get the policy directory
        policy_dir = Path(self.policy_loader.get_policy_dir())
        logging.debug(f"Searching for policy folder '{folder_name}' in {policy_dir}")

        # Approach 1: Direct folder match using rglob
        # This will find folders like "policy_dir/*/eu_ai_act" or "policy_dir/eu_ai_act"
        for path in policy_dir.rglob(f"{folder_name}"):
            if path.is_dir():
                matching_folders.append(str(path))
                logging.debug(f"Found direct match: {path}")

        # If we didn't find any matches using direct glob, try looking for partial path matches
        if not matching_folders:
            logging.debug(
                f"No direct matches found for '{folder_name}', trying alternative approaches"
            )

            # Approach 2: Check all directories and look for paths containing the folder name
            for path in policy_dir.rglob("*"):
                if path.is_dir():
                    # Check if the folder name is part of the path (handles nested paths)
                    rel_path = path.relative_to(policy_dir)
                    path_parts = str(rel_path).split(os.sep)

                    if folder_name in path_parts:
                        matching_folders.append(str(path))
                        logging.debug(
                            f"Found partial path match: {path} (relative: {rel_path})"
                        )

                    # Also check if folder name is part of a version directory (e.g., eu_ai_act/v1)
                    if path.name.startswith("v") and path.name[1:].isdigit():
                        parent = path.parent
                        if parent.name == folder_name:
                            matching_folders.append(str(parent))
                            logging.debug(f"Found versioned directory match: {parent}")

        # Log the search results
        if matching_folders:
            logging.info(
                f"Found {len(matching_folders)} matching folders for '{folder_name}'"
            )
        else:
            logging.warning(
                f"No matching folders found for '{folder_name}' after all search attempts"
            )

        return matching_folders

    def evaluate_by_folder_name(
        self,
        folder_name: str,
        input_data: Dict[str, Any],
        mode: ExecutionMode = "production",
        restrict_to_folder: bool = False,
    ) -> Dict[str, Any]:
        """
        Find folders matching the name and evaluate policies in the first match.

        Args:
            folder_name: Name of the folder to search for
            input_data: Input data for evaluation
            mode: Execution mode (production, development, debug)
            restrict_to_folder: If True, limit evaluation to the specified folder only

        Returns:
            Dict[str, Any]: Results from all policies in the folder
        """
        # Find all matching policy folders
        matching_folders = self.find_matching_policy_folders(folder_name)

        if not matching_folders:
            logging.warning(f"No policy folders found matching: {folder_name}")
            return {
                "error": f"No policy folders found matching: {folder_name}",
                "searched_in": self.policy_loader.get_policy_dir(),
            }

        # Use the first match for evaluation
        target_folder = matching_folders[0]
        target_path = Path(target_folder)

        if not target_path.exists():
            return {
                "error": f"Policy folder does not exist: {target_folder}",
                "searched_in": self.policy_loader.get_policy_dir(),
            }

        rego_files = list(target_path.rglob("*.rego"))
        if not rego_files:
            return {
                "error": f"No .rego policy files found in folder or subfolders: {target_folder}",
                "searched_in": target_folder,
            }

        # Evaluate each policy individually
        individual_results = []
        for rego_file in rego_files:
            package_name = self.extract_package_from_file(rego_file)
            if package_name:
                individual_query = f"data.{package_name}.report_output"
                individual_result = self.evaluate_policy(
                    policy_path=str(rego_file),
                    input_data=input_data,
                    query=individual_query,
                    mode="production",  # Always use production mode for clean output
                    restrict_to_folder=restrict_to_folder,
                    retry_count=0,
                )
                if individual_result and "error" not in individual_result:
                    individual_results.append(
                        {"policy": package_name, "result": individual_result}
                    )

        # Return aggregated results
        if individual_results:
            return {
                "result": {
                    "policy": "Aggregated Individual Results",
                    "results": individual_results,
                    "timestamp": datetime.now().isoformat(),
                }
            }
        else:
            return {
                "error": "No valid results from any policy evaluation",
                "folder": target_folder,
            }

    def evaluate_by_folder_name_with_params(
        self,
        folder_name: str,
        input_data: Dict[str, Any],
        custom_params: Optional[Dict[str, Any]] = None,
        mode: ExecutionMode = "debug",
        restrict_to_folder: bool = False,
    ) -> Dict[str, Any]:
        """
        Find folders matching the name, add parameters, and evaluate policies.

        This method extends evaluate_by_folder_name by adding support for custom
        parameters that are passed to the OPA input.

        Args:
            folder_name: Name of the folder to search for
            input_data: Input data for evaluation (without params)
            custom_params: Custom parameters to override defaults for OPA policies
            mode: Execution mode (production, development, debug)
            restrict_to_folder: If True, limit evaluation to the specified folder only

        Returns:
            Evaluation results or error
        """
        # Validate input types
        if not isinstance(input_data, dict):
            logging.error(f"input_data must be a dictionary, got {type(input_data)}")
            return {"error": "input_data must be a dictionary"}

        if custom_params is not None and not isinstance(custom_params, dict):
            logging.error(
                f"custom_params must be a dictionary, got {type(custom_params)}"
            )
            return {"error": "custom_params must be a dictionary"}

        # Get required parameters with default values
        matching_folders = self.find_matching_policy_folders(folder_name)
        if not matching_folders:
            return {
                "error": f"No policy folders found matching: {folder_name}",
                "searched_in": self.policy_loader.get_policy_dir(),
            }

        # Use the first match to get parameters
        target_folder = matching_folders[0]
        default_params = self.policy_loader.get_required_params_for_folder(
            target_folder
        )
        logging.debug(f"Found default parameters for {folder_name}: {default_params}")

        # Create a deep copy of the input data to ensure we don't modify the original
        # This protects against modifying nested dictionaries
        enhanced_input = copy.deepcopy(input_data)

        # Create a new params dictionary with the correct precedence:
        # 1. Start with default parameters from the policy
        # 2. Add any existing params from the input
        # 3. Override with custom params provided to this method
        params_dict = {
            **default_params,
            **(
                enhanced_input.get("params", {})
                if isinstance(enhanced_input.get("params"), dict)
                else {}
            ),
            **(custom_params or {}),
        }

        # Set the params in the enhanced input
        enhanced_input["params"] = params_dict

        # Log the parameter merging for debugging
        logging.debug(f"Using parameters for OPA evaluation: {params_dict}")

        # Transform the input structure to match what OPA policies expect
        enhanced_input = self._transform_input_for_opa(enhanced_input)

        # Call the original implementation with the enhanced input
        return self.evaluate_by_folder_name(
            folder_name=folder_name,
            input_data=enhanced_input,
            mode=mode,
            restrict_to_folder=restrict_to_folder,
        )

    def evaluate_policy_category(
        self,
        policy_category: str,
        input_data: Dict[str, Any],
        custom_params: Optional[Dict[str, Any]] = None,
        mode: ExecutionMode = "production",
    ) -> Dict[str, Any]:
        """
        Evaluate policies in a specific category using the folder-based approach.

        This is a convenience wrapper around evaluate_by_folder_name_with_params
        that supports the API's evaluate_contract_comprehensive function.

        Args:
            policy_category: The category of policies to evaluate (folder name)
            input_data: Input data for evaluation
            custom_params: Optional custom parameters to override defaults
            mode: Execution mode (production, development, debug)

        Returns:
            Evaluation results
        """
        logging.info(f"Evaluating policies in category: {policy_category}")

        evaluation_results = self.evaluate_by_folder_name_with_params(
            folder_name=policy_category,
            input_data=input_data,
            custom_params=custom_params,
            mode=mode,
            restrict_to_folder=False,  # Allow cross-folder dependencies
        )

        # Save OPA results to file for debugging
        debug_dir = os.path.join(os.getcwd(), "debug_output")
        os.makedirs(debug_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        debug_file = os.path.join(debug_dir, f"opa_results_{timestamp}.json")
        try:
            with open(debug_file, "w") as f:
                json.dump(evaluation_results, f, indent=2, default=str)
            logging.info(f"Saved OPA results to {debug_file} for debugging")
        except Exception as e:
            logging.error(f"Failed to save OPA results for debugging: {e}")

        return evaluation_results

    def _transform_input_for_opa(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform input data to match OPA policy expectations.

        Ensures data at 'results.fairness' is also available at 'metrics.fairness'.

        Args:
            input_data: Original input data

        Returns:
            Transformed input data with proper structure for OPA policies
        """
        # Create a deep copy to avoid modifying the original
        transformed = copy.deepcopy(input_data)

        # If the results key exists but metrics doesn't, map results to metrics
        if "results" in transformed and "metrics" not in transformed:
            transformed["metrics"] = transformed["results"]
            logging.debug("Transformed input data: mapped 'results' to 'metrics'")

        return transformed
