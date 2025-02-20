# **AICertify Contract Interface: Vision & Roadmap**

---

## **1. Vision**

The **core vision** for AICertify is to:
1. **Standardize** how autonomous and semi-autonomous AI systems (especially LLM-based) **report** their interactions and metadata via a **simple contract** (structured data).
2. **Enable** a variety of **evaluators** (LangFair bias/fairness, PII data checks, security, etc.) to parse these contracts offline or in near real-time.
3. **Feed** the evaluation results to **Open Policy Agent (OPA)** policies, generating an **assessment report** and an optional **certificate** of compliance or readiness.

**Why a Contract?**  
- Ensures **consistent** data is provided across diverse AI frameworks (Pydantic AI, LangChain, custom solutions).  
- Minimizes friction by **abstracting** the system’s internal workings behind a uniform Pydantic schema.  
- **Future-proofs** the pipeline for offline or online compliance checks, new evaluators, and new policy rules.

---

## **2. Phase 1: Pydantic Models & Developer-Implemented Contracts**

### **2.1 Overview**

- **Goal**: Provide a base **Pydantic** model (e.g., `AiCertifyContract`) for **LLM-based Python** apps to fill out after running any scenario(s).
- **Offline (Batch) Assessments**: Developers gather multiple interactions or scenarios, each producing a contract instance, which is then **batch-processed** by AICertify.

### **2.2 Key Deliverables**

1. **Core Pydantic Models**  
   - **`AiCertifyContract`**: High-level schema capturing `application_name`, `model_info`, `interactions`, `final_output`, and optional context.  
   - **`Interaction`**: Sub-model for user↔AI exchanges, ensuring each user prompt and AI response is captured with timestamps.  

2. **Developer Integration Guide**  
   - **Manual Approach**: A helper function or docs showing how to instantiate and validate the contract before submission to AICertify.  
   - **Validation**: Basic checks (non-empty fields, at least one interaction, etc.) performed via Pydantic.

3. **Offline “Batch Mode” Support**  
   - Provide a **CLI** or library function to **process** multiple contract files (JSON) at once.  
   - Integration with **evaluation** modules (PII detection, fairness checks, etc.) to run offline.  
   - Output an **aggregate** or per-file compliance result, which can later be mapped to OPA.

### **2.3 Release Scope**  
- **OSS Library**: `pip install aicertify` providing:
  1. **Models** (`AiCertifyContract`),  
  2. **Minimal** developer-facing helpers (`create_contract()`, `validate_contract()`),  
  3. **Batch aggregator** stub or CLI entry to unify multiple contracts.

### **2.4 Example Flow**

1. **Developer** runs their LLM app on N test scenarios.  
2. For each scenario, they **instantiate** an `AiCertifyContract` with relevant fields.  
3. All contract JSON files are passed to AICertify’s batch tool.  
4. The **evaluation** layer (LangFair, PII, etc.) is invoked by AICertify to produce a structured results object.  
5. Results are **mapped** to OPA policies, generating a final pass/fail compliance report.

---

## **3. Phase 2: Decorators & Enhanced Developer Experience**

### **3.1 Overview**

After the core contract model is stable, we’ll introduce **decorators** (or other syntactic sugar) to **automate** contract creation for simpler codebases. This ensures a **smooth developer experience** for standard use cases while retaining the **manual** approach for advanced or complex flows.

### **3.2 Key Enhancements**

1. **`@aicertify_contract` Decorator**  
   - Wraps user-defined functions (like “`run_app_scenario()`”) to intercept inputs and outputs, constructing the Pydantic contract behind the scenes.  
   - Minimizes boilerplate.

2. **Fallback**  
   - For edge cases or concurrency patterns that decorators cannot handle, the existing **manual approach** remains viable.

3. **Extended Validation Hooks**  
   - Configurable validations or pre-checks (e.g., must have at least 5 interactions, must not contain empty AI responses, etc.).

---

## **4. Future Phase: Online / Real-Time Assessments**

While **Phase 1** focuses on **offline** or batch usage, the contract design allows expansion to near **real-time** or continuous monitoring:

- **Streaming** new interactions as `AiCertifyContract` objects or partial logs.  
- **Aggregators** that maintain rolling windows of data for quick compliance checks.  
- **Performance** considerations for high-traffic systems.

However, real-time support and advanced concurrency are postponed until the **core** contract and batch pipeline are stable.

---

## **5. Interaction with Evaluators & OPA**

**Important**: Another team (the “evaluation team”) will build out the modules for:

1. **LangFair** bias/fairness checks,  
2. **PII** detection,  
3. **Security** scanning, etc.

**AICertify** orchestrates how the contract data is **fed** into these evaluators, then **collects** their results:

1. **Mapping** results into a structured “evaluation result” object.  
2. **Passing** that object into **OPA** policy rules (e.g., allow/deny if bias_score > threshold).  
3. **Generating** a final compliance or certification report, possibly signed or labeled.

Thus, the “evaluation” stage is **downstream** of the contract. The **focus** here is building the robust, consistent **input** schema that those evaluators can rely on.

---

## **6. Roadmap Summary**

1. **Phase 1** *(Initial OSS Release)*  
   - **Pydantic contract models**: `AiCertifyContract`, `Interaction`.  
   - **Offline batch** aggregator/CLI.  
   - **Developer manual integration** approach.  
   - Basic validations & JSON output for OPA.

2. **Phase 2** *(Post-Release Enhancements)*  
   - **Decorator** support to automate contract creation for simpler apps.  
   - Extended validations & partial data checks.  
   - Potential minimal real-time integration proof-of-concept.

3. **Future**  
   - **Full Real-Time** streaming support.  
   - Advanced concurrency, multi-LLM bench approach.  
   - Additional domain-specific expansions (logging security, encryption, data lineage).

---

## **7. Conclusion**

By **launching Phase 1** with the **pydantic-based contract** and **offline batch** approach, we lay the **foundation** for developers to easily produce consistent, validated data about their AI apps. This data then **unlocks** robust, multi-check compliance and OPA policy decisions. The **decorators** in a later phase streamline developer experience further, while future expansions bring continuous monitoring and real-time compliance to life.

**Next Steps**:
1. **Finalize** the `AiCertifyContract` and `Interaction` models.  
2. **Implement** a straightforward aggregator for multiple contract files.  
3. **Publish** v0.1.0 as OSS.  
4. Coordinate with the “evaluation team” to feed contract data into PII, fairness, security checks, culminating in an **OPA-based** final compliance report.