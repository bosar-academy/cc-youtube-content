#!/bin/bash
# Install script for Claude Code skills
# Usage: ./install.sh [skill-name]  - install one skill
#        ./install.sh --all         - install all skills

SKILLS_DIR="$HOME/.claude/skills"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

install_skill() {
  local skill="$1"
  local src="$REPO_DIR/skills/$skill"
  local dest="$SKILLS_DIR/$skill"
  
  if [ ! -d "$src" ]; then
    echo "Skill '$skill' not found in this repo."
    return 1
  fi
  
  mkdir -p "$dest"
  cp -r "$src"/* "$dest"/
  echo "Installed: $skill → $dest"
}

if [ "$1" = "--all" ]; then
  for skill_dir in "$REPO_DIR"/skills/*/; do
    skill=$(basename "$skill_dir")
    install_skill "$skill"
  done
  echo "All skills installed."
elif [ -n "$1" ]; then
  install_skill "$1"
else
  echo "Available skills:"
  for skill_dir in "$REPO_DIR"/skills/*/; do
    echo "  - $(basename "$skill_dir")"
  done
  echo ""
  echo "Usage:"
  echo "  ./install.sh <skill-name>   Install a specific skill"
  echo "  ./install.sh --all          Install all skills"
fi
