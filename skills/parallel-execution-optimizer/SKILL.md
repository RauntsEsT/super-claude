---
name: parallel-execution-optimizer
description: Use when the user wants a task done much faster through parallel work, concurrent agents, batched tool calls, isolated worktrees, or many independent verification lanes without losing correctness.
origin: ECC
tools: Read, Write, Edit, Bash, Grep, Glob
---

# Parallel Execution Optimizer

Use this skill when speed comes from doing independent work at the same time.

## Core Pattern

Turn urgency into a dependency graph before acting:

1. Define the objective and done signal
2. Split work into lanes
3. Mark each lane: parallel, sequential, or gated
4. Run independent reads/checks together
5. Keep writes isolated by file, worktree, branch, or service
6. Merge only after evidence shows lanes are compatible
7. End with a verification table

## Lane Matrix

```text
Lane               | Parallel? | Write surface | Risk   | Verification
Repo scan          | yes       | none          | low    | rg/git outputs
Backend patch      | maybe     | src/api       | medium | unit tests
Frontend patch     | maybe     | app/components| medium | screenshot
Deploy readback    | after build| remote       | high   | live URL + logs
```

## Execution Rules

- Batch file reads, searches, status checks together
- Use isolated worktrees for large unrelated implementation lanes
- Start long-running tests/builds in separate sessions, poll deliberately
- Never parallelize destructive commands, migrations, or writes to the same table
- Do not parallelize without an explicit gate for live customer-impacting deploys

## Output Shape

```text
Parallel execution result:
- Lanes run: 5
- Lanes completed: 4
- Blocked lane: deploy readback, waiting on DNS
- Verification: lint pass, unit pass, live smoke pass
```

## Failure Modes
- Concurrency creating conflicting edits
- Treating "fast" as done before correctness proven
- Forgetting to poll running sessions
