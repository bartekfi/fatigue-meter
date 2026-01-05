#!/bin/bash
# Fatigue statusline with gauge bar

input=$(cat)

CACHE_FILE="/tmp/claude-fatigue-status"
CACHE_AGE=300

# Colors
GREEN='\033[32m'
YELLOW='\033[33m'
ORANGE='\033[38;5;208m'
RED='\033[31m'
DIM='\033[2m'
RESET='\033[0m'

get_fatigue_data() {
    python3 << 'PYTHON'
import json
import os
from datetime import datetime
from collections import defaultdict

history_file = os.path.expanduser("~/.claude/history.jsonl")
today = datetime.now().date()
hourly = defaultdict(list)

with open(history_file) as f:
    for line in f:
        try:
            entry = json.loads(line)
            ts = datetime.fromtimestamp(entry.get('timestamp', 0) / 1000)
            if ts.date() == today:
                text = entry.get('display', '')
                if text and not text.startswith('/'):
                    hourly[ts.hour].append(len(text))
        except:
            pass

if not hourly:
    print("50")
    exit()

energies = []
for h in sorted(hourly.keys()):
    lengths = hourly[h]
    avg_len = sum(lengths) / len(lengths)
    grunts = sum(1 for l in lengths if l < 20) / len(lengths)
    energy = min(100, max(0, (avg_len / 2) - (grunts * 40)))
    energies.append(int(energy))

print(energies[-1] if energies else 50)
PYTHON
}

# Check cache
if [ -f "$CACHE_FILE" ]; then
    CACHE_TIME=$(stat -f %m "$CACHE_FILE" 2>/dev/null || stat -c %Y "$CACHE_FILE" 2>/dev/null)
    NOW=$(date +%s)
    if [ $((NOW - CACHE_TIME)) -lt "$CACHE_AGE" ]; then
        ENERGY=$(cat "$CACHE_FILE")
    fi
fi

if [ -z "$ENERGY" ]; then
    ENERGY=$(get_fatigue_data)
    echo "$ENERGY" > "$CACHE_FILE"
fi

# Build gauge bar (10 chars)
FILLED=$((ENERGY / 10))
EMPTY=$((10 - FILLED))
BAR=""
for ((i=0; i<FILLED; i++)); do BAR+="█"; done
for ((i=0; i<EMPTY; i++)); do BAR+="░"; done

# Pick color and qualifier
if [ "$ENERGY" -ge 80 ]; then
    COLOR=$GREEN
    WORD="sharp"
elif [ "$ENERGY" -ge 65 ]; then
    COLOR=$GREEN
    WORD="focused"
elif [ "$ENERGY" -ge 50 ]; then
    COLOR=$YELLOW
    WORD="steady"
elif [ "$ENERGY" -ge 35 ]; then
    COLOR=$ORANGE
    WORD="fading"
elif [ "$ENERGY" -ge 20 ]; then
    COLOR=$RED
    WORD="tired"
else
    COLOR=$RED
    WORD="fried"
fi

echo -e "${DIM}energy${RESET} ${COLOR}${BAR}${RESET} ${COLOR}${WORD}${RESET} ${DIM}(${ENERGY}%)${RESET}"
