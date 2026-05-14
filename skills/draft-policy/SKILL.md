---
name: draft-policy
description: Scaffold a new Rego policy file (with metadata, default rule, and a test sibling) for AICertify, following the project's authoring conventions. Use this when the user wants to add coverage for a new regulation, article, or organizational rule.
argument-hint: "<domain> <framework> <policy_name> [--upstream]"
---

# Draft Policy

Generate a new Rego policy + test file matching AICertify's conventions.

## Inputs

- **domain** — One of: `global`, `international`, `industry_specific`, `operational`.
- **framework** — Existing framework name (e.g. `eu_ai_act`) OR a new one. If new, prompt the user to confirm before creating the directory.
- **policy_name** — `snake_case` filename without `.rego` suffix.
- **--upstream** — Optional flag. If set, draft into [gopal](https://github.com/Principled-Evolution/gopal) instead of the vendored copy. **Strongly preferred** for any policy that should ship to all gopal consumers.

## Steps

1. **Decide repo** — if `--upstream`, target `/home/kapil/Projects/gopal/`. Otherwise the vendored copy at `aicertify/opa_policies/`. **Default recommendation: write upstream and vendor in.**

2. **Confirm directory layout** —
   ```
   <domain>/<framework>/v1/<policy_name>.rego
   <domain>/<framework>/v1/<policy_name>_test.rego
   ```
   Create the directory if it doesn't exist.

3. **Write the policy file** with this skeleton — fill in title, description, and source from the user's input:

   ```rego
   package <domain>.<framework>.v1.<policy_name>

   import data.helper_functions.reporting

   # METADATA
   # title: <one-line summary>
   # description: <what this rule enforces>
   # version: 1
   # source: <URL to the official regulation or standard>

   default allow := false

   allow if {
       # TODO: encode the rule. Reference fields like:
       #   input.system.name
       #   input.system.<your-field>
       true
   }

   report := reporting.compose_report(
       "<framework>.<policy_name>",
       allow,
       [{"name": "<metric_name>", "value": allow, "control_passed": allow}],
   )
   ```

4. **Write the test file**:

   ```rego
   package <domain>.<framework>.v1.<policy_name>_test

   import data.<domain>.<framework>.v1.<policy_name>

   test_allow_when_compliant if {
       <policy_name>.allow with input as {
           "system": {
               # TODO: shape the compliant input
           }
       }
   }

   test_deny_by_default if {
       not <policy_name>.allow with input as {}
   }
   ```

5. **Update the framework README** at `<domain>/<framework>/v1/README.md` to list the new policy. If the README doesn't exist, scaffold it with the standard source + disclaimer template.

6. **Validate** — run from the target repo root:
   ```bash
   opa check --ignore custom/ .
   regal lint --ignore-files custom/ .
   ```
   Surface any errors and offer to fix them.

7. **Remind the user**:
   - Fill in the TODO blocks with the actual rule logic and input shape.
   - Add `# METADATA` with a real `source:` URL — auditors will read this.
   - If drafted upstream in gopal, the next AICertify vendor sync will pull it in.
