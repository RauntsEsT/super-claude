---
name: context-budget
description: Audits Claude Code context window consumption across agents, skills, MCP servers, and rules. Identifies bloat, redundant components, and produces prioritized token-savings recommendations.
origin: ECC
---

# Context Budget

Analyze token overhead across every loaded component and surface actionable optimizations.

## When to Use

- Session performance feels sluggish
- You've recently added many skills, agents, or MCP servers
- Want to know how much context headroom you have
- Planning to add more components

## How It Works

### Phase 1: Inventory

Estimate token consumption per component type:
- **Agents** — count lines × 1.3 words; flag files >200 lines
- **Skills** — count tokens per SKILL.md; flag >400 lines
- **Rules** — count tokens per file; flag >100 lines
- **MCP Servers** — ~500 tokens per tool; flag servers with >20 tools
- **CLAUDE.md** — flag if combined >300 lines

### Phase 2: Classify

| Bucket | Action |
|--------|--------|
| Always needed | Keep |
| Sometimes needed | Consider on-demand |
| Rarely needed | Remove or lazy-load |

### Phase 3: Report

```
Context Budget Report
═══════════════════════════════
Total overhead: ~XX,XXX tokens
Available: ~XXX,XXX tokens (XX%)

Top 3 Optimizations:
1. [action] → save ~X,XXX tokens
2. [action] → save ~X,XXX tokens
3. [action] → save ~X,XXX tokens
```

## Best Practices
- MCP is the biggest lever: each tool ~500 tokens
- Agent descriptions are always loaded even if agent never invoked
- Run after adding any agent, skill, or MCP server
