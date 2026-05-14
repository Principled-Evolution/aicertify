# AICertify Claude Code Skills

This directory ships [Claude Code](https://docs.claude.com/en/docs/claude-code/) skills for working with AICertify. Each subdirectory contains a `SKILL.md` file that Claude Code can invoke as a slash command.

## Available skills

| Skill | What it does |
|---|---|
| [`run-compliance-check`](run-compliance-check/SKILL.md) | Run the end-to-end quickstart and surface the generated report |
| [`evaluate-contract`](evaluate-contract/SKILL.md) | Evaluate a user-supplied contract JSON against any supported framework |
| [`explain-regulation`](explain-regulation/SKILL.md) | Walk every policy in a framework directory and explain what it checks |
| [`draft-policy`](draft-policy/SKILL.md) | Scaffold a new Rego policy with metadata, default rule, and a test sibling |

## Installation

Skills under `skills/` in this repository are intended to be installed into Claude Code's skills directory. The simplest way:

```bash
# From the repo root
mkdir -p ~/.claude/skills
cp -r skills/* ~/.claude/skills/
```

Restart Claude Code. The skills appear as slash commands:

```
/run-compliance-check
/evaluate-contract path/to/contract.json eu_ai_act pdf
/explain-regulation eu_ai_act
/draft-policy international eu_ai_act my_new_rule
```

A first-class `aicertify install` command is on the roadmap to register skills, MCP, and editor hooks in one step.
