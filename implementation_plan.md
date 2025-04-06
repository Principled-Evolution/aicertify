# Flexible Metric Extraction System Implementation Plan

## Overview
This document outlines the implementation plan for a flexible, registry-based metric extraction system for AICertify. The goal is to decouple metric extraction from specific data structures, making it easier to add new evaluators and metrics without modifying code in multiple places.

## Implementation Steps

1. [x] **Create new module for flexible extraction**
   - Create `aicertify/report_generation/flexible_extraction.py`
   - Implement core classes: `MetricExtractor`, utility functions

2. [x] **Implement configuration system**
   - Define `MetricGroup` class
   - Create path-based extractor functions
   - Implement configuration loading

3. [x] **Define default metric configurations**
   - Create configurations for existing metric types (fairness, toxicity, stereotype)
   - Ensure backward compatibility with current data structures

4. [x] **Create feature flag system**
   - Add configuration option to toggle between old and new extraction systems
   - Ensure both systems can run in parallel during transition

5. [x] **Update main extraction function**
   - Modify `extract_metrics` to use the registry-based system when enabled
   - Update `create_evaluation_report` to work with the new system

6. [x] **Implement plugin system for custom extractors**
   - Create registration mechanism for custom extractors
   - Document the extension process

7. [x] **Add unit tests**
   - Test core extraction functionality
   - Test with various data structures
   - Test configuration loading

8. [x] **Update documentation**
   - Document the new architecture
   - Create examples for adding new metrics and evaluators

9. [x] **Validate with real data**
   - Test with debug_report_generation.py
   - Test with debug_policy_evaluation.py
   - Compare results between old and new extraction systems
   - Verify metrics are correctly added to reports

10. [ ] **Final integration**
    - Enable the system by default (if validation is successful)
    - Update any remaining documentation
    - Create examples of adding custom metrics

## Progress Tracking

- **Step 1**: ✅ Completed - Created flexible_extraction.py with core classes and utility functions
- **Step 2**: ✅ Completed - Implemented configuration system with MetricGroup class and path-based extractors
- **Step 3**: ✅ Completed - Created default metric configurations for existing metric types
- **Step 4**: ✅ Completed - Created feature flag system to toggle between old and new extraction systems
- **Step 5**: ✅ Completed - Updated main extraction function to use the registry-based system when enabled
- **Step 6**: ✅ Completed - Implemented plugin system for custom extractors with examples
- **Step 7**: ✅ Completed - Added unit tests for the flexible extraction system
- **Step 8**: ✅ Completed - Created documentation for the flexible extraction system
- **Step 9**: ✅ Completed - Validated with real data using debug_report_generation.py, confirmed metrics match between legacy and flexible systems
- **Step 10**: Not started - Final integration

## Summary

The flexible metric extraction system has been successfully implemented and validated, providing a registry-based approach to metric extraction that decouples it from specific data structures. This makes it easier to add new evaluators and metrics without modifying code in multiple places.

Key features of the system include:
- Registry-based approach to metric extraction
- Path-based extraction from nested data structures
- Configuration-driven metric extraction
- Default configurations for common metric types
- Feature flags for gradual migration
- Plugin system for custom extractors

The system has been validated with real data using the debug_report_generation.py script. Both the legacy and flexible extraction systems now produce identical results for common metrics, with the flexible system also supporting additional metric types (Performance and Accuracy). The system is ready for final integration and can be enabled by default in AICertify using the `AICERTIFY_USE_FLEXIBLE_EXTRACTION` environment variable or programmatically using the `set_feature_flag` function.
