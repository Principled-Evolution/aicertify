# AICertify Documentation

> **Looking for an overview?** Start with the [README](../README.md) — it covers value prop, quickstart, regulatory coverage, and a comparison vs alternatives.

The documentation here is organized along [Diátaxis](https://diataxis.fr/) lines: tutorials get you running, how-tos solve specific problems, reference describes the API, explanation explores design.

## 🎓 Tutorials — get from zero to a working compliance report

- [Quickstart](../examples/quickstart.py) — clone, install, run, inspect the report. ~5 minutes.
- [Sample contract](../examples/sample_contract.json) — the JSON shape a real contract takes.
- [Examples README](../examples/README.md) — index of all shipped examples and their pre-generated outputs.

## 🛠️ How-To Guides — solve a specific problem

- [Run a compliance check against a custom contract](../skills/evaluate-contract/SKILL.md) (Claude Code skill)
- [Add coverage for a new regulation](../skills/draft-policy/SKILL.md) (Claude Code skill)
- [Understand what a framework's policies enforce](../skills/explain-regulation/SKILL.md) (Claude Code skill)
- [Generate a report in PDF / Markdown / JSON / HTML](../examples/quickstart.py) — see the `report_format` argument.

## 📚 Reference — look up specific names

- [Python API](../aicertify/__init__.py) — the public surface re-exported from the package root.
- [CLI](../aicertify/cli.py) — `python -m aicertify.cli` flags and behavior. See also [README#cli](../README.md#cli).
- [Regulatory coverage table](../README.md#regulatory-coverage) — every framework with its policy count.
- [pyproject.toml](../pyproject.toml) — metadata, dependencies, entry points.
- [CHANGELOG](../CHANGELOG.md) — release history.

## 💡 Explanation — understand the design

- [Project overview](../PROJECT_OVERVIEW.md) — the long-form architectural narrative.
- [AGENTS.md](../AGENTS.md) — how AI coding agents (and humans) should work in the repo.
- [Why policy-as-code?](../README.md#why-aicertify) — the differentiation argument.

## 🤝 Contributing & community

- [CONTRIBUTING.md](../CONTRIBUTING.md)
- [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md)
- [Issues](https://github.com/Principled-Evolution/aicertify/issues)
- [Sister project: gopal](https://github.com/Principled-Evolution/gopal) — the policy library AICertify consumes.
