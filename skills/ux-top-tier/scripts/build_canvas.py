#!/usr/bin/env python3
"""Build canvas.json for a design-canvas prototype from a layout file and per-board notes.

Usage:
  python3 build_canvas.py --layout layout.json --project <dir con .dc.html> --notes <dir con *.json> \
      [--src canvas_publicado.json] [--out <project>/canvas.json] [--launch-focused Main.dc.html]

layout.json (ver assets/layout-example.json):
  {
    "title": "Producto — UX objetivo",
    "pages": [
      {"id": "uso-diario", "name": "1 · Uso diario: pantallas clave",
       "rows": [{"title": "Empezar el día", "boards": ["Main", "Inbox", "Cliente360"]}]}
    ],
    "intensive": ["Main", "Inbox"],              # se marcan con « · uso intensivo»
    "titles": {"Main": "1 · Hoy — bandeja"},       # opcional: título del tablero
    "before": {"Main": [{"file": "antes/Main.png", "src": "/_blob/<id>", "label": "Pendientes"}]},
    "new": ["Cliente360"],                         # pantallas nuevas, sin captura del «antes»
    "sidebar": {"board": "Sidebar", "page": "uso-diario", "title": "Navegación"},  # opcional
    "intro": {"page": "uso-diario", "text": "PANTALLAS DE USO INTENSIVO\\n\\n…"},     # opcional
    "launch_page": "uso-diario"
  }

Rows with more than 3 boards wrap onto extra lines of 3 under the same title.

Before captures: for every board in "before" the script writes project/Antes-<Board>.dc.html, a static board
with the screenshot(s) of the real product, and places it right above its board. "src" is the asset url the
canvas returned on upload (/_blob/<id>); "file" is the local copy, relative to layout.json, used to read the
size; "label" names each capture when there are several. Publish the generated boards with canvas.json.

Notes: every *.json in --notes is merged:
  {"Main.dc.html": {"title": "…", "antes": "ANTES · …", "ahora": "AHORA · …"}}
  files named polish-*.json may carry {"Main.dc.html": {"ahora_extra": "• …"}} which is appended to «Ahora».
Fields of --src (the published canvas.json: v, attachments, designSystems, …) are preserved.
"""
import argparse
import html
import json
import pathlib
import re
import struct
import sys

COL_X = [0, 1520, 3040]
BOARD_W = 1440
NOTE_W = 700
NOTE_GAP = 40
NOTE_FLOOR = 560
ROW_GAP = 420
TITLE_OFFSET = 300
BEFORE_PREFIX = 'Antes-'
BEFORE_GAP = 120
LABEL_H = 32
JPEG_SOF = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}

BEFORE_BOARD = '''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Antes · {title}</title>
<script src="./support.js"></script>
<!-- Generado por build_canvas.py con las capturas del «antes». No lo edites a mano: cambia layout.json. -->
</head>
<body>
<x-dc>
<helmet>
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500&amp;display=swap" rel="stylesheet">
<style>body{{margin:0}}</style>
</helmet>
<div style="width: {w}px; height: {h}px; display: flex; flex-direction: column; background: #FAFAFA; font-family: Geist, system-ui, sans-serif; font-size: 13px; color: #5E5E68">
{body}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{w},"height":{h}}}}}'>
class Component extends DCLogic {{
  renderVals() {{ return {{}}; }}
}}
</script>
</body>
</html>
'''


def board_height(project: pathlib.Path, name: str) -> int:
    text = (project / f'{name}.dc.html').read_text(encoding='utf-8')
    m = re.search(r'"\$preview"\s*:\s*\{\s*"width"\s*:\s*\d+\s*,\s*"height"\s*:\s*(\d+)', text)
    return int(m.group(1)) if m else 900


def note_height(text: str) -> int:
    lines = sum(max(1, -(-len(par) // 50)) for par in text.split('\n'))
    return max(NOTE_FLOOR, lines * 32 + 56)


def image_size(path: pathlib.Path):
    """(width, height) of a PNG, JPEG, GIF or WebP file, or None."""
    data = path.read_bytes()
    if data[:8] == b'\x89PNG\r\n\x1a\n':
        return struct.unpack('>II', data[16:24])
    if data[:6] in (b'GIF87a', b'GIF89a'):
        return struct.unpack('<HH', data[6:10])
    if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        kind = data[12:16]
        if kind == b'VP8X':
            return 1 + int.from_bytes(data[24:27], 'little'), 1 + int.from_bytes(data[27:30], 'little')
        if kind == b'VP8L':
            bits = int.from_bytes(data[21:25], 'little')
            return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
        if kind == b'VP8 ':
            w, h = struct.unpack('<HH', data[26:30])
            return w & 0x3FFF, h & 0x3FFF
    if data[:2] == b'\xff\xd8':
        i = 2
        while i + 9 < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in JPEG_SOF:
                h, w = struct.unpack('>HH', data[i + 5:i + 9])
                return w, h
            if marker == 0xFF or marker == 0x01 or 0xD0 <= marker <= 0xD8:
                i += 1 if marker == 0xFF else 2
                continue
            i += 2 + struct.unpack('>H', data[i + 2:i + 4])[0]
    return None


def before_shots(spec, base: pathlib.Path) -> list:
    """Normalise one "before" entry to [{'src', 'label', 'h'}] with the height scaled to the board width."""
    items = spec if isinstance(spec, list) else [spec]
    shots = []
    for item in items:
        if isinstance(item, str):
            item = {'src': item}
        if not item.get('src'):
            sys.exit(f'«before»: falta src (la url /_blob/… que devolvió la subida) en {item}')
        size = None
        if item.get('file'):
            local = base / item['file']
            if not local.exists():
                sys.exit(f'«before»: no existe {local}')
            size = image_size(local)
        h = round(size[1] * BOARD_W / size[0]) if size else 900
        shots.append({'src': item['src'], 'label': item.get('label', ''), 'h': h, 'fit': not size})
    return shots


def write_before_board(project: pathlib.Path, name: str, title: str, shots: list) -> int:
    parts, total = [], 0
    for s in shots:
        if len(shots) > 1:
            parts.append(f'<div style="flex: none; height: {LABEL_H}px; display: flex; align-items: center; padding: 0 16px">'
                         f'{html.escape(s["label"] or "Captura")}</div>')
            total += LABEL_H
        fit = '; object-fit: contain; object-position: top' if s['fit'] else ''
        alt = html.escape('Captura del producto real: ' + (s['label'] or title))
        parts.append(f'<img src="{html.escape(s["src"])}" alt="{alt}" style="display: block; flex: none; width: {BOARD_W}px; height: {s["h"]}px{fit}">')
        total += s['h']
    text = BEFORE_BOARD.format(title=html.escape(title), w=BOARD_W, h=total, body='\n'.join(parts))
    (project / f'{BEFORE_PREFIX}{name}.dc.html').write_text(text, encoding='utf-8')
    return total


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--layout', required=True)
    ap.add_argument('--project', required=True)
    ap.add_argument('--notes', required=True)
    ap.add_argument('--src')
    ap.add_argument('--out')
    ap.add_argument('--launch-focused', help='abre en modo de juego sobre este tablero (para revisar con clics)')
    args = ap.parse_args()

    project = pathlib.Path(args.project)
    layout_path = pathlib.Path(args.layout)
    layout = json.loads(layout_path.read_text(encoding='utf-8'))
    base = json.loads(pathlib.Path(args.src).read_text(encoding='utf-8')) if args.src else {'v': 3, 'attachments': {}, 'designSystems': []}
    prev_boards = base.get('boards', {})

    notes_in, polish = {}, {}
    for p in sorted(pathlib.Path(args.notes).glob('*.json')):
        data = json.loads(p.read_text(encoding='utf-8'))
        (polish if p.name.startswith('polish-') else notes_in).update(data)

    intensive = set(layout.get('intensive', []))
    titles = layout.get('titles', {})
    before = {name: before_shots(spec, layout_path.parent) for name, spec in layout.get('before', {}).items()}
    new_screens = set(layout.get('new', []))
    boards, notes, order, missing, generated, no_before = {}, {}, [], [], [], []

    def title_of(name: str, mark: bool = True) -> str:
        t = titles.get(name) or notes_in.get(f'{name}.dc.html', {}).get('title') or name
        return t + ' · uso intensivo' if mark and name in intensive and 'uso intensivo' not in t else t

    for page in layout['pages']:
        pid = page['id']
        row_y = 0
        for ri, row in enumerate(page['rows']):
            notes[f'{pid}-row{ri + 1}'] = {'kind': 'title1', 'maxW': 4480, 'text': row['title'], 'w': 240,
                                           'x': 0, 'y': row_y - TITLE_OFFSET, 'page': pid}
            lines = [row['boards'][k:k + len(COL_X)] for k in range(0, len(row['boards']), len(COL_X))] or [[]]
            for line in lines:
                present = [(ci, name) for ci, name in enumerate(line) if (project / f'{name}.dc.html').exists()]
                missing += [f'{name}.dc.html' for name in line if not (project / f'{name}.dc.html').exists()]
                band = 0
                for ci, name in present:
                    if name in before:
                        h = write_before_board(project, name, title_of(name, False), before[name])
                        fname = f'{BEFORE_PREFIX}{name}.dc.html'
                        boards[fname] = {'x': COL_X[ci], 'y': row_y, 'w': BOARD_W, 'h': h,
                                         'title': f'Antes · {title_of(name, False)}', 'page': pid}
                        order.append(fname)
                        generated.append(fname)
                        band = max(band, h)
                    elif name not in new_screens:
                        no_before.append(name)
                board_y = row_y + (band + BEFORE_GAP if band else 0)

                row_h = 0
                row_note_h = NOTE_FLOOR
                for ci, name in present:
                    fname = f'{name}.dc.html'
                    h = board_height(project, name)
                    row_h = max(row_h, h)
                    info = notes_in.get(fname, {})
                    b = {'x': COL_X[ci], 'y': board_y, 'w': BOARD_W, 'h': h, 'title': title_of(name),
                         'expand': 'fill', 'is_interactive': True, 'page': pid}
                    for extra in ('frameless', 'radius', 'guides'):
                        if extra in prev_boards.get(fname, {}):
                            b[extra] = prev_boards[fname][extra]
                    boards[fname] = b
                    order.append(fname)
                    antes, ahora = info.get('antes'), info.get('ahora')
                    extra_txt = polish.get(fname, {}).get('ahora_extra')
                    if ahora and extra_txt:
                        ahora = ahora.rstrip() + '\n\nFRICCIÓN MÍNIMA · uso intensivo\n' + extra_txt.strip()
                    note_y = board_y + h + NOTE_GAP
                    if antes:
                        hh = note_height(antes)
                        row_note_h = max(row_note_h, hh)
                        notes[f'{name}-antes'] = {'x': b['x'], 'y': note_y, 'w': NOTE_W, 'maxH': hh, 'size': 24,
                                                  'fill': 'orange', 'text': antes, 'page': pid}
                    if ahora:
                        hh = note_height(ahora)
                        row_note_h = max(row_note_h, hh)
                        notes[f'{name}-ahora'] = {'x': b['x'] + 740, 'y': note_y, 'w': NOTE_W, 'maxH': hh, 'size': 24,
                                                  'fill': 'blue', 'text': ahora, 'page': pid}
                    if not antes or not ahora:
                        print(f'aviso: {fname} sin nota «{"Antes" if not antes else "Ahora"}»', file=sys.stderr)
                row_y = board_y + row_h + NOTE_GAP + row_note_h + ROW_GAP

    sb = layout.get('sidebar')
    if sb and (project / f"{sb['board']}.dc.html").exists():
        fname = f"{sb['board']}.dc.html"
        boards[fname] = {'x': -392, 'y': 0, 'w': 232, 'h': board_height(project, sb['board']),
                         'title': sb.get('title', 'Navegación'), 'is_interactive': True, 'page': sb['page']}
        order.append(fname)

    intro = layout.get('intro')
    if intro:
        h = max(400, sum(max(1, -(-len(par) // 110)) for par in intro['text'].split('\n')) * 32 + 64)
        notes['intro'] = {'x': 0, 'y': -TITLE_OFFSET - 80 - h, 'w': 1440, 'maxH': h, 'size': 24,
                          'text': intro['text'], 'page': intro['page']}

    out = dict(base)
    out['title'] = layout.get('title', base.get('title', 'Prototipo UX'))
    out['boards'] = boards
    out['order'] = order
    out['notes'] = notes
    out['pages'] = [{'id': p['id'], 'name': p['name']} for p in layout['pages']]
    if args.launch_focused:
        out['launch'] = {'view': 'focused', 'file': args.launch_focused}
    else:
        out['launch'] = {'view': 'canvas', 'page': layout.get('launch_page', layout['pages'][0]['id'])}

    dest = pathlib.Path(args.out) if args.out else project / 'canvas.json'
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'tableros {len(boards)} · notas {len(notes)} · páginas {len(out["pages"])} · faltan {missing or "ninguno"} → {dest}')
    if generated:
        print('tableros «Antes» generados (publícalos con el canvas.json): ' + ', '.join(generated))
    if no_before:
        print('aviso: sin captura del «antes» (si son pantallas nuevas, añádelas a "new"): ' + ', '.join(no_before), file=sys.stderr)
    stale = sorted(p.name for p in project.glob(f'{BEFORE_PREFIX}*.dc.html') if p.name not in generated)
    if stale:
        print('aviso: sobran tableros «Antes» de otra ejecución; bórralos y publícalos con null: ' + ', '.join(stale), file=sys.stderr)
    if missing:
        sys.exit(1)


if __name__ == '__main__':
    main()
