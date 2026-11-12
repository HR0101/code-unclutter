#!/usr/bin/env bash
# code-unclutter - Unified Installer for Codex, Claude Code, and Gemini
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[INFO] Installing code-unclutter skill..."

TARGET_DIRS=(
  "$HOME/.codex/skills/code-unclutter"
  "$HOME/.claude/skills/code-unclutter"
  "$HOME/.gemini/skills/code-unclutter"
  "$HOME/.agents/skills/code-unclutter"
)

for target in "${TARGET_DIRS[@]}"; do
  echo "[+] Deploying to: $target"
  mkdir -p "$target/scripts" "$target/references"
  cp "$SCRIPT_DIR/SKILL.md" "$target/SKILL.md"
  cp "$SCRIPT_DIR/README.md" "$target/README.md"
  cp -r "$SCRIPT_DIR/scripts/"* "$target/scripts/"
  cp -r "$SCRIPT_DIR/references/"* "$target/references/"
  chmod +x "$target/scripts/"* 2>/dev/null || true
done

echo "[OK] code-unclutter successfully installed to all agent environments."
