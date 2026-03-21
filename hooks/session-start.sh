#!/bin/bash
# SessionStart hook: loads context automatically at session start
# Checks if Super Claude config exists and loads it

SUPER_CLAUDE_CONFIG="${SUPER_CLAUDE_DIR}/SUPER_CLAUDE.md"

# Check if Super Claude config exists
if [ -f "$SUPER_CLAUDE_CONFIG" ]; then
    echo "{\"hookSpecificOutput\":{\"hookEventName\":\"SessionStart\",\"message\":\"Super Claude v3.0 config loaded from $SUPER_CLAUDE_DIR.\"}}"
fi

exit 0
