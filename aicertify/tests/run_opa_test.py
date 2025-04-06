#!/usr/bin/env python3
"""
Standalone script to test OPA policy imports without loading the entire AICertify package.
This avoids loading transformers and other heavy dependencies.
"""

import json
import os
import sys
import logging
import subprocess
import tempfile
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
OPA_POLICIES_DIR = PROJECT_ROOT / "aicertify" / "opa_policies"
TEST_POLICIES_DIR = OPA_POLICIES_DIR / "test"


def find_opa_binary():
    """Find the OPA binary on the system."""
    # Common locations for OPA binary
    opa_locations = [
        "/usr/local/bin/opa",
        "/usr/bin/opa",
        os.path.expanduser("~/.local/bin/opa"),
    ]

    for location in opa_locations:
        if os.path.isfile(location) and os.access(location, os.X_OK):
            logger.info(f"Found OPA at: {location}")
            return location

    # If not found in common locations, try to find it in PATH
    try:
        result = subprocess.run(
            ["which", "opa"], capture_output=True, text=True, check=True
        )
        opa_path = result.stdout.strip()
        if opa_path:
            logger.info(f"Found OPA in PATH: {opa_path}")
            return opa_path
    except (subprocess.SubprocessError, FileNotFoundError):
        pass

    logger.error(
        "OPA binary not found. Please install OPA and make sure it's in your PATH."
    )
    return None


def evaluate_policy(policy_path, input_data, query=None):
    """Evaluate an OPA policy with the given input data.

    Args:
        policy_path: Path to the policy file or directory
        input_data: Input data for policy evaluation
        query: Optional query to evaluate (default: "data")

    Returns:
        The evaluation result as a dictionary
    """
    opa_path = find_opa_binary()
    if not opa_path:
        return None

    # Use only the test directory as the bundle to avoid errors in other policies
    bundle_path = TEST_POLICIES_DIR

    # Determine the query
    if query is None:
        # If policy_path is a file, extract the package name
        if os.path.isfile(policy_path):
            with open(policy_path, "r") as f:
                content = f.read()
                # Simple regex to extract package name
                import re

                match = re.search(r"package\s+([^\s]+)", content)
                if match:
                    package_name = match.group(1)
                    query = f"data.{package_name}"
                else:
                    query = "data"
        else:
            query = "data"

    # Create a temporary file for the input data
    with tempfile.NamedTemporaryFile(
        mode="w+", suffix=".json", delete=False
    ) as temp_file:
        json.dump(input_data, temp_file)
        temp_file_path = temp_file.name

    try:
        # Construct the OPA command
        cmd = [
            opa_path,
            "eval",
            "--format",
            "json",
            "--bundle",
            str(bundle_path),
            "--input",
            temp_file_path,
            query,
        ]

        logger.info(f"Running OPA command: {' '.join(cmd)}")

        # Run the OPA command
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"OPA evaluation failed: {result.stderr}")
            return None

        # Parse the result
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OPA output: {e}")
            logger.error(f"OPA output: {result.stdout}")
            return None
    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)


def extract_result_value(result):
    """Extract the actual value from an OPA result.

    Args:
        result: The OPA evaluation result

    Returns:
        The extracted value or None if not found
    """
    if not result:
        return None

    # Check if the result is a simple value
    if "result" in result and not isinstance(result["result"], list):
        return result["result"]

    # Check if the result is a list of expressions
    if "result" in result and isinstance(result["result"], list):
        for item in result["result"]:
            if "expressions" in item and isinstance(item["expressions"], list):
                for expr in item["expressions"]:
                    if "value" in expr:
                        return expr["value"]

    return None


def run_tests():
    """Run the OPA policy import tests."""
    # Check if the test policies exist
    test_policy_dir = TEST_POLICIES_DIR
    test_policy_path = test_policy_dir / "policies" / "test_policy.rego"
    test_utils_path = test_policy_dir / "utils" / "test_utils.rego"

    if not test_policy_path.exists():
        logger.error(f"Test policy not found at {test_policy_path}")
        return False

    if not test_utils_path.exists():
        logger.error(f"Test utils not found at {test_utils_path}")
        return False

    logger.info(f"Test policy path: {test_policy_path}")
    logger.info(f"Test utils path: {test_utils_path}")

    # Test: Policy with imports
    logger.info("Running test: Policy with imports")
    input_data = {
        "model": {
            "fairness_score": 0.8,
            "robustness_score": 0.9,
            "has_documentation": True,
        }
    }

    result = evaluate_policy(
        policy_path=str(test_policy_path),
        input_data=input_data,
        query="data.test.policies.compliant_model",
    )

    if result is None:
        logger.error("Test failed: No result from OPA evaluation")
        return False

    # Extract the actual value from the result
    actual_value = extract_result_value(result)
    if not actual_value:
        logger.error(
            f"Test failed: Could not extract value from result. Result: {result}"
        )
        return False

    logger.info(f"Test passed: Policy correctly evaluated with imports")
    logger.info(f"Result: {json.dumps(result, indent=2)}")

    logger.info("All tests passed!")
    return True


if __name__ == "__main__":
    logger.info(f"Python executable: {sys.executable}")
    logger.info(f"Project root: {PROJECT_ROOT}")
    logger.info(f"OPA policies directory: {OPA_POLICIES_DIR}")
    logger.info(f"Test policies directory: {TEST_POLICIES_DIR}")

    success = run_tests()
    sys.exit(0 if success else 1)
