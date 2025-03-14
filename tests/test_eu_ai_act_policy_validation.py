#!/usr/bin/env python3
"""
Test script to verify that all EU AI Act Rego policies pass validation with `opa check`.
This script addresses test PL-02 in the EU AI Act Implementation Test Plan.
"""

import os
import sys
import logging
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("test_eu_ai_act_policy_validation")

def get_all_rego_files_in_eu_ai_act_dir() -> List[Path]:
    """Directly find all .rego files in the EU AI Act policy directory."""
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    policy_dir = script_dir / "aicertify" / "opa_policies" / "international" / "eu_ai_act"
    
    if not policy_dir.exists():
        logger.error(f"EU AI Act policy directory not found at: {policy_dir}")
        return []
    
    # Find all .rego files recursively
    rego_files = list(policy_dir.glob("**/*.rego"))
    
    return rego_files

def run_opa_check(policy_file: Path) -> Tuple[bool, str]:
    """
    Run 'opa check' on a single policy file.
    
    Args:
        policy_file: Path to the policy file to check
        
    Returns:
        Tuple of (success, output) where success is True if the check passed
    """
    try:
        result = subprocess.run(
            ["opa", "check", str(policy_file)],
            capture_output=True,
            text=True,
            check=False
        )
        
        # Check if the command was successful (return code 0)
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, f"Error: {result.stderr}\nOutput: {result.stdout}"
    except Exception as e:
        return False, f"Exception running opa check: {str(e)}"

def test_eu_ai_act_policy_validation():
    """Test if all EU AI Act Rego policies pass validation with 'opa check'."""
    logger.info("Starting EU AI Act policy validation test (PL-02)")
    
    # Get all .rego files in the EU AI Act directory
    policy_files = get_all_rego_files_in_eu_ai_act_dir()
    
    if not policy_files:
        logger.error("Could not find any .rego files in the EU AI Act directory")
        return False
    
    logger.info(f"Found {len(policy_files)} .rego files to validate")
    
    # Track validation results
    validation_results: Dict[str, Tuple[bool, str]] = {}
    all_passed = True
    
    # Validate each policy file
    for policy_file in policy_files:
        logger.info(f"Validating policy: {policy_file.name}")
        success, output = run_opa_check(policy_file)
        validation_results[str(policy_file)] = (success, output)
        
        if not success:
            all_passed = False
            logger.error(f"Validation failed for {policy_file.name}: {output}")
    
    # Summarize results
    if all_passed:
        logger.info(f"All {len(policy_files)} EU AI Act policies passed validation")
    else:
        failed_count = sum(1 for success, _ in validation_results.values() if not success)
        logger.error(f"{failed_count} out of {len(policy_files)} EU AI Act policies failed validation")
    
    return all_passed

if __name__ == "__main__":
    result = test_eu_ai_act_policy_validation()
    
    if result:
        print("\n✅ PASS: All EU AI Act rego policies passed validation with 'opa check'")
        sys.exit(0)
    else:
        print("\n❌ FAIL: Some EU AI Act rego policies failed validation with 'opa check'")
        sys.exit(1) 