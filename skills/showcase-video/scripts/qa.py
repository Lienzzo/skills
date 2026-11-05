#!/usr/bin/env python3
"""Automated QA of a rendered video against its timeline — the machine half of the final
review, run on the actual file (the join, the encode and the audio mux only exist there).

    qa.py <video.mp4|mkv> <src-dir>

Blockers (exit 1 until resolved):
  ✗ frame 0 black or an empty background (it is the thumbnail chat apps and X show)
  ✗ a narrated film (timeline.js VOICE_PROVIDER) still on the scratch voice (`say`)
  ✗ frame count ≠ DURATION × FPS (a bad segment join doubles or truncates), wrong resolution,
    colour not tagged bt709 (mp4), no audio (mp4), loudness outside −14 ±1 LUFS (timeline.js LOUDNESS: −16 in narrated films), true peak > −1 dBTP
  ✗ moments to review: discontinuities (a frame that changes far more than its neighbours:
    jumps, pops, stray cuts) and near-black stretches that are not planned. An instant change is
    planned at a SCENES boundary (±0.12 s), at a cut of a montage scene ({montage: [T.c1, …]}),
    or in timeline.js `INTENDED`: [{ at: T.flash, why: 'the flash' }, { at: T.a, to: T.b, why:
    'verdicts land one by one' }] (cues, so it survives re-timing; a bare T.flash works too).
    A near-black stretch is planned only if it is short (≤ 0.5 s) at a cut, or inside an
    INTENDED range: a 4 s black that starts on a cut is a bug, not a cut. A scene marked
    {montage: true} without its cuts lists its changes as notes (with filmstrips), not blockers.
    Each gets a filmstrip from the file in <src>/out/qa/<name>/: look at it, then fix the bug
    or add it to INTENDED. INTENDED entries that match nothing are listed (stale after a re-time?). A polished 84 s video had ~35 on its first pass — mostly
    instant UI changes (a modal opening, a flash), and that is the point: every instant
    change should be one you meant.
Notes: frozen stretches ≥ 2.5 s, silences ≥ 0.6 s.
Also writes a 1 fps contact sheet of the whole file.
"""
import json, math, os, re, shutil, subprocess, sys

def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)

if len(sys.argv) < 3:
    print(__doc__); sys.exit(2)
video, src = sys.argv[1], sys.argv[2]
name = os.path.splitext(os.path.basename(video))[0]
out = os.path.join(src, 'out', 'qa', name)
shutil.rmtree(out, ignore_errors=True); os.makedirs(out)

TL_JS = "import('./timeline.js').then(m => console.log(JSON.stringify({D: m.DURATION, F: m.FPS, W: m.W, H: m.H, S: m.SCENES || null, I: m.INTENDED || [], fade: (m.T && m.T.fadeOut) || null, VP: m.VOICE_PROVIDER || null, LU: m.LOUDNESS ?? -14})))"
tl = json.loads(run(['node', '-e', TL_JS], cwd=src).stdout)
blockers, notes, review = [], [], []
def ok(msg): print(f'✓ {msg}')
def bad(msg): blockers.append(msg); print(f'✗ {msg}')
def note(msg): notes.append(msg); print(f'• {msg}')
if tl.get('VP') == 'say':
    bad('narration is the scratch voice (vo.py --provider say): fine for timing, never for delivery. Regenerate with `vo.py build <src>` (ElevenLabs) or record it (--provider file)')
elif tl.get('VP'):
    ok(f"narration: {tl['VP']}")

# ── stream facts ───────────────────────────────────────────────────────────────
v = json.loads(run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_packets', '-show_entries', 'stream=width,height,color_space,nb_read_packets', '-of', 'json', video]).stdout)['streams'][0]
dur = float(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', video]).stdout)
has_audio = bool(run(['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=index', '-of', 'csv=p=0', video]).stdout.strip())
want = round(tl['D'] * tl['F'])
n = int(v['nb_read_packets'])
(ok if n == want else bad)(f'frames {n} (timeline {want}) · {dur:.2f} s')
(ok if (v['width'], v['height']) == (tl['W'], tl['H']) else bad)(f"resolution {v['width']}×{v['height']}")

# ── the first frames are the thumbnail ─────────────────────────────────────────
# Chat apps, X and Threads show frame 0 until the video plays: it must be a finished image,
# not black (a fade-in) or an empty background. Saved as frame0.png: judge its composition too.
# Measured on frame 0 at 384×216 grey: the share of pixels away from the dominant (background)
# level. A logo or a headline on black is ~1–6 % of the frame; an empty or black frame is ~0 %.
g = subprocess.run(['ffmpeg', '-v', 'error', '-i', video, '-frames:v', '1', '-vf', 'scale=384:216,format=gray', '-f', 'rawvideo', '-'], capture_output=True).stdout
run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', video, '-frames:v', '1', '-update', '1', os.path.join(out, 'frame0.png')])
if len(g) < 384 * 216:
    note('first frame: could not measure')
else:
    hist = [0] * 256
    for px in g: hist[px] += 1
    bg = max(range(256), key=hist.__getitem__)
    share = sum(c for lv, c in enumerate(hist) if abs(lv - bg) > 16) / len(g)
    if share < 0.002:
        bad(f"frame 0 is {'black or a dark empty background' if bg < 40 else 'an empty background'} ({share:.2%} of it differs from the background): it is the thumbnail, open on a finished image")
    else:
        ok(f'frame 0 has content ({share:.1%} off the background) — judge the thumbnail: {os.path.join(out, "frame0.png")}')
if video.endswith('.mp4'):
    (ok if v.get('color_space') == 'bt709' else bad)(f"colour {v.get('color_space', 'untagged')}")

# ── what counts as planned ─────────────────────────────────────────────────────
scenes = tl['S'] or []
bounds = {s[1] for s in scenes} | {s[2] for s in scenes}
opts = [(s[0], s[1], s[2], s[3]) for s in scenes if len(s) > 3 and isinstance(s[3], dict)]
for sid, a, b, o in opts:  # a montage's own cuts count as cuts
    if isinstance(o.get('montage'), list):
        bounds |= {float(c) for c in o['montage']}
loose_montage = [(sid, a, b) for sid, a, b, o in opts if o.get('montage') is True]
intended = []  # (from, to, why)
for x in tl['I']:
    if isinstance(x, (int, float)):
        intended.append((float(x), float(x), ''))
    elif isinstance(x, dict) and isinstance(x.get('at'), (int, float)):
        intended.append((float(x['at']), float(x.get('to', x['at'])), str(x.get('why', ''))))
    else:
        bad(f'INTENDED entry not understood: {x!r} — a cue (T.flash) or {{ at, to?, why }}')
matched = set()
def planned(t, end=None):
    """An instant change at t, or (with end) a near-black stretch t–end."""
    for k, (a, b, _) in enumerate(intended):
        if a - 0.12 <= t <= b + 0.12 and (end is None or end <= b + 0.12 or a == b and end - t <= 0.5):
            matched.add(k)
            return True
    return any(abs(t - c) <= 0.12 for c in bounds) and (end is None or end - t <= 0.5)
if not scenes:
    note('timeline.js exports no SCENES: every discontinuity is listed for review')

# ── discontinuities: a frame that changes far more than its neighbours ────────
# Continuous motion changes a little every frame; a jump spikes against the local median
# (a 260 px jump of a dark UI scored 0.02 — 40× its neighbours, far below the usual 0.3 cut threshold).
log = run(['ffmpeg', '-hide_banner', '-i', video, '-an', '-vf', "scale=480:-2,select='gte(scene,0)',metadata=print:key=lavfi.scene_score", '-f', 'null', '-']).stderr
ts = [float(x) for x in re.findall(r'pts_time:([\d.]+)', log)]
sc = [float(x) for x in re.findall(r'lavfi.scene_score=([\d.]+)', log)]
events = []
for i, (t, x) in enumerate(zip(ts, sc)):
    around = sorted(sc[max(0, i - 30):i] + sc[i + 1:i + 31]) or [0]
    if x > 0.3 or (x > 0.006 and x > 10 * max(around[len(around) // 2], 0.0004)):
        if events and t - events[-1][1] <= 0.1:
            events[-1][1] = t
        else:
            events.append([t, t])
in_montage = lambda t: next((sid for sid, a, b in loose_montage if a <= t <= b), None)
montage_notes = [(a, b, in_montage(a)) for a, b in events if not planned(a) and in_montage(a)]
review += [('discontinuity', a, b) for a, b in events if not planned(a) and not in_montage(a)]

# ── near-black stretches outside the opening fade-in and the closing fade-out ─
log = run(['ffmpeg', '-hide_banner', '-i', video, '-an', '-vf', 'scale=480:-2,blackdetect=d=0.05:pix_th=0.06', '-f', 'null', '-']).stderr
fade_out = (tl['fade'] or [tl['D'] - 1.5])[0]
for a, b in re.findall(r'black_start:([\d.]+) black_end:([\d.]+)', log):
    a, b = float(a), float(b)
    if b > 0.6 and a < fade_out - 0.05 and not planned(a, b):
        review.append(('near-black', a, b))

# ── a filmstrip from the file for every moment to review ───────────────────────
for kind, a, b in review + [('montage', a, b) for a, b, _ in montage_notes]:
    t0 = max(0, a - 0.25)
    strip = os.path.join(out, f'{a:07.2f}-{kind}.png')
    frames = max(10, min(20, round((b - a + 0.5) * 20)))
    # (no -copyts: with it, -t counts from the absolute timestamp and writes nothing; drawtext adds t0 instead)
    vf = f"fps=20,scale=384:-2,drawtext=text='%{{pts\\:flt\\:{t0:.3f}}}':x=4:y=h-20:fontsize=14:fontcolor=white:box=1:boxcolor=black@0.6,tile={frames}x1"
    r = run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-ss', f'{t0:.3f}', '-i', video, '-t', f'{frames / 20:.2f}', '-vf', vf, '-frames:v', '1', '-update', '1', strip])
    if r.returncode or not os.path.exists(strip):
        run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-ss', f'{t0:.3f}', '-i', video, '-t', f'{frames / 20:.2f}', '-vf', f'fps=20,scale=384:-2,tile={frames}x1', '-frames:v', '1', '-update', '1', strip])
if review:
    bad(f'{len(review)} unplanned moment(s) to review — filmstrips (20 fps, from 0.25 s before) in {out}:')
    for kind, a, b in review:
        print(f'    {a:6.2f}–{b:6.2f} s  {kind}')
    print("    fix each bug; add each intended one to INTENDED in timeline.js, by cue and with its reason: { at: T.modal, why: 'modal opens' } (or { at, to, why } for a run)")
else:
    ok(f'no unplanned discontinuities or near-black stretches ({len(events)} discontinuities, all planned)')
for a, b, sid in montage_notes:
    note(f'{a:.2f} s change inside montage scene `{sid}`: one of its cuts? (filmstrip in {out}; list the cuts as {{montage: [T.c1, …]}} to check them)')
for k, (a, b, why) in enumerate(intended):
    if k not in matched:
        note(f"INTENDED {a:.2f}{f'–{b:.2f}' if b != a else ''} s{f' ({why})' if why else ''} matched no detected change: stale after a re-time (remove it), or a change too small for the detector (keep it)")

# ── frozen stretches ───────────────────────────────────────────────────────────
log = run(['ffmpeg', '-hide_banner', '-i', video, '-an', '-vf', 'scale=480:-2,freezedetect=n=0.0015:d=2.5', '-f', 'null', '-']).stderr
starts = [float(x) for x in re.findall(r'freeze_start: ([\d.]+)', log)]
ends = [float(x) for x in re.findall(r'freeze_end: ([\d.]+)', log)] + [dur]
for a, b in zip(starts, ends):
    note(f'frozen {a:.2f}–{b:.2f} s ({b - a:.1f} s): an intended hold, or a scene that stalls?')

# ── audio ──────────────────────────────────────────────────────────────────────
if has_audio:
    log = run(['ffmpeg', '-hide_banner', '-nostats', '-i', video, '-vn', '-af', 'ebur128=peak=true:framelog=quiet', '-f', 'null', '-']).stderr
    I = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', log)[-1])
    TP = float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS', log)[-1])
    (ok if abs(I - tl['LU']) <= 1 else bad)(f"loudness {I} LUFS (target {tl['LU']})")
    (ok if TP <= -0.9 else bad)(f'true peak {TP} dBTP (max −1)')
    log = run(['ffmpeg', '-hide_banner', '-i', video, '-vn', '-af', 'silencedetect=noise=-50dB:d=0.6', '-f', 'null', '-']).stderr
    for a, b in re.findall(r'silence_start: ([\d.]+)[\s\S]*?silence_end: ([\d.]+)', log):
        a, b = float(a), float(b)
        if a > 0.3 and b < dur - 0.3:
            note(f'silence {a:.2f}–{b:.2f} s: an intended breath?')
elif video.endswith('.mp4'):
    bad('no audio stream')
else:
    print('· no audio in this render: loudness and peaks are checked on the finalized mp4')

# ── contact sheet of the whole file ────────────────────────────────────────────
sheet = os.path.join(out, 'sheet-1fps.png')
cols, rows = 8, math.ceil(dur / 8)
vf = f"fps=1,scale=320:-2,drawtext=text='%{{eif\\:t\\:d}} s':x=6:y=h-24:fontsize=16:fontcolor=white:box=1:boxcolor=black@0.6,tile={cols}x{rows}"
if run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', video, '-vf', vf, '-frames:v', '1', '-update', '1', sheet]).returncode:
    run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', video, '-vf', f'fps=1,scale=320:-2,tile={cols}x{rows}', '-frames:v', '1', '-update', '1', sheet])
print(f'\nwhole-file sheet (1 tile per second): {sheet}')
print(f'{len(blockers)} blocker(s), {len(notes)} note(s)')
sys.exit(1 if blockers else 0)
