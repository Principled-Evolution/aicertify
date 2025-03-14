# AICertify Architecture and Flow Diagram

This document provides diagrams to help understand the architecture and flow of the AICertify library.

## Component Diagram

```mermaid
graph TB
    subgraph "User API"
        A[regulations.py]
        B[application.py]
    end
    
    subgraph "Core Services"
        C[api.py]
        D[evaluators]
        E[opa_core]
        F[report_generation]
    end
    
    subgraph "Data Models"
        G[models/contract.py]
        H[models/evaluation.py]
        I[models/report.py]
    end
    
    subgraph "OPA Policies"
        J[opa_policies]
    end
    
    A -->|loads| E
    A -->|selects| J
    B -->|creates| G
    B -->|calls| C
    C -->|uses| D
    C -->|uses| E
    C -->|generates| F
    D -->|creates| H
    F -->|creates| I
    E -->|evaluates using| J
```

## Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant Regulations as regulations.py
    participant Application as application.py
    participant API as api.py
    participant OPA as opa_core
    participant Evaluators as evaluators
    participant Report as report_generation
    
    User->>Regulations: create()
    Regulations->>OPA: load policies
    Regulations-->>User: RegulationSet
    
    User->>Regulations: add(regulation_name)
    Regulations->>OPA: find_matching_policy_folders()
    OPA-->>Regulations: matching folders
    Regulations-->>User: success
    
    User->>Application: create(name, model_info)
    Application-->>User: Application
    
    User->>Application: add_interaction(input, output)
    Application-->>User: success
    
    User->>Application: evaluate(regulations)
    Application->>API: aicertify_app_for_policy()
    API->>OPA: evaluate_policy_category()
    API->>Evaluators: evaluators for metrics
    Evaluators-->>API: evaluation results
    OPA-->>API: policy results
    API->>Report: generate report
    Report-->>API: report path
    API-->>Application: results and report path
    Application-->>User: evaluation results
    
    User->>Application: get_report()
    Application-->>User: report paths
```

## Implementation Notes

### Key Features

1. **Simple API**: Users only need to interact with `regulations` and `application` modules.
2. **Flexible Regulation Selection**: Users can select specific regulations to evaluate against.
3. **Rich Report Generation**: Comprehensive reports are generated in various formats.
4. **Extensible**: New regulations and evaluators can be added without changing the API.

### Using the Library

The AICertify library follows a simple workflow:

1. Create a regulations set
2. Add specific regulations to the set
3. Create an application
4. Add interactions to the application
5. Evaluate the application against regulations
6. Get the generated reports

### Example Implementation

See the `quickstart.py` file for a complete working example of using the AICertify library.

### Customization Options

- Specify report formats: markdown, PDF, or JSON
- Configure output directories for reports
- Add custom metadata to applications and interactions
- Select specific regulations based on your compliance needs 