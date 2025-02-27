import json
import logging
import os
import subprocess
import traceback
import inspect
import sys
from typing import Dict, List, Union, Any, Optional, Tuple

from aicertify.opa_core.policy_loader import PolicyLoader

logger = logging.getLogger(__name__)

def run_opa_on_compliance_input(
    compliance_input: Dict[str, Any],
    policy_category: str,
    opa_executable_path: str,
) -> Dict[str, Any]:
    """
    Run OPA on the compliance input.

    Args:
        compliance_input: The compliance input to evaluate.
        policy_category: The category of policies to evaluate.
        opa_executable_path: The path to the OPA executable.

    Returns:
        Dict[str, Any]: The results of the OPA evaluation.
    """
    try:
        # Log the start of the OPA evaluation
        logger.info(f"[DEBUG] Starting OPA evaluation for category: {policy_category}")
        logger.info(f"[DEBUG] OPA executable path: {opa_executable_path}")
        logger.info(f"[DEBUG] Current working directory: {os.getcwd()}")
        
        # Check if OPA executable exists
        if not os.path.exists(opa_executable_path):
            logger.error(f"[ERROR] OPA executable not found at {opa_executable_path}")
            return {"error": f"OPA executable not found at {opa_executable_path}"}
        
        # Log the input data structure for debugging
        try:
            logger.info(f"[DEBUG] Input data type: {type(compliance_input)}")
            logger.info(f"[DEBUG] Input data keys: {list(compliance_input.keys())}")
            sample_data = {k: str(v)[:100] + "..." if isinstance(v, str) and len(str(v)) > 100 else v 
                          for k, v in list(compliance_input.items())[:5]}
            logger.info(f"[DEBUG] Sample input data: {json.dumps(sample_data, indent=2)}")
        except Exception as e:
            logger.error(f"[ERROR] Error logging input data: {str(e)}")
        
        # Create a temporary input file for OPA
        input_file_path = os.path.join(os.getcwd(), "temp_input.json")
        logger.info(f"[DEBUG] Creating temporary input file at {input_file_path}")
        
        with open(input_file_path, "w") as f:
            json.dump(compliance_input, f)
        
        # Debug information about PolicyLoader class
        logger.info(f"[DEBUG] PolicyLoader module location: {inspect.getfile(PolicyLoader)}")
        logger.info(f"[DEBUG] Python version: {sys.version}")
        logger.info(f"[DEBUG] Python executable: {sys.executable}")
        logger.info(f"[DEBUG] Python path: {sys.path}")
        
        # Create a PolicyLoader instance
        try:
            logger.info("[DEBUG] Creating PolicyLoader instance")
            policy_loader = PolicyLoader()
            logger.info(f"[DEBUG] PolicyLoader initialized with policies_dir: {policy_loader.policies_dir}")
            
            # Log all available categories
            all_categories = policy_loader.get_categories()
            logger.info(f"[DEBUG] Available policy categories: {all_categories}")
            
            # Check if the requested category exists
            if policy_category not in all_categories:
                logger.warning(f"[WARNING] Requested category '{policy_category}' not found in available categories")
                
                # Try to find a close match
                for category in all_categories:
                    if policy_category.lower() in category.lower() or category.lower() in policy_category.lower():
                        logger.info(f"[DEBUG] Found potential match: '{category}' for requested '{policy_category}'")
            
            # Try multiple variations of the category string
            category_variations = [
                policy_category,
                policy_category.lower(),
                policy_category.replace("_", " "),
                policy_category.replace(" ", "_"),
                policy_category.replace("-", "_"),
                policy_category.replace("_", "-"),
            ]
            
            policy_files = []
            used_variation = None
            
            for variation in category_variations:
                try:
                    logger.info(f"[DEBUG] Trying to get policies with category variation: '{variation}'")
                    variation_policies = policy_loader.get_policies_by_category(variation)
                    if variation_policies:
                        policy_files = variation_policies
                        used_variation = variation
                        logger.info(f"[DEBUG] Successfully found {len(policy_files)} policies using variation: '{variation}'")
                        break
                except Exception as var_err:
                    logger.warning(f"[WARNING] Error retrieving policies for variation '{variation}': {str(var_err)}")
            
            if not policy_files:
                # Try direct inspection of the directory structure
                logger.warning("[WARNING] Could not retrieve policies through standard methods, trying direct inspection")
                for root, dirs, files in os.walk(policy_loader.policies_dir):
                    logger.info(f"[DEBUG] Inspecting directory: {root}")
                    logger.info(f"[DEBUG] Found subdirectories: {dirs}")
                    logger.info(f"[DEBUG] Found files: {files}")
                    
                    # Check if the current directory contains the policy category
                    rel_path = os.path.relpath(root, policy_loader.policies_dir)
                    logger.info(f"[DEBUG] Relative path: {rel_path}")
                    
                    for category_var in category_variations:
                        if category_var.lower() in rel_path.lower():
                            logger.info(f"[DEBUG] Found matching directory for '{category_var}' in '{rel_path}'")
                            for file in files:
                                if file.endswith(".rego"):
                                    policy_path = os.path.join(root, file)
                                    policy_files.append(policy_path)
                                    logger.info(f"[DEBUG] Added policy file: {policy_path}")
                
            if not policy_files:
                error_msg = f"No policies found for category: {policy_category}. Available categories: {all_categories}"
                logger.error(f"[ERROR] {error_msg}")
                return {"error": error_msg}
            
            logger.info(f"[DEBUG] Found {len(policy_files)} policies for category: {policy_category if not used_variation else used_variation}")
            for policy_file in policy_files:
                logger.info(f"[DEBUG] Policy file: {policy_file}")
        
        except Exception as pl_error:
            tb_str = traceback.format_exc()
            logger.error(f"[ERROR] Error initializing PolicyLoader or retrieving policies: {str(pl_error)}")
            logger.error(f"[ERROR] Traceback: {tb_str}")
            return {"error": f"Error retrieving policies: {str(pl_error)}"}
        
        # Run OPA evaluation for each policy file
        all_results = {}
        for policy_file in policy_files:
            try:
                policy_name = os.path.basename(policy_file).replace('.rego', '')
                logger.info(f"[DEBUG] Evaluating policy: {policy_name} from file {policy_file}")
                
                # Extract the package name from the policy file
                package_name = None
                try:
                    with open(policy_file, 'r') as f:
                        policy_content = f.read()
                        package_line = next((line for line in policy_content.split('\n') if line.strip().startswith('package')), None)
                        if package_line:
                            package_name = package_line.strip().split('package ')[1].strip()
                            logger.info(f"[DEBUG] Extracted package name: {package_name}")
                except Exception as pkg_err:
                    logger.warning(f"[WARNING] Could not extract package name from {policy_file}: {str(pkg_err)}")
                
                # If policy file exists, run OPA
                if os.path.exists(policy_file):
                    logger.info(f"[DEBUG] Running OPA with policy file: {policy_file}")
                    
                    # Construct OPA command
                    opa_cmd = [
                        opa_executable_path,
                        "eval",
                        "--format", "json",
                        "--input", input_file_path,
                        "--data", policy_file,
                        "data"
                    ]
                    
                    logger.info(f"[DEBUG] OPA command: {' '.join(opa_cmd)}")
                    
                    # Run the OPA command
                    try:
                        result = subprocess.run(
                            opa_cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            check=True
                        )
                        
                        logger.info(f"[DEBUG] OPA stdout: {result.stdout[:200]}..." if len(result.stdout) > 200 else result.stdout)
                        
                        if result.stderr:
                            logger.warning(f"[WARNING] OPA stderr: {result.stderr}")
                        
                        try:
                            result_json = json.loads(result.stdout)
                            logger.info(f"[DEBUG] OPA result keys: {list(result_json.keys()) if isinstance(result_json, dict) else 'not a dict'}")
                            
                            # Store the result
                            if package_name and isinstance(result_json, dict) and 'result' in result_json:
                                # Extract the result using the package name as a path
                                path_parts = package_name.split('.')
                                current = result_json['result']
                                for part in path_parts:
                                    if isinstance(current, dict) and part in current:
                                        current = current[part]
                                    else:
                                        logger.warning(f"[WARNING] Could not find part '{part}' in result path for package {package_name}")
                                        break
                                
                                all_results[policy_name] = current
                                logger.info(f"[DEBUG] Stored result for {policy_name} using package {package_name}")
                            else:
                                all_results[policy_name] = result_json
                                logger.info(f"[DEBUG] Stored raw result for {policy_name}")
                                
                        except json.JSONDecodeError as json_err:
                            logger.error(f"[ERROR] Failed to parse OPA output as JSON: {str(json_err)}")
                            all_results[policy_name] = {"error": f"Failed to parse output: {str(json_err)}"}
                            
                    except subprocess.CalledProcessError as proc_err:
                        logger.error(f"[ERROR] OPA command failed: {str(proc_err)}")
                        logger.error(f"[ERROR] OPA stderr: {proc_err.stderr}")
                        all_results[policy_name] = {"error": f"OPA evaluation failed: {proc_err.stderr}"}
                    
                else:
                    logger.error(f"[ERROR] Policy file does not exist: {policy_file}")
                    all_results[policy_name] = {"error": f"Policy file not found: {policy_file}"}
                    
            except Exception as policy_err:
                tb_str = traceback.format_exc()
                logger.error(f"[ERROR] Error evaluating policy {policy_file}: {str(policy_err)}")
                logger.error(f"[ERROR] Traceback: {tb_str}")
                all_results[os.path.basename(policy_file)] = {"error": f"Evaluation error: {str(policy_err)}"}
        
        # Clean up temporary file
        try:
            os.remove(input_file_path)
            logger.info(f"[DEBUG] Removed temporary input file: {input_file_path}")
        except Exception as cleanup_err:
            logger.warning(f"[WARNING] Failed to remove temporary file {input_file_path}: {str(cleanup_err)}")
        
        logger.info(f"[DEBUG] OPA evaluation completed with {len(all_results)} policy results")
        return {"results": all_results}
    
    except Exception as e:
        tb_str = traceback.format_exc()
        logger.error(f"[ERROR] Unhandled exception in run_opa_on_compliance_input: {str(e)}")
        logger.error(f"[ERROR] Traceback: {tb_str}")
        return {"error": f"OPA evaluation failed: {str(e)}"} 