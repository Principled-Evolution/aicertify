# EU AI Act Rego Policy Reference List

This document outlines the reference list of EU AI Act-related rego policy files in the AICertify framework. It was derived from the analysis in [eu_ai_act_opa_policy_mapping.md](../docs/eu_ai_act_opa_policy_mapping.md) and our repository search. This list serves as the definitive reference for Task 1.1 and informs subsequent tasks such as formatting/validation (Task 1.2) and policy implementation (Task 1.3).

## Existing Policies (Realistic Implementations)

- **Fairness Policy**
  - **Path:** `aicertify/opa_policies/international/eu_ai_act/v1/fairness/fairness.rego`
  - **Description:** Implements fairness aspects including bias monitoring; partially covers data governance requirements.

- **Transparency Policy**
  - **Path:** `aicertify/opa_policies/international/eu_ai_act/v1/transparency/transparency.rego`
  - **Description:** Implements transparency requirements; covers disclosure of AI system nature and content where applicable.

- **Risk Management Policy**
  - **Path:** `aicertify/opa_policies/international/eu_ai_act/v1/risk_management/risk_management.rego`
  - **Description:** Implements risk management system requirements for high-risk AI systems.

- **Manipulation Policy**
  - **Path:** `aicertify/opa_policies/international/eu_ai_act/v1/prohibited_practices/manipulation.rego`
  - **Description:** Implements prohibition of manipulative or deceptive AI techniques.

## Recommended / Gap Policies to be Developed

Based on the mapping analysis, the following policies have been identified as gaps. For policies that align with evaluator support, realistic, detailed compliance logic should be implemented. For those without corresponding evaluators, placeholders (similar to `diagnostic_safety.rego` for healthcare) will be used.

### Prohibited Practices

- **Vulnerability Exploitation Policy**
  - **Path:** `aicertify/opa_policies/international/eu_ai_act/v1/prohibited_practices/vulnerability_exploitation.rego`

- **Social Scoring Policy**
  - **Path:** `aicertify/opa_policies/international/eu_ai_act/v1/prohibited_practices/social_scoring.rego`

- **Criminal Profiling Policy**
  - **Path:** `aicertify/opa_policies/international/eu_ai_act/v1/prohibited_practices/criminal_profiling.rego`

- **Facial Recognition Scraping Policy**
  - **Path:** `aicertify/opa_policies/international/eu_ai_act/v1/prohibited_practices/facial_recognition_scraping.rego`

- **Emotion Recognition Policy**
  - **Path:** `aicertify/opa_policies/international/eu_ai_act/v1/prohibited_practices/emotion_recognition.rego`

- **Biometric Categorization Policy**
  - **Path:** `aicertify/opa_policies/international/eu_ai_act/v1/prohibited_practices/biometric_categorization.rego`

- **Biometric Identification Policy**
  - **Path:** `aicertify/opa_policies/international/eu_ai_act/v1/prohibited_practices/biometric_identification.rego`

### High-Risk AI Systems and Documentation

- **Technical Documentation Policy**
  - **Path:** `aicertify/opa_policies/international/eu_ai_act/v1/documentation/technical_documentation.rego`

- **Record-Keeping Policy**
  - **Path:** `aicertify/opa_policies/international/eu_ai_act/v1/documentation/record_keeping.rego`

- **Automated Logs Policy**
  - **Path:** `aicertify/opa_policies/international/eu_ai_act/v1/documentation/automated_logs.rego`

- **Human Oversight Policy**
  - **Path:** `aicertify/opa_policies/international/eu_ai_act/v1/human_oversight/human_oversight.rego`

- **Technical Robustness Policy**
  - **Path:** `aicertify/opa_policies/international/eu_ai_act/v1/technical_robustness/robustness.rego`

### General-Purpose AI Models

- **Systemic Risk Classification Policy**
  - **Path:** `aicertify/opa_policies/international/eu_ai_act/v1/gpai/systemic_risk_classification.rego`

- **GPAI Technical Documentation Policy**
  - **Path:** `aicertify/opa_policies/international/eu_ai_act/v1/gpai/technical_documentation.rego`

- **Downstream Transparency Policy**
  - **Path:** `aicertify/opa_policies/international/eu_ai_act/v1/gpai/downstream_transparency.rego`

### Governance and Compliance

- **Conformity Assessment Policy**
  - **Path:** `aicertify/opa_policies/international/eu_ai_act/v1/compliance/conformity_assessment.rego`

- **EU Declaration of Conformity Policy**
  - **Path:** `aicertify/opa_policies/international/eu_ai_act/v1/compliance/declaration_conformity.rego`

- **CE Marking Policy**
  - **Path:** `aicertify/opa_policies/international/eu_ai_act/v1/compliance/ce_marking.rego`

- **Registration Policy**
  - **Path:** `aicertify/opa_policies/international/eu_ai_act/v1/compliance/registration.rego`

- **Provider Obligations Policy**
  - **Path:** `aicertify/opa_policies/international/eu_ai_act/v1/obligations/provider_obligations.rego`

- **Deployer Obligations Policy**
  - **Path:** `aicertify/opa_policies/international/eu_ai_act/v1/obligations/deployer_obligations.rego`

- **Importer Obligations Policy**
  - **Path:** `aicertify/opa_policies/international/eu_ai_act/v1/obligations/importer_obligations.rego`

- **Distributor Obligations Policy**
  - **Path:** `aicertify/opa_policies/international/eu_ai_act/v1/obligations/distributor_obligations.rego`

### Data and Data Governance

- **Data Quality Policy**
  - **Path:** `aicertify/opa_policies/international/eu_ai_act/v1/data_governance/data_quality.rego`

- **Training Data Policy**
  - **Path:** `aicertify/opa_policies/international/eu_ai_act/v1/data_governance/training_data.rego`

## Next Steps

This document serves as the reference for Task 1.1: Identification and listing of EU AI Act rego policy files. Subsequent tasks will address formatting and validation (Task 1.2) and implementation (Task 1.3) according to whether realistic compliance logic or placeholder policies are required.

---

**Senior Developer Note:**
This reference list was constructed in alignment with our overall integration plan for EU AI Act support in AICertify, ensuring that our policy coverage is comprehensive and consistent with the guidance provided by the mapping document. 