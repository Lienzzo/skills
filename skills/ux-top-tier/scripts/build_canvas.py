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
    "sidebar": {"board": "Sidebar", "page": "uso-diario", "title": "Navegación"},  # opcional
    "intro": {"page": "uso-diario", "text": "PANTALLAS DE USO INTENSIVO\\n\\n…"},     # opcional
    "launch_page": "uso-diario"
  }

Rows with more than 3 boards wrap onto extra lines of 3 under the same title.

Notes: every *.json in --notes is merged:
  {"Main.dc.html": {"title": "…", "antes": "ANTES · …", "ahora": "AHORA · …"}}
  files named polish-*.json may carry {"Main.dc.html": {"ahora_extra": "• …"}} which is appended to «Ahora».
Fields of --src (the published canvas.json: v, attachments, designSystems, …) are preserved.
"""
import argparse
import json
import pathlib
import re
import sys

COL_X = [0, 1520, 3040]
NOTE_W = 700
NOTE_GAP = 40
NOTE_FLOOR = 560
ROW_GAP = 420
TITLE_OFFSET = 300


def board_height(project: pathlib.Path, name: str) -> int:
    text = (project / f'{name}.dc.html').read_text(encoding='utf-8')
    m = re.search(r'"\$preview"\s*:\s*\{\s*"width"\s*:\s*\d+\s*,\s*"height"\s*:\s*(\d+)', text)
    return int(m.group(1)) if m else 900


def note_height(text: str) -> int:
    lines = sum(max(1, -(-len(par) // 50)) for par in text.split('\n'))
    return max(NOTE_FLOOR, lines * 32 + 56)


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
    layout = json.loads(pathlib.Path(args.layout).read_text(encoding='utf-8'))
    base = json.loads(pathlib.Path(args.src).read_text(encoding='utf-8')) if args.src else {'v': 3, 'attachments': {}, 'designSystems': []}
    prev_boards = base.get('boards', {})

    notes_in, polish = {}, {}
    for p in sorted(pathlib.Path(args.notes).glob('*.json')):
        data = json.loads(p.read_text(encoding='utf-8'))
        (polish if p.name.startswith('polish-') else notes_in).update(data)

    intensive = set(layout.get('intensive', []))
    titles = layout.get('titles', {})
    boards, notes, order, missing = {}, {}, [], []

    for page in layout['pages']:
        pid = page['id']
        row_y = 0
        for ri, row in enumerate(page['rows']):
            notes[f'{pid}-row{ri + 1}'] = {'kind': 'title1', 'maxW': 4480, 'text': row['title'], 'w': 240,
                                           'x': 0, 'y': row_y - TITLE_OFFSET, 'page': pid}
            lines = [row['boards'][k:k + len(COL_X)] for k in range(0, len(row['boards']), len(COL_X))] or [[]]
            for line in lines:
                row_h = 0
                row_note_h = NOTE_FLOOR
                for ci, name in enumerate(line):
                    fname = f'{name}.dc.html'
                    if not (project / fname).exists():
                        missing.append(fname)
                        continue
                    h = board_height(project, name)
                    row_h = max(row_h, h)
                    info = notes_in.get(fname, {})
                    title = titles.get(name) or info.get('title') or name
                    if name in intensive and 'uso intensivo' not in title:
                        title += ' · uso intensivo'
                    b = {'x': COL_X[ci], 'y': row_y, 'w': 1440, 'h': h, 'title': title,
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
                    note_y = row_y + h + NOTE_GAP
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
                row_y += row_h + NOTE_GAP + row_note_h + ROW_GAP

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
    if missing:
        sys.exit(1)


if __name__ == '__main__':
    main()
