#!/usr/bin/env python
"""
Script to set up DeepEval configuration file.
This will initialize the config file needed by DeepEval's ToxicityMetric.
"""

import os
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def setup_deepeval_config():
    """Set up the DeepEval configuration file."""
    try:
        # Detect DeepEval path
        import deepeval
        
        logger.info(f"DeepEval version: {deepeval.__version__}")
        
        # Use the standard path for DeepEval config
        home_dir = os.path.expanduser("~")
        config_dir = os.path.join(home_dir, '.deepeval')
        config_path = os.path.join(config_dir, 'config.json')
        
        logger.info(f"Using config path: {config_path}")
        
        # Create the directory if it doesn't exist
        os.makedirs(config_dir, exist_ok=True)
        
        # Default configuration for DeepEval
        default_config = {
            "OPENAI_API_KEY": "",  # Replace with your OpenAI API key if you have one
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
        
        # Write the configuration to file
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        logger.info(f"DeepEval configuration file created at {config_path}")
        logger.info("Note: To use OpenAI's API for content safety evaluation, you'll need to add your API key.")
        
        # Also create .deepeval directory in the current project (for local configuration)
        project_config_dir = os.path.join(os.getcwd(), '.deepeval')
        os.makedirs(project_config_dir, exist_ok=True)
        
        project_config_path = os.path.join(project_config_dir, 'config.json')
        with open(project_config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        logger.info(f"Local project DeepEval configuration created at {project_config_path}")
        
        return True
    
    except ImportError:
        logger.error("DeepEval is not installed. Please install with: pip install deepeval")
        return False
    
    except Exception as e:
        logger.error(f"Error setting up DeepEval configuration: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    if setup_deepeval_config():
        print("DeepEval configuration set up successfully.")
    else:
        print("Failed to set up DeepEval configuration.") 