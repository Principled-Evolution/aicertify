# EU AI Act Requirements to OPA Policy Mapping

This document provides a comprehensive mapping between the EU AI Act requirements and the corresponding OPA policies in the AICertify framework. It identifies existing policies and highlights areas where new policies need to be developed to ensure complete coverage of the EU AI Act requirements.

## Table of Contents

1. [Introduction](#introduction)
2. [Prohibited AI Practices](#prohibited-ai-practices)
3. [High-Risk AI Systems Requirements](#high-risk-ai-systems-requirements)
4. [Transparency Obligations](#transparency-obligations)
5. [General-Purpose AI Models](#general-purpose-ai-models)
6. [Governance and Compliance](#governance-and-compliance)
7. [Data and Data Governance](#data-and-data-governance)
8. [Human Oversight](#human-oversight)
9. [Cybersecurity and Technical Robustness](#cybersecurity-and-technical-robustness)
10. [Gaps and Recommendations](#gaps-and-recommendations)

## Introduction

The EU AI Act establishes a comprehensive regulatory framework for artificial intelligence systems based on a risk-based approach. This document maps each requirement from the EU AI Act to the corresponding OPA policy in the AICertify framework, following the policy structure outlined in `opa_policy_structure.md`.

The mapping uses the following structure:
- **Requirement**: The specific requirement from the EU AI Act
- **Article/Section**: The relevant article or section in the EU AI Act
- **Existing Policy**: The current OPA policy that addresses this requirement (if any)
- **Policy Path**: The path to the policy in the AICertify framework
- **Status**: Whether the requirement is fully covered, partially covered, or not covered
- **Recommended Action**: Suggestions for enhancing or creating policies to address gaps

## Prohibited AI Practices

| Requirement | Article/Section | Existing Policy | Policy Path | Status | Recommended Action |
|-------------|----------------|-----------------|-------------|--------|-------------------|
| Prohibition of manipulative or deceptive AI techniques | Art. 5(1)(a) | None | N/A | Not Covered | Create new policy at `international/eu_ai_act/v1/prohibited_practices/manipulation.rego` |
| Prohibition of exploitation of vulnerabilities | Art. 5(1)(b) | None | N/A | Not Covered | Create new policy at `international/eu_ai_act/v1/prohibited_practices/vulnerability_exploitation.rego` |
| Prohibition of social scoring | Art. 5(1)(c) | None | N/A | Not Covered | Create new policy at `international/eu_ai_act/v1/prohibited_practices/social_scoring.rego` |
| Prohibition of criminal risk assessment based solely on profiling | Art. 5(1)(d) | None | N/A | Not Covered | Create new policy at `international/eu_ai_act/v1/prohibited_practices/criminal_profiling.rego` |
| Prohibition of untargeted scraping for facial recognition databases | Art. 5(1)(e) | None | N/A | Not Covered | Create new policy at `international/eu_ai_act/v1/prohibited_practices/facial_recognition_scraping.rego` |
| Prohibition of emotion recognition in workplace/education | Art. 5(1)(f) | None | N/A | Not Covered | Create new policy at `international/eu_ai_act/v1/prohibited_practices/emotion_recognition.rego` |
| Prohibition of biometric categorization for protected characteristics | Art. 5(1)(g) | None | N/A | Not Covered | Create new policy at `international/eu_ai_act/v1/prohibited_practices/biometric_categorization.rego` |
| Prohibition of real-time remote biometric identification in public spaces | Art. 5(1)(h) | None | N/A | Not Covered | Create new policy at `international/eu_ai_act/v1/prohibited_practices/biometric_identification.rego` |

## High-Risk AI Systems Requirements

| Requirement | Article/Section | Existing Policy | Policy Path | Status | Recommended Action |
|-------------|----------------|-----------------|-------------|--------|-------------------|
| Risk Management System | Art. 9 | Risk Management | `international/eu_ai_act/v1/risk_management/risk_management.rego` | Fully Covered | Maintain and update as needed |
| Data and Data Governance | Art. 10 | Fairness (partial) | `international/eu_ai_act/v1/fairness/fairness.rego` | Partially Covered | Extend fairness policy or create dedicated data governance policy |
| Technical Documentation | Art. 11 | None | N/A | Not Covered | Create new policy at `international/eu_ai_act/v1/documentation/technical_documentation.rego` |
| Record-Keeping | Art. 12 | None | N/A | Not Covered | Create new policy at `international/eu_ai_act/v1/documentation/record_keeping.rego` |
| Transparency and Information Provision | Art. 13 | Transparency | `international/eu_ai_act/v1/transparency/transparency.rego` | Fully Covered | Maintain and update as needed |
| Human Oversight | Art. 14 | None | N/A | Not Covered | Create new policy at `international/eu_ai_act/v1/human_oversight/human_oversight.rego` |
| Accuracy, Robustness and Cybersecurity | Art. 15 | None | N/A | Not Covered | Create new policy at `international/eu_ai_act/v1/technical_robustness/robustness.rego` |
| Quality Management System | Art. 17 | None | N/A | Not Covered | Create new policy at `international/eu_ai_act/v1/quality_management/quality_management.rego` |
| Automatically Generated Logs | Art. 19 | None | N/A | Not Covered | Create new policy at `international/eu_ai_act/v1/documentation/automated_logs.rego` |
| Fundamental Rights Impact Assessment | Art. 27 | None | N/A | Not Covered | Create new policy at `international/eu_ai_act/v1/fundamental_rights/impact_assessment.rego` |

## Transparency Obligations

| Requirement | Article/Section | Existing Policy | Policy Path | Status | Recommended Action |
|-------------|----------------|-----------------|-------------|--------|-------------------|
| Disclosure of AI system nature | Art. 50 | Transparency | `international/eu_ai_act/v1/transparency/transparency.rego` | Partially Covered | Enhance transparency policy to explicitly cover disclosure requirements |
| Disclosure of AI-generated content | Art. 50 | None | N/A | Not Covered | Create new policy at `international/eu_ai_act/v1/transparency/content_disclosure.rego` |
| Labeling of deep fakes | Art. 50 | None | N/A | Not Covered | Create new policy at `international/eu_ai_act/v1/transparency/deep_fakes.rego` |

## General-Purpose AI Models

| Requirement | Article/Section | Existing Policy | Policy Path | Status | Recommended Action |
|-------------|----------------|-----------------|-------------|--------|-------------------|
| Classification of GPAI models with systemic risk | Art. 51 | None | N/A | Not Covered | Create new policy at `international/eu_ai_act/v1/gpai/systemic_risk_classification.rego` |
| Technical documentation for GPAI models | Art. 53 | None | N/A | Not Covered | Create new policy at `international/eu_ai_act/v1/gpai/technical_documentation.rego` |
| Transparency information for downstream providers | Art. 53 | None | N/A | Not Covered | Create new policy at `international/eu_ai_act/v1/gpai/downstream_transparency.rego` |

## Governance and Compliance

| Requirement | Article/Section | Existing Policy | Policy Path | Status | Recommended Action |
|-------------|----------------|-----------------|-------------|--------|-------------------|
| Conformity Assessment | Art. 43 | None | N/A | Not Covered | Create new policy at `international/eu_ai_act/v1/compliance/conformity_assessment.rego` |
| EU Declaration of Conformity | Art. 47 | None | N/A | Not Covered | Create new policy at `international/eu_ai_act/v1/compliance/declaration_conformity.rego` |
| CE Marking | Art. 48 | None | N/A | Not Covered | Create new policy at `international/eu_ai_act/v1/compliance/ce_marking.rego` |
| Registration in EU Database | Art. 49 | None | N/A | Not Covered | Create new policy at `international/eu_ai_act/v1/compliance/registration.rego` |
| Provider Obligations | Art. 16 | None | N/A | Not Covered | Create new policy at `international/eu_ai_act/v1/obligations/provider_obligations.rego` |
| Deployer Obligations | Art. 26 | None | N/A | Not Covered | Create new policy at `international/eu_ai_act/v1/obligations/deployer_obligations.rego` |
| Importer Obligations | Art. 23 | None | N/A | Not Covered | Create new policy at `international/eu_ai_act/v1/obligations/importer_obligations.rego` |
| Distributor Obligations | Art. 24 | None | N/A | Not Covered | Create new policy at `international/eu_ai_act/v1/obligations/distributor_obligations.rego` |

## Data and Data Governance

| Requirement | Article/Section | Existing Policy | Policy Path | Status | Recommended Action |
|-------------|----------------|-----------------|-------------|--------|-------------------|
| Data quality and governance | Art. 10 | Fairness (partial) | `international/eu_ai_act/v1/fairness/fairness.rego` | Partially Covered | Create dedicated policy at `international/eu_ai_act/v1/data_governance/data_quality.rego` |
| Training, validation, and testing data requirements | Art. 10 | None | N/A | Not Covered | Create new policy at `international/eu_ai_act/v1/data_governance/training_data.rego` |
| Bias monitoring and mitigation | Art. 10 | Fairness | `international/eu_ai_act/v1/fairness/fairness.rego` | Fully Covered | Maintain and update as needed |

## Human Oversight

| Requirement | Article/Section | Existing Policy | Policy Path | Status | Recommended Action |
|-------------|----------------|-----------------|-------------|--------|-------------------|
| Human oversight measures | Art. 14 | None | N/A | Not Covered | Create new policy at `international/eu_ai_act/v1/human_oversight/oversight_measures.rego` |
| Prevention of automation bias | Art. 14 | None | N/A | Not Covered | Create new policy at `international/eu_ai_act/v1/human_oversight/automation_bias.rego` |
| Human intervention capabilities | Art. 14 | None | N/A | Not Covered | Create new policy at `international/eu_ai_act/v1/human_oversight/intervention_capabilities.rego` |

## Cybersecurity and Technical Robustness

| Requirement | Article/Section | Existing Policy | Policy Path | Status | Recommended Action |
|-------------|----------------|-----------------|-------------|--------|-------------------|
| Accuracy requirements | Art. 15 | None | N/A | Not Covered | Create new policy at `international/eu_ai_act/v1/technical_robustness/accuracy.rego` |
| Robustness against errors | Art. 15 | None | N/A | Not Covered | Create new policy at `international/eu_ai_act/v1/technical_robustness/error_robustness.rego` |
| Cybersecurity measures | Art. 15 | None | N/A | Not Covered | Create new policy at `international/eu_ai_act/v1/technical_robustness/cybersecurity.rego` |

## Gaps and Recommendations

Based on the mapping above, the following key gaps have been identified in the current OPA policy coverage for EU AI Act compliance:

1. **Prohibited AI Practices**: No policies currently exist for any of the prohibited practices outlined in Article 5. This is a critical gap that should be addressed with high priority.

2. **Documentation Requirements**: Technical documentation, record-keeping, and automated logs requirements are not covered by existing policies.

3. **Human Oversight**: No policies exist for ensuring appropriate human oversight of AI systems as required by Article 14.

4. **General-Purpose AI Models**: The requirements for GPAI models, including those with systemic risk, are not covered.

5. **Governance and Compliance**: Conformity assessment, CE marking, and registration requirements are not addressed in the current policy structure.

### Recommended Implementation Strategy

1. **Phase 1 - Critical Gaps**: 
   - Develop policies for prohibited AI practices
   - Implement policies for risk management and transparency (already partially covered)
   - Create policies for human oversight

2. **Phase 2 - Compliance Framework**:
   - Develop policies for conformity assessment and registration
   - Implement policies for technical documentation and record-keeping
   - Create policies for provider and deployer obligations

3. **Phase 3 - Technical Requirements**:
   - Develop policies for accuracy, robustness, and cybersecurity
   - Implement policies for data governance
   - Create policies for GPAI models

4. **Phase 4 - Integration and Testing**:
   - Ensure all policies work together in a coherent framework
   - Test policies against real-world AI systems
   - Refine policies based on testing results

### Policy Composition Strategy

To leverage the composability of the OPA policy structure, the following approach is recommended:

1. **Create Common Libraries**: Develop common rules and functions in the `global/library` directory that can be reused across multiple policies.

2. **Leverage Global Policies**: Build EU AI Act-specific policies on top of the global policies for fairness, transparency, accountability, and toxicity.

3. **Use Versioning**: Implement proper versioning to allow for updates as the interpretation and implementation of the EU AI Act evolves.

4. **Implement Dependency Management**: Ensure that policy dependencies are properly managed and resolved by the PolicyLoader. 