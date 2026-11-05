// Shared timeline of a NARRATED film (explainer mode, references/explainer.md). The voice is
// the grid: takes come from vo.js (scripts/vo.py build), template/voice.js lays them on the
// clock, and every cut, cue and sound below is derived from them. Re-record a take and the
// whole film re-times itself: never type a time a take decides. The music is a bed under the
// voice (its chords still change on bars; its hits sit on the cuts, not on bar lines).
// Every key must be unique: a duplicate silently wins over the earlier one.
import VO from './vo.js'
import { layVoice } from './voice.js'

export const BPM = 120
export const FPS = 60

// First word at 2.2 s: the logo draws under the music first. Gaps: VO.md `(gap …)`.
export const V = layVoice(VO, 2.2)
export const VOICE_PROVIDER = V.provider // qa.py blocks delivering a scratch voice
const TAIL = 3.4 // the end card holds after the last word: its tag needs its reading time (the lint measures it)
export const DURATION = Math.round((V.duration + TAIL) * FPS) / FPS
// Spoken-word loudness (finalize.sh and qa.py read it). −14 LUFS with true peak ≤ −2 dBTP allows
// 12 dB from peak to loudness; a real voice has ~20, so −14 would cost 6–8 dB of limiting on
// every stressed word. −16 is the spoken-word standard (podcasts, AES streaming for speech).
export const LOUDNESS = -16

// One timeline, several formats. Set DEFAULT_FORMAT to the brief's main one; render the
// others with FORMAT=9x16 (env: render.mjs, render-segs.sh, qa.py, audio.ts) — the page
// gets it as ?format=9x16. Scenes lay out from W/H (CSS: var(--W), var(--H),
// html[data-format="9x16"]): reframe per format, never crop a 16:9 render.
export const FORMATS = { '16x9': [1920, 1080], '9x16': [1080, 1920], '1x1': [1080, 1080], '4x5': [1080, 1350] }
const DEFAULT_FORMAT = '16x9'
export const FORMAT = globalThis.process?.env?.FORMAT || new URLSearchParams(globalThis.location?.search ?? '').get('format') || DEFAULT_FORMAT
if (!FORMATS[FORMAT]) throw new Error(`unknown FORMAT ${FORMAT}: use one of ${Object.keys(FORMATS).join(', ')}`)
export const [W, H] = FORMATS[FORMAT]

const cut12 = V.gapMid('l1', 'l2') // cuts sit in the breaths between takes
const cut34 = V.gapMid('l3', 'l4')

export const T = {
  // S1 · the logo draws, then l1 sets up the problem over it
  logo: 0.4,
  draw: [0.4, 1.6],
  word: 1.7,
  s1Out: [cut12 - 0.45, cut12],
  // S2 · l2: the question is typed while it is said; l3: the answer streams with the voice
  ui: cut12,
  type: [V.word('l2', 'type'), V.end('l2')],
  cur: [V.end('l2') - 0.35, V.end('l2') + 0.15],
  send: V.end('l2') + 0.25,
  answer: [V.at('l3'), V.end('l3')],
  push: [V.word('l3', 'cites'), V.word('l3', 'cites') + 1.8], // the camera moves on the word that matters
  s2Out: [cut34 - 0.45, cut34],
  // S3 · end card: its impact lands in the breath, l4 comes once it has decayed (VO.md gap 1.4),
  // and the card holds after it (render.mjs review measures the reading time)
  end: cut34,
  endTag: V.end('l4') + 0.2,
  fadeOut: [DURATION - 0.4, DURATION],
}

// Scene windows [id, from, to, opts?] (cuts in the breaths: never mid-word). Boundaries are the planned cuts: `render.mjs review`
// filmstrips each one, qa.py flags any hard cut the file has that is NOT listed here
// (a jump), and audio.ts reports stem levels per scene.
// opts: { montage: [T.c1, T.c2, …] } its cuts (qa.py checks every other change in it; `true` without
// the list makes them notes, not checks) · { mblur: 4 } renders real
// motion blur there (4 subframes per frame, 4× the render cost: only for whip pans and fast pushes).
export const SCENES = [
  ['title', 0, T.ui],
  ['ui', T.ui, T.end],
  ['end', T.end, DURATION],
]

// Planned instant changes (a flash, a modal that pops open) and planned dark stretches, by cue so
// they follow timing changes, each with its reason: qa.py does not flag them.
//   { at: T.modal, why: 'the modal opens' } · { at: T.v0, to: T.v1, why: 'verdicts land one by one' }
export const INTENDED = []

export const QUESTION = 'What changed this week?'
// Streamed answer: strings are words, {b} is bold, numbers are citation badges, '\n' a paragraph.
export const ANSWER = ['Three things: ', { b: 'new prices' }, ' from Monday ', 1, ', the ', { b: 'summer opening hours' }, ' ', 2, ' and one supplier fewer ', 1, '.']

// When each character of a typed string appears.
export function typingTimes(text, a, b) {
  const n = text.length
  return Array.from({ length: n }, (_, i) => a + ((b - a) * i) / Math.max(1, n - 1))
}

// Times at which each citation badge resolves (mirrors lib.streamAt) — audio.ts pops on them.
export function badgeTimes(parts, a, b, lag = 0.18) {
  const items = []
  for (const p of parts) {
    if (typeof p === 'number') items.push('cb')
    else if (p !== '\n') for (const _ of (typeof p === 'string' ? p : p.b).split(/(?<= )/)) items.push('w')
  }
  return items.map((k, i) => (k === 'cb' ? a + ((b - a) * i) / items.length + lag : null)).filter((x) => x !== null)
}

// Deterministic PRNG shared by both sides (never Math.random: frames must repeat exactly).
export function mulberry32(seed) {
  let a = seed >>> 0
  return () => {
    a = (a + 0x6d2b79f5) >>> 0
    let t = a
    t = Math.imul(t ^ (t >>> 15), t | 1)
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61)
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}
