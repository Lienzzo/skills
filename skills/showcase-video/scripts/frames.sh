#!/bin/bash
# A real video (the app's splash animation with its alpha, a screen recording, a phone capture) as
# a frame sequence the scenes show with lib.js clipAt(): the clip is part of the page, so it
# appears in every review sheet and the reviewer judges it with everything else. Never composite
# a clip over the render afterwards with ffmpeg: nothing in the loop would see it.
#
#   scripts/frames.sh <video> <src> <name> [--fps n] [--from s] [--to s] [--width px]
#     → <src>/assets/clips/<name>/0001.png …  and  clip.js ({ dir, fps, n, w, h, alpha })
#
# PNG keeps the alpha (HEVC/ProRes 4444 with alpha, WebM VP9 with alpha). --fps defaults to the
# clip's own rate, capped at 60 (clipAt holds each frame until the next). --width scales it down
# to what the scene shows it at, x the render's DSF: a 1600 px splash shown 1180 px wide needs no more.
# Its sound, if any: loadTrack(file, from) in audio.ts, at the same time as clipAt.
set -euo pipefail
[ $# -ge 3 ] || { sed -n '2,12p' "$0"; exit 2; }
IN=$1 SRC=$2 NAME=$3; shift 3
FPS='' FROM=0 TO='' WIDTH=''
while [ $# -gt 0 ]; do
  case $1 in
    --fps) FPS=$2; shift 2 ;;
    --from) FROM=$2; shift 2 ;;
    --to) TO=$2; shift 2 ;;
    --width) WIDTH=$2; shift 2 ;;
    *) echo "unknown option $1" >&2; exit 2 ;;
  esac
done
[ -f "$IN" ] || { echo "no such video: $IN" >&2; exit 1; }
[[ $NAME =~ ^[a-z0-9-]+$ ]] || { echo "name: lower case, digits and dashes only" >&2; exit 1; }
probe() { ffprobe -v error -select_streams v:0 -show_entries stream="$1" -of csv=p=0 "$IN"; }
RATE=$(probe avg_frame_rate) PIX=$(probe pix_fmt)
NATIVE=$(python3 -c "from fractions import Fraction as F; print(round(float(F('$RATE')), 3))")
FPS=${FPS:-$(python3 -c "print(min(60, $NATIVE))")}
OUT="$SRC/assets/clips/$NAME"
rm -rf "$OUT" && mkdir -p "$OUT"
VF="fps=$FPS"
[ -n "$WIDTH" ] && VF="$VF,scale=$WIDTH:-2:flags=lanczos"
ARGS=(-v error -ss "$FROM" -i "$IN")
[ -n "$TO" ] && ARGS+=(-t "$(python3 -c "print($TO - $FROM)")")
# The decoder decides whether alpha survives: probe one frame and say so, instead of silently
# shipping a clip with a black box around it.
ffmpeg "${ARGS[@]}" -vf "$VF,format=rgba" -start_number 1 "$OUT/%04d.png"
N=$(find "$OUT" -name '*.png' | wc -l | tr -d ' ')
[ "$N" -gt 0 ] || { echo "no frames extracted" >&2; exit 1; }
read -r W H < <(magick identify -format '%w %h\n' "$OUT/0001.png")
MID=$(printf '%04d' $(( (N + 1) / 2 )))
AMIN=$(magick "$OUT/$MID.png" -alpha extract -format '%[fx:minima]' info:)
ALPHA=$(python3 -c "print('true' if $AMIN < 0.99 else 'false')")
cat > "$OUT/clip.js" <<EOF
// Written by scripts/frames.sh from $(basename "$IN") ($PIX, $NATIVE fps) — re-run it, don't edit.
export default { dir: 'assets/clips/$NAME', fps: $FPS, n: $N, w: $W, h: $H, alpha: $ALPHA }
EOF
SIZE=$(du -sh "$OUT" | cut -f1)
echo "$OUT: $N frames · ${W}×${H} · $FPS fps · alpha $ALPHA · $SIZE"
if [ "$ALPHA" = false ] && [[ $PIX == yuva* || $PIX == *rgba* || $PIX == *bgra* || $PIX == *argb* || $PIX == *abgr* ]]; then
  echo "warning: the source says $PIX but the frames came out opaque — this ffmpeg build may not decode its alpha" >&2
fi
