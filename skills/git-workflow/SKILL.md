---
name: git-workflow
description: Git workflow patterns including branching strategies, commit conventions, merge vs rebase, conflict resolution, and collaborative development best practices.
origin: ECC
---

# Git Workflow Patterns

## When to Activate

- Setting up Git workflow for a new project
- Deciding on branching strategy
- Writing commit messages and PR descriptions
- Resolving merge conflicts

## Branching Strategy (GitHub Flow — Recommended)

```
main (protected, always deployable)
  ├── feature/user-auth      → PR → merge
  ├── feature/payment-flow   → PR → merge
  └── fix/login-bug          → PR → merge
```

## Conventional Commits

```
<type>(<scope>): <subject>

Types: feat, fix, docs, style, refactor, test, chore, perf, ci, revert
```

Examples:
- `feat(auth): add OAuth2 login`
- `fix(api): handle null response in user endpoint`
- `chore(deps): update dependencies`

## Merge vs Rebase

**Merge** — preserves history, use for feature → main
**Rebase** — linear history, use for updating local branch from main

```bash
# Update feature branch
git checkout feature/name
git fetch origin
git rebase origin/main
```

**Never rebase** branches others have based work on.

## Common Commands

```bash
git checkout -b feature/name     # New branch
git stash push -m "WIP: ..."     # Save work
git log --oneline --graph --all  # Visual history
git reset --soft HEAD~1          # Undo last commit (keep changes)
git revert HEAD                  # Safe undo for pushed commits
```

## Anti-Patterns
- Committing directly to main
- Giant PRs (1000+ lines) — break into smaller focused PRs
- Vague commit messages ("update", "fix")
- Force-pushing main — use `git revert` instead
