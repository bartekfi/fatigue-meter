#!/bin/bash
# Prompt Fatigue statusline with gauge bar

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
import json, os, re
from datetime import datetime
from collections import defaultdict

history_file = os.path.expanduser("~/.claude/history.jsonl")
today = datetime.now().date()
hourly_texts = defaultdict(list)

GRUNT_PATTERNS = ['yes', 'no', 'ok', 'okay', 'sure', 'continue', 'go',
                  'do it', 'good', 'great', 'nice', 'thanks', "let's do it",
                  "let's go", 'sounds good']

with open(history_file) as f:
    for line in f:
        try:
            entry = json.loads(line)
            ts = datetime.fromtimestamp(entry.get('timestamp', 0) / 1000)
            if ts.date() == today:
                text = entry.get('display', '')
                if text and not text.startswith('/'):
                    hourly_texts[ts.hour].append(text)
        except json.JSONDecodeError:
            pass

if not hourly_texts:
    print("50")
    exit()

# Use the same formula as the main fatigue tool
last_hour = max(hourly_texts.keys())
texts = hourly_texts[last_hour]
lengths = [len(t) for t in texts]
avg_length = sum(lengths) / len(lengths)
grunts = sum(1 for t in texts if t.lower().strip().rstrip('.!') in GRUNT_PATTERNS or len(t) < 15)
grunt_ratio = grunts / len(texts)
specificity = 0
for t in texts:
    specificity += len(re.findall(r'\b\w+\.(py|js|ts|tsx|go|rs|java|cpp)\b', t, re.I))
    specificity += len(re.findall(r'`[^`]+`', t))
spec_per_prompt = specificity / len(texts)

length_fatigue = max(0, min(100, 100 - (avg_length / 2)))
grunt_fatigue = grunt_ratio * 100
spec_fatigue = max(0, min(100, 100 - (spec_per_prompt * 50)))
fatigue = (length_fatigue * 0.4) + (grunt_fatigue * 0.4) + (spec_fatigue * 0.2)
energy = int(100 - fatigue)
print(max(0, min(100, energy)))
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
