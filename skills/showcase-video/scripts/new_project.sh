#!/usr/bin/env bash
# Scaffold a showcase video project from the skill's template.
# Usage: new_project.sh <project-dir> [--explainer]     e.g. new_project.sh ~/Videos/acme-showcase
#   --explainer: a narrated film (references/explainer.md): the voice-driven timeline.js and
#   audio.ts, voice.js and a VO.md script to replace.
# Creates <project-dir>/src (the code) — deliverables go to <project-dir>/v1, v2… later.
# For a new VERSION of an existing video, copy that version's src instead (cp -r v1/src v2/src).
set -euo pipefail
DIR=${1:?usage: new_project.sh <project-dir> [--explainer]}
MODE=${2:-}
SRC="$DIR/src"
[ -e "$SRC" ] && { echo "$SRC already exists — not overwriting (earlier versions stay intact)"; exit 1; }
mkdir -p "$DIR"
cp -r "$(dirname "$0")/../template" "$SRC"
if [ "$MODE" = "--explainer" ]; then
  cp "$SRC"/explainer/* "$SRC"/
else
  rm "$SRC/voice.js"
fi
rm -r "$SRC/explainer"
mkdir -p "$SRC/out" "$DIR/refs"
chmod +x "$SRC"/*.sh
# The code is versioned with git: commit + tag each delivered version (git tag v2) so any
# earlier cut can be rebuilt exactly, while its mp4s stay untouched in <project-dir>/vN/.
printf 'out/\n' > "$SRC/.gitignore"
git -C "$SRC" init -q && git -C "$SRC" add -A && git -C "$SRC" commit -qm "Template" && echo "git: initialised $SRC"
missing=()
for c in node bun ffmpeg ffprobe magick uv; do command -v $c >/dev/null || missing+=($c); done
[ ${#missing[@]} -gt 0 ] && echo "missing tools: ${missing[*]}"
command -v node >/dev/null && (cd "$SRC" && node pw.mjs) || true
if [ "$MODE" = "--explainer" ]; then
  echo "$SRC ready (narrated). First the takes: python3 $(cd "$(dirname "$0")" && pwd)/vo.py build $SRC --provider say (scratch; ElevenLabs without --provider)"
  echo "Then: cd $SRC && REPORT=1 bun audio.ts && node render.mjs review"
else
  echo "$SRC ready. Smoke test: cd $SRC && node render.mjs sheet 0 2 3.9 5.5 7 8.6 10.6 12.5 && node render.mjs review"
fi
