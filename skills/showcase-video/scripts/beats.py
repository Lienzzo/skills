# /// script
# dependencies = ["librosa>=0.10", "numpy", "soundfile"]
# ///
"""Measure a supplied music track (licensed, or the client's own) so the film cuts on ITS
grid instead of an assumed 120 BPM: tempo, the first downbeat, every bar line, and where the
energy changes (sections, breaths).

    uv run beats.py <track.wav|mp3|m4a> [--jump 3] > assets/beats.json

→ {"bpm", "offset" (first downbeat, s), "bar" (s), "beats": […], "downbeats": […],
   "bars": [{"t", "db"}…] (loudness per bar), "sections": [t…] (bars where it jumps ≥ 2 dB),
   "breaths": [t…] (bars ≥ 6 dB under their neighbours)}
Assumes one steady tempo (library and synthesized music): it fits a single grid to the attacks.
A summary goes to stderr. The downbeat is a heuristic (the beat phase with the most low-end
attack), and tempo can come out halved or doubled: check a few bar lines against the waveform
or with the user before cutting on them.
"""
import json, sys
import numpy as np, librosa

args = sys.argv[1:]
if not args:
    print(__doc__, file=sys.stderr); sys.exit(2)
path = args[0]
jump = float(args[args.index('--jump') + 1]) if '--jump' in args else 2

y, sr = librosa.load(path, sr=None, mono=True)
dur = len(y) / sr
env = librosa.onset.onset_strength(y=y, sr=sr)
et = librosa.times_like(env, sr=sr)
# Downbeat cues: chords change on the downbeat (chroma), and the low end hits there.
S = np.abs(librosa.stft(y))
st = librosa.times_like(S, sr=sr)
chroma = librosa.feature.chroma_stft(S=S**2, sr=sr)
lowS = S[librosa.fft_frequencies(sr=sr) < 150].sum(axis=0)
low = np.maximum(0, np.diff(lowS, prepend=lowS[0]))

# Library and synthesized music keeps one tempo: fit ONE uniform grid (tempo + phase) to the
# attacks instead of trusting beat-by-beat tracking, which skips beats and drifts bar lines.
t0 = float(np.atleast_1d(librosa.feature.tempo(onset_envelope=env, sr=sr))[0])
def fit(bpms):
    best = (-1, 0, 0)
    for bpm in bpms:
        p = 60 / bpm
        for off in np.arange(0, p, 0.004):
            sc = np.interp(np.arange(off, dur, p), et, env).mean()
            if sc > best[0]:
                best = (sc, bpm, off)
    return best
_, bpm, off = fit(np.arange(t0 * 0.97, t0 * 1.03, 0.1))
_, bpm, off = fit(np.arange(bpm - 0.1, bpm + 0.1, 0.005))
beat = 60 / bpm
beats = np.arange(off, dur, beat)
if len(beats) < 8:
    print('too few beats: is this a rhythmic track?', file=sys.stderr); sys.exit(1)
def change(t):  # harmonic change across t: 1 − cosine(chroma one beat before, one beat after)
    a = chroma[:, (st >= t - beat) & (st < t)].mean(axis=1)
    b = chroma[:, (st >= t) & (st < t + beat)].mean(axis=1)
    return 1 - a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9)
inner = [t for t in beats if t > beat and t < dur - beat]
hc = np.array([change(t) for t in inner])
lo = np.interp(inner, st, low)
cue = hc / (hc.mean() + 1e-9) + 0.5 * lo / (lo.mean() + 1e-9)
k0 = int(np.searchsorted(beats, inner[0]))  # inner[i] is beats[k0 + i]
phase = int(np.argmax([cue[[i for i in range(len(inner)) if (k0 + i) % 4 == p]].mean() for p in range(4)]))
downbeats = beats[phase::4]
downbeats = downbeats[downbeats < dur - beat / 2]  # no bar line in the trailing silence
bar = 4 * beat

# Loudness per bar (RMS in dB) → sections (big jumps) and breaths (dips).
rms = librosa.feature.rms(y=y)[0]
rt = librosa.frames_to_time(np.arange(len(rms)), sr=sr)
bars = []
for a in downbeats:
    m = (rt >= a) & (rt < a + bar)
    bars.append({'t': round(float(a), 3), 'db': round(float(20 * np.log10(rms[m].mean() + 1e-9)), 1) if m.any() else None})
dbs = [b['db'] if b['db'] is not None else -120 for b in bars]
sections = [bars[i]['t'] for i in range(1, len(bars)) if abs(dbs[i] - dbs[i - 1]) >= jump]
breaths = [bars[i]['t'] for i in range(1, len(bars) - 1) if dbs[i] <= min(dbs[i - 1], dbs[i + 1]) - 6]

out = {
    'bpm': round(float(bpm), 2),
    'offset': round(float(downbeats[0]), 3),
    'bar': round(float(bar), 4),
    'beats': [round(float(t), 3) for t in beats],
    'downbeats': [round(float(t), 3) for t in downbeats],
    'bars': bars,
    'sections': sections,
    'breaths': breaths,
}
json.dump(out, sys.stdout, indent=1)
print(f'{path}: {out["bpm"]} BPM · first downbeat {out["offset"]} s · bar {out["bar"]} s · {len(downbeats)} bars in {dur:.1f} s', file=sys.stderr)
print(f'  energy jumps at {sections or "none"} · breaths at {breaths or "none"} (mastered tracks hide sections: read the per-bar dB too)', file=sys.stderr)
print('  dB per bar: ' + ' '.join(f'{b["t"]:.1f}:{b["db"]}' for b in bars), file=sys.stderr)
print(f'  timeline.js: export const BPM = {out["bpm"]}; const OFFSET = {out["offset"]}; bar n starts at OFFSET + n * {out["bar"]}', file=sys.stderr)
