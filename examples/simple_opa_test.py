#!/usr/bin/env python
"""
Simple OPA server test script.
This script tests the connection to the OPA server and loads a simple policy.
"""
import os
import sys
import json
import requests
from pathlib import Path

# OPA server URL - using the Windows host IP from WSL
OPA_SERVER_URL = "http://172.29.176.1:8182"

def check_opa_server():
    """Check if the OPA server is running."""
    try:
        response = requests.get(f"{OPA_SERVER_URL}/health")
        if response.status_code == 200:
            print("✅ OPA server is running")
            return True
        else:
            print(f"❌ OPA server returned status code: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ Error connecting to OPA server: {str(e)}")
        return False

def load_simple_policy():
    """Load a simple policy into the OPA server."""
    # Simple policy that always returns true
    policy = """
    package test

    default allow = true
    """
    
    try:
        response = requests.put(
            f"{OPA_SERVER_URL}/v1/policies/test",
            data=policy,
            headers={"Content-Type": "text/plain"}
        )
        
        if response.status_code in (200, 201):
            print("✅ Successfully loaded test policy")
            return True
        else:
            print(f"❌ Failed to load policy: {response.status_code} - {response.text}")
            return False
    except requests.RequestException as e:
        print(f"❌ Error loading policy: {str(e)}")
        return False

def test_policy_evaluation():
    """Test policy evaluation."""
    input_data = {"user": "alice", "action": "read"}
    
    try:
        response = requests.post(
            f"{OPA_SERVER_URL}/v1/data/test/allow",
            json={"input": input_data},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Policy evaluation successful: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Policy evaluation failed: {response.status_code} - {response.text}")
            return False
    except requests.RequestException as e:
        print(f"❌ Error evaluating policy: {str(e)}")
        return False

def main():
    """Main function."""
    print("🔍 Testing OPA server connection and policy evaluation")
    
    # Step 1: Check if OPA server is running
    if not check_opa_server():
        print("❌ OPA server is not running. Please start it with:")
        print("   /mnt/c/opa/opa.exe run --server --addr :8182")
        return
    
    # Step 2: Load a simple policy
    if not load_simple_policy():
        print("❌ Failed to load policy. Check OPA server logs.")
        return
    
    # Step 3: Test policy evaluation
    if not test_policy_evaluation():
        print("❌ Failed to evaluate policy. Check OPA server logs.")
        return
    
    print("✅ All tests passed! OPA server is working correctly.")

if __name__ == "__main__":
    main() 