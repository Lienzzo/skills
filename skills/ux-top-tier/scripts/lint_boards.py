#!/usr/bin/env python3
"""Static checks for prototype screens: the anti-"vibecoding" visual rules plus format rules.

Works with both prototype formats:
  - single HTML page (assets/prototype-template.html): visual rules, focus style, dark theme, reduced motion;
  - design-canvas boards (*.dc.html): the same visual rules plus the canvas format rules.

Usage:
  python3 lint_boards.py --project <dir> [Board | file.html ...] [--ban "texto:motivo" ...]

Without names it checks every *.html in the folder. A bare name (Main) means Main.dc.html.
Prints "<file>: ok" or the problems found. Exit code 1 if any file has problems.
"""
import argparse
import pathlib
import re
import sys

EMOJI = re.compile('[\U0001F300-\U0001FAFF☀-⛿✀-➿]')
ALLOWED_SYMBOLS = {'✓', '⌘', '⏎', '✦'}
HOLE = re.compile(r'\{\{([^}]*)\}\}')
VALID_HOLE = re.compile(r'^\s*[A-Za-z_$][\w$]*(\.[\w$]+)*\s*$|^\s*(true|false|null|-?\d+(\.\d+)?)\s*$')
FONT_SIZE = re.compile(r'font-size:\s*(\d+(?:\.\d+)?)px')
BANNED = {
    'linear-gradient': 'degradado',
    'radial-gradient': 'degradado',
    'conic-gradient': 'degradado',
    'text-transform: uppercase': 'antetítulo en mayúsculas',
    'text-transform:uppercase': 'antetítulo en mayúsculas',
}
BANNED_CANVAS = {
    'innerHTML': 'innerHTML',
    'appendChild': 'appendChild',
}


def resolve(project: pathlib.Path, names: list) -> list:
    if not names:
        return sorted(project.glob('*.html'))
    return [project / (n if n.endswith('.html') else f'{n}.dc.html') for n in names]


def check(path: pathlib.Path, banned: dict, shared: set) -> list:
    text = path.read_text(encoding='utf-8')
    canvas = path.name.endswith('.dc.html')
    problems = []

    rules = {**banned, **BANNED_CANVAS} if canvas else banned
    for needle, label in rules.items():
        if needle in text:
            problems.append(f'{label}: {needle}')
    emojis = set(EMOJI.findall(text)) - ALLOWED_SYMBOLS
    if emojis:
        problems.append(f'emoji: {"".join(sorted(emojis))}')
    big = sorted({float(s) for s in FONT_SIZE.findall(text) if float(s) >= 28})
    if big:
        problems.append('titular de 28 px o más: ' + ', '.join(f'{s:g}px' for s in big))
    if ('@keyframes' in text or 'animation:' in text) and 'prefers-reduced-motion' not in text:
        problems.append('animación sin @media (prefers-reduced-motion)')

    if not canvas:
        if ':focus-visible' not in text:
            problems.append('sin estilo :focus-visible')
        if 'data-theme="dark"' not in text and 'prefers-color-scheme: dark' not in text:
            problems.append('sin tema oscuro ([data-theme="dark"] o prefers-color-scheme)')
        return problems

    if '<script src="./support.js"></script>' not in text:
        problems.append('falta support.js')
    if 'class Component extends DCLogic' not in text:
        problems.append('falta class Component extends DCLogic')
    if 'data-dc-script' not in text:
        problems.append('falta data-dc-script')
    if path.name[:-len('.dc.html')] not in shared and '.hov:hover' not in text:
        problems.append('helmet sin reglas hover/focus')
    for hole in HOLE.findall(text):
        if not VALID_HOLE.match(hole):
            problems.append(f'hueco no válido (solo rutas): {{{{{hole}}}}}')
    for tag in ['sc-for', 'sc-if', 'dc-import']:
        opened = len(re.findall(rf'<{tag}\b', text))
        closed = text.count(f'</{tag}>')
        if opened != closed:
            problems.append(f'{tag} abiertos {opened} / cerrados {closed}')
    for tag in ['sc-for', 'sc-if']:
        for match in re.finditer(rf'<{tag}\b[^>]*>', text):
            if 'hint-placeholder' not in match.group(0):
                problems.append(f'{tag} sin hint-*: {match.group(0)[:80]}')
    if not re.search(r"data-props='([^']*)'", text):
        problems.append('sin data-props')
    if re.search(r'<textarea[^>]*>\s*\{\{', text):
        problems.append('hueco dentro de <textarea> (usa value="{{x}}" onChange)')
    preview = re.search(r'"\$preview"\s*:\s*\{\s*"width"\s*:\s*(\d+)\s*,\s*"height"\s*:\s*(\d+)', text)
    minh = re.search(r'<div class="\{\{themeClass\}\}"[^>]*?min-height:\s*(\d+)px', text)
    if preview and minh and int(preview.group(2)) != int(minh.group(1)):
        problems.append(f'$preview.height {preview.group(2)} ≠ min-height {minh.group(1)}')
    return problems


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', required=True, help='carpeta con los .html o .dc.html')
    parser.add_argument('--ban', action='append', default=[], help='"texto:motivo" adicional prohibido (p. ej. jerga del proyecto)')
    parser.add_argument('--shared', action='append', default=['Sidebar'], help='componentes compartidos del lienzo sin helmet propio')
    parser.add_argument('boards', nargs='*')
    args = parser.parse_args()
    project = pathlib.Path(args.project)
    if not project.is_dir():
        sys.exit(f'No existe la carpeta {project}')
    banned = dict(BANNED)
    for item in args.ban:
        needle, _, label = item.partition(':')
        banned[needle] = label or 'prohibido'
    paths = resolve(project, args.boards)
    if not paths:
        sys.exit(f'No hay archivos .html en {project}')
    failed = False
    for path in paths:
        if not path.exists():
            print(f'{path.name}: NO EXISTE')
            failed = True
            continue
        problems = check(path, banned, set(args.shared))
        failed = failed or bool(problems)
        print(f'{path.name}: ' + ('ok' if not problems else '; '.join(problems)))
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
