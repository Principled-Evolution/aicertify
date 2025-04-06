Key Requirements:
1. Simple and minimally intrusive integration for developers
2. Maintain orthogonality (separation of concerns)
3. Support for contract validation
4. Allow developers to select different OPA policies
5. Hide implementation details of evaluators from developers
6. Future-proof for adding new evaluators and policies

Looking at the example Loan-Application-Evaluator.py, I can see that it already has some contract generation code. Let's examine how it currently works:

1. It runs the loan evaluation session
2. It captures interactions in a list of dictionaries
3. It creates an AICertifyContract using `create_contract`
4. It validates the contract with `validate_contract`
5. It saves the contract with `save_contract`

But it doesn't actually run any evaluation or generate reports. I need to design an approach that builds on this pattern while keeping changes minimal.

Here's my proposed architecture:</think># AICertify Integration Architecture for AI Application Developers

## Current State Analysis

Looking at your codebase, I see three key components of the evaluation pipeline:

1. **Contract Generation** - Apps like `Loan-Application-Evaluator.py` already capture interactions and create `AiCertifyContract` objects
2. **Evaluation System** - Internal AICertify components that assess the contracts using various metrics
3. **OPA Policy Validation** - Applying specific compliance frameworks to evaluation results

## Proposed Developer Integration Workflow

For AI application developers, I recommend a minimal-friction approach with three simple steps:

### 1. Capture Interactions (Already Implemented)

Developers are already collecting interactions and creating contracts:

```python
captured_interactions.append({
    "input_text": question,
    "output_text": result.data.response,
    "metadata": {"agent": "LoanDecision"}
})

contract = create_contract(application_name, model_info, captured_interactions)
```

### 2. Request Evaluation

After creating and saving the contract, developers should be able to request evaluation with a single line:

```python
# Option 1: Evaluate from saved contract file
evaluation_result = await aicertify.evaluate_contract(
    contract_path=file_path,
    policy_category="eu_ai_act"  # Developer selects relevant policy
)

# Option 2: Evaluate directly from contract object
evaluation_result = await aicertify.evaluate_contract_object(
    contract=contract,
    policy_category="eu_ai_act"
)
```

### 3. Retrieve & Display Results (Optional)

Developers can access evaluation results and display or integrate them as needed:

```python
# Print summary of evaluation
print(f"Evaluation result: {evaluation_result['summary']}")

# Access report
if "report_path" in evaluation_result:
    print(f"Report generated at: {evaluation_result['report_path']}")
```

## Architectural Design Principles

The AICertify architecture should follow these principles to ensure minimal developer friction:

1. **Clean Interface Boundary**
   - Expose only what developers need: contract creation and evaluation
   - Keep all evaluator implementation details hidden

2. **Policy Selection Without Implementation Knowledge**
   - Developers select policies by name/category without needing to understand evaluator implementations
   - Policy selection should be simple strings or enums

3. **Progressive Enhancement**
   - Basic integration requires minimal code
   - Additional parameters for advanced users who need more control

4. **Orthogonal Concerns**
   - Contract creation is separate from evaluation
   - Evaluation is separate from policy validation
   - Report generation is separate from results

## Implementation Recommendations

To implement this developer-friendly approach:

1. **Create a Simple Entry Point Module**
   ```python
   # aicertify/api.py or aicertify/__init__.py
   async def evaluate_contract(contract_path: str, policy_category: str, **options) -> Dict[str, Any]:
       """One-line evaluation from a contract file path"""
       pass

   async def evaluate_contract_object(contract: AiCertifyContract, policy_category: str, **options) -> Dict[str, Any]:
       """One-line evaluation from a contract object"""
       pass
   ```

2. **Document Available Policies**
   - Provide clear documentation on available policy categories
   - Include examples for common use cases

3. **Streamline Import Structure**
   - Allow importing evaluation functions directly from main package
   - Eliminate need to navigate complex package structure

## Developer Documentation

The documentation should focus on these key points:

1. **Installation**
   ```
   pip install aicertify
   ```

2. **Integration Steps**
   - Capture app interactions
   - Create AICertify contract
   - Request evaluation with desired policy
   - Retrieve results

3. **Policy Selection Guide**
   - List of available policy categories with descriptions
   - Recommendations for different types of applications
   - Process for requesting new policies

4. **Examples**
   - Basic integration (3-5 lines of code)
   - Custom metadata integration
   - Advanced configuration options

## Benefits of This Approach

1. **Minimal Developer Effort** - Just 2-3 lines of code after contract creation
2. **Separation of Concerns** - Developers only need to know about contracts and policies
3. **Future-Proof** - New evaluators and metrics can be added without changing the API
4. **Framework Agnostic** - Works with any AI framework that can produce the right contract structure
