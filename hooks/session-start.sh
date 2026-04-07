#!/bin/bash
# SessionStart hook: loads context automatically at session start
# Checks if Super Claude config exists and loads it
# If .dream_pending exists, signals KAIROS to run

SUPER_CLAUDE_DIR="${SUPER_CLAUDE_DIR:-$HOME/SuperClaude}"
SUPER_CLAUDE_CONFIG="$SUPER_CLAUDE_DIR/SUPER_CLAUDE.md"
DREAM_PENDING="$SUPER_CLAUDE_DIR/.dream_pending"

if [ -f "$SUPER_CLAUDE_CONFIG" ]; then
    if [ -f "$DREAM_PENDING" ]; then
        DREAM_DATE=$(cat "$DREAM_PENDING")
        rm -f "$DREAM_PENDING"
        echo "{\"hookSpecificOutput\":{\"hookEventName\":\"SessionStart\",\"message\":\"Super Claude v3.0 loaded. KAIROS: dream_pending from $DREAM_DATE — consolidating memory.\"}}"
    else
        echo "{\"hookSpecificOutput\":{\"hookEventName\":\"SessionStart\",\"message\":\"Super Claude v3.0 config loaded from $SUPER_CLAUDE_DIR.\"}}"
    fi
fi

exit 0
