---
name: skill-stocktake
description: "Use when auditing Claude skills and commands for quality. Supports Quick Scan (changed skills only) and Full Stocktake modes with sequential subagent batch evaluation."
origin: ECC
---

# skill-stocktake

Slash command (`/skill-stocktake`) that audits all Claude skills and commands using a quality checklist + AI holistic judgment.

## Scope

Targets:
- `~/.claude/skills/` — global skills
- `{cwd}/.claude/skills/` — project-level skills (if exists)

## Modes

| Mode | Trigger | Duration |
|------|---------|---------|
| Quick Scan | `results.json` exists | 5–10 min |
| Full Stocktake | No `results.json`, or `/skill-stocktake full` | 20–30 min |

## Full Stocktake Flow

### Phase 1 — Inventory
Enumerate skill files, extract frontmatter, collect modification times.

### Phase 2 — Quality Evaluation

Evaluate each skill against checklist:
- Content overlap with other skills checked
- Overlap with MEMORY.md / CLAUDE.md checked
- Freshness of technical references verified
- Usage frequency considered

Verdict per skill:

| Verdict | Meaning |
|---------|---------|
| Keep | Useful and current |
| Improve | Worth keeping, specific improvements needed |
| Update | Referenced technology outdated |
| Retire | Low quality, stale, or redundant |
| Merge into [X] | Substantial overlap with another skill |

### Phase 3 — Summary Table

| Skill | Verdict | Reason |
|-------|---------|--------|

### Phase 4 — Consolidation

- **Retire/Merge**: present justification, confirm with user before action
- **Improve**: present specific suggestions
- **Update**: present updated content with verified sources

## Results Cache
`~/.claude/skills/skill-stocktake/results.json`
