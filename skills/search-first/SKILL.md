---
name: search-first
description: Research-before-coding workflow. Search for existing tools, libraries, and patterns before writing custom code. Invokes the researcher agent.
origin: ECC
---

# /search-first — Research Before You Code

Systematizes the "search for existing solutions before implementing" workflow.

## Trigger

Use this skill when:
- Starting a new feature that likely has existing solutions
- Adding a dependency or integration
- The user asks "add X functionality" and you're about to write code
- Before creating a new utility, helper, or abstraction

## Workflow

1. **Need Analysis** — Define what functionality is needed
2. **Parallel Search** — npm/PyPI, MCP servers, GitHub, web
3. **Evaluate** — Score candidates (functionality, maintenance, license)
4. **Decide** — Adopt / Extend / Build Custom
5. **Implement** — Install package or write minimal custom code

## Decision Matrix

| Signal | Action |
|--------|--------|
| Exact match, well-maintained, MIT/Apache | **Adopt** |
| Partial match, good foundation | **Extend** |
| Multiple weak matches | **Compose** |
| Nothing suitable | **Build** |

## Quick Mode

Before writing utility code, check:
0. Does this already exist in the repo? (`rg` search)
1. Is this a common problem? → npm/PyPI
2. Is there an MCP for this? → `~/.claude/settings.json`
3. Is there a skill? → `~/.claude/skills/`
4. GitHub implementation? → Code search

## Anti-Patterns
- Writing utility without checking if one exists
- Ignoring MCP capabilities
- Over-customizing existing libraries
