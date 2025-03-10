# Parameterization Approach for Gopal OPA Policies

This document provides a step-by-step guide to help developers implement the **parameterization strategy** in their Gopal OPA policies. Under this approach, you store relevant thresholds (or other numeric values) in the OPA input object rather than hardcoding them in `.rego` code. The policy then reads these values at runtime, enabling flexible use with a variety of aggregator or evaluator pipelines (e.g., AICertify).

---

## 1. Overview

**Purpose**  
- Decouple numeric thresholds (e.g., fairness, toxicity) from the policy logic itself.  
- Preserve policy reusability across different scoring ranges (e.g., 0–1.0, 0–100).  
- Allow external systems like AICertify to override default policy thresholds by passing parameters in the input JSON.

**Scope**  
- Update your existing `.rego` file(s) to read thresholds from something like `input.params`.  
- Document an updated input JSON schema for OPA evaluation so external systems know exactly what keys to provide.

---

## 2. Updating the Rego Policy

Below is an example of how you might modify a simple policy file (`fairness.rego`) to support parameterization. In this example, we assume you want to compare a “fairness score” against a threshold:

```1:57:aicertify/opa_policies/global/v1/fairness/fairness.rego
# RequiredMetrics:
#   - fairness.score
#   - content_safety.toxicity_score
#
package global.v1.fairness

default allow := false

allow if {
    # Use parameterized threshold from input.params.fairness_threshold
    input.metrics.fairness.score >= object.get(input.params, "fairness_threshold", 0.8)
}

non_compliant if {
    # If fairness score is below threshold, it's non-compliant
    input.metrics.fairness.score < object.get(input.params, "fairness_threshold", 0.8)
}

# Any additional policy rules...
```

### Key Changes

1. **Parameter Usage**  
   Instead of a hardcoded numeric (e.g., `0.8`), the policy now retrieves the threshold with:
   ```rego
   object.get(input.params, "fairness_threshold", 0.8)
   ```
   The **third argument** in `object.get` (`0.8`) is a default if `input.params.fairness_threshold` is not supplied.

2. **No Hardcoded Logic**  
   By removing direct numeric references from the policy logic, you enable flexible usage for any pipeline or aggregator.

---

## 3. Updating the Input JSON Structure

To evaluate this policy with OPA, an external system (like AICertify) must provide the following JSON structure:

```json
{
  "metrics": {
    "fairness": {
      "score": 0.85
    },
    "content_safety": {
      "toxicity_score": 0.02
    }
  },
  "params": {
    "fairness_threshold": 0.8
  }
}
```

### Required Fields

1. **metrics**  
   - **fairness.score** (numeric): The actual fairness score produced by your evaluator.  
   - **content_safety.toxicity_score** (numeric): Shown here only as an example; optional if your policy references it.

2. **params**  
   - **fairness_threshold** (numeric): The threshold against which you compare the `fairness.score`.  
   - This key name (`fairness_threshold`) must match the string used in your `.rego` to read the parameter:
     ```rego
     object.get(input.params, "fairness_threshold", 0.8)
     ```

### Optional Fields

- You may add more parameters for additional rules. For example, `params.toxicity_threshold` if your policy also checks content-safety scores.  
- If a parameter is missing in `params`, the policy will fall back on the default value you specified (e.g., `0.8`).

---

## 4. Validation and Testing

1. **Local OPA Check**  
   - Ensure your `.rego` file is valid by running:
     ```bash
     opa check aicertify/opa_policies/global/v1/fairness/fairness.rego
     ```
   - Add any other `.rego` files if they import or reference this policy to resolve dependencies.

2. **Test With Sample Data**  
   - Create a JSON file (e.g., `test_input.json`) like the one above:
     ```json
     {
       "metrics": { "fairness": { "score": 0.75 } },
       "params": { "fairness_threshold": 0.8 }
     }
     ```
   - Evaluate with OPA:
     ```bash
     opa eval --input test_input.json --data aicertify/opa_policies/global/v1/fairness/fairness.rego "data.global.v1.fairness"
     ```
   - Check the `allow` and `non_compliant` results to confirm correct behavior.

---

## 5. Summary of Implementation

1. **Identify Hardcoded Thresholds**  
   - Locate each `.rego` rule that uses a numeric threshold or scale-based logic.

2. **Replace With `object.get(input.params, "key", default_value)`**  
   - Keep a sensible default that works if the user doesn’t provide anything in `input.params`.

3. **Update Documentation & Schemas**  
   - Document each parameter (e.g., `fairness_threshold`, `toxicity_threshold`) in a **params** object.  
   - Make sure your aggregator or external system (like AICertify) knows to supply that parameter.

4. **Validate**  
   - Use `opa check` and sample JSON input to ensure the policy still compiles and runs as expected.

---

## 6. Next Steps

- If you need more advanced logic (e.g., comparing multiple thresholds, picking an operator dynamically), consider using a small utility function in `.rego` or building a more elaborate schema under `params`.  
- Keep the naming consistent (`fairness_threshold`, `toxicity_threshold`, etc.) across your `.rego` files to maintain clarity.  
- Periodically review your defaults to ensure they still match any domain or regulatory requirements.

---

**End of Document**

# Parameterization Approach for Gopal OPA Policies

This document describes how to **parameterize** your `.rego` files and explicitly note both **metrics** and **required threshold parameters** at the file level. Keeping these items together helps users of Gopal (including those leveraging AICertify) clearly see which inputs must be supplied in the JSON data structure.

---

## 1. Including Threshold Params in the Policy Header

When you define **required metrics** in a comment block at the top of each `.rego` file, you can also include a **RequiredParams** section to list all threshold parameters. This ensures that developers reading the policy can quickly identify exactly which keys to supply in their `input` object.

For example:

```rego
# RequiredMetrics:
#   - fairness.score
#   - content_safety.toxicity_score
#
# RequiredParams:
#   - fairness_threshold
#
package global.v1.fairness

default allow := false

allow if {
    # Use parameterized threshold from input.params.fairness_threshold
    input.metrics.fairness.score >= object.get(input.params, "fairness_threshold", 0.8)
}
```

### Benefits of Inserting a `RequiredParams` Section

1. **Improves Clarity**: Policy authors and external users can easily see what numeric or boolean parameters must be passed in.  
2. **Guides Input Construction**: Tools like AICertify can parse the comment block and automatically ensure that the `params` object contains the required thresholds.  
3. **Minimizes Hardcoding**: By specifying “fairness_threshold” as a required parameter, you keep the logic flexible for any aggregator or pipeline.

---

## 2. Documenting the Updated Input JSON

Developers or automated tools should consult the policy’s `RequiredParams` list and ensure they pass the necessary values in the `input.params` object. For a policy referencing `fairness_threshold`, the minimal JSON might look like:

```json
{
  "metrics": {
    "fairness": {
      "score": 0.85
    },
    "content_safety": {
      "toxicity_score": 0.02
    }
  },
  "params": {
    "fairness_threshold": 0.8
  }
}
```

If your `.rego` file has **multiple** required parameters, include them similarly:

```json
{
  "metrics": {
    "fairness": { "score": 0.85 },
    "content_safety": { "toxicity_score": 0.02 }
  },
  "params": {
    "fairness_threshold": 0.8,
    "toxicity_threshold": 0.1
  }
}
```

---

## 3. Recommended Steps to Update Your Policies

1. **Add `RequiredParams` Section**  
   - At the top of each `.rego` file, in the same comment block as your `RequiredMetrics`, list any threshold parameters needed by that specific policy.
2. **Use `object.get` in Policy Rules**  
   - For each parameter reference, use `object.get(input.params, "your_param_name", default_value)` or an equivalent safe-access approach.  
   - Example:
     ```rego
     input.metrics.fairness.score >= object.get(input.params, "fairness_threshold", 0.8)
     ```
3. **Document the Default Value**  
   - In the comment block, mention any default threshold to guide the user on your policy’s fallback behavior:
     ```rego
     # RequiredParams:
     #   - fairness_threshold (default 0.8)
     ```
4. **Update External Docs**  
   - In your broader documentation, show how the “params” object must include these keys for successful evaluation.  

---

## 4. Example: Full `.rego` Snippet

Here’s a short example of a `.rego` file demonstrating a fairness check using a threshold parameter, with both **RequiredMetrics** and **RequiredParams** in the header:

```rego
# RequiredMetrics:
#   - fairness.score
#
# RequiredParams:
#   - fairness_threshold (default 0.8)
#
package global.v1.fairness

default allow := false

allow if {
    input.metrics.fairness.score >= object.get(input.params, "fairness_threshold", 0.8)
}

non_compliant if {
    input.metrics.fairness.score < object.get(input.params, "fairness_threshold", 0.8)
}
```

---

## 5. Validation & Best Practices

1. **opa check**  
   - Always validate your `.rego` policies:
     ```bash
     opa check path/to/your/policy/fairness.rego
     ```
2. **Reference the Comment Block**  
   - If you build custom tooling (e.g., AICertify scripts), parse the `# RequiredParams:` line(s) to ensure the `input.params` object is properly populated.  
3. **Use Meaningful Parameter Names**  
   - E.g., “fairness_threshold” is self-explanatory; names like “fthr” are cryptic.  
4. **Avoid Overstuffing**  
   - If a policy grows to require many parameters, consider whether it should be split into multiple policies or combined at a higher abstraction.

---

## 6. Conclusion

By co-locating **RequiredMetrics** and **RequiredParams** in your `.rego` file’s comment block, developers and integrators (like AICertify) can easily identify exactly which inputs must be supplied. This approach keeps your library **orthogonal**—you’re not hardcoding specific numeric values—and fosters clarity for any external system that needs to pass threshold data to **Gopal** OPA policies.