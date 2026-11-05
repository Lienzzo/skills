// Real screens of the product, for scenes that put the actual app under the camera: the
// agent's own Chromium (never the user's logged-in browser), dsf 2 so a camera push up to 2×
// stays sharp, personal data replaced in the DOM before every shot, and the box of every
// element the cursor will touch saved for the scene.
//
//   node capture.mjs login <url> [state=../.auth/state.json]
//       opens a window: the HUMAN logs in (never type their password), then closes it; the
//       session is saved outside src/ (it holds cookies: never commit or publish it).
//   A capture script per film (e.g. capture-shots.mjs, kept in src/ so captures can be redone):
//       import { openApp } from './capture.mjs'
//       const app = await openApp('http://localhost:3000/inbox', { anonymize: [['Jane Roe', 'Client A']] })
//       await app.shot('01-inbox')                                          // → assets/ui/01-inbox.png
//       await app.shot('02-card', app.page.getByRole('article').first())     // one element
//       app.boxes.send = await app.box(app.page.getByRole('button', { name: 'Send' }))
//       await app.close()                                                    // → assets/ui/boxes.json
// Boxes are [centerX, centerY, width, height] in CSS px of the capture viewport: draw a full
// shot at that size in the scene and they line up with it (scale them with the image otherwise).
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { loadPlaywright, chromePath, fullChromePath } from './pw.mjs'

const ROOT = path.dirname(fileURLToPath(import.meta.url))
const STATE = path.join(ROOT, '../.auth/state.json')

// Text nodes, field values, titles and placeholders; dev overlays (Next.js, Vite) removed.
export async function anonymize(page, pairs = []) {
  await page.evaluate((pairs) => {
    for (const sel of ['nextjs-portal', 'vite-error-overlay', '[data-nextjs-toast]', '#__next-build-watcher']) for (const el of document.querySelectorAll(sel)) el.remove()
    const swap = (s) => pairs.reduce((acc, [a, b]) => acc.split(a).join(b), s)
    const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT)
    for (let n = walk.nextNode(); n; n = walk.nextNode()) if (pairs.some(([a]) => n.nodeValue.includes(a))) n.nodeValue = swap(n.nodeValue)
    for (const el of document.querySelectorAll('input, textarea')) el.value = swap(el.value)
    for (const el of document.querySelectorAll('[title], [placeholder], [aria-label]'))
      for (const at of ['title', 'placeholder', 'aria-label']) if (el.hasAttribute(at)) el.setAttribute(at, swap(el.getAttribute(at)))
  }, pairs)
}

// Network quiet, fonts loaded, and a moment for entrance animations to finish.
export async function settle(page, ms = 400) {
  await page.waitForLoadState('networkidle').catch(() => {})
  await page.evaluate(() => document.fonts.ready)
  await page.waitForTimeout(ms)
}

export async function openApp(url, { state = STATE, width = 1920, height = 1080, dsf = 2, locale, colorScheme, anonymize: pairs = [], out = path.join(ROOT, 'assets/ui') } = {}) {
  const { chromium } = await loadPlaywright()
  const browser = await chromium.launch({ executablePath: chromePath() })
  const ctx = await browser.newContext({
    viewport: { width, height },
    deviceScaleFactor: dsf,
    ...(locale && { locale }),
    ...(colorScheme && { colorScheme }),
    ...(fs.existsSync(state) && { storageState: state }),
  })
  const page = await ctx.newPage()
  await page.goto(url)
  await settle(page)
  fs.mkdirSync(out, { recursive: true })
  const boxesFile = path.join(out, 'boxes.json')
  const boxes = fs.existsSync(boxesFile) ? JSON.parse(fs.readFileSync(boxesFile, 'utf8')) : {}
  return {
    page,
    boxes,
    settle: (ms) => settle(page, ms),
    // The whole viewport, or one element (a locator): anonymized first, every time.
    async shot(name, target) {
      if (!/^[\w.-]+$/.test(name) || name.startsWith('.')) throw new Error(`shot name must be a plain file name: ${name}`)
      await anonymize(page, pairs)
      const file = path.join(out, `${name}.png`)
      await (target ? target.screenshot({ path: file }) : page.screenshot({ path: file }))
      console.log('✓', path.relative(ROOT, file))
      return file
    },
    async box(target) {
      const r = await target.boundingBox()
      if (!r) throw new Error(`no box (hidden or detached): ${target}`)
      return [Math.round(r.x + r.width / 2), Math.round(r.y + r.height / 2), Math.round(r.width), Math.round(r.height)]
    },
    async close() {
      fs.writeFileSync(boxesFile, JSON.stringify(boxes, null, 1))
      await browser.close()
    },
  }
}

// A visible window where the human logs in; the session is saved when they close it.
export async function login(url, file = STATE, { headless = false, until = (page) => page.waitForEvent('close', { timeout: 0 }) } = {}) {
  const { chromium } = await loadPlaywright()
  const browser = await chromium.launch({ headless, executablePath: headless ? chromePath() : fullChromePath() })
  const ctx = await browser.newContext({ viewport: null })
  const page = await ctx.newPage()
  await page.goto(url)
  console.log('Log in in the window, then close the tab. Nothing typed there is read or stored, only the session cookies.')
  await until(page)
  // Owner-only from the first byte: a 700 folder, a 600 temp file renamed into place.
  fs.mkdirSync(path.dirname(file), { recursive: true, mode: 0o700 })
  fs.chmodSync(path.dirname(file), 0o700)
  const tmp = `${file}.${process.pid}.tmp`
  const fd = fs.openSync(tmp, 'w', 0o600)
  fs.writeSync(fd, JSON.stringify(await ctx.storageState()))
  fs.closeSync(fd)
  fs.renameSync(tmp, file)
  await browser.close()
  console.log(`session saved: ${file} (keep it out of git; delete it when the film is delivered)`)
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const [mode, url, state] = process.argv.slice(2)
  if (mode !== 'login' || !url) throw new Error('usage: node capture.mjs login <url> [state-file]')
  await login(url, state ? path.resolve(state) : STATE)
}
