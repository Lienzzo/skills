#!/usr/bin/env bash
# Soundtrack → mastered WAV (−14 LUFS integrated, true peak ≤ −2 dBTP so the AAC encode,
# which lifts peaks by up to ~1 dB, still stays under qa.py's −1 dBTP), then the deliverables into $DEST:
#   <name>.mp4 (master, crf 17) · <name>-web.mp4 (crf 22) · <name>-share.mp4 (720p, ≤ SHARE_MB, for chat apps)
# Usage: SRC=out/video.mkv NAME=product-showcase-v2 DEST=../v2 ./finalize.sh
# Takes minutes (three slow encodes): run it in the background.
# Refuses to overwrite existing deliverables (earlier versions stay side by side) unless FORCE=1.
# Each file is written as .part and renamed when complete, so an interrupted run never leaves a
# truncated deliverable: RESUME=1 re-runs the same version and skips the files already done.
set -euo pipefail
cd "$(dirname "$0")"
SRC=${SRC:-out/video.mkv}; NAME=${NAME:-showcase}; DEST=${DEST:-out}; SHARE_MB=${SHARE_MB:-15}
mkdir -p "$DEST"
for f in "$DEST/$NAME.mp4" "$DEST/$NAME-web.mp4" "$DEST/$NAME-share.mp4"; do
  [ -e "$f" ] && [ -z "${FORCE:-}${RESUME:-}" ] && { echo "$f exists — pick a new NAME/DEST (RESUME=1 to finish an interrupted run of this version, FORCE=1 to redo it)"; exit 1; }
done
todo() { [ -n "${FORCE:-}" ] || [ ! -e "$1" ] || { echo "$1 already done"; return 1; }; }

bun audio.ts >/dev/null
# Mastering. Linear gain when the peaks allow it (keeps the intro-to-drop contrast). When they
# don't — hits far above the bed, the usual case with synthesized SFX — linear gain alone stops
# short of −14 LUFS (a past film came out at −17.5). Then a look-ahead limiter at 4× oversampling
# (so it limits true peaks, not just samples) catches only those peaks, with its delay
# compensated (latency=1: sound stays on its frame), and the gain is corrected until −14 ±0.3.
measure() {
  local M; M=$(ffmpeg -hide_banner -nostats -i "$1" -af ebur128=peak=true:framelog=quiet -f null - 2>&1)
  I=$(echo "$M" | grep -m1 " I:" | awk '{print $2}')
  TP=$(echo "$M" | grep -A1 "True peak" | grep Peak | awk '{print $2}')
}
CEIL=-2.0
measure out/audio_raw.wav
G=$(python3 -c "print(round(-14-($I),2))")
if python3 -c "import sys; sys.exit(0 if ($TP)+($G) <= $CEIL else 1)"; then
  ffmpeg -hide_banner -loglevel error -y -i out/audio_raw.wav -af "volume=${G}dB" -c:a pcm_s24le out/audio.wav
  measure out/audio.wav
  echo "master: linear gain ${G} dB → ${I} LUFS, ${TP} dBTP"
else
  TP0=$TP
  LIM=$(python3 -c "print(round(10**(($CEIL-0.4)/20),4))")
  for k in 1 2 3 4; do
    ffmpeg -hide_banner -loglevel error -y -i out/audio_raw.wav \
      -af "volume=${G}dB,aresample=192000,alimiter=limit=${LIM}:attack=2:release=60:level=0:latency=1,aresample=48000" \
      -c:a pcm_s24le out/audio.wav
    measure out/audio.wav
    python3 -c "import sys; sys.exit(0 if abs(-14-($I)) <= 0.3 else 1)" && break
    G=$(python3 -c "print(round(($G)+(-14-($I)),2))")
  done
  GR=$(python3 -c "print(round(($TP0)+($G)-($TP),1))")
  echo "master: gain ${G} dB + limiter (−${GR} dB on the loudest peaks) → ${I} LUFS, ${TP} dBTP"
  python3 -c "import sys; sys.exit(0 if ($GR) <= 6 else 1)" || echo "warning: the limiter takes ${GR} dB off the loudest hits, so they lose their punch. Lower those SFX in audio.ts (REPORT=1 shows which) and rerun."
fi
python3 -c "import sys; sys.exit(0 if abs(-14-($I)) <= 0.5 and ($TP) <= -1.5 else 1)" \
  || { echo "master out of spec (${I} LUFS, ${TP} dBTP): the mix is too spiky — lower the loudest SFX in audio.ts (REPORT=1)"; exit 1; }

# Chunks were converted RGB→YUV with swscale's default (BT.601): re-matrix to BT.709 and tag it,
# otherwise colours shift slightly in browsers/players.
VF="scale=in_color_matrix=bt601:out_color_matrix=bt709:in_range=tv:out_range=tv,format=yuv420p"
TAGS=(-colorspace bt709 -color_primaries bt709 -color_trc bt709)
F="$DEST/$NAME.mp4"
if todo "$F"; then
  ffmpeg -hide_banner -loglevel error -y -i "$SRC" -i out/audio.wav -map 0:v -map 1:a -vf "$VF" \
    -c:v libx264 -preset slow -crf 17 -tune grain -profile:v high -level 4.2 -g 120 "${TAGS[@]}" \
    -c:a aac -b:a 320k -ar 48000 -shortest -movflags +faststart -f mp4 "$F.part"
  mv "$F.part" "$F"
fi
F="$DEST/$NAME-web.mp4"
if todo "$F"; then
  ffmpeg -hide_banner -loglevel error -y -i "$SRC" -i out/audio.wav -map 0:v -map 1:a -vf "$VF" \
    -c:v libx264 -preset slow -crf 22 -aq-mode 3 -profile:v high -level 4.2 -g 120 "${TAGS[@]}" \
    -c:a aac -b:a 256k -ar 48000 -shortest -movflags +faststart -f mp4 "$F.part"
  mv "$F.part" "$F"
fi
# Share copy: 2-pass to a size budget (WhatsApp-style limits recompress or refuse big files),
# long edge 1280 px whatever the format (720p landscape, 720×1280 vertical, 1280² square).
F="$DEST/$NAME-share.mp4"
if todo "$F"; then
  DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$SRC")
  VK=$(python3 -c "print(max(300, int($SHARE_MB * 8192 * 0.96 / $DUR - 128)))")
  SC="scale='if(gte(iw,ih),1280,-2)':'if(gte(iw,ih),-2,1280)':flags=lanczos"
  P=$(mktemp -u out/pass-XXXX)
  ffmpeg -hide_banner -loglevel error -y -i "$SRC" -vf "$VF,$SC" -c:v libx264 -preset slow -b:v ${VK}k -pass 1 -passlogfile "$P" -an -f null /dev/null
  ffmpeg -hide_banner -loglevel error -y -i "$SRC" -i out/audio.wav -map 0:v -map 1:a -vf "$VF,$SC" \
    -c:v libx264 -preset slow -b:v ${VK}k -pass 2 -passlogfile "$P" "${TAGS[@]}" \
    -c:a aac -b:a 128k -ar 48000 -shortest -movflags +faststart -f mp4 "$F.part"
  mv "$F.part" "$F"
  rm -f "$P"*
fi
ls -lh "$DEST/$NAME.mp4" "$DEST/$NAME-web.mp4" "$DEST/$NAME-share.mp4"
