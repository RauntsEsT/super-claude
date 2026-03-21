#!/bin/bash
# Ralph Self-Healing Loop: jätkab AINULT kui viimane sõnum viitab selgelt veale
# Vaikimisi: laseb peatuda

INPUT=$(cat)

# Kui juba stop hook loop'is — lase peatuda
STOP_HOOK_ACTIVE=$(echo "$INPUT" | python -c "import sys,json; d=json.load(sys.stdin); print(d.get('stop_hook_active', False))" 2>/dev/null)
if [ "$STOP_HOOK_ACTIVE" = "True" ]; then
    exit 0
fi

# Loe viimast sõnumit
LAST_MSG=$(echo "$INPUT" | python -c "import sys,json; d=json.load(sys.stdin); print(d.get('last_assistant_message', '')[:500])" 2>/dev/null)

# Jätka AINULT kui viimane sõnum viitab selgelt veale/krahhile
if echo "$LAST_MSG" | grep -qiE "(error|failed|crash|traceback|exception|ebaõnnestus|viga tekkis)"; then
    RALPH_STATE_FILE="/tmp/ralph_state.json"
    RETRY_COUNT=0
    if [ -f "$RALPH_STATE_FILE" ]; then
        RETRY_COUNT=$(python -c "import json; d=json.load(open('$RALPH_STATE_FILE')); print(d.get('retry_count', 0))" 2>/dev/null || echo 0)
    fi

    if [ "$RETRY_COUNT" -ge 3 ]; then
        rm -f "$RALPH_STATE_FILE"
        exit 0
    fi

    NEW_COUNT=$((RETRY_COUNT + 1))
    echo "{\"retry_count\": $NEW_COUNT}" > "$RALPH_STATE_FILE"
    echo "{\"decision\":\"block\",\"reason\":\"Ralph: tuvastatud viga, proovin parandada (katse $NEW_COUNT/3).\"}"
    exit 0
fi

# Vaikimisi: lase peatuda
rm -f "/tmp/ralph_state.json"
exit 0
