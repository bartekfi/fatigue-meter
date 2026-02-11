# Prompt Fatigue

**Are you prompting Claude at your best, or just mashing Enter?**

```
energy ██████░░░░ steady (63%)
```

Prompt Fatigue tracks your energy levels throughout the day by analyzing your Claude Code prompt history. It detects when you're sharp, when you're fading, and when you should probably take a break.

100% local. No data leaves your machine.

<!-- TODO: Add terminal recording GIF here -->

## Install

Inside Claude Code, run:

```
/plugin marketplace add bartekfi/fatigue-meter
/plugin install prompt-fatigue@fatigue-meter
```

That's it. The status bar energy gauge configures itself on next session.

<details>
<summary>Alternative: manual install</summary>

```bash
git clone https://github.com/bartekfi/fatigue-meter.git ~/.claude/skills/fatigue
```

Add to `~/.claude/settings.json`:

```json
{
  "permissions": {
    "allow": ["Bash(~/.claude/skills/fatigue/fatigue:*)"]
  }
}
```
</details>

## Usage

Once installed, just ask Claude: *"check my fatigue"*, *"how's my energy today?"*, or *"show me my laziest prompts"*.

Or invoke directly:

```
fatigue --today       # Today's hourly energy
fatigue --yesterday   # Yesterday's breakdown
fatigue --week        # This week's daily energy
fatigue --shame       # Your laziest prompts
fatigue --pride       # Your best prompts
fatigue --stamina     # Quality heatmap
fatigue --trend       # Weekly trend
fatigue --session     # Energy decay within sessions
```

## What It Looks Like

### Hourly energy breakdown

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

### Hall of shame

Your laziest prompts, ranked. We all have them.

```
Hall of Shame:
  1. "ok do it" (score: 1.0)
  2. "yes" (score: 1.0)
  3. "fix it" (score: 1.5)
  4. "looks good" (score: 1.0)
  5. "can you make it better" (score: 2.1)
```

### Hall of fame

Your most detailed, high-effort prompts.

```
Hall of Fame:
  1. "Refactor the auth middleware in src/middleware/auth.ts to use..." (score: 9.2)
  2. "Add integration tests for the /api/users endpoint. Cover th..." (score: 8.8)
  3. "The build fails on CI because `tsconfig.json` references pa..." (score: 8.5)
```

### Status bar

A live energy gauge at the bottom of Claude Code, updated every 5 minutes:

```
energy ████████░░ sharp (82%)
energy ██████░░░░ steady (63%)
energy ████░░░░░░ fading (42%)
energy ██░░░░░░░░ tired (25%)
```

## Energy Scale

| Energy | Level | Meaning |
|--------|-------|---------|
| 80%+   | 🟢 sharp | Peak focus, detailed prompts |
| 65-80% | 🟢 focused | Good energy, specific requests |
| 50-65% | 🟡 steady | Normal, adequate prompts |
| 35-50% | 🟠 fading | Getting tired, shorter prompts |
| 20-35% | 🔴 tired | Low energy, vague requests |
| <20%   | 🔴 fried | Take a break |

## How Scoring Works

### Energy score (--today, --yesterday, --week)

Three signals, weighted:

| Signal | Weight | What it measures |
|--------|--------|-----------------|
| Prompt length | 40% | Shorter prompts = more fatigued. A 200-char prompt scores much better than a 30-char one. |
| Grunt ratio | 40% | Percentage of "yes", "ok", "continue", "do it" and other low-effort patterns. Also catches anything under 15 characters. |
| Specificity | 20% | File references (`auth.ts`), inline code (`` `foo()` ``), and `@mentions`. These disappear when you're tired. |

The formula: `energy = 100 - (length_fatigue * 0.4 + grunt_fatigue * 0.4 + specificity_fatigue * 0.2)`

### Quality score (--shame, --pride, --stamina)

A 1-10 score with five dimensions:

| Dimension | Weight | Positive signals |
|-----------|--------|-----------------|
| Specificity | 25% | File paths, code refs, inline code, URLs, CamelCase/snake_case identifiers |
| Context | 25% | "because", "so that", "in order to", "the goal is" |
| Clarity | 20% | Imperative language ("add", "fix", "refactor") vs passive ("can you", "would it be") |
| Constraints | 15% | "should", "must", "ensure", "make sure", "validate" |
| Verification | 15% | "test", "verify", "assert", "should pass", "build" |

**Penalties** for hedge words ("maybe", "probably", "just", "quick") and vague terms ("make it better", "fix it", "whatever").

**Bonuses** for structure (bullet points, numbered lists) and reasonable length (30+ words).

### What counts as a grunt?

These patterns score a flat 1.0 — the lowest possible:

```
yes, no, ok, okay, sure, yep, nope, continue, go, do it,
good, great, nice, cool, fine, perfect, awesome, thanks,
let's do it, let's go, sounds good, looks good
```

Plus any single-character response, bare numbers, and one-word questions.

## Requirements

- Python 3.10+
- Claude Code
- macOS or Linux

## Contributing

The easiest way to help: **add grunt patterns** you've caught yourself using. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
