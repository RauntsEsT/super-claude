# Super Claude

A team-based AI system for [Claude Code](https://claude.ai/code). Instead of a single AI assistant, Super Claude gives you a coordinated team of five expert roles — all working together on every task, automatically.

Just type **"Super Claude"** in Claude Code to activate.

---

## What is Super Claude?

Super Claude is a workflow layer on top of Claude Code that coordinates multiple specialized expert personas for every task:

- **Architect** — designs structure, selects technologies, thinks about scalability
- **Builder** — writes minimal, clean, working code following the Architect's plan
- **QA** — reviews all code for security vulnerabilities, logic errors, and edge cases before it reaches you
- **UX Designer** — ensures every output is intuitive and usable
- **Project Manager** — keeps focus, breaks tasks into parts, tracks what's done and what's next

Plus a set of specialized agents:
- **GUI Operator** — takes over mouse and keyboard for GUI tasks via `computer-control` MCP
- **Playwright Agent** — browser automation (forms, scraping, UI testing)
- **Futurist** — checks tech stack currency, deprecations, CVEs, trending alternatives
- **Brutal Critic** — grades output from 3 angles (technical, user, business). Score < 7 → Builder fixes it
- **Android Architect** — modern Android/Kotlin/Compose expert
- **Unity Architect** — high-performance Unity/C# expert
- **Session Closer** — saves session summaries, updates project state, commits to git

---

## Requirements

- [Claude Code](https://claude.ai/code) (CLI)
- Python 3.10+
- Node.js 18+ (for Playwright MCP)
- pip

---

## Quick Install

**Windows (PowerShell):**
```powershell
git clone https://github.com/RaunoArike/super-claude.git
cd super-claude
powershell -ExecutionPolicy Bypass -File install.ps1
```

**macOS / Linux:**
```bash
git clone https://github.com/RaunoArike/super-claude.git
cd super-claude
bash install.sh
```

The installer will ask where to store your Super Claude configuration (default: `~/SuperClaude`), then set everything up automatically.

---

## What Gets Installed

| Component | Destination | Purpose |
|-----------|-------------|---------|
| `SUPER_CLAUDE.md` | `~/SuperClaude/` | Main configuration — the team's rulebook |
| `skills/super-claude` | `~/.claude/skills/` | Activation skill — loads team on startup |
| `skills/brutal-critic` | `~/.claude/skills/` | 3-angle code review skill |
| `skills/futurist` | `~/.claude/skills/` | Tech Radar / dependency audit skill |
| `skills/notebooklm` | `~/.claude/skills/` | Google NotebookLM integration |
| `skills/yt-search` | `~/.claude/skills/` | YouTube search via yt-dlp |
| `skills/session-close` | `~/.claude/skills/` | Session summary + git commit |
| `skills/product-designer` | `~/.claude/skills/` | UI/UX concepts with React+Tailwind |
| `mcp-servers/computer-control` | `~/.claude/mcp-servers/` | OS-level mouse/keyboard/screen control |
| `hooks/auto-lint.sh` | `~/.claude/hooks/` | Auto-formats files after every Edit/Write |
| `hooks/ralph-loop.sh` | `~/.claude/hooks/` | Auto-continues on detected errors (max 3x) |
| `hooks/session-start.sh` | `~/.claude/hooks/` | Loads project context at session start |

**Python packages installed:** `mcp`, `pywinauto` (Windows), `pyautogui`, `Pillow`, `yt-dlp`, `notebooklm`

**Node packages installed:** `@playwright/mcp`

---

## Usage

### Activate Super Claude
Just type in Claude Code:
```
Super Claude
```

The system automatically:
1. Loads `SUPER_CLAUDE.md` configuration
2. Reads current project state
3. Reads last session notes
4. Reports team status and next steps
5. Starts working if there's unfinished business

### Available Skills
Invoke directly with slash commands:

| Command | What it does |
|---------|-------------|
| `/super-claude` | Activate team mode |
| `/brutal-critic` | Critique from 3 angles (technical/user/business) |
| `/futurist` | Tech Radar — trends, deprecations, CVEs |
| `/yt-search` | YouTube search returning metadata JSON |
| `/notebooklm` | Google NotebookLM notebook management |
| `/session-close` | Save session summary + git commit |
| `/product-designer` | UI/UX concepts with React+Tailwind preview |

### computer-control MCP
Gives Claude direct control of your screen:
```
screenshot()        — take a screenshot
click_element()     — click a UI element by name
type_text()         — type into active window
hotkey()            — keyboard shortcuts (ctrl+c, alt+tab...)
focus_window()      — bring a window into focus
scroll()            — scroll with mouse wheel
get_windows()       — list open windows
```

---

## Project Structure

```
~/SuperClaude/
├── SUPER_CLAUDE.md        ← team configuration (edit to customize)
├── PROJECT_STATE.md       ← current project overview (auto-updated)
└── sessions/
    └── 2026-03-21.md      ← session logs (auto-created)
```

To customize the team behavior, edit `~/SuperClaude/SUPER_CLAUDE.md`.

---

## How It Works

Super Claude runs entirely within Claude Code's existing skill and hook system — no external services, no subscriptions, no API keys beyond your Claude Code subscription.

- **Skills** are markdown files that Claude Code reads when you invoke `/skill-name`
- **Hooks** are shell scripts that run automatically on Claude Code events (PostToolUse, Stop, SessionStart)
- **MCP servers** extend Claude Code with new tools (computer-control adds GUI automation)
- **SUPER_CLAUDE.md** is the team rulebook, loaded at activation

The team coordination is prompt-based: the system instructs Claude to reason through problems from multiple expert perspectives, run quality checks, and only deliver final results.

---

## License

MIT — do whatever you want with it.
