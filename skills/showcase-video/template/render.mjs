// Frame-exact renderer: headless Chromium seeks the page to each frame's time and
// screenshots it; ffmpeg encodes the PNG stream. Modes:
//   node render.mjs serve [--port 4173]                     live preview with sound, for humans
//   node render.mjs preview 3.2 12 [--dsf 1]                → out/preview-<t>.png (full size)
//   node render.mjs sheet 1 2.5 4 … [--out f.png]           → one labelled contact sheet
//   node render.mjs sheet --from 9.6 --to 10.4 --step 0.05  (filmstrip across a cut)
//   node render.mjs review [--scene id] [--tag name]        → out/review/<tag>/: a sheet per scene,
//        [--phone-min 12]                                     a filmstrip per planned cut, phone-size
//                                                             sheets, lint.md (off-frame text, seek order,
//                                                             reading time of every data-read text)
//   node render.mjs render [--workers 2] [--dsf 2] [--from 0 --to 12] [--name video] → out/<name>.mkv
// FORMAT=9x16 node render.mjs … renders another format of the same timeline (see timeline.js).
import http from 'node:http'
import fs from 'node:fs'
import path from 'node:path'
import { spawn, spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { DURATION, FPS, W, H, SCENES, FORMAT } from './timeline.js'
import * as TL from './timeline.js' // TL.V: the laid-out narration, in a narrated film
import { loadPlaywright, chromePath } from './pw.mjs'
import { montage } from './montage.mjs'

const ROOT = path.dirname(fileURLToPath(import.meta.url))
const OUT = path.join(ROOT, 'out')
fs.mkdirSync(OUT, { recursive: true })
const args = process.argv.slice(2)
const mode = args[0]
const opt = (name, def) => {
  const i = args.indexOf(`--${name}`)
  return i >= 0 ? args[i + 1] : def
}
const times = () => args.slice(1).filter((a, i, all) => /^[\d.]+$/.test(a) && !/^--/.test(all[i - 1] ?? ''))
const range = (a, b, st) => {
  const ts = []
  for (let t = a; t <= b + 1e-9; t += st) ts.push(Math.round(t * 1000) / 1000)
  return ts
}

// Duplicate keys in timeline.js's T silently override earlier ones (a real bug that shipped once).
{
  const src = fs.readFileSync(path.join(ROOT, 'timeline.js'), 'utf8')
  const a = src.indexOf('export const T = {')
  const keys = [...src.slice(a, src.indexOf('\n}', a)).matchAll(/^\s{2}(\w+):/gm)].map((m) => m[1])
  const dup = keys.filter((k, i) => keys.indexOf(k) !== i)
  if (dup.length) console.error(`timeline.js: duplicate keys in T: ${[...new Set(dup)].join(', ')}`)
}

const TYPES = { '.json': 'application/json', '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css', '.woff2': 'font/woff2', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.wav': 'audio/wav', '.mp3': 'audio/mpeg' }
function serve(port = 0) {
  return new Promise((res) => {
    const srv = http.createServer((req, rsp) => {
      // Local and inside the project only: other Host names (DNS rebinding) and paths that
      // climb out of src/ (`..%2f` reaches ../.auth, the capture session) are refused.
      if (!['127.0.0.1', 'localhost'].includes((req.headers.host || '').replace(/:\d+$/, ''))) return rsp.writeHead(403).end()
      let p
      try {
        p = path.resolve(ROOT, '.' + decodeURIComponent(new URL(req.url, 'http://x').pathname))
      } catch {
        return rsp.writeHead(400).end()
      }
      if (p !== ROOT && !p.startsWith(ROOT + path.sep)) return rsp.writeHead(403).end()
      fs.readFile(p.endsWith('/') ? path.join(p, 'index.html') : p, (err, buf) => {
        if (err) return rsp.writeHead(404).end()
        rsp.writeHead(200, { 'content-type': TYPES[path.extname(p)] || 'application/octet-stream', 'cache-control': 'no-store' }).end(buf)
      })
    })
    srv.listen(port, '127.0.0.1', () => res(srv))
  })
}

if (mode === 'serve') {
  const srv = await serve(Number(opt('port', 4173)))
  const base = `http://127.0.0.1:${srv.address().port}/index.html?format=${FORMAT}`
  console.log(`live preview (with out/audio.wav if rendered): ${base}&play   ·   from 26 s: ${base}&play=26   ·   one frame: ${base}&t=18.5`)
  console.log('space pause · ←/→ ±1 s · shift ±0.1 s · h hide timecode · Ctrl-C to stop')
  await new Promise(() => {})
}

let pageErrors = 0
// Wait until the page is really ready. `evaluate(() => window.__ready)` alone returns at once
// if main.js hasn't run yet (a scene module with a top-level await delays it): the first frames
// of every worker then came out black. Wait for __ready to exist, then for it to resolve; a
// rejected __ready (a font or image that failed) aborts instead of rendering a broken frame.
async function pageReady(page) {
  // A script error before __ready exists (a syntax error in a scene) would otherwise wait out
  // the timeout. openPage records page errors from before goto() returns (page.__err).
  let iv
  const failed = new Promise((_, fail) => (iv = setInterval(() => page.__err && fail(new Error(`page failed before it was ready: ${page.__err}`)), 100)))
  try {
    await Promise.race([failed, page.waitForFunction(() => window.__ready !== undefined && typeof window.__seek === 'function', null, { timeout: 60000 })])
  } finally {
    clearInterval(iv)
    failed.catch(() => {})
  }
  const ok = await page.evaluate(() => window.__ready)
  if (ok !== true) throw new Error(`window.__ready resolved to ${JSON.stringify(ok)}, expected true`)
}

async function openPage(browser, url, dsf) {
  const ctx = await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: dsf })
  const page = await ctx.newPage()
  page.on('console', (m) => m.type() === 'error' && (pageErrors++, console.error('[page]', m.text())))
  page.on('pageerror', (e) => (pageErrors++, (page.__err ??= e.message), console.error('[pageerror]', e.message)))
  await page.goto(url)
  await pageReady(page)
  const cdp = await ctx.newCDPSession(page)
  const shot = async (t, scale = 1) => {
    await page.evaluate((t) => window.__seek(t), t)
    const clip = scale === 1 ? undefined : { x: 0, y: 0, width: W, height: H, scale }
    const { data } = await cdp.send('Page.captureScreenshot', { format: 'png', optimizeForSpeed: true, clip })
    return Buffer.from(data, 'base64')
  }
  return { page, shot }
}

// Small labelled frames tiled into one image: read it to judge a whole scene or a cut at a glance.
// Each tile is labelled with its time (drawn by Chromium: see montage.mjs).
async function sheet(shot, ts, out, cols = 6, scale = 0.25) {
  const items = []
  for (const t of ts) items.push({ src: await shot(t, scale), label: `${t}s` })
  return montage(browser, items, out, { cols })
}

// What a phone shows: the frame at 390 px wide (a 16:9 video in a portrait phone, or a
// vertical one full screen). Pages stay under ~1900 px so an image reader sees them at
// true size: text you can't read here is too small for anyone watching on a phone.
async function phoneSheets(shot, ts, dir) {
  const scale = 390 / W
  const cols = 4
  const rows = Math.max(1, Math.floor(1900 / (H * scale + 6)))
  const pages = []
  for (let i = 0; i * cols * rows < ts.length; i++) pages.push(await sheet(shot, ts.slice(i * cols * rows, (i + 1) * cols * rows), path.join(dir, `phone-${i + 1}.png`), cols, scale))
  return pages
}

// Seek order must not matter: render workers and segments jump around the timeline. A frame
// shot playing forward from a fresh page vs reached backwards that differs means at(t) leaves
// state behind (a style set in one branch and never reset).
async function orderLint(page, shot, ts) {
  page.__err = undefined
  await page.reload()
  await pageReady(page)
  const fwd = new Map()
  for (const t of ts) fwd.set(t, await shot(t))
  const bad = []
  const dir = fs.mkdtempSync(path.join(OUT, 'order-'))
  try {
    const [fa, fb] = [path.join(dir, 'a.png'), path.join(dir, 'b.png')]
    for (const t of [...ts].reverse()) {
      const a = fwd.get(t)
      const b = await shot(t)
      if (a.equals(b)) continue
      // Big blurs (shadows) rasterise with ±1-level noise: count only pixels off by more than 3 %.
      fs.writeFileSync(fa, a)
      fs.writeFileSync(fb, b)
      // AE prints "1234" (or "1234 (0.01)"); anything else means compare failed: never a silent pass.
      const r = spawnSync('magick', ['compare', '-metric', 'AE', '-fuzz', '3%', fa, fb, 'null:'], { encoding: 'utf8' })
      const ae = parseFloat(r.stderr)
      if (!Number.isFinite(ae)) throw new Error(`magick compare failed at ${t} s: ${(r.error?.message || r.stderr || 'no output').trim()}`)
      if (ae > 20) bad.push(t)
    }
  } finally {
    fs.rmSync(dir, { recursive: true, force: true })
  }
  return bad.reverse()
}

// Text that is visible but partly outside the frame at time t (clipped bubbles, captions
// pushed off-screen). Intentional crops show up too: the reviewer decides.
async function offFrameText(page, t) {
  await page.evaluate((t) => window.__seek(t), t)
  return page.evaluate(({ W, H }) => {
    const hits = []
    const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT)
    for (let n = walk.nextNode(); n; n = walk.nextNode()) {
      const text = n.textContent.trim()
      const el = n.parentElement
      if (!text || !el || !el.checkVisibility({ opacityProperty: true, visibilityProperty: true })) continue
      let o = 1
      for (let e = el; e; e = e.parentElement) o *= Number(getComputedStyle(e).opacity)
      if (o < 0.3) continue
      const r = document.createRange()
      r.selectNodeContents(n)
      for (const b of r.getClientRects()) {
        const inside = b.right > 0 && b.bottom > 0 && b.left < W && b.top < H
        const out = b.left < -1 || b.top < -1 || b.right > W + 1 || b.bottom > H + 1
        if (b.width > 1 && inside && out) hits.push(text.slice(0, 60))
      }
    }
    return [...new Set(hits)]
  }, { W, H })
}

// Reading lint. Every piece of text the viewer must read carries `data-read` (any value but
// "0"); `data-read="0"` marks text that is not meant to be read (a UI's incidental labels, a
// capture's chrome) and everything inside it. Sampled every 1/15 s from the DOM itself:
// - a declared text counts as readable while its visible words are on screen at ≥ 0.85
//   opacity (summed over its ancestors) and fully inside the frame; text that types or streams
//   in counts from the frame its last word appears;
// - each readable stretch must last ≥ 0.4 s per word + 0.5 s (SKILL.md);
// - a text of 3+ words that lands while another one still needs its reading time is "two things
//   to read at once";
// - its size on a 390 px-wide phone (font size × camera scale × 390 / W);
// - text of 22 px or more that isn't declared at all is listed (and counts as a problem), and a
//   scene that shows such text but declares none is NOT CHECKED: never a pass.
const READ_STEP = 1 / 15
async function readProbe(page, t) {
  await page.evaluate((t) => window.__seek(t), t)
  return page.evaluate(({ W, H }) => {
    const opacityOf = (el, stop) => {
      let o = 1
      for (let e = el; e && e !== stop; e = e.parentElement) o *= Number(getComputedStyle(e).opacity)
      return o
    }
    const shown = (el) => el.checkVisibility({ opacityProperty: true, visibilityProperty: true })
    const inFrame = (r) => r.width > 0 && r.left >= -1 && r.top >= -1 && r.right <= W + 1 && r.bottom <= H + 1
    const pxSize = (el) => {
      const r = el.getBoundingClientRect()
      const scale = el.offsetWidth ? r.width / el.offsetWidth : 1
      return parseFloat(getComputedStyle(el).fontSize) * scale
    }
    // Global covers (the fade to black, a flash) are siblings, not ancestors: main.js reports them.
    const veil = Math.min(1, Math.max(0, window.__veil?.() ?? 0))
    const out = { declared: [], loose: [] }
    window.__readIds ??= new WeakMap()
    let next = window.__readNext ?? 0
    for (const el of document.querySelectorAll('[data-read]')) {
      if (el.dataset.read === '0' || el.parentElement?.closest('[data-read="0"]')) continue
      if (!window.__readIds.has(el)) window.__readIds.set(el, next++)
      const id = window.__readIds.get(el)
      const label = el.dataset.read && el.dataset.read !== '1' ? el.dataset.read : (el.id || el.className || el.tagName).toString().slice(0, 40)
      // Only the words that are actually visible (typed, streamed or revealed word by word).
      // The frame test uses the boxes of those words, not the element's (a wide container
      // can overhang the frame while its text sits inside).
      const words = []
      let inside = true
      const walk = document.createTreeWalker(el, NodeFilter.SHOW_TEXT)
      for (let n = walk.nextNode(); n; n = walk.nextNode()) {
        const p = n.parentElement
        if (p.closest('[data-read="0"]')) continue // excluded inside a declared text
        if (!n.textContent.trim() || !shown(p) || opacityOf(p, el) < 0.5) continue
        words.push(n.textContent)
        const rg = document.createRange()
        rg.selectNodeContents(n)
        for (const b of rg.getClientRects()) if (b.width > 1 && !inFrame(b)) inside = false
      }
      const text = words.join(' ').replace(/\s+/g, ' ').replace(/\s+([,.;:!?])/g, '$1').trim()
      const ok = !!text && inside && shown(el) && opacityOf(el) * (1 - veil) >= 0.85
      out.declared.push({ id, label, text, ok, px: ok ? pxSize(el) : 0 })
    }
    if (window.__readNext === undefined || next > window.__readNext) window.__readNext = next
    // Text nobody declared: visible at ≥ 0.85 opacity and ≥ 22 px on the stage (a normal caption
    // is 32–48 px; rebuilt UI text under a zoom gets there too: put data-read="0" on its window).
    // Reported once per block, so a headline split into word spans is one entry.
    const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT)
    for (let n = walk.nextNode(); n; n = walk.nextNode()) {
      const p = n.parentElement
      const text = n.textContent.trim()
      if (!text || !p || p.closest('[data-read]') || !shown(p)) continue
      if (opacityOf(p) * (1 - veil) < 0.85 || pxSize(p) < 22) continue
      const r = document.createRange()
      r.selectNodeContents(n)
      if (!inFrame(r.getBoundingClientRect())) continue
      const blk = p.closest('h1,h2,h3,h4,h5,h6,p,li,div') ?? p
      window.__looseIds ??= new WeakMap()
      if (!window.__looseIds.has(blk)) window.__looseIds.set(blk, (window.__looseNext = (window.__looseNext ?? 0) + 1))
      out.loose.push({ key: window.__looseIds.get(blk), text: blk.textContent.replace(/\s+/g, ' ').trim().slice(0, 50) || text.slice(0, 50) })
    }
    return out
  }, { W, H })
}

// Same read only if the new text extends the old one: every old word still there, in order
// (words may be inserted, e.g. a citation badge landing mid-sentence), and the last old word
// may still be typing; or it is the same text with a number still counting. Anything else is a
// new message, and the old one is judged on its own.
function sameRead(a, b) {
  // A number counting up or down is one read: readable once it settles (the clock restarts).
  if (a.replace(/[\d.,]+/g, '#') === b.replace(/[\d.,]+/g, '#')) return true
  const toks = (s) => s.split(' ').map((w) => w.replace(/[^\p{L}\p{N}]/gu, '')).filter(Boolean) // punctuation moves as badges land
  const A = toks(a), B = toks(b)
  let j = 0
  for (let i = 0; i < A.length; i++) {
    const last = i === A.length - 1
    while (j < B.length && !(B[j] === A[i] || (last && B[j].startsWith(A[i])))) j++
    if (j++ >= B.length) return false
  }
  return true
}

async function readingLint(page, scenes, phoneMin) {
  const words = (s) => s.split(/\s+/).filter((w) => /[\p{L}\p{N}]/u.test(w)).length
  const lines = []
  const runs = [] // { id, label, a, b, text, from, px, edge }
  const loose = new Map()
  const declaredIn = new Map(scenes.map(([id]) => [id, 0]))
  // One continuous pass over the window (a text can stay on screen across a cut).
  const a0 = Math.min(...scenes.map((s) => s[1]))
  const b0 = Math.max(...scenes.map((s) => s[2]))
  const sceneAt = (t) => (scenes.find(([, a, b]) => t >= a && t < b) ?? scenes[scenes.length - 1])[0]
  const open = new Map()
  for (const [k, t] of range(a0, b0 - 1e-6, READ_STEP).entries()) {
    const sid = sceneAt(t)
    const { declared, loose: lz } = await readProbe(page, t)
    for (const { key, text } of lz) {
      const seen = loose.get(key) // one entry per block: first time seen, longest text (typing grows)
      if (!seen) loose.set(key, [sid, t, text])
      else if (text.length > seen[2].length) seen[2] = text
    }
    for (const d of declared) {
      if (d.ok) declaredIn.set(sid, declaredIn.get(sid) + 1)
      let r = open.get(d.id)
      if (d.ok && r && !sameRead(r.text, d.text)) {
        runs.push(r) // the same element now says something else: that is a new read
        open.delete(d.id)
        r = undefined
      }
      if (d.ok && r) {
        if (d.text !== r.text) r.from = t // still typing/streaming: the clock starts at its last word
        r.text = d.text
        r.b = t
        r.px = Math.min(r.px, d.px)
      } else if (d.ok) open.set(d.id, { id: d.id, label: d.label, a: t, b: t, from: t, text: d.text, px: d.px, edge: k === 0 && a0 > 0 })
      else if (r) {
        runs.push(r)
        open.delete(d.id)
      }
    }
  }
  // Still on screen when the window ends: fine at the end of the film, unknown otherwise.
  for (const r of open.values()) runs.push({ ...r, edge: r.edge || b0 < DURATION - 1e-6, tail: b0 >= DURATION - 1e-6 })
  const short = [], small = [], crowd = []
  for (const r of runs) {
    const n = words(r.text)
    if (!n) continue
    const held = r.b - r.from + READ_STEP
    const need = 0.4 * n + 0.5
    if (held + READ_STEP / 2 < need && !r.edge) short.push(`- ${r.from.toFixed(2)}–${(r.b + READ_STEP).toFixed(2)} s · "${r.text.slice(0, 60)}" (${n} words): readable ${held.toFixed(2)} s, needs ${need.toFixed(1)} s`)
    if (r.px * (390 / W) < phoneMin) small.push(`- ${r.from.toFixed(2)} s · "${r.text.slice(0, 50)}": ${(r.px * (390 / W)).toFixed(1)} px on a 390 px phone`)
  }
  const big = runs.filter((r) => words(r.text) >= 3).sort((x, y) => x.from - y.from)
  for (let i = 0; i < big.length; i++)
    for (let j = i + 1; j < big.length; j++) {
      // The second one lands while the first still needs its reading time.
      const due = big[i].from + 0.4 * words(big[i].text) + 0.5
      if (big[j].id !== big[i].id && big[j].from < due && big[j].from <= big[i].b + READ_STEP)
        crowd.push(`- ${big[j].from.toFixed(2)} s · "${big[j].text.slice(0, 40)}" arrives while "${big[i].text.slice(0, 40)}" still needs until ${due.toFixed(2)} s`)
    }
  const unchecked = [...declaredIn].filter(([sid, n]) => !n && [...loose.values()].some(([s]) => s === sid)).map(([sid]) => sid)
  lines.push(`Rule: ≥ 0.4 s per word + 0.5 s, one thing to read at a time, ≥ ${phoneMin} px on a 390 px phone. Sampled every ${READ_STEP.toFixed(3)} s from the DOM (\`data-read\`).`, '')
  lines.push(unchecked.length ? `**NOT CHECKED** — scenes with text but no \`data-read\`: ${unchecked.join(', ')}. Declare what must be read (or \`data-read="0"\`) and rerun; this is not a pass.` : `Declared texts measured: ${runs.length}.`, '')
  lines.push('### Too short to read', '', ...(short.length ? short : ['none']), '')
  lines.push('### Two things to read at once', '', ...(crowd.length ? crowd : ['none']), '')
  lines.push(`### Small on a phone (judge only if the film will be watched on phones)`, '', ...(small.length ? small : ['none']), '')
  lines.push('### Text not declared (≥ 22 px: mark it `data-read`, or `data-read="0"` on its container if it is not meant to be read)', '', ...(loose.size ? [...loose.values()].map(([sid, t, s]) => `- ${sid} ${t.toFixed(2)} s · "${s}"`) : ['none']))
  return { lines, problems: short.length + crowd.length + unchecked.length + loose.size }
}

const { chromium } = await loadPlaywright()
const srv = await serve()
const url = `http://127.0.0.1:${srv.address().port}/index.html?format=${FORMAT}`
const browser = await chromium.launch({ executablePath: chromePath(), args: ['--font-render-hinting=none', '--force-color-profile=srgb', '--disable-lcd-text'] })

if (mode === 'preview') {
  const { shot } = await openPage(browser, url, Number(opt('dsf', 1)))
  for (const a of times()) {
    const f = path.join(OUT, `preview-${a}.png`)
    fs.writeFileSync(f, await shot(Number(a)))
    console.log(f)
  }
} else if (mode === 'sheet') {
  const ts = opt('from') !== undefined ? range(Number(opt('from')), Number(opt('to', Number(opt('from')) + 1)), Number(opt('step', 0.1))) : times().map(Number)
  const { shot } = await openPage(browser, url, 1)
  console.log(await sheet(shot, ts, opt('out', path.join(OUT, `sheet-${ts[0]}-${ts[ts.length - 1]}.png`)), Number(opt('cols', 6)), Number(opt('scale', 0.25))))
} else if (mode === 'review') {
  // The review pack for one loop iteration: what the reviewer looks at, plus machine lint.
  const tag = opt('tag', new Date().toISOString().slice(0, 16).replace(/[:T]/g, '-'))
  const dir = path.join(OUT, 'review', tag)
  fs.mkdirSync(dir, { recursive: true })
  const only = opt('scene')
  const scenes = SCENES.filter(([id]) => !only || id === only)
  const { page, shot } = await openPage(browser, url, 1)
  const lines = [`# Review pack ${tag}`, '']
  for (const [id, a, b] of scenes) {
    const st = Math.max(0.25, Math.round(((b - a) / 36) * 20) / 20)
    lines.push(`- scene \`${id}\` ${a}–${b} s (every ${st} s): ${path.basename(await sheet(shot, range(a, b - 0.01, st), path.join(dir, `scene-${id}.png`)))}`)
  }
  const cuts = [...new Set(SCENES.map(([, a]) => a))].filter((c) => c > 0 && (!only || scenes.some(([, a, b]) => c === a || c === b)))
  for (const c of cuts) lines.push(`- cut at ${c} s (±0.3 s every 0.05 s): ${path.basename(await sheet(shot, range(Math.max(0, c - 0.3), Math.min(DURATION, c + 0.3), 0.05), path.join(dir, `cut-${c}.png`), 13, 0.2))}`)
  const bars = scenes.flatMap(([, a, b]) => range(a + 0.5, b - 0.01, 2))
  lines.push(`- phone size (390 px wide, one frame per bar): ${(await phoneSheets(shot, bars, dir)).map((f) => path.basename(f)).join(', ')}`)
  lines.push('', '## Lint: frames that depend on seek order (state carried between frames)', '')
  const probe = scenes.flatMap(([, a, b]) => range(a, b - 0.01, Math.max(0.25, DURATION / 48)))
  const unstable = await orderLint(page, shot, probe)
  lines.push(unstable.length ? `- differ when reached backwards at: ${unstable.join(', ')} s — find the style at(t) sets in one branch and never resets` : 'none')
  lines.push('', '## Lint: text partly outside the frame', '')
  const seen = new Map()
  for (const [, a, b] of scenes)
    for (const t of range(a, b - 0.01, 0.25)) for (const s of await offFrameText(page, t)) seen.set(s, [...(seen.get(s) || []), t])
  if (!seen.size) lines.push('none')
  for (const [s, ts] of seen) lines.push(`- "${s}" at ${ts[0]}–${ts[ts.length - 1]} s`)
  lines.push('', '## Lint: reading time', '')
  const reading = await readingLint(page, scenes, Number(opt('phone-min', 12)))
  lines.push(...reading.lines)
  lines.splice(1, 0, reading.problems ? `**Reading lint: ${reading.problems} problem(s)** — fix them before the reviewer sees the pack (section at the end).` : 'Reading lint: clean (phone sizes, if any, are listed at the end).', '')
  if (pageErrors) lines.push('', `## ${pageErrors} page error(s) — see the console output`)
  fs.writeFileSync(path.join(dir, 'lint.md'), lines.join('\n') + '\n')
  console.log(lines.join('\n'))
  // A narrated film: what is SAID when, scene by scene, so the reviewer can check every claim
  // against what is on screen during its words (and catch on-screen text that repeats it).
  if (TL.V?.lines?.length) {
    const nar = [`# Narration (${TL.V.provider} voice) — what is said, when`, '']
    for (const [sid, a, b] of scenes) {
      const ls = TL.V.lines.filter((l) => l.t1 > a && l.t0 < b)
      if (!ls.length) continue
      nar.push(`## ${sid} · ${a.toFixed(2)}–${b.toFixed(2)} s`, '')
      for (const l of ls) nar.push(`- ${l.t0.toFixed(2)}–${l.t1.toFixed(2)} s · ${l.id}: "${l.text}"`)
      nar.push('')
    }
    fs.writeFileSync(path.join(dir, 'narration.md'), nar.join('\n'))
    console.log(`\nnarration.md: ${TL.V.lines.length} take(s) laid out for the reviewer`)
  }
  console.log(`\n${dir}`)
} else if (mode === 'render') {
  const name = opt('name', 'video')
  const workers = Number(opt('workers', 2))
  const dsf = Number(opt('dsf', 2))
  // Motion blur where a scene asks for it ({ mblur: n }): n subframes spread over half a frame
  // (a 180° shutter, looking back in time, never before the scene starts) are averaged by
  // ffmpeg. Frames elsewhere send one shot n times, so the stream rate stays constant.
  const SUB = Math.max(1, ...SCENES.map(([, , , o]) => o?.mblur ?? 1))
  const subTimes = (t) => {
    const sc = SCENES.find(([, a, b]) => t >= a && t < b)
    const n = sc?.[3]?.mblur ?? 1
    return Array.from({ length: n }, (_, i) => Math.max(sc ? sc[1] : 0, t - (i / n) * (0.5 / FPS)))
  }
  const blend = SUB > 1 ? `,tmix=frames=${SUB},select='eq(mod(n,${SUB}),${SUB - 1})',setpts=N/(${FPS}*TB)` : ''
  const f0 = Math.round(Number(opt('from', 0)) * FPS)
  const f1 = Math.round(Number(opt('to', DURATION)) * FPS)
  const total = f1 - f0
  const per = Math.ceil(total / workers)
  const started = Date.now()
  let done = 0
  const chunks = []
  await Promise.all(
    Array.from({ length: workers }, async (_, w) => {
      const a = f0 + w * per
      const b = Math.min(f1, a + per)
      if (a >= b) return
      const file = path.join(OUT, `${name}-chunk-${String(w).padStart(2, '0')}.mkv`)
      chunks[w] = file
      const { shot } = await openPage(browser, url, dsf)
      // dsf 2 = supersampled (3840×2160 → lanczos down): crisper text and hairlines.
      const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS * SUB), '-c:v', 'png', '-i', '-',
        '-vf', `scale=${W}:${H}:flags=lanczos${blend},format=yuv444p`, '-r', String(FPS), '-c:v', 'libx264', '-preset', 'medium', '-crf', '8', '-g', '120', file], { stdio: ['pipe', 'inherit', 'inherit'] })
      const closed = new Promise((r) => ff.on('close', r))
      for (let f = a; f < b; f++) {
        const ts = subTimes(f / FPS)
        const bufs = []
        for (const t of ts) bufs.push(await shot(t))
        for (let k = 0; k < SUB; k++) {
          const buf = bufs[Math.floor((k * bufs.length) / SUB)]
          if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r))
        }
        done++
        if (done % 60 === 0) {
          const el = (Date.now() - started) / 1000
          process.stdout.write(`\r${done}/${total} frames · ${(done / el).toFixed(1)} fps · eta ${Math.round(((total - done) * el) / done)}s   `)
        }
      }
      ff.stdin.end()
      await closed
    }),
  )
  console.log(`\nrendered ${total} frames in ${Math.round((Date.now() - started) / 1000)}s${SUB > 1 ? ` (motion blur: ${SUB} subframes in ${SCENES.filter(([, , , o]) => o?.mblur > 1).map(([id]) => id).join(', ')})` : ''}`)
  const list = path.join(OUT, `${name}-chunks.txt`)
  fs.writeFileSync(list, chunks.filter(Boolean).map((c) => `file '${c}'`).join('\n'))
  await new Promise((r) => spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', list, '-c', 'copy', path.join(OUT, `${name}.mkv`)], { stdio: 'inherit' }).on('close', r))
  for (const c of chunks.filter(Boolean)) fs.rmSync(c, { force: true })
  console.log(path.join(OUT, `${name}.mkv`))
} else {
  console.error('usage: node render.mjs serve | preview <t…> | sheet <t…> | sheet --from a --to b --step s | review [--scene id] | render [--workers n --dsf n --from a --to b --name x]')
}
if (pageErrors) console.error(`${pageErrors} page error(s) — fix before trusting these frames`)
await browser.close()
srv.close()
process.exit(pageErrors ? 1 : 0)
