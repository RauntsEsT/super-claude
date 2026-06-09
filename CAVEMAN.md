# Caveman Plugin

Token compression for Claude Code. ~65% output token savings.

## Install

```powershell
# Windows
powershell.exe -ExecutionPolicy Bypass -File "$env:TEMP\caveman-install.ps1"
# (download first: irm https://raw.githubusercontent.com/JuliusBrussee/caveman/main/install.ps1 -OutFile $env:TEMP\caveman-install.ps1)
```

Or via Claude Code plugin system:
```
claude plugin marketplace add JuliusBrussee/caveman
claude plugin install caveman@caveman
```

## Skills

| Skill | Trigger | Effect |
|-------|---------|--------|
| `/caveman [lite\|full\|ultra]` | "talk like caveman" | 75% fewer output tokens |
| `/caveman-compress <file>` | compress memory file | ~46% input token savings (permanent) |
| `/caveman-commit` | "write commit" | Conventional Commits, ≤50 chars |
| `/caveman-review` | "code review" | One-line PR comments |
| `/caveman-stats` | "/caveman-stats" | Session token savings + USD |

## Benchmarks (real API measurements)

Average 65% output reduction across 10 prompts.

| Task | Normal | Caveman | Saved |
|------|-------:|--------:|------:|
| React re-render debug | 1180 | 159 | 87% |
| Auth middleware fix | 704 | 121 | 83% |
| PostgreSQL pool setup | 2347 | 380 | 84% |
| Git rebase vs merge | 702 | 292 | 58% |
| **Average** | **1214** | **294** | **65%** |

## Notes

- Installed as Claude Code plugin (not manual skill)
- Hooks: `caveman-activate.js`, `caveman-mode-tracker.js` (SessionStart + UserPromptSubmit)
- MCP shrink proxy: `caveman-shrink` (wraps any MCP server, compresses tool descriptions)
- Auto-drops caveman for: security warnings, irreversible actions, ambiguous sequences
- Source: https://github.com/JuliusBrussee/caveman (MIT)
