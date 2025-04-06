#!/usr/bin/env python3
import sys
import logging
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import the PolicyLoader
from aicertify.opa_core.policy_loader import PolicyLoader

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def test_policy_loader():
    """Test that the PolicyLoader can find and load policies from the submodule."""
    logging.info("Testing PolicyLoader with submodule...")

    # Create a PolicyLoader instance
    loader = PolicyLoader()

    # Log the policies directory
    logging.info(f"Policies directory: {loader.policies_dir}")

    # Try to get EU AI Act policies
    eu_policies = loader.get_policies("international", "eu_ai_act")
    if eu_policies:
        logging.info(f"Found {len(eu_policies)} EU AI Act policies")
        for policy in eu_policies:
            logging.info(f"  - {policy}")
    else:
        logging.error("Failed to find EU AI Act policies")

    # Try to get global policies
    global_policies = loader.get_policies("global", "")
    if global_policies:
        logging.info(f"Found {len(global_policies)} global policies")
        for policy in global_policies:
            logging.info(f"  - {policy}")
    else:
        logging.error("Failed to find global policies")

    # Try to get custom policies
    custom_policies = loader.get_policies("custom", "example")
    if custom_policies:
        logging.info(f"Found {len(custom_policies)} custom policies")
        for policy in custom_policies:
            logging.info(f"  - {policy}")
    else:
        logging.error("Failed to find custom policies")

    logging.info("PolicyLoader test completed")


if __name__ == "__main__":
    test_policy_loader()
