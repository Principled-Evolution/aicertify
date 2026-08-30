# AICertify Documentation

> **Looking for an overview?** Start with the [README](../README.md) — it covers the evaluation model, quickstart, regulatory coverage, evidence boundaries, and where AICertify fits.

The documentation here is organized along [Diátaxis](https://diataxis.fr/) lines: tutorials get you running, how-tos solve specific problems, reference describes the API, explanation explores design.

## Tutorials

- [Quickstart](../examples/quickstart.py) — clone, install, run, and inspect the report.
- [Sample contract](../examples/sample_contract.json) — the JSON shape a real contract takes.
- [Examples README](../examples/README.md) — index of the forkable application examples and their maintained expected reports.

## How-to guides

- [Run a compliance check against a custom contract](../skills/evaluate-contract/SKILL.md) (Claude Code skill)
- [Add coverage for a new regulation](../skills/draft-policy/SKILL.md) (Claude Code skill)
- [Understand what a framework's policies enforce](../skills/explain-regulation/SKILL.md) (Claude Code skill)
- [Generate a report in PDF / Markdown / JSON / HTML](../examples/quickstart.py) — see the `report_format` argument.
- [Map existing tool outputs into GOPAL metrics](adapters.md) — adapters for Detoxify, model cards, Fairlearn, and Perspective.
- [Write a custom evaluator](writing-an-evaluator.md) — metric declaration, registration, delivery, and tests.

## Reference

- [Python API](../aicertify/__init__.py) — the public surface re-exported from the package root.
- [CLI](../aicertify/cli.py) — `python -m aicertify.cli` flags and behavior. See also [README#cli](../README.md#cli).
- [Regulatory coverage table](../README.md#regulatory-coverage) — every framework with its policy count.
- [pyproject.toml](../pyproject.toml) — metadata, dependencies, entry points.
- [CHANGELOG](../CHANGELOG.md) — release history.

## Explanation

- [AGENTS.md](../AGENTS.md) — architecture, repository conventions, and guidance for AI coding agents and human contributors.
- [Why AICertify](why-aicertify.md) — evidence model, reproducibility boundary, and the division of responsibility between AICertify, GOPAL, OPA, and evaluators.

## Contributing and community

- [CONTRIBUTING.md](../CONTRIBUTING.md)
- [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md)
- [Issues](https://github.com/Principled-Evolution/aicertify/issues)
- [Sister project: gopal](https://github.com/Principled-Evolution/gopal) — the policy library AICertify consumes.
