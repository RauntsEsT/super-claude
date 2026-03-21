#!/usr/bin/env bash
# Super Claude Installer — Linux / macOS
# Run with: bash install.sh

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║       Super Claude v1.0 Installer        ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════╝${NC}"
echo ""

# ── Ask for Super Claude directory ──────────────────────────────────────────
DEFAULT_DIR="$HOME/SuperClaude"
read -r -p "Super Claude directory (press Enter for default: $DEFAULT_DIR): " INPUT_DIR
if [ -z "$INPUT_DIR" ]; then
    SUPER_CLAUDE_DIR="$DEFAULT_DIR"
else
    SUPER_CLAUDE_DIR="$INPUT_DIR"
fi

echo ""
echo -e "${YELLOW}Installing to:${NC}"
echo "  Super Claude dir : $SUPER_CLAUDE_DIR"
echo "  Claude skills    : $HOME/.claude/skills/"
echo "  Claude hooks     : $HOME/.claude/hooks/"
echo "  MCP servers      : $HOME/.claude/mcp-servers/"
echo ""

# ── Get script directory ─────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Create directories ───────────────────────────────────────────────────────
echo -e "${GREEN}[1/6] Creating directories...${NC}"
mkdir -p "$SUPER_CLAUDE_DIR/sessions"
mkdir -p "$HOME/.claude/skills"
mkdir -p "$HOME/.claude/hooks"
mkdir -p "$HOME/.claude/mcp-servers/computer-control"

# ── Copy SUPER_CLAUDE.md with path substitution ──────────────────────────────
echo -e "${GREEN}[2/6] Installing SUPER_CLAUDE.md...${NC}"
sed -e "s|{{SUPER_CLAUDE_DIR}}|$SUPER_CLAUDE_DIR|g" \
    -e "s|{{USER_HOME}}|$HOME|g" \
    "$SCRIPT_DIR/SUPER_CLAUDE.md" > "$SUPER_CLAUDE_DIR/SUPER_CLAUDE.md"

# ── Copy skills ──────────────────────────────────────────────────────────────
echo -e "${GREEN}[3/6] Installing skills...${NC}"
for skill in super-claude brutal-critic futurist notebooklm yt-search session-close product-designer; do
    mkdir -p "$HOME/.claude/skills/$skill"
    cp -r "$SCRIPT_DIR/skills/$skill/." "$HOME/.claude/skills/$skill/"
    echo -e "  ${GRAY}✓ $skill${NC}"
done

# Update super-claude skill.md path
sed -i.bak \
    -e "s|{{SUPER_CLAUDE_DIR}}|$SUPER_CLAUDE_DIR|g" \
    -e "s|{{USER_HOME}}|$HOME|g" \
    "$HOME/.claude/skills/super-claude/skill.md" && \
    rm -f "$HOME/.claude/skills/super-claude/skill.md.bak"

# Update product-designer skill path
sed -i.bak \
    -e "s|{{USER_HOME}}|$HOME|g" \
    "$HOME/.claude/skills/product-designer/skill.md" && \
    rm -f "$HOME/.claude/skills/product-designer/skill.md.bak"

# ── Copy hooks ───────────────────────────────────────────────────────────────
echo -e "${GREEN}[4/6] Installing hooks...${NC}"
for hook in auto-lint.sh ralph-loop.sh session-start.sh; do
    sed -e "s|{{SUPER_CLAUDE_DIR}}|$SUPER_CLAUDE_DIR|g" \
        "$SCRIPT_DIR/hooks/$hook" > "$HOME/.claude/hooks/$hook"
    chmod +x "$HOME/.claude/hooks/$hook"
    echo -e "  ${GRAY}✓ $hook${NC}"
done

# Set SUPER_CLAUDE_DIR in shell profile
PROFILE_FILE="$HOME/.bashrc"
if [ -f "$HOME/.zshrc" ]; then
    PROFILE_FILE="$HOME/.zshrc"
fi

if ! grep -q "SUPER_CLAUDE_DIR" "$PROFILE_FILE" 2>/dev/null; then
    echo "" >> "$PROFILE_FILE"
    echo "# Super Claude" >> "$PROFILE_FILE"
    echo "export SUPER_CLAUDE_DIR=\"$SUPER_CLAUDE_DIR\"" >> "$PROFILE_FILE"
    echo -e "  ${GRAY}✓ SUPER_CLAUDE_DIR exported to $PROFILE_FILE${NC}"
fi

# ── Copy MCP server ──────────────────────────────────────────────────────────
echo -e "${GREEN}[5/6] Installing MCP server...${NC}"
cp "$SCRIPT_DIR/mcp-servers/computer-control/server.py" \
   "$HOME/.claude/mcp-servers/computer-control/server.py"
echo -e "  ${GRAY}✓ computer-control/server.py${NC}"

# Register MCP server with Claude
MCP_SERVER_PATH="$HOME/.claude/mcp-servers/computer-control/server.py"
echo -e "  Registering computer-control MCP server..."
if command -v claude &>/dev/null; then
    claude mcp add computer-control python "$MCP_SERVER_PATH" 2>/dev/null || true
    echo -e "  ${GRAY}✓ MCP server registered${NC}"
else
    echo -e "  ${YELLOW}! claude CLI not found. Register manually:${NC}"
    echo "    claude mcp add computer-control python \"$MCP_SERVER_PATH\""
fi

# ── Install dependencies ──────────────────────────────────────────────────────
echo -e "${GREEN}[6/6] Installing dependencies...${NC}"

echo -e "  Installing Python packages..."
pip install mcp pyautogui Pillow yt-dlp notebooklm --quiet
echo -e "  ${GRAY}✓ Python packages installed${NC}"

# Note: pywinauto is Windows-only, skip on Linux/Mac
echo -e "  ${GRAY}Note: pywinauto (Windows GUI automation) skipped on this platform${NC}"

echo -e "  Installing Node packages..."
npm install -g @playwright/mcp 2>/dev/null || echo -e "  ${YELLOW}! npm not found, skipping Node packages${NC}"
echo -e "  ${GRAY}✓ Node packages installed${NC}"

# ── Create PROJECT_STATE.md template ─────────────────────────────────────────
if [ ! -f "$SUPER_CLAUDE_DIR/PROJECT_STATE.md" ]; then
    cat > "$SUPER_CLAUDE_DIR/PROJECT_STATE.md" <<EOF
# Project State

## Current Project
[Set your active project here]

## Status
- Installation: Complete
- Last updated: $(date +%Y-%m-%d)

## Next Steps
- Type "Super Claude" in Claude Code to activate
EOF
fi

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         Installation Complete!           ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Reload your shell: source $PROFILE_FILE"
echo "  2. Open Claude Code"
echo "  3. Type: Super Claude"
echo "  4. The team activates automatically"
echo ""
echo -e "${CYAN}Super Claude directory: $SUPER_CLAUDE_DIR${NC}"
echo -e "${CYAN}Skills installed to   : $HOME/.claude/skills/${NC}"
echo ""
echo -e "${GREEN}Enjoy your AI team!${NC}"
