import json
import requests
from typing import Dict, Any, Optional
import os

class OpaClient:
    """Client for connecting to an external OPA server."""
    
    def __init__(self, base_url: str = "http://localhost:8182"):
        """Initialize OPA client with the server URL.
        
        Args:
            base_url: The base URL of the OPA server, defaults to http://localhost:8182
        """
        self.base_url = base_url
        self.verify_connection()
    
    def verify_connection(self) -> bool:
        """Verify that the OPA server is running and accessible.
        
        Returns:
            bool: True if connection is successful
            
        Raises:
            ConnectionError: If unable to connect to the OPA server
        """
        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print(f"Successfully connected to OPA server at {self.base_url}")
                return True
            else:
                raise ConnectionError(f"OPA server returned status code: {response.status_code}")
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to connect to OPA server at {self.base_url}: {str(e)}")
    
    def load_policy(self, policy_name: str, policy_content: str) -> bool:
        """Load a policy into the OPA server.
        
        Args:
            policy_name: Name of the policy (without .rego extension)
            policy_content: Content of the Rego policy
            
        Returns:
            bool: True if policy was successfully loaded
        """
        url = f"{self.base_url}/v1/policies/{policy_name}"
        headers = {"Content-Type": "text/plain"}
        
        response = requests.put(url, data=policy_content, headers=headers)
        if response.status_code in (200, 201):
            print(f"Successfully loaded policy '{policy_name}'")
            return True
        else:
            print(f"Failed to load policy '{policy_name}': {response.status_code} - {response.text}")
            return False
    
    def load_policy_from_file(self, policy_path: str) -> bool:
        """Load a policy file into the OPA server.
        
        Args:
            policy_path: Path to the .rego policy file
            
        Returns:
            bool: True if policy was successfully loaded
        """
        try:
            with open(policy_path, 'r') as f:
                policy_content = f.read()
            
            policy_name = os.path.basename(policy_path)
            if policy_name.endswith('.rego'):
                policy_name = policy_name[:-5]  # Remove .rego extension
            
            return self.load_policy(policy_name, policy_content)
        except Exception as e:
            print(f"Error loading policy from file {policy_path}: {str(e)}")
            return False
    
    def load_data(self, path: str, data: Any) -> bool:
        """Load data into the OPA server's data document.
        
        Args:
            path: Path in the data document (e.g., "input" or "context")
            data: JSON-serializable data to load
            
        Returns:
            bool: True if data was successfully loaded
        """
        url = f"{self.base_url}/v1/data/{path}"
        headers = {"Content-Type": "application/json"}
        
        response = requests.put(url, data=json.dumps({"input": data}), headers=headers)
        if response.status_code in (200, 201, 204):
            print(f"Successfully loaded data at path '{path}'")
            return True
        else:
            print(f"Failed to load data at path '{path}': {response.status_code} - {response.text}")
            return False
    
    def evaluate_policy(self, policy_path: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a policy with the given input data.
        
        Args:
            policy_path: Path to the policy in the OPA data document (e.g., "example/allow")
            input_data: Input data for policy evaluation
            
        Returns:
            Dict: The evaluation result
        """
        url = f"{self.base_url}/v1/data/{policy_path}"
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(url, data=json.dumps({"input": input_data}), headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Policy evaluation failed: {response.status_code} - {response.text}")
            return {"result": None, "error": f"Status code: {response.status_code}"}

# Example usage
if __name__ == "__main__":
    # Create OPA client
    client = OpaClient()
    
    # Example policy
    example_policy = """
    package example

    # Allow if the user is an admin
    allow {
        input.user.role == "admin"
    }

    # Allow if the user has explicit permission
    allow {
        input.user.permissions[_] == input.action
    }
    """
    
    # Load the policy
    client.load_policy("example", example_policy)
    
    # Define test input
    test_input = {
        "user": {
            "id": "user1",
            "role": "regular",
            "permissions": ["read", "write"]
        },
        "action": "write"
    }
    
    # Evaluate the policy
    result = client.evaluate_policy("example/allow", test_input)
    print("Evaluation result:", result) 