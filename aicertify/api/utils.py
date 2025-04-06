"""
AICertify API Utilities Module

This module provides utility functions for the AICertify API.
"""

import json
import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

# Import core utilities
from aicertify.api.core import CustomJSONEncoder

def save_json(data: Dict[str, Any], file_path: str, ensure_dir: bool = True) -> bool:
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save
        file_path: Path to save the file
        ensure_dir: Whether to ensure the directory exists
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if ensure_dir:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, cls=CustomJSONEncoder)
        
        logger.info(f"Data saved to {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving data to {file_path}: {e}")
        return False

def load_json(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Load data from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Loaded data, or None if loading failed
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        logger.info(f"Data loaded from {file_path}")
        return data
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        return None

def get_timestamp_str() -> str:
    """
    Get a formatted timestamp string for filenames.
    
    Returns:
        Formatted timestamp string
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def sanitize_filename(name: str) -> str:
    """
    Sanitize a string for use as a filename.
    
    Args:
        name: String to sanitize
        
    Returns:
        Sanitized string
    """
    # Replace spaces with underscores
    name = name.replace(' ', '_')
    
    # Remove invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '')
    
    return name
