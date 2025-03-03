#!/usr/bin/env python
"""
Simple script to test OPA connection directly.
"""
import os
import json
import requests
import subprocess
import tempfile
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s [%(levelname)s] %(message)s')

# OPA server URL
OPA_SERVER_URL = "http://localhost:8182"

def test_opa_server_health():
    """Test if OPA server is responding to health checks."""
    try:
        response = requests.get(f"{OPA_SERVER_URL}/health", timeout=5)
        logging.info(f"Health check status code: {response.status_code}")
        if response.status_code == 200:
            logging.info("OPA server is healthy")
            return True
        else:
            logging.error(f"OPA server health check failed: {response.text}")
            return False
    except requests.RequestException as e:
        logging.error(f"Error connecting to OPA server: {str(e)}")
        return False

def test_opa_data_endpoint():
    """Test if OPA server is responding to data endpoint."""
    try:
        response = requests.get(f"{OPA_SERVER_URL}/v1/data", timeout=5)
        logging.info(f"Data endpoint status code: {response.status_code}")
        if response.status_code == 200:
            logging.info(f"Data response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            logging.error(f"OPA data endpoint failed: {response.text}")
            return False
    except requests.RequestException as e:
        logging.error(f"Error connecting to OPA data endpoint: {str(e)}")
        return False

def test_opa_query(path="test/hello"):
    """Test querying a specific path in OPA."""
    try:
        response = requests.get(f"{OPA_SERVER_URL}/v1/data/{path}", timeout=5)
        logging.info(f"Query status code: {response.status_code}")
        if response.status_code == 200:
            logging.info(f"Query response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            logging.error(f"OPA query failed: {response.text}")
            return False
    except requests.RequestException as e:
        logging.error(f"Error querying OPA: {str(e)}")
        return False

def test_opa_policy_evaluation():
    """Test evaluating a policy with input data."""
    input_data = {
        "fairness_score": 0.9,
        "content_safety_score": 0.95,
        "risk_management_score": 0.92
    }
    
    try:
        headers = {"Content-Type": "application/json"}
        url = f"{OPA_SERVER_URL}/v1/data/healthcare/multi_specialist/diagnostic_safety/is_compliant"
        payload = {"input": input_data}
        
        logging.info(f"Sending request to: {url}")
        logging.info(f"With payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        logging.info(f"Evaluation status code: {response.status_code}")
        
        if response.status_code == 200:
            logging.info(f"Evaluation response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            logging.error(f"OPA evaluation failed: {response.text}")
            return False
    except requests.RequestException as e:
        logging.error(f"Error evaluating policy: {str(e)}")
        return False

def test_local_opa_binary():
    """Test if local OPA binary is working."""
    # Try to find OPA binary
    opa_paths = [
        os.environ.get("OPA_PATH"),
        "/mnt/c/opa/opa.exe",
        "/mnt/c/opa/opa_windows_amd64.exe",
        "C:/opa/opa.exe",
        "C:/opa/opa_windows_amd64.exe"
    ]
    
    opa_path = None
    for path in opa_paths:
        if path and os.path.exists(path) and os.access(path, os.X_OK):
            opa_path = path
            break
    
    if not opa_path:
        logging.error("OPA binary not found")
        return False
    
    logging.info(f"Found OPA binary at: {opa_path}")
    
    # Create a simple test policy
    test_policy = """
    package test
    
    import rego.v1
    
    hello := "world"
    
    simple_rule if {
        true
    }
    """
    
    # Create a temporary policy file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.rego', delete=False) as policy_file:
        policy_file.write(test_policy)
        policy_path = policy_file.name
    
    # Create a temporary input file
    input_data = {"test": "input"}
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as input_file:
        json.dump(input_data, input_file)
        input_path = input_file.name
    
    try:
        # Run OPA eval command
        cmd = [
            opa_path,
            "eval",
            "--format", "json",
            "--data", policy_path,
            "--input", input_path,
            "data.test"
        ]
        
        logging.info(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logging.info(f"OPA eval succeeded: {result.stdout}")
            return True
        else:
            logging.error(f"OPA eval failed: {result.stderr}")
            return False
    except Exception as e:
        logging.error(f"Error running OPA eval: {str(e)}")
        return False
    finally:
        # Clean up temporary files
        if os.path.exists(policy_path):
            os.unlink(policy_path)
        if os.path.exists(input_path):
            os.unlink(input_path)

if __name__ == "__main__":
    print("\n=== Testing OPA Server Health ===")
    test_opa_server_health()
    
    print("\n=== Testing OPA Data Endpoint ===")
    test_opa_data_endpoint()
    
    print("\n=== Testing OPA Query ===")
    test_opa_query()
    
    print("\n=== Testing OPA Policy Evaluation ===")
    test_opa_policy_evaluation()
    
    print("\n=== Testing Local OPA Binary ===")
    test_local_opa_binary() 