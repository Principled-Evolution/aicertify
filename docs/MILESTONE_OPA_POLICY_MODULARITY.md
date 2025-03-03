# Milestone: OPA Policy Modularity & Externalization for First Release

## Goals
- **Future Safety:** Ensure our policies can eventually cover global, international, industry-specific, company/corporate, and DevSecOps/AIOps needs.
- **Keep It Simple:** For the first release, only the most significant verticals and standards are prioritized.
- **Clear Topology:** The folder structure must be obvious and self-evident to external viewers.
- **Easy to Appreciate & Maintain:** The solution should be straightforward so that others can easily contribute and the repository gains traction in OSS.
- **Externalization:** Evaluate the best option of hosting the policies in a separate OSS repository to boost visibility, cross marketing, and community contributions.

## Tasks and Done Criteria

### 1. Audit Existing OPA Policies and Identify Priority Verticals
- **Task Details:**
  - Review current OPA policies in AICertify.
  - Identify and compile policies corresponding to:
    - **EU AI Act** (@eu_ai_act)
    - **India Regulatory Framework** (@india)
    - **NIST AI Standard (AI-600-1)** (@nist.ai.600-1)
    - **Global Regulations** (@global-regulations-rated.md)
    - **Industry-Specific Guidelines** (@industry-specific-landscape.md)
- **Done Criteria:**
  - A prioritized list of policy modules is documented with inline references to the related files.
  - Team approval on the list of priority verticals.

### 2. Design the Modular Folder Structure
- **Task Details:**
  - Define a clear, modular directory structure that groups policies into:
    - **Global/General Policies**
    - **International Policies** (with subfolders such as `eu_ai_act/`, `india/`, and `nist/`)
    - **Industry-Specific Policies** (e.g., `bfs/`, `healthcare/`, `automotive/`)
  - **Proposed Structure Example:**
    ```
    opa_policies/
    ├── global/
    │   ├── global_compliance.rego
    │   └── trust_standards.rego
    ├── international/
    │   ├── eu_ai_act/
    │   │   ├── ai_act_policy.rego
    │   │   └── compliance_policy.rego
    │   ├── india/
    │   │   └── digital_india_policy.rego
    │   └── nist/
    │       └── nist_ai_600_1.rego
    └── industry_specific/
        ├── bfs/
        │   └── bfs_policy.rego
        ├── healthcare/
        │   └── healthcare_policy.rego
        └── automotive/
            └── automotive_policy.rego
    ```
- **Done Criteria:**
  - A clear folder structure is defined and documented.
  - The structure is reviewed and approved by the team.

### 3. Document Policy Organization with Diagrams
- **Task Details:**
  - Create a new documentation file (e.g., `opa_policy_structure.md`) that:
    - Explains the folder structure and policy grouping.
    - Uses diagrammatic representation (e.g., Mermaid diagrams) to illustrate the topology.
- **Done Criteria:**
  - `opa_policy_structure.md` exists with detailed explanations.
  - At least one Mermaid diagram is included. For example:
    ```mermaid
    graph TD
      A[opa_policies/] --> B[global/]
      A --> C[international/]
      A --> D[industry_specific/]
      C --> E[eu_ai_act/]
      C --> F[india/]
      C --> G[nist/]
      D --> H[bfs/]
      D --> I[healthcare/]
      D --> J[automotive/]
    ```
  - The documentation is clear and accessible for external contributors.

### 4. Evaluate Externalization Options for OPA Policies
- **Task Details:**
  - Research and document the approach to externalize the OPA policies to a separate OSS repository (e.g., `AICertify-Policies`).
  - Assess benefits such as:
    - Increased OSS visibility and potential GitHub stars.
    - Easier community contributions and cross marketing.
    - Better alignment with OPA community standards.
  - Draft initial guidelines and a README for the external policies repository.
- **Done Criteria:**
  - A plan document or preliminary repository skeleton is created.
  - Guidelines and instructions for integration with AICertify are documented.
  - A cross-reference in the main AICertify README or developer docs notes the external repository.

### 5. Review and Validate the Modularity
- **Task Details:**
  - Conduct a peer review of the new folder structure and documentation.
  - Run integration tests with AICertify to ensure that the policies are correctly referenced and applied.
- **Done Criteria:**
  - Peer review sign-off.
  - Integration tests pass successfully.
  - Documentation and structure are deemed easy to understand and maintain by external contributors.

## Milestone Completion Criteria
- All tasks are completed, with a clear and modular OPA policy structure documented.
- The folder topology is self-evident, showing clear segmentation of global, international, and industry-specific policies.
- Comprehensive documentation with diagrams is available to guide users.
- A plan for potential externalization is in place and cross-referenced in the main repository.
- Stakeholder approval is achieved and the milestone is signed off. 