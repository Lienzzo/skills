#!/usr/bin/env node
/*
 * Logic check for .dc.html boards without rendering them.
 *
 * For each board:
 *   1. Instantiates the Component with a minimal DCLogic stub and calls renderVals().
 *   2. Verifies that every {{hole}} in the markup resolves (except loop variables).
 *   3. Calls every function returned by renderVals once (simulating clicks/inputs) and re-renders,
 *      reporting any exception.
 *   4. Flags setState calls made during render (they loop in the real runtime).
 *
 * Only for design-canvas boards (*.dc.html). The single HTML page is checked in the browser.
 *
 * Usage: node check_logic.js <project-dir> Board1 [Board2 ...]
 * Exit code 1 if any board fails.
 */
const fs = require('fs');
const path = require('path');

const [dir, ...names] = process.argv.slice(2);
if (!dir || !names.length) {
  console.error('Uso: node check_logic.js <carpeta> Tablero1 [Tablero2 ...]');
  process.exit(2);
}

let failed = false;
const realSetTimeout = global.setTimeout;
const realClearTimeout = global.clearTimeout;

for (const name of names) {
  try {
    failed = checkBoard(name) || failed;
  } catch (e) {
    console.log(`${name}: ERROR inesperado: ${e.message}`);
    failed = true;
  } finally {
    global.setTimeout = realSetTimeout;
    global.clearTimeout = realClearTimeout;
  }
}

process.exit(failed ? 1 : 0);

// Returns true when the board fails.
function checkBoard(name) {
  const file = path.join(dir, name.endsWith('.dc.html') ? name : name + '.dc.html');
  if (!fs.existsSync(file)) {
    console.log(`${name}: NO EXISTE (${file})`);
    return true;
  }
  const html = fs.readFileSync(file, 'utf8');
  if (!html.includes('data-dc-script')) {
    console.log(`${name}: falta <script type="text/x-dc" data-dc-script> (¿es un tablero del lienzo?)`);
    return true;
  }
  const code = html.split('data-dc-script')[1].split('>').slice(1).join('>').split('</script>')[0];

  let inRender = false;
  let renderSetState = 0;
  class DCLogic {
    constructor(props) { this.props = props || {}; this.state = {}; }
    setState(p) {
      if (inRender) renderSetState++;
      this.state = Object.assign({}, this.state, typeof p === 'function' ? p(this.state) : p);
    }
  }

  global.setTimeout = () => 0;
  global.clearTimeout = () => {};
  let Component;
  try {
    Component = new Function('DCLogic', code + '\nreturn Component;')(DCLogic);
  } catch (e) {
    console.log(`${name}: ERROR al evaluar el script: ${e.message}`);
    return true;
  }

  const props = {};
  const propsDecl = html.match(/data-props='([^']*)'/);
  if (propsDecl) {
    try {
      const decl = JSON.parse(propsDecl[1]);
      for (const [k, v] of Object.entries(decl)) if (!k.startsWith('$') && v && 'default' in v) props[k] = v.default;
    } catch (e) { /* ignore */ }
  }

  const c = new Component(props);
  if (typeof c.componentDidMount === 'function') {
    try { c.componentDidMount(); } catch (e) { console.log(`${name}: componentDidMount lanza: ${e.message}`); }
  }

  const render = () => { inRender = true; try { return c.renderVals(); } finally { inRender = false; } };
  let vals;
  try {
    vals = render();
  } catch (e) {
    console.log(`${name}: ERROR en renderVals inicial: ${e.message}`);
    return true;
  }

  const markup = html.split('<script type="text/x-dc"')[0];
  const holes = [...markup.matchAll(/\{\{\s*([\w$.]+)\s*\}\}/g)].map((m) => m[1]);
  const loopVars = new Set([...markup.matchAll(/\bas="(\w+)"/g)].map((m) => m[1]));
  const missing = [...new Set(holes.filter((h) => {
    const root = h.split('.')[0];
    if (loopVars.has(root) || ['true', 'false', 'null'].includes(h) || /^-?\d/.test(h)) return false;
    let v = vals;
    for (const k of h.split('.')) { if (v == null) return true; v = v[k]; }
    return v === undefined;
  }))];

  const fns = [];
  (function walk(v, depth) {
    if (depth > 7 || v == null) return;
    if (typeof v === 'function') { fns.push(v); return; }
    if (Array.isArray(v)) { v.forEach((x) => walk(x, depth + 1)); return; }
    if (typeof v === 'object') Object.values(v).forEach((x) => walk(x, depth + 1));
  })(vals, 0);

  let errors = 0;
  const fakeEvent = { target: { value: 'x', checked: true }, key: 'x', preventDefault() {}, stopPropagation() {} };
  for (const f of fns) {
    try { f(fakeEvent); render(); } catch (e) { errors++; if (errors <= 5) console.log(`${name}: manejador lanza: ${e.message}`); }
  }

  const ok = !missing.length && !errors && !renderSetState;
  console.log(`${name}: ${ok ? 'ok' : 'REVISAR'} · manejadores ${fns.length} · errores ${errors} · huecos sin resolver ${missing.length ? missing.join(', ') : 'ninguno'}${renderSetState ? ` · setState durante render ${renderSetState}` : ''}`);
  return !ok;
}
