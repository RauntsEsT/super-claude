---
name: continuous-learning-v2
description: Instinct-based learning system that observes sessions via hooks, creates atomic instincts with confidence scoring, and evolves them into skills/commands/agents. v2.1 adds project-scoped instincts to prevent cross-project contamination.
origin: ECC
version: 2.1.0
---

# Continuous Learning v2.1 — Instinct-Based Architecture

Turns Claude Code sessions into reusable knowledge through atomic "instincts" with confidence scoring.

## When to Activate

- Setting up automatic learning from sessions
- Reviewing learned instincts
- Evolving instincts into full skills/commands/agents
- Managing project-scoped vs global instincts

## The Instinct Model

An instinct is a small learned behavior:

```yaml
---
id: prefer-functional-style
trigger: "when writing new functions"
confidence: 0.7
domain: "code-style"
scope: project
---
Action: Use functional patterns over classes when appropriate.
Evidence: Observed 5 instances, user corrected class-based to functional 2x.
```

## How It Works

```
Session Activity
      ↓
Hooks capture prompts + tool use (100% reliable)
      ↓
Pattern Detection (background Haiku agent)
      ↓
Instincts created/updated with confidence scores
      ↓
/evolve → clusters → skills/commands/agents
```

## Commands

| Command | Description |
|---------|-------------|
| `/instinct-status` | Show all instincts with confidence |
| `/evolve` | Cluster instincts into skills/commands |
| `/instinct-export` | Export instincts to file |
| `/instinct-import <file>` | Import instincts |
| `/promote [id]` | Promote project instinct to global |
| `/projects` | List known projects and instinct counts |

## Confidence Scoring

| Score | Meaning |
|-------|---------|
| 0.3 | Tentative — suggested not enforced |
| 0.5 | Moderate — applied when relevant |
| 0.7 | Strong — auto-approved |
| 0.9 | Near-certain — core behavior |

## Scope Decision

| Pattern Type | Scope |
|-------------|-------|
| Language/framework conventions | project |
| Security practices | global |
| General best practices | global |
| Tool workflow preferences | global |

## Manual Install Hook (if not using plugin)

Add to `~/.claude/settings.json`:
```json
{
  "hooks": {
    "PreToolUse": [{"matcher": "*", "hooks": [{"type": "command", "command": "~/.claude/skills/continuous-learning-v2/hooks/observe.sh"}]}],
    "PostToolUse": [{"matcher": "*", "hooks": [{"type": "command", "command": "~/.claude/skills/continuous-learning-v2/hooks/observe.sh"}]}]
  }
}
```
