#!/bin/bash
# AutoDream: sessiooni lõpus konsolideerib mälu automaatselt
# Käivitub Stop hookina — analüüsib sessiooni ja uuendab PROJECT_STATE.md

INPUT=$(cat)

# Ära käivitu kui stop_hook_active (Ralph loopis)
STOP_HOOK_ACTIVE=$(echo "$INPUT" | python -c "import sys,json; d=json.load(sys.stdin); print(d.get('stop_hook_active', False))" 2>/dev/null)
if [ "$STOP_HOOK_ACTIVE" = "True" ]; then
    exit 0
fi

SUPER_CLAUDE_DIR="${SUPER_CLAUDE_DIR:-$HOME/SuperClaude}"
STATE_FILE="$SUPER_CLAUDE_DIR/PROJECT_STATE.md"
SESSIONS_DIR="$SUPER_CLAUDE_DIR/sessions"
TODAY=$(date +%Y-%m-%d)
SESSION_FILE="$SESSIONS_DIR/$TODAY.md"

# Loo sessions kaust kui pole
mkdir -p "$SESSIONS_DIR"

# Kui PROJECT_STATE puudub, loo tühi
if [ ! -f "$STATE_FILE" ]; then
    echo "# Project State\n\nNo active project." > "$STATE_FILE"
fi

# Kirjuta AutoDream trigger — Claude loeb selle järgmisel sessioonil
DREAM_TRIGGER="$SUPER_CLAUDE_DIR/.dream_pending"
echo "$TODAY" > "$DREAM_TRIGGER"

echo "{\"hookSpecificOutput\":{\"hookEventName\":\"Stop\",\"message\":\"AutoDream: mälu konsolideerimine käivitatud ($TODAY).\"}}"
exit 0
