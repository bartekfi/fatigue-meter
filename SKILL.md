---
name: "Fatigue"
description: "Track your prompting energy levels throughout the day. Use when curious about fatigue patterns, checking if you're burning out, or seeing how energy varies by hour/day."
---

# Fatigue

Track your prompting energy levels. See when you're sharp vs running on fumes.

## When to Use

- Check today's energy levels by hour
- See weekly patterns
- Spot fatigue before burnout
- Compare energy across days

## The Command

```bash
fatigue --today               # Today's hourly energy sparkline
fatigue --yesterday           # Yesterday's hourly breakdown
fatigue --week                # This week's daily breakdown
fatigue --stamina             # GitHub-style heatmap (hour x day)
fatigue --session             # Energy by position in session
fatigue --trend               # Weekly trend comparison
fatigue --shame               # Show your laziest prompts
fatigue --pride               # Show your best prompts
```

## Energy Scale

| Energy | Indicator | Meaning |
|--------|-----------|---------|
| 70%+ | 🟢 | Sharp, focused |
| 50-70% | 🟡 | Normal |
| 30-50% | 🟠 | Fatigued |
| <30% | 🔴 | Running on fumes |

## How It Works

Fatigue detection based on:
- **Prompt length**: shorter = more fatigued
- **Grunt ratio**: "yes", "ok", "continue" patterns
- **Specificity**: file refs, code mentions fade when tired

## Example Output

```
Hours:  09  10  11  12  13  14  15  16
Energy: ▆   ▅   ▇   ▆   ▇   █   ▁   ▅

Hour    Energy  Len   Grunts  Bar
14:00 🟢  72%   160     0%    ███████░░░
15:00 🟠  36%    48    33%    ███░░░░░░░
```

## Permissions

Add to always-allowed:

```json
{
  "permissions": {
    "allow": ["Bash(fatigue *)"]
  }
}
```
