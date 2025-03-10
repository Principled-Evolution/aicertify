"""
Flexible metric extraction system for AICertify.

This module provides a registry-based approach to metric extraction, allowing
for flexible and extensible extraction of metrics from evaluation results.
"""

import json
import logging
import os
from typing import Any, Callable, Dict, List, Optional, Union

from pydantic import BaseModel

# Import models from existing code
from aicertify.report_generation.report_models import MetricValue, PolicyResult

# Import default metric configurations
from aicertify.report_generation.metric_configs import get_default_metric_configs

logger = logging.getLogger(__name__)


class MetricExtractor:
    """
    Registry-based metric extraction system.
    
    This class provides a central registry for metric extractors, allowing
    different components to register extractors for specific metric types.
    """
    
    _extractors = {}
    _initialized = False
    
    @classmethod
    def register(cls, metric_type: str, extractor_fn: Callable):
        """
        Register an extractor function for a specific metric type.
        
        Args:
            metric_type: Type of metrics to extract (e.g., "fairness", "toxicity")
            extractor_fn: Function that takes an evaluation result and returns a list of MetricValue objects
        """
        cls._extractors[metric_type] = extractor_fn
        logger.debug(f"Registered extractor for metric type: {metric_type}")
    
    @classmethod
    def extract_all(cls, evaluation_result: Dict[str, Any]) -> Dict[str, List[MetricValue]]:
        """
        Extract all metrics from the evaluation result using registered extractors.
        
        Args:
            evaluation_result: Dictionary containing evaluation metrics
            
        Returns:
            Dictionary mapping metric group names to lists of MetricValue objects
        """
        # Ensure default extractors are registered
        if not cls._initialized:
            register_default_extractors()
        
        all_metrics = {}
        
        for metric_type, extractor_fn in cls._extractors.items():
            try:
                metrics = extractor_fn(evaluation_result)
                all_metrics[metric_type] = metrics
                logger.debug(f"Extracted {len(metrics)} metrics for {metric_type}")
            except Exception as e:
                logger.warning(f"Error extracting {metric_type} metrics: {e}")
                all_metrics[metric_type] = []
        
        return all_metrics


def get_nested_value(data: Dict[str, Any], path: str) -> Any:
    """
    Get a value from a nested dictionary using dot notation.
    
    Args:
        data: Dictionary to extract value from
        path: Dot-notation path to the value (e.g., "metrics.fairness.score")
        
    Returns:
        The value at the specified path, or None if not found
    """
    if not data or not isinstance(data, dict):
        return None
    
    parts = path.split('.')
    current = data
    
    for part in parts:
        if isinstance(current, dict) and part in current and current[part] is not None:
            current = current[part]
        else:
            return None
    
    return current


def create_path_extractor(
    paths: List[str], 
    metric_name: str, 
    display_name: str, 
    default_value: Optional[Any] = None
) -> Callable:
    """
    Create an extractor function that tries multiple paths to find a metric.
    
    Args:
        paths: List of dot-notation paths to try (e.g., ["metrics.fairness.score", "fairness_metrics.score"])
        metric_name: Name of the metric to extract
        display_name: Display name for the metric
        default_value: Default value if metric not found
        
    Returns:
        Function that extracts the metric from an evaluation result
    """
    def extractor(evaluation_result: Dict[str, Any]) -> Optional[MetricValue]:
        for path in paths:
            value = get_nested_value(evaluation_result, path)
            if value is not None:
                return MetricValue(name=metric_name, display_name=display_name, value=value)
        
        # If we get here, no path matched
        if default_value is not None:
            return MetricValue(name=metric_name, display_name=display_name, value=default_value)
        return None
    
    return extractor


class MetricGroup:
    """
    Configuration for a group of related metrics.
    
    This class represents a group of related metrics, such as fairness metrics
    or toxicity metrics, and provides methods for extracting those metrics
    from evaluation results.
    """
    
    def __init__(self, name: str, display_name: str, metrics_config: Optional[Dict[str, Any]] = None):
        """
        Initialize a metric group.
        
        Args:
            name: Name of the metric group (e.g., "fairness")
            display_name: Display name for the metric group (e.g., "Fairness Metrics")
            metrics_config: Dictionary of metric configurations
        """
        self.name = name
        self.display_name = display_name
        self.metrics_config = metrics_config or {}
    
    def extract_metrics(self, evaluation_result: Dict[str, Any]) -> List[MetricValue]:
        """
        Extract all metrics in this group from the evaluation result.
        
        Args:
            evaluation_result: Dictionary containing evaluation metrics
            
        Returns:
            List of MetricValue objects
        """
        metrics = []
        
        for metric_name, config in self.metrics_config.items():
            extractor = create_path_extractor(
                config["paths"],
                metric_name,
                config["display_name"],
                config.get("default_value")
            )
            
            metric = extractor(evaluation_result)
            if metric:
                metrics.append(metric)
        
        return metrics


def load_metric_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load metric configuration from a file or use defaults.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Dictionary containing metric configuration
    """
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading metric configuration from {config_path}: {e}")
    
    # Return empty configuration if no file provided or error loading
    return {"metric_groups": []}


def register_metrics_from_config(config: Dict[str, Any]) -> None:
    """
    Register metric extractors from configuration.
    
    Args:
        config: Dictionary containing metric configuration
    """
    for group_name, group_config in config.items():
        metric_group = MetricGroup(
            name=group_name,
            display_name=group_config["display_name"],
            metrics_config=group_config.get("metrics", {})
        )
        MetricExtractor.register(group_name, metric_group.extract_metrics)
        logger.info(f"Registered metric group: {group_name} with {len(group_config.get('metrics', {}))} metrics")


def register_default_extractors() -> None:
    """
    Register default metric extractors.
    
    This function registers extractors for the default metric types (fairness, toxicity, etc.)
    using the default configurations.
    """
    config = get_default_metric_configs()
    register_metrics_from_config(config)
    MetricExtractor._initialized = True
    logger.info("Registered default metric extractors")


def register_custom_extractor(metric_type: str, extractor_fn: Callable) -> None:
    """
    Register a custom metric extractor.
    
    Args:
        metric_type: Type of metrics to extract (e.g., "fairness", "toxicity")
        extractor_fn: Function that takes an evaluation result and returns a list of MetricValue objects
    """
    MetricExtractor.register(metric_type, extractor_fn)
    logger.info(f"Registered custom extractor for metric type: {metric_type}")


def extract_metrics(evaluation_result: Dict[str, Any]) -> Dict[str, List[MetricValue]]:
    """
    Extract all metrics from evaluation results using the registry.
    
    Args:
        evaluation_result: Dictionary containing evaluation metrics
        
    Returns:
        Dictionary mapping metric group names to lists of MetricValue objects
    """
    return MetricExtractor.extract_all(evaluation_result) 