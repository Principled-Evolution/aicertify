"""
Default metric configurations for AICertify.

This module provides default configurations for metric extraction, ensuring
backward compatibility with existing data structures while providing a flexible
foundation for future extensions.
"""

from typing import Dict, Any, List

# Fairness metrics configuration
FAIRNESS_METRICS = {
    "ftu_satisfied": {
        "paths": [
            "fairness_metrics.ftu_satisfied",
            "fairness.ftu_satisfied",
            "metrics.fairness.ftu_satisfied",
            "summary.fairness.ftu_satisfied",
        ],
        "default_value": False,
        "display_name": "FTU Satisfied"
    },
    "counterfactual_score": {
        "paths": [
            "fairness_metrics.counterfactual_score",
            "fairness.counterfactual_score",
            "metrics.fairness.counterfactual_score",
            "summary.fairness.counterfactual_score",
            "counterfactual_score",  # Direct at root level
            "phase1_results.results.fairness.details.counterfactual_score",  # Phase 1 evaluator results
        ],
        "default_value": 0.0,
        "display_name": "Counterfactual Score"
    },
    "stereotype_score": {
        "paths": [
            "fairness_metrics.stereotype_score",
            "fairness.stereotype_score",
            "metrics.fairness.stereotype_score",
            "summary.fairness.stereotype_score",
            "stereotype_score",  # Direct at root level
            "phase1_results.results.fairness.details.stereotype_score",  # Phase 1 evaluator results
        ],
        "default_value": 0.0,
        "display_name": "Stereotype Score"
    },
    "sentiment_bias": {
        "paths": [
            "fairness_metrics.sentiment_bias",
            "fairness_metrics.details.sentiment_bias",  # Nested in details
            "fairness.sentiment_bias",
            "fairness.details.sentiment_bias",  # Nested in details
            "metrics.fairness.sentiment_bias",
            "metrics.fairness.details.sentiment_bias",  # Nested in details
            "summary.fairness.sentiment_bias",
            "sentiment_bias",  # Direct at root level
            "phase1_results.results.fairness.details.sentiment_bias",  # Phase 1 evaluator results
        ],
        "default_value": 0.0,
        "display_name": "Sentiment Bias"
    },
    "race_word_count": {
        "paths": [
            "fairness_metrics.race_word_count",
            "fairness.race_word_count",
            "metrics.fairness.race_word_count",
            "summary.fairness.race_word_count",
        ],
        "default_value": 0,
        "display_name": "Race Word Count"
    },
    "gender_word_count": {
        "paths": [
            "fairness_metrics.gender_word_count",
            "fairness.gender_word_count",
            "metrics.fairness.gender_word_count",
            "summary.fairness.gender_word_count",
        ],
        "default_value": 0,
        "display_name": "Gender Word Count"
    },
    "combined_score": {
        "paths": [
            "fairness_metrics.combined_score",
            "fairness.combined_score",
            "metrics.fairness.combined_score",
            "summary.fairness.combined_score",
            "combined_score",  # Direct at root level
            "phase1_results.results.fairness.details.combined_score",  # Phase 1 evaluator results
        ],
        "default_value": 0.0,
        "display_name": "Combined Score"
    },
    "bleu_similarity": {
        "paths": [
            "fairness_metrics.bleu_similarity",
            "fairness_metrics.details.bleu_similarity",  # Nested in details
            "fairness.bleu_similarity",
            "fairness.details.bleu_similarity",  # Nested in details
            "metrics.fairness.bleu_similarity",
            "metrics.fairness.details.bleu_similarity",  # Nested in details
            "summary.fairness.bleu_similarity",
            "bleu_similarity",  # Direct at root level
            "phase1_results.results.fairness.details.bleu_similarity",  # Phase 1 evaluator results
        ],
        "default_value": 0.0,
        "display_name": "BLEU Similarity"
    },
    "rouge_similarity": {
        "paths": [
            "fairness_metrics.rouge_similarity",
            "fairness_metrics.details.rouge_similarity",  # Nested in details
            "fairness.rouge_similarity",
            "fairness.details.rouge_similarity",  # Nested in details
            "metrics.fairness.rouge_similarity",
            "metrics.fairness.details.rouge_similarity",  # Nested in details
            "summary.fairness.rouge_similarity",
            "rouge_similarity",  # Direct at root level
            "phase1_results.results.fairness.details.rouge_similarity",  # Phase 1 evaluator results
        ],
        "default_value": 0.0,
        "display_name": "ROUGE Similarity"
    },
    "gender_bias_detected": {
        "paths": [
            "fairness_metrics.gender_bias_detected",
            "fairness_metrics.details.gender_bias",  # Nested in details with different name
            "fairness.gender_bias_detected",
            "fairness.details.gender_bias",  # Nested in details with different name
            "metrics.fairness.gender_bias_detected",
            "metrics.fairness.details.gender_bias",  # Nested in details with different name
            "summary.fairness.gender_bias_detected",
            "gender_bias_detected",  # Direct at root level
            "gender_bias",  # Direct at root level with different name
            "phase1_results.results.fairness.details.gender_bias_detected",  # Phase 1 evaluator results
        ],
        "default_value": False,
        "display_name": "Gender Bias Detected"
    },
    "racial_bias_detected": {
        "paths": [
            "fairness_metrics.racial_bias_detected",
            "fairness_metrics.details.racial_bias",  # Nested in details with different name
            "fairness.racial_bias_detected",
            "fairness.details.racial_bias",  # Nested in details with different name
            "metrics.fairness.racial_bias_detected",
            "metrics.fairness.details.racial_bias",  # Nested in details with different name
            "summary.fairness.racial_bias_detected",
            "racial_bias_detected",  # Direct at root level
            "racial_bias",  # Direct at root level with different name
            "phase1_results.results.fairness.details.racial_bias_detected",  # Phase 1 evaluator results
        ],
        "default_value": False,
        "display_name": "Racial Bias Detected"
    },
}

# Toxicity metrics configuration
TOXICITY_METRICS = {
    "toxic_fraction": {
        "paths": [
            "content_safety.toxic_fraction",
            "toxicity.toxic_fraction",
            "metrics.toxicity.toxic_fraction",
            "summary.toxicity.toxic_fraction",
            "toxic_fraction",  # Direct at root level
            "content_safety.details.toxic_fraction",  # Nested in details
            "phase1_results.results.content_safety.details.toxic_fraction",  # Phase 1 evaluator results
        ],
        "default_value": 0.0,
        "display_name": "Toxic Fraction"
    },
    "max_toxicity": {
        "paths": [
            "content_safety.max_toxicity",
            "toxicity.max_toxicity",
            "metrics.toxicity.max_toxicity",
            "summary.toxicity.max_toxicity",
            "max_toxicity",  # Direct at root level
            "content_safety.details.max_toxicity",  # Nested in details
            "phase1_results.results.content_safety.details.max_toxicity",  # Phase 1 evaluator results
        ],
        "default_value": 0.0,
        "display_name": "Max Toxicity"
    },
    "toxicity_probability": {
        "paths": [
            "content_safety.toxicity_probability",
            "toxicity.toxicity_probability",
            "metrics.toxicity.toxicity_probability",
            "summary.toxicity.toxicity_probability",
            "toxicity_probability",  # Direct at root level
            "content_safety.details.toxicity_probability",  # Nested in details
            "phase1_results.results.content_safety.details.toxicity_probability",  # Phase 1 evaluator results
        ],
        "default_value": 0.0,
        "display_name": "Toxicity Probability"
    },
    "content_safety_score": {
        "paths": [
            "content_safety.score",
            "toxicity.content_safety_score",
            "metrics.toxicity.content_safety_score",
            "summary.toxicity.content_safety_score",
            "content_safety_score",  # Direct at root level
            "phase1_results.results.content_safety.score",  # Phase 1 evaluator results
        ],
        "default_value": 0.0,
        "display_name": "Content Safety Score"
    },
}

# Stereotype metrics configuration
STEREOTYPE_METRICS = {
    "stereotype_score": {
        "paths": [
            "fairness_metrics.stereotype_score",
            "stereotype.stereotype_score",
            "metrics.stereotype.stereotype_score",
            "summary.stereotype.stereotype_score",
            "stereotype_score",  # Direct at root level
            "phase1_results.results.fairness.details.stereotype_score",  # Phase 1 evaluator results
        ],
        "default_value": 0.0,
        "display_name": "Stereotype Score"
    },
    "gender_bias_detected": {
        "paths": [
            "fairness_metrics.gender_bias_detected",
            "stereotype.gender_bias_detected",
            "metrics.stereotype.gender_bias_detected",
            "summary.stereotype.gender_bias_detected",
            "gender_bias_detected",  # Direct at root level
            "phase1_results.results.fairness.details.gender_bias_detected",  # Phase 1 evaluator results
        ],
        "default_value": False,
        "display_name": "Gender Bias Detected"
    },
    "racial_bias_detected": {
        "paths": [
            "fairness_metrics.racial_bias_detected",
            "stereotype.racial_bias_detected",
            "metrics.stereotype.racial_bias_detected",
            "summary.stereotype.racial_bias_detected",
            "racial_bias_detected",  # Direct at root level
            "phase1_results.results.fairness.details.racial_bias_detected",  # Phase 1 evaluator results
        ],
        "default_value": False,
        "display_name": "Racial Bias Detected"
    },
    "bias_score": {
        "paths": [
            "fairness_metrics.bias_score",
            "stereotype.bias_score",
            "metrics.stereotype.bias_score",
            "summary.stereotype.bias_score",
            "bias_score",  # Direct at root level
        ],
        "default_value": 0.0,
        "display_name": "Bias Score"
    },
}

# Performance metrics configuration
PERFORMANCE_METRICS = {
    "latency_ms": {
        "paths": [
            "performance.latency_ms",
            "metrics.performance.latency_ms",
            "summary.performance.latency_ms",
            "latency_ms",  # Direct at root level
        ],
        "default_value": 0,
        "display_name": "Latency (ms)"
    },
    "tokens_per_second": {
        "paths": [
            "performance.tokens_per_second",
            "metrics.performance.tokens_per_second",
            "summary.performance.tokens_per_second",
            "tokens_per_second",  # Direct at root level
        ],
        "default_value": 0,
        "display_name": "Tokens Per Second"
    },
    "memory_usage_mb": {
        "paths": [
            "performance.memory_usage_mb",
            "metrics.performance.memory_usage_mb",
            "summary.performance.memory_usage_mb",
            "memory_usage_mb",  # Direct at root level
        ],
        "default_value": 0,
        "display_name": "Memory Usage (MB)"
    },
}

# Accuracy metrics configuration
ACCURACY_METRICS = {
    "precision": {
        "paths": [
            "accuracy.precision",
            "metrics.accuracy.precision",
            "summary.accuracy.precision",
            "precision",  # Direct at root level
        ],
        "default_value": 0.0,
        "display_name": "Precision"
    },
    "recall": {
        "paths": [
            "accuracy.recall",
            "metrics.accuracy.recall",
            "summary.accuracy.recall",
            "recall",  # Direct at root level
        ],
        "default_value": 0.0,
        "display_name": "Recall"
    },
    "f1_score": {
        "paths": [
            "accuracy.f1_score",
            "metrics.accuracy.f1_score",
            "summary.accuracy.f1_score",
            "f1_score",  # Direct at root level
        ],
        "default_value": 0.0,
        "display_name": "F1 Score"
    },
}

# Combined metric configurations
DEFAULT_METRIC_CONFIGS = {
    "fairness": {
        "display_name": "Fairness Metrics",
        "metrics": FAIRNESS_METRICS
    },
    "toxicity": {
        "display_name": "Toxicity Metrics",
        "metrics": TOXICITY_METRICS
    },
    "stereotype": {
        "display_name": "Stereotype Metrics",
        "metrics": STEREOTYPE_METRICS
    },
    "performance": {
        "display_name": "Performance Metrics",
        "metrics": PERFORMANCE_METRICS
    },
    "accuracy": {
        "display_name": "Accuracy Metrics",
        "metrics": ACCURACY_METRICS
    }
}

def get_default_metric_configs():
    """
    Get the default metric configurations.
    
    Returns:
        dict: The default metric configurations.
    """
    return DEFAULT_METRIC_CONFIGS 