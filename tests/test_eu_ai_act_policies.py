#!/usr/bin/env python3
"""
Test script to verify that all EU AI Act Rego policies are found by the policy loader.
This script addresses test PL-01 in the EU AI Act Implementation Test Plan.
"""

import os
import sys
import logging
from pathlib import Path
from typing import List

# Add the parent directory to the path so we can import from aicertify
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the PolicyLoader
from aicertify.opa_core.policy_loader import PolicyLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("test_eu_ai_act_policies")


def get_all_rego_files_in_eu_ai_act_dir() -> List[Path]:
    """Directly find all .rego files in the EU AI Act policy directory."""
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    policy_dir = (
        script_dir / "aicertify" / "opa_policies" / "international" / "eu_ai_act"
    )

    if not policy_dir.exists():
        logger.error(f"EU AI Act policy directory not found at: {policy_dir}")
        return []

    # Find all .rego files recursively
    rego_files = list(policy_dir.glob("**/*.rego"))

    return rego_files


def test_eu_ai_act_policy_loading():
    """Test if all EU AI Act Rego policies are found by the policy loader."""
    logger.info("Starting EU AI Act policy loading test (PL-01)")

    # Initialize the policy loader
    policy_loader = PolicyLoader()

    # Get all policies for the EU AI Act category
    loaded_policies = policy_loader.get_policies_by_category("eu_ai_act")

    if not loaded_policies:
        logger.error("No EU AI Act policies were loaded by the policy loader")
        return False

    # Get all .rego files in the EU AI Act directory directly
    expected_policy_files = get_all_rego_files_in_eu_ai_act_dir()

    if not expected_policy_files:
        logger.error("Could not find any .rego files in the EU AI Act directory")
        return False

    # Print what was loaded for debugging
    logger.info(f"Found {len(loaded_policies)} policies via policy loader")
    logger.info(
        f"Found {len(expected_policy_files)} .rego files in EU AI Act directory"
    )

    # Get policy filenames (without path) from loaded policies
    # The loaded policies have a specific format we need to parse
    # Example: international/eu_ai_act/v1/prohibited_practices/manipulation.rego
    loaded_policy_filenames = set()
    for policy_path in loaded_policies:
        filename = os.path.basename(policy_path)
        loaded_policy_filenames.add(filename.lower())

    # Get filenames from directly found files
    expected_policy_filenames = set()
    for policy_file in expected_policy_files:
        expected_policy_filenames.add(policy_file.name.lower())

    # Find missing policies
    missing_policies = expected_policy_filenames - loaded_policy_filenames

    # Check if all expected policies were loaded
    if missing_policies:
        logger.error(
            f"The following EU AI Act policies were not loaded: {missing_policies}"
        )
        return False

    logger.info(f"Successfully loaded {len(loaded_policies)} EU AI Act policies")
    logger.info("All expected EU AI Act policies were found by the policy loader")
    return True


if __name__ == "__main__":
    result = test_eu_ai_act_policy_loading()

    if result:
        print("\n✅ PASS: All EU AI Act rego policies were found by the policy loader")
        sys.exit(0)
    else:
        print(
            "\n❌ FAIL: Some EU AI Act rego policies were not found by the policy loader"
        )
        sys.exit(1)
