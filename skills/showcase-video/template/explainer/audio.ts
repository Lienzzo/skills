// Soundtrack of a NARRATED film: a music bed under the voice, every UI/transition sound, and the
// narration itself, all from the same timeline. `bun audio.ts` → out/audio_raw.wav;
// `REPORT=1 bun audio.ts` also prints each stem per scene and the voice over the bed per take.
// The film's length and cuts come from the takes (timeline.js), so nothing here assumes a bar
// count: the bed covers DURATION in whole bars, and the hits sit on the cuts (T.ui, T.end).
import { T, V, SCENES, DURATION, QUESTION, ANSWER, badgeTimes, typingTimes, mulberry32 } from './timeline.js'
import { B, place, placeSt, kick, hat, crash, padChord, pluck, bassNote, mallet, bell, whoosh, riser, reverseCymbal, impact, pop, click, keyTick, tick, sparkle, placeVoice, mixdown } from './synth.ts'

// ── harmony · one chord per bar (2 s), cycled for as long as the film runs ───
const CH: Record<string, { root: number; pad: number[]; arp: number[] }> = {
  Gm: { root: 43, pad: [58, 62, 67, 70], arp: [67, 70, 74, 79] },
  Eb: { root: 39, pad: [58, 63, 67, 70], arp: [67, 70, 75, 79] },
  Bb: { root: 46, pad: [58, 62, 65, 70], arp: [65, 70, 74, 77] },
  F: { root: 41, pad: [57, 60, 65, 69], arp: [65, 69, 72, 77] },
}
const LOOP = ['Gm', 'Eb', 'Bb', 'F']
const BARS = Math.ceil(DURATION / 2)
const endBar = Math.floor(T.end / 2) // from the end card's bar: resolve to B♭
const chordAt = (b: number) => (b >= endBar ? 'Bb' : LOOP[b % LOOP.length])
const firstGrooveBar = Math.ceil(T.ui / 2) // whole bars only: a cut off the bar line never indexes a fraction

// Pad all the way; its filter opens over the opening, before the first word.
for (let b = 0; b < BARS; b++) {
  const t0 = b * 2
  const intro = t0 < T.ui
  const last = b === BARS - 1
  const cut = (t: number) => (intro ? 600 + 1800 * Math.min(1, (t0 + t) / T.ui) : last ? 3000 - 1400 * Math.min(1, t / 2) : 2600)
  placeSt(B.pad, padChord(CH[chordAt(b)].pad, last ? 2.2 : 2, { atk: b === 0 ? 1.2 : 0.25, rel: last ? 1.6 : 0.5, cut }), t0, intro ? 0.38 : 0.3, { verb: 0.3 })
}
// A soft arp in 8ths (not 16ths: under a voice, less is more), quiet before the product scene.
const ARP = [0, 2, 1, 3, 2, 0, 3, 1]
for (let s = 4; s * 0.25 < DURATION - 0.5; s++) {
  const t = s * 0.25
  if (t >= T.ui - 0.5 && t < T.ui) continue // a breath before the cut
  const ch = CH[chordAt(Math.floor(t / 2))]
  place(B.music, pluck(ch.arp[ARP[s % 8]], s % 2 ? 0.55 : 0.8, t < T.ui ? 0.35 : 0.7), t, 0.15, s % 2 ? 0.3 : -0.3, { delay: 0.25, verb: 0.2 })
}
for (let b = firstGrooveBar; b < BARS - 1 && b * 2 < T.end; b++) place(B.bass, bassNote(CH[chordAt(b)].root, 2, false), b * 2, 0.4)
place(B.bass, bassNote(CH.Bb.root - 12, 2, false), Math.ceil(T.end / 2) * 2, 0.4)

// A light pulse through the product scene: kick on 1 and 3, soft hats (the voice ducks them more).
const kicks: number[] = []
for (let t = firstGrooveBar * 2; t < T.end - 0.01; t += 1) kicks.push(t)
for (const t of kicks) place(B.drums, kick(0.8), t, 0.4)
{
  const hr = mulberry32(99)
  for (let t = firstGrooveBar * 2 + 0.5; t < T.end; t += 1) place(B.drums, hat(), t, 0.05 * (0.85 + 0.3 * hr()), 0.25)
}

// ── transitions: every cut gets a sound; hits on the cuts, not on bar lines ──
placeSt(B.sfx, { L: riser(1.2), R: riser(1.2) }, T.ui - 1.2, 0.14)
place(B.sfx, impact(), T.ui, 0.25, 0, { verb: 0.2 })
place(B.drums, crash(), T.ui, 0.15, 0.2, { verb: 0.3 })
place(B.sfx, whoosh(0.5, 400, 3500, 1.2, 0.7), T.s1Out[0], 0.16, 0, { verb: 0.3 })
place(B.sfx, whoosh(0.45, 3000, 500, 1.2, 0.4), T.s2Out[0], 0.14, 0, { verb: 0.3 })
place(B.sfx, reverseCymbal(0.8), T.end - 0.8, 0.22)
place(B.sfx, impact(3.0), T.end, 0.5, 0, { verb: 0.45 })
place(B.drums, crash(2.6), T.end, 0.2, 0, { verb: 0.45 })

// ── S1 · the logo draws ───────────────────────────────────────────────────────
;[62, 65, 67, 70, 74, 77, 79].forEach((n, i) => place(B.music, pluck(n, 0.8, 0.5), T.draw[0] + i * 0.14, 0.13, -0.5 + i * 0.16, { verb: 0.4, delay: 0.3 }))
place(B.sfx, bell(79, 2.4), T.draw[1] - 0.2, 0.12, 0, { verb: 0.5 })
for (let i = 0; i < 6; i++) place(B.sfx, tick(2800 + i * 260, 0.01), T.word + i * 0.06, 0.08, -0.4 + i * 0.15, { verb: 0.25 })

// ── S2 · UI: key ticks, click on send, a pop per citation ────────────────────
{
  const kr = mulberry32(5)
  for (const t of typingTimes(QUESTION, T.type[0], T.type[1])) place(B.sfx, keyTick(kr), t, 0.09 + kr() * 0.03, (kr() - 0.5) * 0.4)
}
place(B.sfx, click(), T.send - 0.02, 0.35, 0.3)
place(B.sfx, pop(1400, 800, 0.1, 0.03), T.send + 0.05, 0.14, 0.3, { verb: 0.2 })
badgeTimes(ANSWER, T.answer[0], T.answer[1]).forEach((t, i) => place(B.sfx, pop(1200 + i * 150, 700 + i * 60, 0.09, 0.025), t, 0.12, -0.3 + i * 0.3, { verb: 0.2 }))

// ── S3 · end card ─────────────────────────────────────────────────────────────
sparkle(T.end + 0.1, [82, 86, 89, 94], 0.09, 0.08)
place(B.music, mallet(82, 1.6), T.endTag, 0.12, 0.1, { verb: 0.4, delay: 0.3 })

// ── the narration ─────────────────────────────────────────────────────────────
placeVoice(V.lines)
mixdown({ kicks, sections: SCENES, voice: V.lines, voiceOverBed: 10 })
