"""
History parser - reads and processes ~/.claude/history.jsonl
"""

import json
import os
import re
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Iterator


@dataclass
class Prompt:
    """A single user prompt from history."""
    text: str              # Typed text only (pasted content stripped)
    timestamp: datetime
    project: str
    has_paste: bool        # Whether pasted content was present
    raw_display: str       # Original display field


HISTORY_PATH = os.path.expanduser("~/.claude/history.jsonl")

# Pattern to strip pasted text markers
PASTE_PATTERN = re.compile(r'\[Pasted text #\d+ \+\d+ lines\]')
IMAGE_PATTERN = re.compile(r'\[Image #\d+\]')


def strip_paste_markers(text: str) -> str:
    """Remove pasted text and image markers from display text."""
    text = PASTE_PATTERN.sub('', text)
    text = IMAGE_PATTERN.sub('', text)
    return text.strip()


def is_command(text: str) -> bool:
    """Check if text is a slash command or system command."""
    return text.startswith('/') or text.startswith('[')


def read_history(
    limit: int = None,
    days: int = None,
    project: str = None,
    skip_commands: bool = True,
    today_only: bool = False,
    yesterday_only: bool = False
) -> Iterator[Prompt]:
    """
    Read prompts from history file.

    Args:
        limit: Max number of prompts to return
        days: Only include prompts from last N days
        project: Filter by project name (partial match)
        skip_commands: Skip slash commands and system messages
        today_only: Only include prompts from today (since midnight)
        yesterday_only: Only include prompts from yesterday

    Yields:
        Prompt objects
    """
    if not os.path.exists(HISTORY_PATH):
        return

    cutoff_ts = None
    cutoff_end_ts = None

    if today_only:
        # Midnight today
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_ts = today_start.timestamp() * 1000
    elif yesterday_only:
        # Yesterday midnight to today midnight
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today_start - timedelta(days=1)
        cutoff_ts = yesterday_start.timestamp() * 1000
        cutoff_end_ts = today_start.timestamp() * 1000
    elif days:
        cutoff_ts = (datetime.now().timestamp() - days * 86400) * 1000

    count = 0
    with open(HISTORY_PATH, 'r') as f:
        for line in f:
            if limit and count >= limit:
                break

            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            display = entry.get('display', '')
            timestamp = entry.get('timestamp', 0)
            proj = entry.get('project', '')
            pasted = entry.get('pastedContents', {})

            # Skip if before cutoff
            if cutoff_ts and timestamp < cutoff_ts:
                continue

            # Skip if after end cutoff (for yesterday_only)
            if cutoff_end_ts and timestamp >= cutoff_end_ts:
                continue

            # Skip commands
            if skip_commands and is_command(display):
                continue

            # Filter by project
            if project and project.lower() not in proj.lower():
                continue

            # Strip paste markers
            clean_text = strip_paste_markers(display)

            # Skip empty prompts
            if not clean_text:
                continue

            yield Prompt(
                text=clean_text,
                timestamp=datetime.fromtimestamp(timestamp / 1000),
                project=proj,
                has_paste=bool(pasted),
                raw_display=display
            )
            count += 1


def get_all_prompts(**kwargs) -> list[Prompt]:
    """Get all prompts as a list."""
    return list(read_history(**kwargs))


def get_projects() -> list[str]:
    """Get list of unique projects in history."""
    projects = set()
    for prompt in read_history(skip_commands=False):
        if prompt.project:
            projects.add(prompt.project)
    return sorted(projects)
