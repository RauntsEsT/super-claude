# Super Claude Installer — Windows PowerShell
# Run with: powershell -ExecutionPolicy Bypass -File install.ps1

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║       Super Claude v1.0 Installer        ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ── Ask for Super Claude directory ──────────────────────────────────────────
$defaultDir = "$HOME\SuperClaude"
$inputDir = Read-Host "Super Claude directory (press Enter for default: $defaultDir)"
if ([string]::IsNullOrWhiteSpace($inputDir)) {
    $SUPER_CLAUDE_DIR = $defaultDir
} else {
    $SUPER_CLAUDE_DIR = $inputDir
}

Write-Host ""
Write-Host "Installing to:" -ForegroundColor Yellow
Write-Host "  Super Claude dir : $SUPER_CLAUDE_DIR"
Write-Host "  Claude skills    : $HOME\.claude\skills\"
Write-Host "  Claude hooks     : $HOME\.claude\hooks\"
Write-Host "  MCP servers      : $HOME\.claude\mcp-servers\"
Write-Host ""

# ── Get script directory ─────────────────────────────────────────────────────
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path

# ── Create directories ───────────────────────────────────────────────────────
Write-Host "[1/6] Creating directories..." -ForegroundColor Green
New-Item -ItemType Directory -Force -Path $SUPER_CLAUDE_DIR | Out-Null
New-Item -ItemType Directory -Force -Path "$HOME\.claude\skills" | Out-Null
New-Item -ItemType Directory -Force -Path "$HOME\.claude\hooks" | Out-Null
New-Item -ItemType Directory -Force -Path "$HOME\.claude\mcp-servers\computer-control" | Out-Null
New-Item -ItemType Directory -Force -Path "$SUPER_CLAUDE_DIR\sessions" | Out-Null

# ── Copy SUPER_CLAUDE.md with path substitution ──────────────────────────────
Write-Host "[2/6] Installing SUPER_CLAUDE.md..." -ForegroundColor Green
$superClaudeContent = Get-Content "$SCRIPT_DIR\SUPER_CLAUDE.md" -Raw
$superClaudeContent = $superClaudeContent -replace '\{\{SUPER_CLAUDE_DIR\}\}', $SUPER_CLAUDE_DIR
$superClaudeContent = $superClaudeContent -replace '\{\{USER_HOME\}\}', $HOME
$superClaudeContent | Set-Content "$SUPER_CLAUDE_DIR\SUPER_CLAUDE.md" -Encoding UTF8

# ── Copy skills ──────────────────────────────────────────────────────────────
Write-Host "[3/6] Installing skills..." -ForegroundColor Green
$skills = @("super-claude", "brutal-critic", "futurist", "notebooklm", "yt-search", "session-close", "product-designer")
foreach ($skill in $skills) {
    $src = "$SCRIPT_DIR\skills\$skill"
    $dst = "$HOME\.claude\skills\$skill"
    New-Item -ItemType Directory -Force -Path $dst | Out-Null
    Copy-Item -Path "$src\*" -Destination $dst -Recurse -Force
    Write-Host "  ✓ $skill" -ForegroundColor Gray
}

# ── Update super-claude skill.md path ────────────────────────────────────────
$skillMdPath = "$HOME\.claude\skills\super-claude\skill.md"
$skillContent = Get-Content $skillMdPath -Raw
$skillContent = $skillContent -replace '\{\{SUPER_CLAUDE_DIR\}\}', $SUPER_CLAUDE_DIR
$skillContent = $skillContent -replace '\{\{USER_HOME\}\}', $HOME
$skillContent | Set-Content $skillMdPath -Encoding UTF8

# Also update product-designer skill path
$designerSkillPath = "$HOME\.claude\skills\product-designer\skill.md"
$designerContent = Get-Content $designerSkillPath -Raw
$designerContent = $designerContent -replace '\{\{USER_HOME\}\}', $HOME
$designerContent | Set-Content $designerSkillPath -Encoding UTF8

# ── Copy hooks ───────────────────────────────────────────────────────────────
Write-Host "[4/6] Installing hooks..." -ForegroundColor Green
$hooks = @("auto-lint.sh", "ralph-loop.sh", "session-start.sh")
foreach ($hook in $hooks) {
    $hookContent = Get-Content "$SCRIPT_DIR\hooks\$hook" -Raw
    $hookContent = $hookContent -replace '\{\{SUPER_CLAUDE_DIR\}\}', ($SUPER_CLAUDE_DIR -replace '\\', '/')
    $hookContent | Set-Content "$HOME\.claude\hooks\$hook" -Encoding UTF8
    Write-Host "  ✓ $hook" -ForegroundColor Gray
}

# Set SUPER_CLAUDE_DIR as a persistent user environment variable
[System.Environment]::SetEnvironmentVariable("SUPER_CLAUDE_DIR", $SUPER_CLAUDE_DIR, "User")

# ── Copy MCP server ──────────────────────────────────────────────────────────
Write-Host "[5/6] Installing MCP server..." -ForegroundColor Green
Copy-Item -Path "$SCRIPT_DIR\mcp-servers\computer-control\server.py" `
          -Destination "$HOME\.claude\mcp-servers\computer-control\server.py" -Force
Write-Host "  ✓ computer-control/server.py" -ForegroundColor Gray

# Register MCP server with Claude
$mcpServerPath = "$HOME\.claude\mcp-servers\computer-control\server.py"
Write-Host "  Registering computer-control MCP server..." -ForegroundColor Gray
try {
    & claude mcp add computer-control python $mcpServerPath 2>&1 | Out-Null
    Write-Host "  ✓ MCP server registered" -ForegroundColor Gray
} catch {
    Write-Host "  ! Could not auto-register MCP (claude CLI not found). Run manually:" -ForegroundColor Yellow
    Write-Host "    claude mcp add computer-control python `"$mcpServerPath`"" -ForegroundColor Gray
}

# ── Install dependencies ──────────────────────────────────────────────────────
Write-Host "[6/6] Installing dependencies..." -ForegroundColor Green

Write-Host "  Installing Python packages..." -ForegroundColor Gray
pip install mcp pywinauto pyautogui Pillow yt-dlp notebooklm --quiet
Write-Host "  ✓ Python packages installed" -ForegroundColor Gray

Write-Host "  Installing Node packages..." -ForegroundColor Gray
npm install -g @playwright/mcp 2>&1 | Out-Null
Write-Host "  ✓ Node packages installed" -ForegroundColor Gray

# ── Create PROJECT_STATE.md template ─────────────────────────────────────────
if (-not (Test-Path "$SUPER_CLAUDE_DIR\PROJECT_STATE.md")) {
    @"
# Project State

## Current Project
[Set your active project here]

## Status
- Installation: Complete
- Last updated: $(Get-Date -Format "yyyy-MM-dd")

## Next Steps
- Type "Super Claude" in Claude Code to activate
"@ | Set-Content "$SUPER_CLAUDE_DIR\PROJECT_STATE.md" -Encoding UTF8
}

# ── Done ──────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║         Installation Complete!           ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Open Claude Code"
Write-Host "  2. Type: Super Claude"
Write-Host "  3. The team activates automatically"
Write-Host ""
Write-Host "Super Claude directory: $SUPER_CLAUDE_DIR" -ForegroundColor Cyan
Write-Host "Skills installed to   : $HOME\.claude\skills\" -ForegroundColor Cyan
Write-Host ""
Write-Host "Enjoy your AI team!" -ForegroundColor Green
