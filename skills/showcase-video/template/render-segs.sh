#!/usr/bin/env bash
# Resumable render: 12 s segments, each marked out/<name>-seg-NN.ok once complete.
# Re-running skips finished segments, so a watchdog stop, a crash or a reboot resumes
# where it stopped. A stopped segment is retried with fewer workers.
# Each .ok records a fingerprint of everything the picture depends on (code, styles, assets,
# vo.js: not the audio) plus the segment's bounds: after any change every segment re-renders,
# so a re-timed voice can never be joined to frames of the old timing. KEEP_SEGS=1 trusts the
# existing .ok files (only when you know the change touched none of them).
# Usage: ./render-segs.sh [name=video] [workers=2] [dsf=2]   (SEG=12 to change length)
set -u
cd "$(dirname "$0")"
NAME=${1:-video}; W0=${2:-2}; DSF=${3:-2}; SEG=${SEG:-12}
mkdir -p out
read -r DUR FPS < <(node -e "import('./timeline.js').then(m => console.log(m.DURATION, m.FPS))")
FP=$(set -o pipefail; { find . \( -path ./out -o -path ./.git -o -path ./node_modules -o -path ./assets/vo \) -prune -o -type f \
  ! -name '*.ts' ! -name '*.md' ! -name '*.sh' -print0 | LC_ALL=C sort -z | xargs -0 shasum && echo "${FORMAT:-} $DSF"; } | shasum | cut -c1-16) \
  || { echo "could not fingerprint the sources (unreadable file?)"; exit 1; }
segs=()
while read -r i a b <&3; do
  n=$(printf "%s-seg-%02d" "$NAME" "$i")
  segs+=("$n")
  if [ -f "out/$n.mkv" ] && [ -f "out/$n.ok" ] && { [ -n "${KEEP_SEGS:-}" ] || [ "$(cat "out/$n.ok")" = "$FP $a $b" ]; }; then echo "$n done"; continue; fi
  ok=
  for workers in $W0 $(seq $((W0 - 1)) -1 1) 1 1; do
    rm -f "out/$n.mkv" out/"$n"-chunk-*.mkv
    node render.mjs render --workers "$workers" --dsf "$DSF" --from "$a" --to "$b" --name "$n" > "out/$n.log" 2>&1 &
    pid=$!
    ./watchdog.sh $pid >> "out/$n.log" 2>&1
    wait $pid 2>/dev/null
    if grep -q "page error" "out/$n.log"; then echo "$n: page errors, see out/$n.log"; exit 1; fi
    if grep -q "rendered .* frames" "out/$n.log" && [ -f "out/$n.mkv" ]; then echo "$FP $a $b" > "out/$n.ok"; echo "$n rendered ($workers workers)"; ok=1; break; fi
    echo "$n interrupted, retrying with fewer workers"; sleep 30
  done
  [ -n "$ok" ] || { echo "$n FAILED"; exit 1; }
done 3< <(node -e "for (let a = 0, i = 0; a < $DUR - 1e-9; a += $SEG, i++) console.log(i, a, Math.min($DUR, a + $SEG))")
# Join exactly this run's segments: leftovers from a longer earlier cut are not on the list
# (a looser glob also matches chunk files and doubles the video).
printf "file '$PWD/out/%s.mkv'\n" "${segs[@]}" > "out/$NAME-segs.txt"
ffmpeg -y -loglevel error -f concat -safe 0 -i "out/$NAME-segs.txt" -c copy "out/$NAME.mkv"
got=$(ffprobe -v error -select_streams v:0 -count_packets -show_entries stream=nb_read_packets -of csv=p=0 "out/$NAME.mkv")
want=$(node -e "console.log(Math.round($DUR * $FPS))")
if [ "$got" = "$want" ]; then echo "out/$NAME.mkv: $got frames ✓"; else echo "out/$NAME.mkv: $got frames, expected $want ✗"; exit 1; fi
