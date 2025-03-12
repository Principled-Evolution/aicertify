import re
import logging
from typing import Dict, List, Optional, Any, NamedTuple
from pathlib import Path

logger = logging.getLogger(__name__)

class RegoMetadata(NamedTuple):
    """Metadata extracted from a Rego file."""
    required_metrics: List[str]
    required_params: Dict[str, Any]  # Parameter name -> default value
    file_path: str
    package_name: str

def _convert_default_value(default_value_str: Optional[str]) -> Any:
    """
    Convert a default value string to the appropriate Python type.
    
    Args:
        default_value_str: String representation of the default value
        
    Returns:
        Converted value as bool, int, float, or string
    """
    if default_value_str is None:
        return None
        
    # Handle boolean values
    if default_value_str.lower() == 'true':
        return True
    elif default_value_str.lower() == 'false':
        return False
    
    # Handle numeric values
    try:
        value = float(default_value_str)
        # Convert to int if it's a whole number
        if value.is_integer():
            return int(value)
        return value
    except ValueError:
        # If it's not a number, return as string
        # If the string is quoted, remove the quotes
        if (default_value_str.startswith('"') and default_value_str.endswith('"')) or \
           (default_value_str.startswith("'") and default_value_str.endswith("'")):
            return default_value_str[1:-1]
        return default_value_str

def parse_rego_file_metadata(file_path: str) -> RegoMetadata:
    """
    Parse a Rego file to extract required metrics and parameters.
    
    Args:
        file_path: Path to the Rego file
        
    Returns:
        RegoMetadata object containing required metrics and parameters
        
    Raises:
        FileNotFoundError: If the specified file doesn't exist
        Exception: If there's an error parsing the file
    """
    try:
        # Open with explicit UTF-8 encoding for cross-platform compatibility
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        logger.error(f"Rego file not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error reading Rego file {file_path}: {str(e)}")
        raise
    
    # Extract package name - allow for whitespace before and after
    package_match = re.search(r'^\s*package\s+([^\s]+)', content, re.MULTILINE)
    package_name = package_match.group(1) if package_match else ""
    if not package_name:
        logger.warning(f"No package name found in {file_path}")
    
    # Extract required metrics using findall for more direct extraction
    metrics = []
    metrics_section = re.search(r'^\s*#\s*RequiredMetrics:\s*\n((?:\s*#\s*-\s*[^\n]+\n)+)', content, re.MULTILINE)
    if metrics_section:
        # Extract all metric lines in one pass
        metric_matches = re.findall(r'^\s*#\s*-\s*(.+?)(?:\s*(?:#.*)?)?$', 
                                   metrics_section.group(1), 
                                   re.MULTILINE)
        metrics = [m.strip() for m in metric_matches]
    else:
        logger.debug(f"No RequiredMetrics section found in {file_path}")
    
    # Extract required parameters
    params = {}
    params_section = re.search(r'^\s*#\s*RequiredParams:\s*\n((?:\s*#\s*-\s*[^\n]+\n)+)', content, re.MULTILINE)
    if params_section:
        # Parse each parameter line
        param_pattern = r'^\s*#\s*-\s*([^\s(]+)(?:\s*\(default\s*([^)]+)\))?(?:\s*(?:#.*)?)?$'
        param_matches = re.findall(param_pattern, params_section.group(1), re.MULTILINE)
        
        for param_name, default_value_str in param_matches:
            params[param_name.strip()] = _convert_default_value(default_value_str.strip() if default_value_str else None)
    else:
        logger.debug(f"No RequiredParams section found in {file_path}")
    
    return RegoMetadata(
        required_metrics=metrics,
        required_params=params,
        file_path=file_path,
        package_name=package_name
    )
