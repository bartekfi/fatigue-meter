# Contributing to Prompt Fatigue

Thanks for wanting to help! This tool gets better with community contributions.

## Quick Start

1. **Clone and run**
   ```bash
   git clone https://github.com/bartekfi/fatigue-meter.git
   cd prompt-fatigue
   chmod +x fatigue
   ./fatigue --today
   ```

2. **Make changes**
   - All code is in `fatigue` (main CLI) and `lib/` (modules)
   - No dependencies needed - pure Python 3.10+

3. **Test your changes**
   ```bash
   ./fatigue --today
   ./fatigue --week
   ./fatigue --shame
   ```

## Adding Grunt Patterns (Most Fun!)

The community's best contribution: catching lazy prompt patterns.

Edit `lib/analyzer.py` and add to the `LAZY_PATTERNS` list:

```python
LAZY_PATTERNS = [
    r'^(yes|no|ok|okay|sure)\.?!?$',
    r'^(continue|go|do it)\.?!?$',
    # Add your pattern here!
]
```

Examples of good additions:
- Common typos that indicate rushing ("yeha", "oaky")
- Platform-specific lazy patterns ("yup", "nah")
- Tired language patterns ("just do it", "whatever works")

Use regex or exact strings. Test against your own history to verify.

## Adding Fatigue Signals

Want to track a new energy indicator? Edit `calculate_fatigue_metrics()` in `fatigue`:

```python
def calculate_fatigue_metrics(prompts):
    # Add new metric here
    your_metric = calculate_something(prompts)

    return {
        'avg_length': ...,
        'grunt_ratio': ...,
        'your_metric': your_metric,  # Add to return dict
    }
```

Then update the fatigue calculation to use it.

## Pull Requests

1. **Keep it simple** - This is a single-file CLI tool. No frameworks.
2. **Test with real data** - Run against your own `~/.claude/history.jsonl`
3. **Describe the pattern** - If adding grunt patterns, explain what they catch
4. **No breaking changes** - Keep the CLI API stable

## Style Guide

- Follow the existing code style (simple, direct)
- No defensive coding - fail fast
- Comments explain "why", not "what"
- Keep functions short and readable

## Ideas for Contributions

- New grunt patterns (most welcome!)
- Additional fatigue signals (code quality indicators)
- Output formatting improvements
- Documentation fixes
- Performance optimizations

## Questions?

Open an issue or PR. We're friendly.
