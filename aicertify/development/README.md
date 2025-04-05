# AICertify Development Scripts

This directory contains development and debugging scripts that are not part of the main AICertify API but are useful for development and testing purposes.

## Debug Scripts

- `debug_policy_evaluation.py`: Debug script for testing policy evaluation without full application integration
- `debug_policy_evaluation_eu_ai_act.py`: Debug script specific to EU AI Act policy evaluation
- `debug_report_generation.py`: Debug script for testing the report generation system

## Dependency-Specific Testing Scripts

- `check_langfair_api.py`: Script for testing LangFair API integration
- `test_deepeval_directly.py`: Script for testing DeepEval integration directly
- `test_deepeval_toxicity.py`: Script for testing DeepEval toxicity evaluation

## Usage Notes

These scripts are intended for development and debugging purposes only. They may not follow the same API patterns as the main AICertify API and may not be maintained with the same level of backward compatibility.

For production use, please refer to the examples in the `/examples` directory, particularly `quickstart.py`, which demonstrates the current recommended API approach.
