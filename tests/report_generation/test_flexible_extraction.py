"""
Unit tests for the flexible extraction system.

This module contains tests for the flexible metric extraction system,
ensuring that it correctly extracts metrics from evaluation results.
"""


from aicertify.models.evaluation import MetricValue
from aicertify.report_generation.flexible_extraction import (
    MetricExtractor,
    get_nested_value,
    create_path_extractor,
    MetricGroup,
    register_metrics_from_config,
    extract_metrics
)


def test_get_nested_value():
    """Test extracting nested values from dictionaries."""
    data = {"a": {"b": {"c": 42}}}
    assert get_nested_value(data, "a.b.c") == 42
    assert get_nested_value(data, "a.b.d") is None
    assert get_nested_value(data, "a.x.c") is None
    assert get_nested_value({}, "a.b.c") is None
    assert get_nested_value(None, "a.b.c") is None


def test_create_path_extractor():
    """Test creating path-based extractors."""
    data = {"metrics": {"fairness": {"score": 0.8}}}
    extractor = create_path_extractor(
        paths=["metrics.fairness.score"],
        metric_name="fairness_score",
        display_name="Fairness Score",
        default_value=0.0
    )
    
    metric = extractor(data)
    assert metric is not None
    assert metric.name == "fairness_score"
    assert metric.display_name == "Fairness Score"
    assert metric.value == 0.8
    
    # Test with multiple paths
    data = {"fairness_metrics": {"score": 0.8}}
    extractor = create_path_extractor(
        paths=["metrics.fairness.score", "fairness_metrics.score"],
        metric_name="fairness_score",
        display_name="Fairness Score",
        default_value=0.0
    )
    
    metric = extractor(data)
    assert metric is not None
    assert metric.value == 0.8
    
    # Test with missing value
    data = {"metrics": {"toxicity": {"score": 0.2}}}
    extractor = create_path_extractor(
        paths=["metrics.fairness.score"],
        metric_name="fairness_score",
        display_name="Fairness Score",
        default_value=0.0
    )
    
    metric = extractor(data)
    assert metric is not None
    assert metric.value == 0.0


def test_metric_group():
    """Test the MetricGroup class."""
    data = {
        "metrics": {
            "fairness": {
                "score": 0.8,
                "bias": 0.2
            }
        }
    }
    
    group = MetricGroup(
        name="fairness",
        display_name="Fairness Metrics",
        metrics_config=[
            {
                "name": "fairness_score",
                "display_name": "Fairness Score",
                "paths": ["metrics.fairness.score"],
                "default_value": 0.0
            },
            {
                "name": "bias",
                "display_name": "Bias",
                "paths": ["metrics.fairness.bias"],
                "default_value": 0.0
            }
        ]
    )
    
    metrics = group.extract_metrics(data)
    assert len(metrics) == 2
    assert metrics[0].name == "fairness_score"
    assert metrics[0].value == 0.8
    assert metrics[1].name == "bias"
    assert metrics[1].value == 0.2


def test_metric_extractor():
    """Test the MetricExtractor class."""
    # Clear the registry
    MetricExtractor._extractors = {}
    MetricExtractor._initialized = False
    
    def fairness_extractor(data):
        return [MetricValue(name="fairness", display_name="Fairness", value=0.8)]
    
    def toxicity_extractor(data):
        return [MetricValue(name="toxicity", display_name="Toxicity", value=0.2)]
    
    MetricExtractor.register("fairness", fairness_extractor)
    MetricExtractor.register("toxicity", toxicity_extractor)
    
    metrics = MetricExtractor.extract_all({})
    assert len(metrics) == 2
    assert "fairness" in metrics
    assert "toxicity" in metrics
    assert metrics["fairness"][0].value == 0.8
    assert metrics["toxicity"][0].value == 0.2


def test_register_metrics_from_config():
    """Test registering metrics from a configuration."""
    # Clear the registry
    MetricExtractor._extractors = {}
    MetricExtractor._initialized = False
    
    config = {
        "metric_groups": [
            {
                "name": "fairness",
                "display_name": "Fairness Metrics",
                "metrics": [
                    {
                        "name": "fairness_score",
                        "display_name": "Fairness Score",
                        "paths": ["metrics.fairness.score"],
                        "default_value": 0.0
                    }
                ]
            }
        ]
    }
    
    register_metrics_from_config(config)
    assert "fairness" in MetricExtractor._extractors
    
    data = {"metrics": {"fairness": {"score": 0.8}}}
    metrics = MetricExtractor._extractors["fairness"](data)
    assert len(metrics) == 1
    assert metrics[0].name == "fairness_score"
    assert metrics[0].value == 0.8


def test_extract_metrics():
    """Test the extract_metrics function."""
    # Clear the registry
    MetricExtractor._extractors = {}
    MetricExtractor._initialized = False
    
    config = {
        "metric_groups": [
            {
                "name": "fairness",
                "display_name": "Fairness Metrics",
                "metrics": [
                    {
                        "name": "fairness_score",
                        "display_name": "Fairness Score",
                        "paths": ["metrics.fairness.score"],
                        "default_value": 0.0
                    }
                ]
            },
            {
                "name": "toxicity",
                "display_name": "Toxicity Metrics",
                "metrics": [
                    {
                        "name": "toxicity_score",
                        "display_name": "Toxicity Score",
                        "paths": ["metrics.toxicity.score"],
                        "default_value": 0.0
                    }
                ]
            }
        ]
    }
    
    register_metrics_from_config(config)
    
    data = {
        "metrics": {
            "fairness": {"score": 0.8},
            "toxicity": {"score": 0.2}
        }
    }
    
    metrics = extract_metrics(data)
    assert len(metrics) == 2
    assert "fairness" in metrics
    assert "toxicity" in metrics
    assert metrics["fairness"][0].value == 0.8
    assert metrics["toxicity"][0].value == 0.2 