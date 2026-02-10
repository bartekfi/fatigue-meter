#!/bin/bash
# Prompt Fatigue installer for Claude Code
set -e

INSTALL_DIR="$HOME/.claude/skills/fatigue"

echo "Installing prompt-fatigue to $INSTALL_DIR..."

# Create skill directory
mkdir -p "$INSTALL_DIR/lib"

# Copy only necessary files (not .git, __pycache__, etc.)
cp fatigue "$INSTALL_DIR/"
cp statusline.sh "$INSTALL_DIR/"
cp lib/__init__.py lib/analyzer.py lib/history.py lib/storage.py lib/report.py "$INSTALL_DIR/lib/"
cp SKILL.md "$INSTALL_DIR/"

# Set permissions
chmod +x "$INSTALL_DIR/fatigue"
chmod +x "$INSTALL_DIR/statusline.sh"

echo ""
echo "Installed! Now add to ~/.claude/settings.json:"
echo ""
echo '  "permissions": {'
echo '    "allow": ["Bash(~/.claude/skills/fatigue/fatigue:*)"]'
echo '  }'
echo ""
echo "Optional status bar:"
echo ""
echo '  "statusLine": {'
echo '    "type": "command",'
echo '    "command": "~/.claude/skills/fatigue/statusline.sh"'
echo '  }'
echo ""
echo "Restart Claude Code, then try: fatigue --today"
