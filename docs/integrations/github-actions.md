# Running AICertify in GitHub Actions

AICertify can run as a pull-request status check so that the same contract, evaluator configuration, and policy set used locally can also be evaluated in CI. This page shows how to adapt [`.github/workflows/example-aicertify.yaml`](../../.github/workflows/example-aicertify.yaml) into a required check.

## What you copy

| File | Where it goes | What it does |
| --- | --- | --- |
| [`.github/workflows/example-aicertify.yaml`](../../.github/workflows/example-aicertify.yaml) | `.github/workflows/ai-compliance.yaml` | Installs AICertify and OPA, evaluates a contract, uploads the report |
| [`examples/github-actions/gate.py`](../../examples/github-actions/gate.py) | anywhere the workflow can reach | Converts policy results into an exit code |

## Inputs

Three values control the example workflow. They are exposed as `workflow_dispatch` inputs for interactive testing; in a repository-specific workflow they can be fixed in `env:` instead.

| Input | Meaning | Default |
| --- | --- | --- |
| `contract` | Path to the contract JSON describing the AI system | `examples/customer-support-bot/input_contract.json` |
| `framework` | Framework to evaluate against: `eu_ai_act`, `uk`, `bfs`, `legal`, `nist`, … | `eu_ai_act` |
| `fail_on` | `any` fails the job when a policy denies; `none` reports without gating | `none` |

Run `aicertify explain <framework>` to list the fields read by the selected framework before creating the contract.

## Adopt it in three steps

**1. Begin with `fail_on: none`.**

A contract that omits required declarations or measured inputs will produce policy denials. Reporting without gating on the first run lets you inspect those gaps before making the check required.

**2. Populate the contract.**

```bash
aicertify explain eu_ai_act
aicertify init-contract --policy eu_ai_act > contract.json
```

`init-contract` writes the declared fields under `context` as `null`, nested into the shape read by the policies. Replace the values that apply to the system. A field left as `null` is omitted from policy input, so missing evidence remains missing rather than being converted into an explicit `false` value.

**3. Enable gating.**

After the contract and evaluator inputs represent the evidence you intend to enforce, set `fail_on: any`. Then configure the workflow job as a required status check under the repository's branch-protection settings.

## Two implementation details

### Check out the policy submodule

The GOPAL policy library is pinned at `aicertify/opa_policies` as a git submodule. Configure `actions/checkout` with `submodules: true`:

```yaml
- uses: actions/checkout@v4
  with:
    submodules: true
```

Without the submodule, the policy directory is empty and an evaluation can produce zero policy verdicts. `gate.py` maps zero verdicts to exit code 2 so that missing policy input cannot be reported as a passing compliance gate.

### Cache evaluator model downloads

Fairness and content-safety evaluators may download transformer models on first use. Caching the Hugging Face and Torch directories avoids repeating those downloads on warm CI runs:

```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.cache/huggingface
      ~/.cache/torch
    key: aicertify-models-${{ runner.os }}-${{ hashFiles('pyproject.toml') }}
```

## Exit codes

`gate.py` distinguishes policy denial from evaluation failure:

| Code | Meaning |
| --- | --- |
| 0 | Every policy passed, or `--fail-on none` is configured |
| 1 | At least one policy denied and `--fail-on any` is configured |
| 2 | The evaluation could not produce a valid set of policy verdicts |

Exit code 2 covers conditions such as a missing contract, an OPA failure, or an evaluation that produced no verdicts. Those conditions do not establish a policy result and therefore must not be folded into the passing case.

## Outputs

The example workflow produces:

- **A job-summary table** containing each policy and its verdict.
- **Pull-request annotations** for denied policies, including the reported reason.
- **`compliance-summary.json`** for downstream automation:

  ```json
  {
    "framework": "uk",
    "total": 6,
    "passed": 6,
    "failed": 0,
    "policies": [{ "name": "UK GDPR Automated Decision-Making (Articles 22A-22D)", "passed": true }]
  }
  ```

- **The generated report**, uploaded with `if: always()` so the artifact remains available when the gate fails.

## Evaluating more than one framework

Use a matrix when the same contract must be evaluated against multiple framework policy sets. `fail-fast: false` allows every framework to complete even when one produces a denial:

```yaml
strategy:
  fail-fast: false
  matrix:
    framework: [eu_ai_act, uk, global]
steps:
  # …
  - run: |
      python examples/github-actions/gate.py \
        --contract contract.json \
        --policy ${{ matrix.framework }} \
        --fail-on any \
        --summary-json compliance-summary-${{ matrix.framework }}.json
```

## When GOPAL alone is sufficient

If the required facts and metrics already exist and the workflow only needs Rego policy verdicts, the GOPAL bundles can be evaluated directly with OPA. See [GOPAL's GitHub Actions example](https://github.com/Principled-Evolution/gopal/tree/main/examples/github-actions).

Use the AICertify workflow when CI also needs application-contract handling, evaluator-produced metrics, or generated evidence reports around the policy evaluation.
