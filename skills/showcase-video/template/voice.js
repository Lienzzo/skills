// Narrated films: lays the voice takes (vo.js, written by scripts/vo.py) on the film's clock.
// timeline.js derives its cues from the result, so a re-recorded take moves every cut, cue and
// sound with it: never type a time that a take decides.
//
//   import VO from './vo.js'
//   export const V = layVoice(VO, 1.2)              // first word at 1.2 s
//   V.at('l2'), V.end('l2')                          // first and last word of a take
//   V.word('l2', '47'), V.word('l3', 'fuentes', 2)   // a word (2nd occurrence), for a pop or a cut
//   V.gapMid('l2', 'l3')                             // middle of the breath between two takes: a cut
//   V.duration                                       // last word of the last take
//
// Takes follow each other with `gap` seconds of silence (VO.md `id (gap 0.9): …` overrides one,
// opts.gapBefore = { l4: 1.2 } overrides it from here). Spacing uses the voiced span (first word
// to last word), not the file: each file is placed at its first word minus its lead silence.

// Words match without case, punctuation or accents: V.word('l2', 'criticos') finds "críticos."
export const norm = (w) => w.normalize('NFD').replace(/\p{M}/gu, '').toLowerCase().replace(/[^\p{L}\p{N}]/gu, '')

export function layVoice(VO, start = 1, { gap = 0.35, gapBefore = {} } = {}) {
  if (!VO?.lines?.length) throw new Error('vo.js has no takes: run scripts/vo.py build <src>')
  const lines = []
  let t = start
  for (const l of VO.lines) {
    if (lines.length) t += gapBefore[l.id] ?? l.gap ?? gap
    const at = t - l.words[0].t0 // the file starts here
    const words = l.words.map((w) => ({ w: w.w, n: norm(w.w), t0: at + w.t0, t1: at + w.t1 }))
    const line = { id: l.id, text: l.text, file: l.file, at, t0: words[0].t0, t1: words.at(-1).t1, words }
    lines.push(line)
    t = line.t1
  }
  const byId = Object.fromEntries(lines.map((l) => [l.id, l]))
  const get = (id) => byId[id] ?? fail(`no take "${id}" in vo.js (takes: ${lines.map((l) => l.id).join(', ')})`)
  return {
    provider: VO.provider,
    lines,
    at: (id) => get(id).t0,
    end: (id) => get(id).t1,
    gapMid: (a, b) => (get(a).t1 + get(b).t0) / 2,
    word(id, w, nth = 1) {
      const l = get(id)
      const hits = l.words.filter((x) => x.n === norm(w))
      return (hits[nth - 1] ?? fail(`take "${id}" has no "${w}" #${nth}: "${l.text}" (the script changed?)`)).t0
    },
    wordEnd(id, w, nth = 1) {
      const l = get(id)
      const hits = l.words.filter((x) => x.n === norm(w))
      return (hits[nth - 1] ?? fail(`take "${id}" has no "${w}" #${nth}: "${l.text}"`)).t1
    },
    duration: lines.at(-1).t1,
  }
}

function fail(msg) {
  throw new Error(msg)
}
