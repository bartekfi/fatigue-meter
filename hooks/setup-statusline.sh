#!/bin/bash
# Auto-configure fatigue statusline on first run
SETTINGS="$HOME/.claude/settings.json"
STATUSLINE_CMD="${CLAUDE_PLUGIN_ROOT}/statusline.sh"

# Skip if settings doesn't exist
[ -f "$SETTINGS" ] || exit 0

# Skip if statusline already configured
grep -q "statusLine" "$SETTINGS" 2>/dev/null && exit 0

# Add statusline config
python3 -c "
import json
with open('$SETTINGS') as f:
    s = json.load(f)
s['statusLine'] = {'type': 'command', 'command': '$STATUSLINE_CMD'}
with open('$SETTINGS', 'w') as f:
    json.dump(s, f, indent=2)
"
