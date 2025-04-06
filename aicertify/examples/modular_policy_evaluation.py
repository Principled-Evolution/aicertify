#!/usr/bin/env python3
"""
Example script demonstrating the modular OPA policy evaluation capabilities.

This script shows how to use the enhanced PolicyLoader and OpaEvaluator to:
1. Load policies by category, subcategory, and version
2. Resolve policy dependencies for composition
3. Evaluate policies against input data
4. Process evaluation results
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any

from aicertify.opa_core.policy_loader import PolicyLoader
from aicertify.opa_core.evaluator import OpaEvaluator
# Ensure the aicertify package is in the Python path
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("policy_evaluation_example")

def load_sample_input() -> Dict[str, Any]:
    """Load a sample input for policy evaluation."""
    sample_input = {
        "metadata": {
            "version": "1.0.0",
            "name": "Sample AI System",
            "description": "A sample AI system for testing OPA policy evaluation",
            "domain": "general",
            "organization": "AICertify"
        },
        "documentation": {
            "technical_documentation": {
                "provided": True,
                "completeness_score": 0.9,
                "last_updated": "2023-10-15"
            },
            "disclosure": {
                "deepfake_notification": True,
                "ai_use_notification": True
            }
        },
        "model": {
            "type": "large_language_model",
            "training": {
                "dataset_documentation": True,
                "bias_mitigation_steps": ["data_augmentation", "balanced_sampling"],
                "privacy_preserving_techniques": ["differential_privacy"]
            },
            "oversight": {
                "human_review": True,
                "automated_monitoring": True
            }
        },
        "risk_assessment": {
            "performed": True,
            "level": "medium",
            "mitigations_documented": True
        },
        "testing": {
            "fairness": {
                "performed": True,
                "metrics": ["demographic_parity", "equal_opportunity"],
                "groups_tested": ["gender", "age", "ethnicity"]
            },
            "robustness": {
                "performed": True,
                "adversarial_testing": True
            }
        }
    }
    return sample_input

def print_results(results, category: str, subcategory: str = "", version: str = None):
    """Pretty print the evaluation results."""
    if subcategory:
        header = f"{category}/{subcategory}"
    else:
        header = category
        
    if version:
        header += f" (version: {version})"
    
    print(f"\n{'=' * 80}")
    print(f"EVALUATION RESULTS: {header}")
    print(f"{'=' * 80}")
    
    for i, result in enumerate(results, 1):
        if "error" in result:
            print(f"Error: {result['error']}")
            continue
            
        if "result" not in result:
            print(f"Unexpected result format: {result}")
            continue
            
        # Extract actual OPA result
        opa_result = result["result"]
        
        print(f"\nPolicy #{i}:")
        print(f"  Overall Compliance: {'✅ COMPLIANT' if opa_result.get('overall_result', False) else '❌ NON-COMPLIANT'}")
        
        # Print policy details if available
        if "policy" in opa_result:
            print(f"  Policy: {opa_result['policy']}")
        if "version" in opa_result:
            print(f"  Version: {opa_result['version']}")
            
        # Print details if available
        if "details" in opa_result:
            print("\n  Details:")
            for key, value in opa_result["details"].items():
                if isinstance(value, dict):
                    print(f"    {key}:")
                    for subkey, subvalue in value.items():
                        print(f"      {subkey}: {subvalue}")
                else:
                    print(f"    {key}: {value}")
                    
        # Print recommendations if available
        if "recommendations" in opa_result:
            print("\n  Recommendations:")
            for rec in opa_result["recommendations"]:
                print(f"    - {rec}")
    
    print(f"\n{'=' * 80}\n")

def main():
    """Main function demonstrating policy evaluation."""
    try:
        # Initialize the policy loader and evaluator
        policy_loader = PolicyLoader()
        evaluator = OpaEvaluator()
        
        # Load sample input data
        input_data = load_sample_input()
        
        # Step 1: List available policy categories and subcategories
        print("Available policy categories and subcategories:")
        categories = policy_loader.get_all_categories()
        for category, subcategory in categories:
            if subcategory:
                print(f"  - {category}/{subcategory}")
            else:
                print(f"  - {category}")
                
        # Step 2: Evaluate policies from different categories/subcategories
        
        # Global policies
        global_policies = policy_loader.get_policies("global")
        if global_policies:
            print("\nEvaluating global policies...")
            global_results = [evaluator.evaluate_policy(policy, input_data) for policy in global_policies]
            print_results(global_results, "global")
        
        # EU AI Act policies
        eu_policies = policy_loader.get_policies("international", "eu_ai_act")
        if eu_policies:
            print("\nEvaluating EU AI Act policies...")
            eu_results = [evaluator.evaluate_policy(policy, input_data) for policy in eu_policies]
            print_results(eu_results, "international", "eu_ai_act")
        
        # Banking & Financial Services policies
        bfs_policies = policy_loader.get_policies("industry_specific", "bfs")
        if bfs_policies:
            print("\nEvaluating Banking & Financial Services policies...")
            bfs_results = [evaluator.evaluate_policy(policy, input_data) for policy in bfs_policies]
            print_results(bfs_results, "industry_specific", "bfs")
        
        # Step 3: Demonstrate version selection
        # Evaluate a specific version of a policy
        eu_v1_policies = policy_loader.get_policies("international", "eu_ai_act", "v1")
        if eu_v1_policies:
            print("\nEvaluating EU AI Act policies (v1)...")
            eu_v1_results = [evaluator.evaluate_policy(policy, input_data) for policy in eu_v1_policies]
            print_results(eu_v1_results, "international", "eu_ai_act", "v1")
        
        # Step 4: Demonstrate policy dependency resolution
        # Get all policies with their dependencies
        eu_transparency_policy = next((p for p in eu_policies if "transparency" in p), None)
        if eu_transparency_policy:
            print("\nResolving dependencies for EU AI Act transparency policy...")
            dependencies = policy_loader.resolve_policy_dependencies([eu_transparency_policy])
            print(f"Found {len(dependencies)} policies (including dependencies):")
            for dep in dependencies:
                print(f"  - {Path(dep).name}")
            
            # Evaluate the policy with dependencies
            result = evaluator.evaluate_policy(eu_transparency_policy, input_data)
            print_results([result], "international", "eu_ai_act (with dependencies)")
            
        # Step 5: Use the convenience method to evaluate all policies in a category
        print("\nEvaluating all operational policies...")
        operational_results = evaluator.evaluate_policies_by_category("operational", input_data)
        print_results(operational_results, "operational")
        
        print("Policy evaluation demonstration completed successfully.")
        
    except Exception as e:
        logger.error(f"Error in policy evaluation demonstration: {e}", exc_info=True)
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main()) 