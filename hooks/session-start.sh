#!/bin/bash
# SessionStart hook: loads Super Claude context at session start

SUPER_CLAUDE_DIR="${SUPER_CLAUDE_DIR:-$HOME/SuperClaude}"
SUPER_CLAUDE_CONFIG="$SUPER_CLAUDE_DIR/SUPER_CLAUDE.md"

if [ -f "$SUPER_CLAUDE_CONFIG" ]; then
    echo "{\"hookSpecificOutput\":{\"hookEventName\":\"SessionStart\",\"message\":\"Super Claude v3.0 config loaded from $SUPER_CLAUDE_DIR.\"}}"
fi

exit 0
