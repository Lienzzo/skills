#!/usr/bin/env bash
# Contact sheet of every asset a video will use, each labelled with what it is and where it
# comes from — shown to the user for approval before building.
# Usage: asset_sheet.sh out.png "file|label" "file|label" …
#   e.g. asset_sheet.sh refs/assets.png "src/assets/logo-source.png|Logo · repo public/logo.svg" \
#        "src/assets/appstore-es.svg|App Store badge ES · official"
set -euo pipefail
OUT=${1:?usage: asset_sheet.sh out.png "file|label" …}; shift
args=()
for item in "$@"; do
  f=${item%%|*}; l=${item#*|}; [ "$l" = "$item" ] && l=$(basename "$f")
  [ -e "$f" ] || { echo "missing: $f"; exit 1; }
  args+=("$f|$l")
done
# Rasterise SVGs (logos, store badges) first: an <img> of an SVG with no size can come out blank.
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
for i in "${!args[@]}"; do
  f=${args[$i]%%|*}
  case "$f" in *.svg) magick -background none -density 300 "$f" -resize 840x560 "$tmp/$i.png" && args[$i]="$tmp/$i.png|${args[$i]#*|}" ;; esac
done
# Labels are drawn by Chromium (montage.mjs): ImageMagick builds without FreeType drop them silently.
node "$(dirname "$0")/../template/montage.mjs" "$OUT" --cols 4 --fit 420x280 --caption "${args[@]}"
