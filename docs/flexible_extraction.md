# Flexible Metric Extraction System

## Overview

The Flexible Metric Extraction System is a registry-based approach to extracting metrics from evaluation results in AICertify. It provides a flexible and extensible way to extract metrics from various data structures, making it easier to add new evaluators and metrics without modifying code in multiple places.

## Key Features

- **Registry-based approach**: Metric extractors are registered with a central registry, allowing for easy extension.
- **Path-based extraction**: Metrics can be extracted from nested data structures using dot-notation paths.
- **Configuration-driven**: Metric extraction can be configured using JSON configuration files.
- **Default configurations**: Default configurations are provided for common metric types.
- **Feature flags**: The system can be enabled or disabled using feature flags.
- **Plugin system**: Custom extractors can be registered for new metric types.

## Architecture

The system consists of the following components:

1. **MetricExtractor**: A registry-based class that manages metric extractors and provides methods for extracting metrics.
2. **MetricGroup**: A class that represents a group of related metrics and provides methods for extracting those metrics.
3. **Path-based extraction**: Functions for extracting values from nested data structures using dot-notation paths.
4. **Configuration system**: Functions for loading and registering metric configurations.
5. **Feature flags**: Configuration options for enabling or disabling the system.
6. **Plugin system**: Mechanisms for registering custom extractors.

## Usage

### Enabling the System

The flexible extraction system can be enabled using the `AICERTIFY_USE_FLEXIBLE_EXTRACTION` environment variable:

```bash
export AICERTIFY_USE_FLEXIBLE_EXTRACTION=true
```

Alternatively, it can be enabled programmatically:

```python
from aicertify.report_generation.config import set_feature_flag

set_feature_flag("use_flexible_extraction", True)
```

### Using Default Configurations

The system comes with default configurations for common metric types:

- Fairness metrics
- Toxicity metrics
- Stereotype metrics
- Performance metrics
- Accuracy metrics

These configurations are automatically registered when the system is initialized.

### Creating Custom Extractors

Custom extractors can be created and registered in several ways:

#### 1. Using the MetricGroup class

```python
from aicertify.report_generation.flexible_extraction import MetricGroup, register_custom_extractor

# Create a metric group
metric_group = MetricGroup(
    name="custom_metrics",
    display_name="Custom Metrics",
    metrics_config=[
        {
            "name": "custom_metric",
            "display_name": "Custom Metric",
            "paths": ["metrics.custom.value", "custom_metrics.value"],
            "default_value": 0.0
        }
    ]
)

# Register the metric group
register_custom_extractor("custom_metrics", metric_group.extract_metrics)
```

#### 2. Using a custom function

```python
from aicertify.models.evaluation import MetricValue
from aicertify.report_generation.flexible_extraction import register_custom_extractor

def extract_custom_metrics(evaluation_result):
    metrics = []
    
    # Extract custom metrics
    if "custom_data" in evaluation_result:
        custom_data = evaluation_result["custom_data"]
        metrics.append(
            MetricValue(
                name="custom_metric",
                display_name="Custom Metric",
                value=custom_data.get("value", 0.0)
            )
        )
    
    return metrics

# Register the custom extractor
register_custom_extractor("custom_metrics", extract_custom_metrics)
```

#### 3. Using the helper function

```python
from aicertify.report_generation.custom_extractors import create_custom_extractor

create_custom_extractor(
    metric_type="custom_metrics",
    display_name="Custom Metrics",
    metrics_config=[
        {
            "name": "custom_metric",
            "display_name": "Custom Metric",
            "paths": ["metrics.custom.value", "custom_metrics.value"],
            "default_value": 0.0
        }
    ]
)
```

### Using Configuration Files

Metric configurations can be loaded from JSON files:

```python
from aicertify.report_generation.flexible_extraction import load_metric_config, register_metrics_from_config

# Load configuration from file
config = load_metric_config("path/to/config.json")

# Register metrics from configuration
register_metrics_from_config(config)
```

Example configuration file:

```json
{
  "metric_groups": [
    {
      "name": "custom_metrics",
      "display_name": "Custom Metrics",
      "metrics": [
        {
          "name": "custom_metric",
          "display_name": "Custom Metric",
          "paths": ["metrics.custom.value", "custom_metrics.value"],
          "default_value": 0.0
        }
      ]
    }
  ]
}
```

## Adding New Evaluators

When adding a new evaluator to AICertify, follow these steps to integrate it with the flexible extraction system:

1. **Define the metrics**: Identify the metrics that the evaluator will produce.
2. **Create a configuration**: Create a configuration for the metrics.
3. **Register the configuration**: Register the configuration with the system.

Example:

```python
from aicertify.report_generation.flexible_extraction import register_metrics_from_config

# Define the configuration
config = {
    "metric_groups": [
        {
            "name": "new_evaluator",
            "display_name": "New Evaluator Metrics",
            "metrics": [
                {
                    "name": "new_metric",
                    "display_name": "New Metric",
                    "paths": [
                        "metrics.new_evaluator.new_metric",
                        "new_evaluator_metrics.new_metric",
                        "new_evaluator.new_metric",
                        "new_metric"
                    ],
                    "default_value": 0.0
                }
            ]
        }
    ]
}

# Register the configuration
register_metrics_from_config(config)
```

## Best Practices

1. **Use descriptive names**: Use descriptive names for metric types and metrics.
2. **Provide multiple paths**: Provide multiple paths for each metric to handle different data structures.
3. **Set default values**: Set appropriate default values for metrics.
4. **Document metrics**: Document the metrics that your evaluator produces.
5. **Test extraction**: Test that your metrics can be extracted correctly.

## Troubleshooting

If metrics are not being extracted correctly, check the following:

1. **Data structure**: Ensure that the data structure matches the paths in the configuration.
2. **Registration**: Ensure that the extractor is registered correctly.
3. **Feature flag**: Ensure that the flexible extraction system is enabled.
4. **Logging**: Check the logs for any errors or warnings.

## Conclusion

The Flexible Metric Extraction System provides a flexible and extensible way to extract metrics from evaluation results in AICertify. By decoupling metric extraction from specific data structures, it makes it easier to add new evaluators and metrics without modifying code in multiple places. 