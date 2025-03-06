"""
Configuration settings for the AICertify report generation system.

This module provides configuration settings and feature flags for the
report generation system, allowing for gradual migration from the old
extraction system to the new flexible extraction system.
"""

import os
from typing import Dict, Any

# Feature flags
FEATURE_FLAGS = {
    # Enable the new flexible extraction system
    "use_flexible_extraction": os.environ.get("AICERTIFY_USE_FLEXIBLE_EXTRACTION", "true").lower() == "true",
    
    # Path to custom metric configuration file
    "metric_config_path": os.environ.get("AICERTIFY_METRIC_CONFIG_PATH", None),
}

def get_feature_flag(flag_name: str, default: Any = None) -> Any:
    """
    Get the value of a feature flag.
    
    Args:
        flag_name: Name of the feature flag
        default: Default value if flag not found
        
    Returns:
        Value of the feature flag, or default if not found
    """
    return FEATURE_FLAGS.get(flag_name, default)

def set_feature_flag(flag_name: str, value: Any) -> None:
    """
    Set the value of a feature flag.
    
    Args:
        flag_name: Name of the feature flag
        value: Value to set
    """
    FEATURE_FLAGS[flag_name] = value

def use_flexible_extraction() -> bool:
    """
    Check if the flexible extraction system should be used.
    
    Returns:
        True if the flexible extraction system should be used, False otherwise
    """
    return get_feature_flag("use_flexible_extraction", False)

def get_metric_config_path() -> str:
    """
    Get the path to the custom metric configuration file.
    
    Returns:
        Path to the custom metric configuration file, or None if not set
    """
    return get_feature_flag("metric_config_path", None) 