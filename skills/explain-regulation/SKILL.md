---
name: explain-regulation
description: Walk through every Rego policy under a given regulatory framework and explain in plain English what each one checks. Use this when the user wants to understand what coverage a framework actually provides before running it.
argument-hint: "<framework name, e.g. eu_ai_act>"
---

# Explain Regulation

Produce a plain-English audit-grade summary of what a regulatory framework's policies enforce.

## Steps

1. **Resolve the framework directory** — locate it under `aicertify/opa_policies/`:
   - `international/<name>/v1/`
   - `industry_specific/<name>/v1/`
   - `operational/<name>/v1/`

   If not found, list available frameworks instead and stop.

2. **Enumerate policies** — list every `.rego` file in the directory (excluding `*_test.rego`).

3. **For each policy**:
   - Read the file.
   - Extract the `# METADATA` block (title, description, source link).
   - Identify the `default allow` (or equivalent) and the conditions under which it returns `true`.
   - Translate the rule into one or two plain-English sentences.

4. **Produce a structured output**:

   ```
   ## Framework: <name>

   **<policy_name>** — <one-line description>
   - **What it checks**: <plain-English rule logic>
   - **Source**: <link from metadata>
   - **Status**: ✅ active | 🚧 placeholder

   <repeat for each policy>

   ## Coverage Summary
   - Policies: N
   - Articles covered: <if discernible from metadata>
   - Gaps: <any obvious un-covered areas>
   ```

5. **Surface placeholders** — if a policy file has an empty body, only a default rule, or comments saying "TODO/Pending", explicitly flag it as placeholder in the output. Honesty here matters; auditors will read this summary.

## Notes

- Cross-link to the upstream [gopal](https://github.com/Principled-Evolution/gopal) policy if it exists. The `.rego` files in this repo are a vendored copy.
- Don't editorialize about whether the regulation is "good" — just describe what the policies check.
