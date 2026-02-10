# Prompt Fatigue

**Are you prompting Claude at your best, or just mashing Enter?**

Track your Claude Code prompting energy levels throughout the day. See when you're sharp, spot when you're fading, and catch yourself before you burn out.

```
energy ██████░░░░ steady (63%)
```

<!-- TODO: Add terminal recording GIF here -->

## Why This Exists

Your prompt quality directly affects Claude's output quality. When you're tired, your prompts get shorter, vaguer, and lazier — and Claude's responses suffer. Prompt Fatigue makes this invisible pattern visible.

No judgment. Just data.

## The Fun Part

```bash
fatigue --shame    # See your laziest prompts (we all have them)
fatigue --pride    # See your best work
```

## Install

### Option A: Claude Code plugin (recommended)

From inside Claude Code, run:

```
/plugin marketplace add bartekfi/fatigue-meter
/plugin install prompt-fatigue@fatigue-meter
```

Then use `/prompt-fatigue:fatigue` or just ask Claude to check your fatigue.

### Option B: Clone + install script

```bash
git clone https://github.com/bartekfi/fatigue-meter.git
cd fatigue-meter
./install.sh
```

### Option C: Manual install as Claude Code skill

```bash
git clone https://github.com/bartekfi/fatigue-meter.git ~/.claude/skills/fatigue
```

Then add to `~/.claude/settings.json`:

```json
{
  "permissions": {
    "allow": ["Bash(~/.claude/skills/fatigue/fatigue:*)"]
  }
}
```

### Option D: pip (for global CLI use)

```bash
pip install git+https://github.com/bartekfi/fatigue-meter.git
```

## Usage

```bash
fatigue --today       # Today's hourly energy levels
fatigue --yesterday   # Yesterday's breakdown
fatigue --week        # This week's daily energy
fatigue --stamina     # GitHub-style quality heatmap
fatigue --trend       # Weekly trend comparison
fatigue --shame       # Hall of shame (laziest prompts)
fatigue --pride       # Hall of fame (best prompts)
fatigue --session     # Energy decay within sessions
fatigue --json        # Raw JSON output
```

## Example Output

```
TODAY'S ENERGY LEVELS
============================================================
Date: 2026-01-15 | Prompts: 42 | Energy: 68%

Hours:  09  10  11  12  13  14  15
Energy: ▇   ▆   █   ▅   ▃   ▁   ▅

Hour    Energy  Len   Grunts  Spec   Bar
-------------------------------------------------------
09:00 🟢  78%   210     5%    2.1   ███████░░░
10:00 🟢  72%   185     8%    1.8   ███████░░░
11:00 🟢  82%   290     3%    3.2   ████████░░
12:00 🟡  58%   120    15%    1.0   █████░░░░░
13:00 🟠  42%    65    35%    0.4   ████░░░░░░
14:00 🔴  18%    22    60%    0.1   █░░░░░░░░░
15:00 🟡  55%   140    12%    1.2   █████░░░░░

😴 FATIGUING: Fatigue 22% → 45% (+23%)
```

## Energy Scale

| Energy | Word | Color | Meaning |
|--------|------|-------|---------|
| 80%+   | sharp | green | Peak focus, detailed prompts |
| 65-80% | focused | green | Good energy, specific requests |
| 50-65% | steady | yellow | Normal, adequate prompts |
| 35-50% | fading | orange | Getting tired, shorter prompts |
| 20-35% | tired | red | Low energy, vague requests |
| <20%   | fried | red | Take a break |

## Status Bar

Add a live energy gauge to your Claude Code status bar:

```json
{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/skills/fatigue/statusline.sh"
  }
}
```

Shows your current energy with a 5-minute cache:

```
energy ████████░░ sharp (82%)
energy ██████░░░░ steady (63%)
energy ████░░░░░░ fading (42%)
```

## How It Works

Prompt Fatigue reads your local Claude Code history (`~/.claude/history.jsonl`) and scores each prompt using heuristics:

**Fatigue signals** (energy reports):
- **Prompt length** — shorter prompts indicate less effort
- **Grunt ratio** — "yes", "ok", "continue" patterns signal fatigue
- **Specificity** — file references and code mentions fade when you're tired

**Quality scoring** (detailed reports):
- **Specificity (25%)** — file paths, code references, inline code
- **Context (25%)** — reasoning markers ("because", "so that")
- **Clarity (20%)** — imperative vs passive language
- **Constraints (15%)** — acceptance criteria markers
- **Verification (15%)** — testing and validation mentions

All processing is **100% local**. No data leaves your machine.

## Requirements

- Python 3.10+
- Claude Code
- macOS or Linux

## Contributing

Contributions welcome! The easiest way to help: **add grunt patterns** you've caught yourself using. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
