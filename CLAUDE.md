# Claude Code — Project Context for AICertify

> **Read [AGENTS.md](AGENTS.md) first.** This file inherits all of those instructions and only adds Claude Code-specific notes.

## What you're working on

**AICertify** evaluates AI applications against regulatory frameworks (EU AI Act, NIST AI RMF, +13 more) using [OPA](https://www.openpolicyagent.org/) policies from [gopal](https://github.com/Principled-Evolution/gopal). The deliverable is an audit-ready compliance report (PDF / Markdown / JSON / HTML).

## Fast orientation

When the user asks a question about the codebase, in order:

1. **For "how does the eval flow work?"** → read [examples/quickstart.py](examples/quickstart.py). It's the canonical user path.
2. **For "what's covered by regulation X?"** → look in `aicertify/opa_policies/<domain>/<framework>/v1/`.
3. **For "what does a report look like?"** → open one in `examples/outputs/`.
4. **For "what's the public Python API?"** → read `aicertify/__init__.py` — it's the surface contract.

## Conventions Claude Code should respect

- **Use TodoWrite** for multi-step tasks (this is the user's preferred tracking).
- **Run the quickstart** before claiming a feature works end-to-end. Type-check and tests verify code correctness; the quickstart verifies *user-facing* correctness.
- **When editing OPA policies in `aicertify/opa_policies/`**, remind the user that these are vendored from [gopal](https://github.com/Principled-Evolution/gopal) and the upstream copy should usually be edited first.
- **Reports** — when changing report templates, open the generated PDF (`examples/outputs/eu_ai_act/`) and inspect it visually. Don't assume rendering correctness from the code alone.

## Useful skills

This project ships Claude Code skills in [`skills/`](skills/). To register them, copy into your Claude Code skills directory:

```bash
mkdir -p ~/.claude/skills && cp -r skills/* ~/.claude/skills/
```

Available slash commands once registered:

- `/run-compliance-check` — Run the end-to-end quickstart and surface the generated report
- `/evaluate-contract` — Evaluate a user-supplied contract JSON against any supported framework
- `/explain-regulation` — Walk every policy in a framework directory and explain what it checks
- `/draft-policy` — Scaffold a new Rego policy with metadata, default rule, and a test sibling

See [`skills/README.md`](skills/README.md) for the full list and conventions.

## What NOT to do in this repo

- Don't run `python examples/quickstart.py` repeatedly without cleaning `reports/` — the directory accumulates artifacts.
- Don't add Python ≥3.13 syntax (project pins to 3.12).
- Don't switch package manager — poetry is canonical, `pip install -e .` works for users.
- Don't claim MCP-compatibility yet — an MCP server is on the roadmap, not shipped.

## Session etiquette

The author prefers terse, surgical responses. Present the plan first when ambiguous; ask before introducing new abstractions.
