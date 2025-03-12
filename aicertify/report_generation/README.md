# AICertify Report Generation

This module provides functionality for generating evaluation reports from AICertify evaluation results.

## Flexible Metric Extraction System

The flexible metric extraction system is a registry-based approach to extracting metrics from evaluation results. It decouples metric extraction from specific data structures, making it easier to add new evaluators and metrics without modifying code in multiple places.

### Key Features

- **Registry-based approach**: Metric extractors are registered with a central registry, allowing different components to register extractors for specific metric types.
- **Path-based extraction**: Metrics are extracted from nested data structures using dot notation paths.
- **Configuration-driven**: Metric extraction is driven by configuration, making it easy to add new metrics without modifying code.
- **Default configurations**: Default configurations are provided for common metric types (fairness, toxicity, stereotype, performance, accuracy).
- **Feature flags**: Feature flags allow for gradual migration from the legacy extraction system to the flexible system.
- **Plugin system**: A plugin system allows for custom extractors to be registered.

### Usage

#### Basic Usage

To use the flexible extraction system, set the feature flag:

```python
from aicertify.report_generation.feature_flags import set_feature_flag

# Enable the flexible extraction system
set_feature_flag("use_flexible_extraction", True)

# Use the extraction functions as usual
from aicertify.report_generation.data_extraction import extract_metrics
metrics = extract_metrics(evaluation_result)
```

#### Adding Custom Metrics

To add custom metrics, create a configuration for your metric group:

```python
from aicertify.report_generation.metric_configs import DEFAULT_METRIC_CONFIGS

# Add a new metric group
DEFAULT_METRIC_CONFIGS["my_custom_group"] = {
    "display_name": "My Custom Metrics",
    "metrics": {
        "my_metric": {
            "paths": [
                "my_custom_group.my_metric",
                "metrics.my_custom_group.my_metric",
                "my_metric",  # Direct at root level
            ],
            "default_value": 0.0,
            "display_name": "My Metric"
        }
    }
}
```

#### Custom Extractors

For more complex extraction logic, you can register custom extractors:

```python
from aicertify.models.evaluation import MetricValue
from aicertify.report_generation.flexible_extraction import register_custom_extractor

def my_custom_extractor(evaluation_result):
    # Custom extraction logic
    metrics = []
    
    # Add metrics
    metrics.append(MetricValue(
        name="my_metric",
        display_name="My Metric",
        value=calculate_my_metric(evaluation_result)
    ))
    
    return metrics

# Register the custom extractor
register_custom_extractor("my_custom_group", my_custom_extractor)
```

### Configuration Format

The metric configuration format is as follows:

```python
{
    "metric_group_name": {
        "display_name": "Metric Group Display Name",
        "metrics": {
            "metric_name": {
                "paths": [
                    "path.to.metric",
                    "alternative.path.to.metric",
                ],
                "default_value": 0.0,
                "display_name": "Metric Display Name"
            }
        }
    }
}
```

### Feature Flags

The flexible extraction system can be enabled or disabled using feature flags:

```python
from aicertify.report_generation.feature_flags import set_feature_flag, get_feature_flag

# Enable the flexible extraction system
set_feature_flag("use_flexible_extraction", True)

# Check if the flexible extraction system is enabled
is_enabled = get_feature_flag("use_flexible_extraction")
```

You can also set the feature flag using an environment variable:

```bash
export AICERTIFY_USE_FLEXIBLE_EXTRACTION=1
```

## Legacy Extraction System

The legacy extraction system is still available and is used by default. It provides functions for extracting metrics from evaluation results using hardcoded paths.

To use the legacy extraction system, ensure the feature flag is disabled:

```python
from aicertify.report_generation.feature_flags import set_feature_flag

# Disable the flexible extraction system (use legacy)
set_feature_flag("use_flexible_extraction", False)
```

## Report Generation

The report generation functionality is provided by the `ReportGenerator` class, which generates Markdown reports from evaluation results.

```python
from aicertify.report_generation.report_generator import ReportGenerator
from aicertify.report_generation.data_extraction import create_evaluation_report

# Create an evaluation report
report = create_evaluation_report(evaluation_result, opa_results)

# Generate a Markdown report
report_generator = ReportGenerator()
markdown_content = report_generator.generate_markdown_report(report)

# Write the report to a file
with open("report.md", "w") as f:
    f.write(markdown_content)
``` 