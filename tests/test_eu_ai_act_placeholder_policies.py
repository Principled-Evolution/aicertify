#!/usr/bin/env python3
"""
Test script to verify that placeholder policies are properly loaded and identified.
This script addresses test PL-04 in the EU AI Act Implementation Test Plan.
"""

import os
import sys
import logging
import re
from typing import Dict

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
logger = logging.getLogger("test_eu_ai_act_placeholder_policies")


def is_placeholder_policy(policy_content: str) -> bool:
    """
    Check if a policy is a placeholder based on its content.

    Args:
        policy_content: The content of the policy file

    Returns:
        True if the policy is a placeholder, False otherwise
    """
    # Check for placeholder indicators in the policy content
    placeholder_indicators = [
        "PLACEHOLDER",
        "placeholder",
        "implementation_pending",
        "Pending detailed implementation",
    ]

    for indicator in placeholder_indicators:
        if indicator in policy_content:
            return True

    return False


def get_policy_metadata(policy_content: str) -> Dict:
    """
    Extract metadata from a policy file content.

    Args:
        policy_content: The content of the policy file

    Returns:
        Dictionary containing metadata or empty dict if not found
    """
    # Look for metadata := { ... } pattern
    metadata_match = re.search(r"metadata\s*:=\s*{([^}]*)}", policy_content, re.DOTALL)

    if metadata_match:
        metadata_str = metadata_match.group(1)

        # Extract key-value pairs
        metadata = {}
        for line in metadata_str.split("\n"):
            line = line.strip()
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().strip('"')
                value = value.strip().strip(",").strip('"')
                metadata[key] = value

        return metadata

    return {}


def test_eu_ai_act_placeholder_policies():
    """Test if placeholder policies are properly loaded and identified."""
    logger.info("Starting EU AI Act placeholder policy test (PL-04)")

    # Initialize the policy loader
    policy_loader = PolicyLoader()

    # Get all policies for the EU AI Act category
    loaded_policies = policy_loader.get_policies_by_category("eu_ai_act")

    if not loaded_policies:
        logger.error("No EU AI Act policies were loaded by the policy loader")
        return False

    logger.info(f"Found {len(loaded_policies)} EU AI Act policies")

    # Track placeholder policies
    placeholder_policies = []
    non_placeholder_policies = []

    # Check each policy to see if it's a placeholder
    for policy_path in loaded_policies:
        # Get the policy content
        policy_content = None
        try:
            with open(policy_path, "r") as f:
                policy_content = f.read()
        except Exception as e:
            logger.error(f"Error reading policy file {policy_path}: {str(e)}")
            continue

        if policy_content is None:
            continue

        # Check if it's a placeholder
        is_placeholder = is_placeholder_policy(policy_content)

        # Get metadata
        metadata = get_policy_metadata(policy_content)
        status = metadata.get("status", "")

        # Log the policy status
        policy_name = os.path.basename(policy_path)
        if is_placeholder:
            logger.info(f"Found placeholder policy: {policy_name} (Status: {status})")
            placeholder_policies.append((policy_path, status))
        else:
            logger.info(f"Found non-placeholder policy: {policy_name}")
            non_placeholder_policies.append(policy_path)

    # Summarize results
    logger.info(
        f"Found {len(placeholder_policies)} placeholder policies and {len(non_placeholder_policies)} non-placeholder policies"
    )

    # Check if we found any placeholder policies
    if not placeholder_policies:
        logger.error("No placeholder policies were found")
        return False

    # Print details of placeholder policies
    logger.info("Placeholder policies:")
    for policy_path, status in placeholder_policies:
        logger.info(f"  - {os.path.basename(policy_path)}: {status}")

    return True


if __name__ == "__main__":
    result = test_eu_ai_act_placeholder_policies()

    if result:
        print("\n✅ PASS: Placeholder policies were properly loaded and identified")
        sys.exit(0)
    else:
        print("\n❌ FAIL: Placeholder policies were not properly loaded or identified")
        sys.exit(1)
