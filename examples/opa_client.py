import json
import json
import requests
from requests.exceptions import RequestException
from typing import Dict, Any, Optional
import os

class OpaClientError(Exception):
    """Base exception for OpaClient errors."""
    pass

class OpaConnectionError(OpaClientError):
    """Raised when connection to the OPA server fails."""
    pass

class OpaPolicyError(OpaClientError):
    """Raised for errors related to OPA policy loading or evaluation."""
    pass

class OpaClient:
    """
    Client for interacting with an external Open Policy Agent (OPA) server.

    Provides methods to check connection, load policies/data, and evaluate policies.
    """
    DEFAULT_OPA_URL = "http://localhost:8181"

    def __init__(self):
        """
        Initialize OPA client.

        Reads the OPA server URL from the `OPA_BASE_URL` environment variable.
        If the environment variable is not set, it defaults to `DEFAULT_OPA_URL`.

        Raises:
            OpaConnectionError: If unable to connect to the OPA server upon initialization.
        """
        opa_url = os.getenv('OPA_BASE_URL', self.DEFAULT_OPA_URL)
        self.base_url = opa_url.rstrip('/') # Ensure no trailing slash
        print(f"Initializing OpaClient with base URL: {self.base_url}") # Added log
        try:
            self.verify_connection()
        except RequestException as e:
            # Wrap the RequestException in our custom error type for consistency
            raise OpaConnectionError(f"Failed to connect to OPA server during initialization at {self.base_url}: {str(e)}") from e
    
    def verify_connection(self) -> None:
        """
        Verify that the OPA server is running and accessible via its health endpoint.

        Raises:
            OpaConnectionError: If unable to connect or the server returns an unhealthy status.
            requests.exceptions.RequestException: For underlying network issues.
        """
        health_url = f"{self.base_url}/health"
        try:
            response = requests.get(health_url, timeout=5) # Added timeout
            response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
            print(f"Successfully connected to OPA server at {self.base_url}")
        except RequestException as e:
            # Catch RequestException and re-raise as OpaConnectionError
            raise OpaConnectionError(f"Failed to connect to OPA server health endpoint at {health_url}: {str(e)}") from e
        except Exception as e:
             # Catch other potential errors during request or status check
            raise OpaConnectionError(f"An unexpected error occurred while verifying connection to {health_url}: {str(e)}") from e

    def load_policy(self, policy_name: str, policy_content: str) -> None:
        """
        Load or update a policy on the OPA server.

        Args:
            policy_name: Identifier for the policy (e.g., 'my_policy').
                         This will be used in the URL path: /v1/policies/{policy_name}.
            policy_content: A string containing the full Rego policy code.

        Raises:
            OpaPolicyError: If the server fails to load the policy (e.g., invalid Rego, server error).
            requests.exceptions.RequestException: For underlying network issues.
        """
        url = f"{self.base_url}/v1/policies/{policy_name}"
        headers = {"Content-Type": "text/plain"}

        try:
            response = requests.put(url, data=policy_content.encode('utf-8'), headers=headers, timeout=10) # Ensure UTF-8 encoding
            response.raise_for_status() # Check for HTTP errors
            print(f"Successfully loaded policy '{policy_name}'")
        except RequestException as e:
            # More specific error message including response details if available
            error_details = f"Network error: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                 error_details = f"Status code: {e.response.status_code}. Response: {e.response.text}"
            raise OpaPolicyError(f"Failed to load policy '{policy_name}' to {url}. {error_details}") from e
        except Exception as e:
            raise OpaPolicyError(f"An unexpected error occurred loading policy '{policy_name}': {str(e)}") from e
    
    def load_policy_from_file(self, policy_path: str) -> None:
        """
        Load a policy file into the OPA server.

        Args:
            policy_path: Path to the .rego policy file.

        Raises:
            FileNotFoundError: If the policy file does not exist.
            OpaPolicyError: If reading the file or loading the policy fails.
            requests.exceptions.RequestException: For underlying network issues during policy loading.
        """
        try:
            with open(policy_path, 'r', encoding='utf-8') as f: # Specify encoding
                policy_content = f.read()

            # Derive policy name from filename (strip .rego)
            policy_name = os.path.basename(policy_path)
            if policy_name.lower().endswith('.rego'):
                policy_name = policy_name[:-5]

            if not policy_name:
                 raise OpaPolicyError(f"Could not derive a valid policy name from path: {policy_path}")

            self.load_policy(policy_name, policy_content)
        except FileNotFoundError:
            raise # Re-raise FileNotFoundError directly
        except OpaPolicyError:
             raise # Re-raise OpaPolicyError directly
        except RequestException:
             raise # Re-raise RequestException directly
        except Exception as e:
            # Catch other potential errors like permission issues during file read
            raise OpaPolicyError(f"Error reading or loading policy from file {policy_path}: {str(e)}") from e

    def load_data(self, path: str, data: Any) -> None:
        """
        Load data into the OPA server's data document at a specified path.

        Note: This typically overwrites the data at the given path.

        Args:
            path: The hierarchical path where the data should be stored (e.g., 'my_app/config').
            data: JSON-serializable data to load.

        Raises:
            OpaClientError: If the server fails to load the data.
            requests.exceptions.RequestException: For underlying network issues.
            TypeError: If data is not JSON serializable.
        """
        url = f"{self.base_url}/v1/data/{path.strip('/')}" # Ensure path doesn't start/end with /
        headers = {"Content-Type": "application/json"}

        try:
            # OPA expects the data directly, not nested under 'input' for PUT /v1/data
            json_data = json.dumps(data)
        except TypeError as e:
            raise TypeError(f"Data for path '{path}' is not JSON serializable: {str(e)}") from e

        try:
            response = requests.put(url, data=json_data.encode('utf-8'), headers=headers, timeout=10)
            response.raise_for_status() # Checks for 4xx/5xx errors
            # Status 204 No Content is also a success for PUT /v1/data
            print(f"Successfully loaded data at path '{path}' (Status: {response.status_code})")
        except RequestException as e:
            error_details = f"Network error: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                 error_details = f"Status code: {e.response.status_code}. Response: {e.response.text}"
            raise OpaClientError(f"Failed to load data to path '{path}' at {url}. {error_details}") from e
        except Exception as e:
            raise OpaClientError(f"An unexpected error occurred loading data to '{path}': {str(e)}") from e
    
    def evaluate_policy(self, policy_query: str, input_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Evaluate a policy rule or query data from the OPA server.

        Args:
            policy_query: The OPA query path (e.g., "data.example.allow" or just "data.users").
            input_data: Optional dictionary containing input data for the policy evaluation.
                        This will be available as `input` within the Rego policies.

        Returns:
            Dict: The evaluation result from the OPA server.

        Raises:
            OpaPolicyError: If the evaluation fails (e.g., policy not found, server error).
            requests.exceptions.RequestException: For underlying network issues.
            TypeError: If input_data is not JSON serializable.
        """
        # Ensure query starts with 'v1/data/' or adapt as needed based on OPA version/setup
        # Common practice is to query paths starting from 'data.'
        if not policy_query.startswith('/'):
             policy_query = '/' + policy_query.replace('.', '/') # Convert dot notation to path

        url = f"{self.base_url}/v1{policy_query}"
        headers = {"Content-Type": "application/json"}

        request_body: Optional[bytes] = None
        if input_data is not None:
             try:
                 # OPA expects evaluation input under the "input" key for POST requests
                 request_body = json.dumps({"input": input_data}).encode('utf-8')
             except TypeError as e:
                 raise TypeError(f"Input data for query '{policy_query}' is not JSON serializable: {str(e)}") from e

        try:
             # Use GET if no input data, POST if input data is provided
             if request_body:
                 response = requests.post(url, data=request_body, headers=headers, timeout=10)
             else:
                 response = requests.get(url, headers=headers, timeout=10)

             response.raise_for_status() # Raises HTTPError for 4xx/5xx

             # Check if response is valid JSON before returning
             try:
                 result = response.json()
                 # OPA often wraps results in a 'result' key
                 return result.get('result', result) if isinstance(result, dict) else result
             except json.JSONDecodeError as e:
                 raise OpaPolicyError(f"OPA server returned non-JSON response for query '{policy_query}'. Status: {response.status_code}. Response text: {response.text[:1000]}") from e

        except RequestException as e:
            error_details = f"Network error: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                 error_details = f"Status code: {e.response.status_code}. Response: {e.response.text}"

            # Provide more specific error based on status code if possible
            status_code = e.response.status_code if hasattr(e, 'response') and e.response is not None else None
            if status_code == 404:
                 raise OpaPolicyError(f"Policy or data not found at query path '{policy_query}' (404). URL: {url}. {error_details}", 404) from e
            else:
                 raise OpaPolicyError(f"Policy evaluation failed for query '{policy_query}'. {error_details}", status_code) from e
        except Exception as e:
            raise OpaPolicyError(f"An unexpected error occurred during policy evaluation for '{policy_query}': {str(e)}") from e


# Example usage (demonstrates improved error handling)
if __name__ == "__main__":
    try:
        # Create OPA client - URL is now determined by environment variable or default
        print("Attempting to initialize OPA Client...")
        client = OpaClient()
        print("-" * 20)

        # Example policy
        example_policy_content = """
        package example

        # Default rule: deny
        default allow = false

        # Allow if the user is an admin
        allow {
            input.user.role == "admin"
        }

        # Allow if the user has the specific required permission for the action
        allow {
            required_permission := data.permissions[input.action] # Get required permission from data
            input.user.permissions[_] == required_permission
        }
        """

        # Example data (permissions required for actions)
        permissions_data = {
            "read": "read_access",
            "write": "write_access",
            "delete": "admin_access"
        }

        # Load the policy and data
        client.load_policy("example", example_policy_content)
        client.load_data("permissions", permissions_data) # Load data under 'permissions' path

        # --- Test Case 1: User with correct permission ---
        test_input_1 = {
            "user": {
                "id": "user1",
                "role": "editor",
                "permissions": ["read_access", "write_access"]
            },
            "action": "write"
        }
        # Query the 'allow' rule within the 'example' package
        result_1 = client.evaluate_policy("data.example.allow", test_input_1)
        print(f"Test Case 1 (action='write', role='editor', perms=['read_access', 'write_access']) -> allow: {result_1}")
        assert result_1 is True

        # --- Test Case 2: User without correct permission ---
        test_input_2 = {
            "user": {
                "id": "user2",
                "role": "viewer",
                "permissions": ["read_access"]
            },
            "action": "write" # Requires 'write_access'
        }
        result_2 = client.evaluate_policy("data.example.allow", test_input_2)
        print(f"Test Case 2 (action='write', role='viewer', perms=['read_access']) -> allow: {result_2}")
        assert result_2 is False

        # --- Test Case 3: Admin user ---
        test_input_3 = {
            "user": {
                "id": "admin_user",
                "role": "admin",
                "permissions": [] # Permissions don't matter if role is admin
            },
            "action": "delete"
        }
        result_3 = client.evaluate_policy("data.example.allow", test_input_3)
        print(f"Test Case 3 (action='delete', role='admin') -> allow: {result_3}")
        assert result_3 is True

        # --- Test Case 4: Querying data directly ---
        retrieved_data = client.evaluate_policy("data.permissions") # Query the loaded data
        print(f"Retrieved Data (data.permissions): {retrieved_data}")
        assert retrieved_data == permissions_data

        # --- Test Case 5: Non-existent policy (demonstrates 404 handling) ---
        try:
             client.evaluate_policy("data.non_existent.rule")
        except OpaPolicyError as e:
             print(f"Test Case 5 (Non-existent policy) -> Expected Error: {e}")
             assert e.status_code == 404 # Check if the status code is captured

    except OpaConnectionError as e:
         print(f"\n[ERROR] Could not connect to OPA server: {e}")
    except OpaClientError as e:
         print(f"\n[ERROR] An OPA client error occurred: {e}")
    except Exception as e:
         print(f"\n[ERROR] An unexpected error occurred: {e}")
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
