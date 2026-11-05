// Playwright and a headless Chromium for render.mjs and capture.mjs (never the user's own browser).
// `node pw.mjs` checks both and says how to install what is missing.
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { spawnSync } from 'node:child_process'
import { fileURLToPath, pathToFileURL } from 'node:url'

const HINT = 'npm i -g playwright && npx playwright install chromium-headless-shell (or set PLAYWRIGHT=/path/to/playwright/index.mjs)'

// Playwright from a local install, $PLAYWRIGHT, the global npm root, or mise.
export async function loadPlaywright() {
  const home = os.homedir()
  const npmRoot = spawnSync('npm', ['root', '-g'], { encoding: 'utf8' }).stdout?.trim()
  const candidates = [process.env.PLAYWRIGHT, 'playwright', npmRoot && `${npmRoot}/playwright/index.mjs`, `${home}/.local/share/mise/installs/npm-playwright/latest/node_modules/playwright/index.mjs`].filter(Boolean)
  for (const c of candidates) {
    try {
      return await import(c.startsWith('/') ? pathToFileURL(c).href : c)
    } catch {}
  }
  throw new Error(`playwright not found: ${HINT}`)
}

// The newest installed browser build of a kind, found on disk: a Playwright package newer
// than the downloaded browsers would otherwise look for a build that isn't there.
function newest(prefix, subs) {
  const dir = process.platform === 'darwin' ? path.join(os.homedir(), 'Library/Caches/ms-playwright') : path.join(os.homedir(), '.cache/ms-playwright')
  const builds = fs.existsSync(dir) ? fs.readdirSync(dir).filter((d) => d.startsWith(prefix) && /^\d+$/.test(d.slice(prefix.length))).sort((a, b) => Number(b.slice(prefix.length)) - Number(a.slice(prefix.length))) : []
  for (const b of builds)
    for (const sub of subs) {
      const p = path.join(dir, b, sub)
      if (fs.existsSync(p)) return p
    }
  return undefined
}
// The headless shell renders faster than full Chromium.
export function chromePath() {
  if (process.env.CHROME) return process.env.CHROME
  return newest('chromium_headless_shell-', ['chrome-headless-shell-linux64', 'chrome-headless-shell-mac-arm64', 'chrome-headless-shell-mac-x64'].map((d) => `${d}/chrome-headless-shell`))
}
// Full Chromium, for a visible window (capture.mjs login): the headless shell can't show one.
export function fullChromePath() {
  const app = (d) => [`${d}/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing`, `${d}/Chromium.app/Contents/MacOS/Chromium`]
  return newest('chromium-', [...app('chrome-mac-arm64'), ...app('chrome-mac-x64'), ...app('chrome-mac'), 'chrome-linux64/chrome', 'chrome-linux/chrome'])
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  try {
    await loadPlaywright()
    console.log(`playwright ✓ · headless shell ${chromePath() ? '✓' : 'missing (full Chromium will be used): npx playwright install chromium-headless-shell'} · Chromium for capture.mjs login ${fullChromePath() ? '✓' : 'missing: npx playwright install chromium'}`)
  } catch (e) {
    console.log(e.message)
    process.exit(1)
  }
}
