---
name: security-scan
description: Scan your Claude Code configuration (.claude/ directory) for security vulnerabilities, misconfigurations, and injection risks using AgentShield. Checks CLAUDE.md, settings.json, MCP servers, hooks, and agent definitions.
origin: ECC
---

# Security Scan Skill

Audit Claude Code configuration for security issues using AgentShield.

## When to Activate

- Setting up a new Claude Code project
- After modifying `.claude/settings.json`, `CLAUDE.md`, or MCP configs
- Before committing configuration changes
- Periodic security hygiene checks

## What It Scans

| File | Checks |
|------|--------|
| `CLAUDE.md` | Hardcoded secrets, auto-run instructions, prompt injection |
| `settings.json` | Overly permissive allow lists, missing deny lists |
| `mcp.json` | Risky MCP servers, hardcoded env secrets, supply chain risks |
| `hooks/` | Command injection, data exfiltration, silent error suppression |
| `agents/*.md` | Unrestricted tool access, prompt injection surface |

## Usage

```bash
# Install
npm install -g ecc-agentshield

# Basic scan
npx ecc-agentshield scan

# Auto-fix safe issues
npx ecc-agentshield scan --fix

# Deep analysis with Claude Opus
export ANTHROPIC_API_KEY=your-key
npx ecc-agentshield scan --opus --stream
```

## Severity Grades

| Grade | Score | Meaning |
|-------|-------|---------|
| A | 90-100 | Secure |
| B | 75-89 | Minor issues |
| C | 60-74 | Needs attention |
| D | 40-59 | Significant risks |
| F | 0-39 | Critical vulnerabilities |

## Critical Findings (fix immediately)
- Hardcoded API keys in config files
- `Bash(*)` in allow list (unrestricted shell)
- Command injection in hooks via `${file}` interpolation
