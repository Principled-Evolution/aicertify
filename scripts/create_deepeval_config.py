#!/usr/bin/env python
"""
Script to create a properly formatted DeepEval configuration file.
This ensures DeepEval has access to the OpenAI API key for content safety evaluation.
"""

import os
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def create_deepeval_config():
    """Create DeepEval configuration files in the necessary locations."""
    # Get OpenAI API key from environment
    openai_api_key = os.environ.get("OPENAI_API_KEY", "")
    if not openai_api_key:
        logger.warning("OPENAI_API_KEY not found in environment variables.")
        logger.warning("DeepEval will not be able to perform content safety evaluation.")
        return False

    # Create configuration in user's home directory
    home_dir = os.path.expanduser("~")
    user_config_dir = os.path.join(home_dir, ".deepeval")
    os.makedirs(user_config_dir, exist_ok=True)
    
    user_config_file = os.path.join(user_config_dir, "config.json")
    
    # Create configuration in project directory
    project_dir = os.getcwd()
    project_config_dir = os.path.join(project_dir, ".deepeval")
    os.makedirs(project_config_dir, exist_ok=True)
    
    project_config_file = os.path.join(project_config_dir, "config.json")
    
    # Create configuration content
    config = {
        "OPENAI_API_KEY": openai_api_key,
        "ANTHROPIC_API_KEY": "",
        "HUGGINGFACE_API_KEY": "",
        "COHERE_API_KEY": "",
        "LANGCHAIN_API_KEY": "",
        "OPENAI_ORG_ID": "",
        "USE_LOCAL_MODEL": False,
        "LOCAL_MODEL_API_KEY": "http://localhost:8000/v1",
        "EVALUATE_SCRIPT_PATH": "",
        "EVALUATE_WITH_TRACING": False,
        "TRACING_API_KEY": "",
        "TRACING_API_URL": "",
        "TRACING_PROJECT": "",
        "ENABLE_LLAMA_GUARD": False,
        "saved_models": {}
    }
    
    # Write configuration files
    try:
        with open(user_config_file, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Created DeepEval config in user directory: {user_config_file}")
        
        with open(project_config_file, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Created DeepEval config in project directory: {project_config_file}")
        
        return True
    except Exception as e:
        logger.error(f"Error creating DeepEval config: {e}")
        return False

if __name__ == "__main__":
    if create_deepeval_config():
        print("DeepEval configuration created successfully.")
    else:
        print("Failed to create DeepEval configuration.") 