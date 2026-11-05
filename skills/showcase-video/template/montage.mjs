// Labelled contact sheets drawn by Chromium, so labels never depend on ImageMagick or ffmpeg
// having a font engine (builds without FreeType drop every label silently).
//   node montage.mjs out.png [--cols 6] [--fit 420x280] [--caption] [--title text] file[|label] …
// --fit: each image scaled to fit that box; --caption: label under the tile instead of on it.
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'
import { loadPlaywright, chromePath } from './pw.mjs'

const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c])

// items: [{ src: file path or PNG Buffer, label }]
export async function montage(browser, items, out, { cols = 6, fit, caption = false, title, gap = 3, bg = '#222' } = {}) {
  const [fw, fh] = fit ? fit.split('x').map(Number) : []
  const box = fit ? `width:${fw}px;height:${fh}px;object-fit:contain` : ''
  const tiles = items.map(({ src, label }) => {
    const url = Buffer.isBuffer(src) ? `data:image/png;base64,${src.toString('base64')}` : pathToFileURL(path.resolve(src)).href
    return `<figure><img src="${url}" style="${box}">${label ? `<figcaption>${esc(label)}</figcaption>` : ''}</figure>`
  })
  const css = `
    body { margin: 0; display: inline-block; background: ${bg}; font: 500 15px/1.3 system-ui, sans-serif; color: #e8e8ee; }
    h1 { margin: 0; padding: 14px 16px 4px; font-size: 20px; }
    main { display: grid; grid-template-columns: repeat(${cols}, max-content); gap: ${gap}px; padding: ${gap}px; }
    figure { position: relative; margin: 0; }
    img { display: block; }
    figcaption { ${caption ? `width: ${fw ? `${fw}px` : 'auto'}; padding: 6px 2px 10px;` : 'position: absolute; left: 4px; bottom: 4px; padding: 1px 5px; border-radius: 3px; background: #000a; color: #fff;'} }`
  // A file next to `out` so file:// images load from a file:// page.
  const html = `${out}.montage.html`
  fs.writeFileSync(html, `<!doctype html><meta charset="utf-8"><style>${css}</style>${title ? `<h1>${esc(title)}</h1>` : ''}<main>${tiles.join('')}</main>`)
  const page = await browser.newPage({ viewport: { width: 800, height: 600 }, deviceScaleFactor: 1 })
  try {
    await page.goto(pathToFileURL(path.resolve(html)).href)
    await page.evaluate(() => Promise.all([...document.images].map((i) => i.decode().catch(() => {}))))
    const { width, height } = await page.evaluate(() => document.body.getBoundingClientRect())
    await page.setViewportSize({ width: Math.ceil(width), height: Math.ceil(height) })
    await page.screenshot({ path: out })
  } finally {
    await page.close()
    fs.rmSync(html, { force: true })
  }
  return out
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2)
  const opts = {}
  const items = []
  const out = args.shift()
  if (!out) throw new Error('usage: node montage.mjs out.png [--cols n] [--fit WxH] [--caption] [--title text] file[|label] …')
  for (let i = 0; i < args.length; i++) {
    const a = args[i]
    if (a === '--cols') opts.cols = Number(args[++i])
    else if (a === '--fit') opts.fit = args[++i]
    else if (a === '--title') opts.title = args[++i]
    else if (a === '--caption') opts.caption = true
    else {
      const [src, ...label] = a.split('|')
      if (!fs.existsSync(src)) throw new Error(`missing: ${src}`)
      items.push({ src, label: label.join('|') })
    }
  }
  const { chromium } = await loadPlaywright()
  const browser = await chromium.launch({ executablePath: chromePath() })
  try {
    console.log(await montage(browser, items, out, opts))
  } finally {
    await browser.close()
  }
}
