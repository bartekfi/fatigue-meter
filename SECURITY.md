# Security Policy

## Data Handling

Prompt Fatigue is a **100% local tool**. It makes zero network calls.

- **Reads**: `~/.claude/history.jsonl` (read-only, never modified)
- **Writes**: `data/scores.db` (local SQLite database with prompt previews -- first 100 characters of each prompt)
- **Caches**: `/tmp/claude-fatigue-status` (statusline cache, auto-expires)

Your prompt history never leaves your machine.

## Reporting a Vulnerability

If you find a security issue, please open a GitHub issue or email the maintainers directly. Since this is a local-only tool, most security concerns would be around:

- Unintended data exposure in the SQLite database
- Path traversal in history file reading
- Script injection via prompt content

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |
