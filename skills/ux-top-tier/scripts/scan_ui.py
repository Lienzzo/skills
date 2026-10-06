#!/usr/bin/env python3
"""UI quality scan for prototype screens. Catches the bugs that make a prototype feel "decent" instead of "top tier".

Works with the single HTML page (assets/prototype-template.html) and with design-canvas boards (*.dc.html).

Checks:
  ids      visible technical IDs (e.g. CLS-218, PER-0931) in markup or data strings
  nested   <a>/<button> nested inside another <a>/<button>
  flex     (canvas) literal text mixed with a {{hole}} as direct children of a flex container ("Espera47 min")
  menus    popovers/menus open by default in the initial state (keys like menuOpen: true, open: 'x')
  tokens   CSS variables used but not defined in the light theme, or defined in light but missing in dark
  links    canvas: href="X.dc.html" to a board that does not exist; page: href="#x" to a screen that does not exist
  plural   "1 <palabra>s" literal patterns (e.g. "1 entregas")
  before   page: a screen without its «before» capture (before: null marks a new screen) or a capture file that
           does not exist

Usage:
  python3 scan_ui.py --project <dir> [Board | file.html ...] [--allow-id SKU] [--skip menus]
Without names it scans every *.html in the folder except the generated Antes-*.dc.html boards. A bare name (Main) means Main.dc.html.
Exit code 1 if anything is reported.
"""
import argparse
import pathlib
import re
import sys
from html.parser import HTMLParser

VOID = {'br', 'img', 'input', 'meta', 'link', 'hr', 'path', 'circle', 'rect', 'line', 'polyline', 'polygon', 'ellipse', 'source'}
ID_RE = re.compile(r"""['">]([A-Z]{2,5}-\d{2,5})['"<]""")
OPEN_STATE_RE = re.compile(r"\b((?!peek|panel|side|drawer)\w*(?:[Oo]pen|[Mm]enu|[Pp]opover|[Dd]ropdown)\w*)\s*:\s*(true|'[^']+')")
LIGHT_RE = re.compile(r'(?:\.pp|:root)\{([^}]*)\}')
DARK_RE = re.compile(r'(?:\.pp\.dark|:root\[data-theme="dark"\])\{([^}]*)\}')
SCREEN_ID_RE = re.compile(r"""screen\(\{\s*id:\s*['"]([\w-]+)['"]""")
BEFORE_RE = re.compile(r"""\bbefore\s*:\s*(null|false|\[[^\]]*\]|(['"])[^'"]*\2)""")
IMAGE_RE = re.compile(r"""['"]([^'"]+\.(?:png|jpe?g|webp|gif|avif))['"]""", re.I)
GENERATED = 'Antes-'  # tableros con las capturas del «antes», generados por build_canvas.py
PLURAL_RE = re.compile(r"[>'\s]1 ([a-záéíóúñ]{3,}s)\b")
INVARIANT = {
    'mes', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'tesis', 'crisis', 'análisis', 'virus', 'campus',
    'bus', 'gas', 'atlas', 'caos', 'dosis', 'síntesis', 'énfasis', 'oasis', 'cactus', 'bonus', 'plus', 'status',
    'corpus', 'lapsus',
}


def singular(word: str) -> bool:
    return word in INVARIANT or word.endswith(('is', 'us', 'ss', 'ás', 'és', 'ís', 'ós', 'ús'))


class FlexTextParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.hits = []

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        style = dict(attrs).get('style', '') or ''
        flex = bool(re.search(r'display:\s*(inline-)?flex', style)) or '{{' in style
        self.stack.append([tag, flex, [], self.getpos()[0]])

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        while self.stack:
            node = self.stack.pop()
            if node[0] == tag:
                if node[1]:
                    for chunk in node[2]:
                        s = chunk.strip()
                        if '{{' in s and re.search(r'\s', re.sub(r'\{\{[^}]*\}\}', 'X', s)) and re.sub(r'\{\{[^}]*\}\}', '', s).strip():
                            self.hits.append((node[3], s[:80]))
                break

    def handle_data(self, data):
        if self.stack:
            self.stack[-1][2].append(data)


def resolve(project: pathlib.Path, names: list) -> list:
    if not names:
        return sorted(p for p in project.glob('*.html') if not p.name.startswith(GENERATED))
    return [project / (n if n.endswith('.html') else f'{n}.dc.html') for n in names]


def line_of(text: str, pos: int) -> int:
    return text[:pos].count('\n') + 1


def scan(path: pathlib.Path, project: pathlib.Path, allow_ids: list, skip: set) -> list:
    text = path.read_text(encoding='utf-8')
    canvas = path.name.endswith('.dc.html')
    if canvas:
        parts = text.split('<script type="text/x-dc"')
        html, js = parts[0], (parts[1] if len(parts) > 1 else '')
    else:
        html = js = text
    out = []
    if 'ids' not in skip:
        for m in ID_RE.finditer(text):
            if not any(m.group(1).startswith(a) for a in allow_ids):
                out.append(f'ids:{line_of(text, m.start())}: ID técnico visible «{m.group(1)}» (usa una ruta legible)')
    if 'nested' not in skip:
        stack = []
        for m in re.finditer(r'<(/?)(a|button)\b', html):
            tag = m.group(2)
            if m.group(1):
                if stack and stack[-1] == tag:
                    stack.pop()
            else:
                if stack:
                    out.append(f'nested:{line_of(html, m.start())}: <{tag}> dentro de <{stack[-1]}>')
                stack.append(tag)
    if canvas and 'flex' not in skip:
        parser = FlexTextParser()
        parser.feed(html)
        for line, s in parser.hits:
            out.append(f'flex:{line}: texto y hueco mezclados en contenedor flex: «{s}» (envuélvelo en <span>)')
    if 'menus' not in skip:
        initial = re.findall(r'this\.state\s*=\s*\{(.*?)\};', js, re.S) + re.findall(r'\binitial\s*:\s*\{([^}]*)\}', js)
        for block in initial:
            for m in OPEN_STATE_RE.finditer(block):
                out.append(f'menus: estado inicial {m.group(1)}: {m.group(2)} (¿popover abierto por defecto?)')
    if 'tokens' not in skip:
        light, dark = LIGHT_RE.search(text), DARK_RE.search(text)
        if light and dark:
            defined = set(re.findall(r'(--[\w-]+):', light.group(1)))
            defined_dark = set(re.findall(r'(--[\w-]+):', dark.group(1)))
            used = set(re.findall(r'var\((--[\w-]+)\s*[,)]', text))
            for v in sorted(used - defined):
                out.append(f'tokens: {v} usado sin definir en el tema claro')
            for v in sorted(defined - defined_dark):
                out.append(f'tokens: {v} definido en el tema claro pero no en el oscuro')
        elif not canvas:
            out.append('tokens: no encuentro :root{…} y :root[data-theme="dark"]{…}')
    if 'links' not in skip:
        if canvas:
            for target in sorted(set(re.findall(r'href="([\w-]+\.dc\.html)', text))):
                if not (project / target).exists():
                    out.append(f'links: enlace roto a {target}')
        else:
            sources = [text] + [p.read_text(encoding='utf-8') for p in sorted((project / 'screens').glob('*.js'))]
            ids = {i for src in sources for i in SCREEN_ID_RE.findall(src)}
            for target in sorted(set(re.findall(r'href="#([\w-]+)"', text))):
                if target not in ids:
                    out.append(f'links: enlace a #{target}, que no es ninguna pantalla')
    if not canvas and 'before' not in skip:
        sources = [text] + [p.read_text(encoding='utf-8') for p in sorted((project / 'screens').glob('*.js'))]
        for src in sources:
            starts = list(SCREEN_ID_RE.finditer(src))
            for i, m in enumerate(starts):
                chunk = src[m.start():starts[i + 1].start() if i + 1 < len(starts) else len(src)]
                found = BEFORE_RE.search(chunk)
                if not found:
                    out.append(f'before: la pantalla «{m.group(1)}» no tiene captura del antes (before: null si es nueva)')
                    continue
                for img in IMAGE_RE.findall(found.group(1)):
                    if not (project / img).exists():
                        out.append(f'before: la captura {img} de «{m.group(1)}» no existe')
    if 'plural' not in skip:
        for m in PLURAL_RE.finditer(html):
            if not singular(m.group(1)):
                out.append(f'plural:{line_of(html, m.start())}: «1 {m.group(1)}»')
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', required=True, help='carpeta con los .html o .dc.html')
    parser.add_argument('--allow-id', action='append', default=[], help='prefijo de código de negocio permitido (p. ej. SKU)')
    parser.add_argument('--skip', action='append', default=[], help='checks a saltar: ids nested flex menus tokens links plural before')
    parser.add_argument('boards', nargs='*')
    args = parser.parse_args()
    project = pathlib.Path(args.project)
    if not project.is_dir():
        sys.exit(f'No existe la carpeta {project}')
    paths = resolve(project, args.boards)
    if not paths:
        sys.exit(f'No hay archivos .html en {project}')
    total = 0
    for path in paths:
        if not path.exists():
            print(f'{path.name}: NO EXISTE')
            total += 1
            continue
        for item in scan(path, project, args.allow_id, set(args.skip)):
            print(f'{path.name} {item}')
            total += 1
    print(f'— {total} avisos en {len(paths)} archivos')
    sys.exit(1 if total else 0)


if __name__ == '__main__':
    main()
