# EU AI Act Implementation Test Plan

This document outlines the comprehensive test plan for validating the EU AI Act compliance implementation in the AICertify framework. It covers all major components that need to be tested and provides a tracking mechanism for test results.

## Test Environment Setup

Before executing the tests, ensure the following prerequisites are met:

1. AICertify repository is cloned and up-to-date
2. Python environment is set up with all required dependencies installed
3. Required external services (if any) are configured and accessible
4. Test data directory exists under `examples/test_data/eu_ai_act/`

## Test Categories and Test Cases

### Category 1: Policy Loading and Validation

| Test ID | Description | Expected Result | Status | Notes |
|---------|-------------|-----------------|--------|-------|
| PL-01 | Verify all EU AI Act rego policies are found by policy loader | All policies under `eu_ai_act` folder are loaded | Pending | |
| PL-02 | Check that rego policies pass validation with `opa check` | No errors or warnings from `opa check` | Pending | |
| PL-03 | Verify policy folder mapping works with `policy_category="eu_ai_act"` | Policy category correctly maps to `international/eu_ai_act` | Pending | |
| PL-04 | Test policy loader's handling of placeholder policies | Placeholder policies are properly loaded and identified | Pending | |

### Category 2: ModelCard Interface

| Test ID | Description | Expected Result | Status | Notes |
|---------|-------------|-----------------|--------|-------|
| MC-01 | Create minimal valid ModelCard | ModelCard object created without errors | Pending | |
| MC-02 | Create comprehensive ModelCard with all fields | ModelCard object created with all fields populated | Pending | |
| MC-03 | Verify ModelCard validation (e.g., risk_category validation) | Invalid values raise appropriate validation errors | Pending | |
| MC-04 | Test helper function `create_model_card` | ModelCard created with required fields and optional kwargs | Pending | |
| MC-05 | Test `get_compliance_level` for different ModelCard completeness levels | Returns appropriate level ('minimal', 'partial', 'comprehensive') | Pending | |

### Category 3: Contract Integration

| Test ID | Description | Expected Result | Status | Notes |
|---------|-------------|-----------------|--------|-------|
| CI-01 | Integrate ModelCard with ModelInfo in AiCertifyContract | ModelInfo correctly stores ModelCard | Pending | |
| CI-02 | Test `create_contract_with_model_card` function | Contract created with ModelCard and proper context | Pending | |
| CI-03 | Verify `eu_ai_act` context extraction from ModelCard | ModelCard risk_category and relevant_articles in context | Pending | |
| CI-04 | Test contract loading with ModelCard from file | Contract loaded with ModelCard intact | Pending | |

### Category 4: Evaluator Integration

| Test ID | Description | Expected Result | Status | Notes |
|---------|-------------|-----------------|--------|-------|
| EI-01 | Test EU AI Act specific evaluators with contract | Evaluators run without errors | Pending | |
| EI-02 | Test focus area filtering in `evaluate_eu_ai_act_compliance` | Only specified evaluators are executed | Pending | |
| EI-03 | Verify evaluator outputs conform to expected schema | Outputs include required fields in standardized format | Pending | |
| EI-04 | Test evaluator threshold configuration | Thresholds properly affect compliance determination | Pending | |

### Category 5: OPA Policy Evaluation

| Test ID | Description | Expected Result | Status | Notes |
|---------|-------------|-----------------|--------|-------|
| OPA-01 | Test OPA evaluation with EU AI Act policies | OPA evaluation completes without errors | Pending | |
| OPA-02 | Verify OPA results structure for EU AI Act policies | Results include policy-specific compliance determinations | Pending | |
| OPA-03 | Test merging of evaluator results with OPA policies | Integrated results correctly combine both sources | Pending | |
| OPA-04 | Test policy evaluation with different risk categories | Risk category appropriately affects evaluation rigor | Pending | |

### Category 6: End-to-End Testing

| Test ID | Description | Expected Result | Status | Notes |
|---------|-------------|-----------------|--------|-------|
| E2E-01 | Run `debug_policy_evaluation_eu_ai_act.py` with test contract | Script executes without errors | Pending | |
| E2E-02 | Execute `EU_AI_Act_Compliance_Example.py` healthcare example | Healthcare example completes without errors | Pending | |
| E2E-03 | Execute `EU_AI_Act_Compliance_Example.py` finance example | Finance example completes without errors | Pending | |
| E2E-04 | Verify PDF report generation | PDF reports are generated with expected content | Pending | |
| E2E-05 | Test with non-compliant contract | Non-compliance correctly identified in results | Pending | |

### Category 7: Developer Experience

| Test ID | Description | Expected Result | Status | Notes |
|---------|-------------|-----------------|--------|-------|
| DX-01 | Verify developer guide examples work as documented | Examples execute without errors | Pending | |
| DX-02 | Test API usability with minimal configuration | API usable with reasonable defaults | Pending | |
| DX-03 | Verify error messages are helpful | Error messages provide clear guidance | Pending | |

## Test Execution Plan

1. Create test contracts with various levels of compliance for testing
2. Execute policy loading and validation tests (PL-* tests)
3. Test ModelCard interface (MC-* tests)
4. Test contract integration (CI-* tests)
5. Test evaluator integration (EI-* tests)
6. Test OPA policy evaluation (OPA-* tests)
7. Perform end-to-end testing (E2E-* tests)
8. Verify developer experience (DX-* tests)

## Test Data Preparation

The following test data should be prepared:

1. **Compliant Healthcare Contract**: A contract for a healthcare AI system with a comprehensive model card and interactions that comply with EU AI Act requirements.
2. **Non-Compliant Finance Contract**: A contract for a financial AI system with interactions that violate EU AI Act prohibitions (e.g., contains manipulative content).
3. **Minimal Model Card Contract**: A contract with only minimal model card information.
4. **High-Risk Contract**: A contract for an AI system explicitly marked as high-risk with the relevant model card fields.

## Test Result Tracking

For each test, update the Status column with one of:
- ✅ PASS: Test passed successfully
- ❌ FAIL: Test failed
- ⚠️ PARTIAL: Test partially passed with issues
- ⏳ PENDING: Test not yet executed

Add detailed notes about test execution, any issues encountered, and steps to reproduce failures in the Notes column.

## Issue Remediation

For any failed tests:
1. Document the exact nature of the failure
2. Identify the root cause
3. Implement fixes
4. Re-run the test to confirm the issue is resolved
5. Update the test status and notes

## Completion Criteria

The EU AI Act implementation is considered tested and validated when:
1. All tests have been executed
2. All tests have passed successfully (Status: PASS)
3. All identified issues have been fixed and verified 