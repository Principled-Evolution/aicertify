"""
Custom metric extractors for AICertify.

This module provides examples and utilities for creating and registering
custom metric extractors for the AICertify report generation system.
"""

import logging
from typing import Dict, Any, List

from aicertify.models.evaluation import MetricValue
from aicertify.report_generation.flexible_extraction import (
    register_custom_extractor,
    MetricGroup
)

logger = logging.getLogger(__name__)


def create_custom_extractor(
    metric_type: str,
    display_name: str,
    metrics_config: List[Dict[str, Any]]
) -> None:
    """
    Create and register a custom metric extractor.
    
    Args:
        metric_type: Type of metrics to extract (e.g., "llm_performance")
        display_name: Display name for the metric group (e.g., "LLM Performance Metrics")
        metrics_config: List of metric configurations
    """
    metric_group = MetricGroup(
        name=metric_type,
        display_name=display_name,
        metrics_config=metrics_config
    )
    
    register_custom_extractor(metric_type, metric_group.extract_metrics)
    logger.info(f"Registered custom extractor for {metric_type}")


# Example: Custom LLM Performance Metrics Extractor
def register_llm_performance_metrics() -> None:
    """
    Register a custom extractor for LLM performance metrics.
    
    This is an example of how to create and register a custom extractor
    for a new type of metrics.
    """
    create_custom_extractor(
        metric_type="llm_performance",
        display_name="LLM Performance Metrics",
        metrics_config=[
            {
                "name": "tokens_per_second",
                "display_name": "Tokens Per Second",
                "paths": [
                    "metrics.llm_performance.tokens_per_second",
                    "llm_performance.tokens_per_second",
                    "tokens_per_second"
                ],
                "default_value": 0
            },
            {
                "name": "prompt_tokens",
                "display_name": "Prompt Tokens",
                "paths": [
                    "metrics.llm_performance.prompt_tokens",
                    "llm_performance.prompt_tokens",
                    "prompt_tokens"
                ],
                "default_value": 0
            },
            {
                "name": "completion_tokens",
                "display_name": "Completion Tokens",
                "paths": [
                    "metrics.llm_performance.completion_tokens",
                    "llm_performance.completion_tokens",
                    "completion_tokens"
                ],
                "default_value": 0
            },
            {
                "name": "total_tokens",
                "display_name": "Total Tokens",
                "paths": [
                    "metrics.llm_performance.total_tokens",
                    "llm_performance.total_tokens",
                    "total_tokens"
                ],
                "default_value": 0
            }
        ]
    )


# Example: Custom Function-Based Extractor
def extract_custom_metrics(evaluation_result: Dict[str, Any]) -> List[MetricValue]:
    """
    Extract custom metrics using a function-based approach.
    
    This is an example of how to create a custom extractor function
    that uses custom logic to extract metrics.
    
    Args:
        evaluation_result: Dictionary containing evaluation metrics
        
    Returns:
        List of MetricValue objects
    """
    metrics = []
    
    # Example: Calculate a derived metric
    if "response_times" in evaluation_result:
        response_times = evaluation_result["response_times"]
        if isinstance(response_times, list) and response_times:
            avg_response_time = sum(response_times) / len(response_times)
            metrics.append(
                MetricValue(
                    name="avg_response_time",
                    display_name="Average Response Time (ms)",
                    value=avg_response_time
                )
            )
    
    # Example: Extract a nested metric with custom logic
    if "model_info" in evaluation_result:
        model_info = evaluation_result["model_info"]
        if isinstance(model_info, dict):
            # Extract model name
            if "name" in model_info:
                metrics.append(
                    MetricValue(
                        name="model_name",
                        display_name="Model Name",
                        value=model_info["name"]
                    )
                )
            
            # Extract model version
            if "version" in model_info:
                metrics.append(
                    MetricValue(
                        name="model_version",
                        display_name="Model Version",
                        value=model_info["version"]
                    )
                )
    
    return metrics


def register_all_custom_extractors() -> None:
    """
    Register all custom extractors.
    
    This function can be called during application initialization
    to register all custom extractors.
    """
    # Register LLM performance metrics extractor
    register_llm_performance_metrics()
    
    # Register function-based custom extractor
    register_custom_extractor("custom", extract_custom_metrics)
    
    logger.info("Registered all custom extractors") 