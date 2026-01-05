# Fatigue

Track your Claude Code prompting energy levels. See when you're sharp vs running on fumes.

```
energy ██████░░░░ steady (63%)
```

## What It Does

Analyzes your Claude Code prompt history and calculates "energy" based on:
- **Prompt length** - shorter prompts = more fatigued
- **Grunt ratio** - "yes", "ok", "continue" patterns indicate fatigue
- **Specificity** - file refs and code mentions fade when tired

## Installation

### 1. Install the skill

```bash
mkdir -p ~/.claude/skills
cp -r . ~/.claude/skills/fatigue
chmod +x ~/.claude/skills/fatigue/fatigue
```

### 2. Add to allowed commands (optional)

Add to `~/.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(~/.claude/skills/fatigue/fatigue:*)"
    ]
  }
}
```

### 3. Enable status bar

Add to `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/skills/fatigue/statusline.sh"
  }
}
```

Then restart Claude Code.

## Usage

```bash
fatigue --today               # Today's hourly energy
fatigue --yesterday           # Yesterday's breakdown
fatigue --week                # This week's daily breakdown
fatigue --stamina             # GitHub-style heatmap
fatigue --trend               # Weekly trend comparison
fatigue --shame               # Your laziest prompts
fatigue --pride               # Your best prompts
```

## Energy Scale

| Energy | Word | Color | Meaning |
|--------|------|-------|---------|
| 80%+ | sharp | green | Peak focus |
| 65-80% | focused | green | Good energy |
| 50-65% | steady | yellow | Normal |
| 35-50% | fading | orange | Getting tired |
| 20-35% | tired | red | Low energy |
| <20% | fried | red | Take a break |

## Example Output

```
TODAY'S ENERGY LEVELS
============================================================
Date: 2025-12-20 | Prompts: 77 | Energy: 62%

Hour    Energy  Len   Grunts  Bar
-------------------------------------------------------
10:00 🟡  62%   142    17%    ██████░░░░
11:00 🟡  50%    69     9%    █████░░░░░
12:00 🟡  60%   240    50%    ██████░░░░
13:00 🔴  20%    15    58%    ██░░░░░░░░
14:00 🟠  45%   124    50%    ████░░░░░░
15:00 🟢  80%   362     0%    ████████░░
```

## Status Bar

The status bar shows your current energy level:

```
energy ████████░░ sharp (82%)
energy ██████░░░░ steady (63%)
energy ████░░░░░░ fading (42%)
energy ██░░░░░░░░ tired (25%)
```

Cached for 5 minutes to keep it fast.
