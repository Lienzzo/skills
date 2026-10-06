# Prototipo: lienzo de diseño o página HTML

Dos formatos con la misma disciplina:

- **Lienzo de diseño** (secciones 1–6): `.dc.html` + `canvas.json`, el tipo de artefacto «Design» de claude.ai. **Es el formato por defecto siempre que el agente tenga artefactos de claude.ai** (en Claude Code, la herramienta `Artifact`): el prototipo se ve como un canvas, con todas las pantallas a la vista, cada una con su «antes» encima y sus notas debajo. **Las instrucciones del tipo mandan.** Léelas tras el `quickstart` (intent `design`). Estas secciones resumen lo que funcionó en un proyecto real con 52 tableros y las trampas que conviene evitar. Es un formato del propio producto y puede cambiar.
- **Página HTML** (sección 7): para agentes sin artefactos de claude.ai. Funciona en cualquier sitio, como archivo local o despliegue estático.

Los dos llevan la captura del «antes» de cada pantalla (sección 8).

## Índice
1. Crear el artefacto y la carpeta local
2. Anatomía de un tablero
3. Huecos, control de flujo y eventos
4. Componentes compartidos (barra lateral)
5. `canvas.json`: tableros, notas, páginas, lanzamiento
6. Publicar y revisar
7. Página HTML (sin artefactos de claude.ai)
8. Capturas del «antes» (los dos formatos)

## 1. Crear el artefacto y la carpeta local

1. Llama a `Artifact` con `action: "quickstart"` e `intent: "design"`. Crea el artefacto con el `type_url` que te devuelva, un `title` con el nombre del producto (por ejemplo, «Producto — UX objetivo») y `auto_open: "after_first_write"`, sin archivos. Así se crea en modo «Design» y se ve como un canvas. No lo publiques como página HTML suelta.
2. Lee el `project/canvas.json` inicial con `Artifact action: "read"` y `path`. Guárdalo: `scripts/build_canvas.py` lo usa como base para conservar los campos del tipo.
3. Trabaja en una carpeta local temporal (en Claude Code, el scratchpad). Usa `project/` para los `.dc.html` y el `canvas.json`, y `notes/` para el JSON de notas de cada agente.
4. Para publicar, pasa `url` del artefacto, `root`=<carpeta>, `file_path`=<el archivo principal> y `files`={"project/X.dc.html": "project/X.dc.html", …}. Publica solo lo que cambia.

## 2. Anatomía de un tablero

Plantilla completa en `assets/board-template.dc.html`. Resumen:

```html
<!doctype html>
<html lang="es">
<head><meta charset="utf-8"><title>Pantalla · Producto</title><script src="./support.js"></script></head>
<body>
<x-dc>
<helmet>
  <link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&amp;family=Geist+Mono:wght@400;500&amp;display=swap" rel="stylesheet">
  <style>body{margin:0} .pp{…tokens…} .pp.dark{…} .pp .hov:hover{background:var(--hover) !important} …</style>
</helmet>
<div class="{{themeClass}}" style="display:flex; min-height:900px; …">
  <div style="flex:0 0 232px; display:flex">
    <dc-import name="Sidebar" active="clientes" sub="" hint-size="232px,900px"></dc-import>
  </div>
  <div style="flex:999 1 560px; min-width:0; margin:8px 8px 8px 0; …panel…"> … </div>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{"dark":{"editor":"boolean","default":false},"$preview":{"width":1440,"height":900}}'>
class Component extends DCLogic {
  constructor(props) { super(props); this.state = { selected: 'a' }; }
  renderVals() {
    return { themeClass: this.props.dark ? 'pp dark' : 'pp', /* … */ };
  }
}
</script>
</body>
</html>
```

- Usa 1440×900 por tablero. Si necesitas más alto, ajusta `$preview.height` y `min-height`, y el constructor del lienzo lo leerá.
- La prop `dark` permite revisar el modo oscuro desde el editor.

## 3. Huecos, control de flujo y eventos

- **Huecos `{{a.b}}`: solo búsquedas** de una ruta. Sin expresiones, ternarios ni llamadas. Todo se calcula en `renderVals()`, incluidos los estilos dinámicos: `style="{{row.style}}"`.
- **Listas:** `<sc-for list="{{rows}}" as="r" hint-placeholder-count="5"> … {{r.name}} … </sc-for>`.
- **Condiciones:** `<sc-if value="{{hasPeek}}" hint-placeholder-val="{{true}}"> … </sc-if>`. Todo `sc-for` y `sc-if` lleva su atributo `hint-*`.
- **Eventos:**
  - `onClick="{{fn}}"`, donde `fn` es una función devuelta por `renderVals`, normalmente un cierre que llama a `this.setState`;
  - en los inputs, `value="{{v}}" onChange="{{fn}}"`, y `fn` recibe el evento (`e.target.value`);
  - `onKeyDown` puede no estar soportado, así que ofrece siempre el equivalente como botón.
- **Navegación:** `<a href="OtroTablero.dc.html">` navega entre tableros en el modo de juego.
- **Prohibido:**
  - `innerHTML` y `appendChild`;
  - huecos dentro de `<textarea>…</textarea>`;
  - texto literal junto a un hueco como hijos directos de un contenedor flex;
  - `<a>` o `<button>` anidados.
- **Variables de bucle:** el nombre de `as` sirve dentro del bucle. Desde un `sc-for` anidado se puede leer la variable del exterior.

## 4. Componentes compartidos (barra lateral)

- `Sidebar.dc.html` con `data-props` del tipo `{"active":{"editor":"enum","options":[…]}, "sub":{"editor":"text"}}` y `$preview` 232×900. Plantilla en `assets/sidebar-template.dc.html`.
- Cada pantalla la importa con `<dc-import name="Sidebar" active="…" sub="…" hint-size="232px,900px">`.
- Los contadores de la barra lateral son fijos en el componente, así que deben cuadrar con lo que muestran las pantallas (bandeja, pestañas). Revísalos al final.

## 5. `canvas.json`

Campos observados (consérvalos desde el `canvas.json` publicado):

```json
{
  "v": 3, "title": "Producto — UX objetivo", "attachments": {}, "designSystems": [],
  "pages": [{"id": "uso-diario", "name": "1 · Uso diario: pantallas clave"}],
  "launch": {"view": "canvas", "page": "uso-diario"},
  "order": ["Main.dc.html", "…", "Sidebar.dc.html"],
  "boards": {
    "Main.dc.html": {"x": 0, "y": 0, "w": 1440, "h": 900, "title": "1 · Hoy · uso intensivo",
                      "expand": "fill", "is_interactive": true, "page": "uso-diario"}
  },
  "notes": {
    "uso-diario-row1": {"kind": "title1", "maxW": 4480, "text": "Empezar el día…", "w": 240, "x": 0, "y": -300, "page": "uso-diario"},
    "Main-antes": {"x": 0, "y": 940, "w": 700, "maxH": 560, "size": 24, "fill": "orange", "text": "ANTES · Hoy\n\n• …", "page": "uso-diario"},
    "Main-ahora": {"x": 740, "y": 940, "w": 700, "maxH": 560, "size": 24, "fill": "blue", "text": "AHORA · Hoy\n\n• …", "page": "uso-diario"}
  }
}
```

- **Distribución:** 3 tableros por fila con x = 0, 1520 y 3040. El título de fila va 300 px por encima y las notas «Antes / Ahora» debajo de cada tablero. La siguiente fila deja sitio a la nota más alta.
- **Capturas del «antes»:** si la fila tiene capturas, gana una franja de tableros `Antes-<Tablero>.dc.html` encima, cada uno sobre su pantalla y 120 px por encima de ella (sección 8). De arriba abajo se lee: el «antes», el rediseño y sus notas.
- **Lanzamiento:**
  - `{"view":"canvas","page":"…"}` abre el lienzo;
  - `{"view":"focused","file":"Main.dc.html"}` abre directamente el modo de juego, útil para revisar con clics.
- **Notas:** el editor normaliza `size` a 24 y puede añadir `attachments`. Si la publicación se rechaza, lee la versión publicada, fusiona y vuelve a publicar.
- **Generación:** usa `scripts/build_canvas.py --layout layout.json --notes notes/ --project project/ --src canvas_publicado.json`. Ver `assets/layout-example.json`.

## 6. Publicar y revisar

- Publica por tandas: los tableros terminados más el `canvas.json` al final.
- Revisa en el navegador:
  - abre el artefacto en una pestaña nueva;
  - con `launch` enfocado entras en modo de juego;
  - navega con los enlaces del propio prototipo (barra lateral, pestañas).
- Antes de cada tanda de clics, haz una captura nueva: si cambia el tamaño de la ventana, cambian las coordenadas.
- La herramienta `find` no ve dentro del iframe; usa capturas y `zoom` para revisar detalles.
- La consola del artefacto no suele ser accesible. Para depurar la lógica, usa `scripts/check_logic.js` en node.
- **Al terminar:** deja `launch` en la primera página del lienzo, publica el `canvas.json` final y cierra la pestaña que abriste.

## 7. Página HTML (sin artefactos de claude.ai)

Parte de `assets/prototype-template.html`. Es una sola página sin dependencias (solo la fuente Geist de Google Fonts) que ya trae:

- barra lateral con grupos y contadores, ⌘K para ir a cualquier pantalla y conmutador de tema claro u oscuro;
- rutas por `#pantalla`, de modo que cada pantalla tiene su enlace;
- estado por pantalla, avisos con «Deshacer» (también ⌘Z) y atajos de teclado reales (J/K, E, Esc, /, ⌘⏎);
- el panel «Notas Antes / Ahora», que se abre como tercera columna sin tapar la pantalla;
- «Ver antes» (⇧A), que cambia la pantalla por la captura del producto real y vuelve con Esc;
- dos pantallas de ejemplo: una bandeja de uso intensivo con vista lateral y trabajo en serie, y un directorio con tabla.

**Cómo se añade una pantalla.** Una llamada a `screen({...})` con `id`, `title`, `group`, `before`, `initial`, `render(s)`, `actions`, `keys` y `notes`. El comentario del motor explica cada campo.

- `render` devuelve `` h`…` ``: las interpolaciones se escapan solas y las listas se pintan con `.map(...)`. Para atributos booleanos, escribe `'true'` o `'false'` explícitamente.
- Los botones lanzan acciones con `data-act="nombre"` y `data-arg="…"`. Los campos guardan su valor con `data-model="clave"`, y el buscador con `data-search` se enfoca con «/».
- Para lo reversible usa `ctx.flash(patch, texto)`: aplica el cambio, avisa y permite deshacer. `ctx.say(texto)` avisa sin deshacer.
- Los datos, ficticios y coherentes con la hoja de verdad. Si varias pantallas muestran a la misma persona, que coincida en todas.

**Con subagentes.** Cada uno escribe solo `screens/<id>.js` (una o varias llamadas a `screen`), y tú añades `<script src="screens/<id>.js"></script>` después del motor. Así se respeta la propiedad de archivos.

**Revisión.**
- `lint_boards.py` y `scan_ui.py` funcionan sobre la página. `scan_ui.py` lee también `screens/*.js` para comprobar los enlaces `#pantalla` y que cada pantalla tenga su captura del «antes» y que el archivo exista.
- La lógica se prueba en el navegador: abre cada pantalla, pulsa cada acción y deshaz, prueba los atajos y mira el modo oscuro y el ancho de móvil.

**Publicación.** En un despliegue estático o como archivo para abrir en local, siempre con la carpeta `antes/` al lado de la página. Si el entorno tiene artefactos de claude.ai, el prototipo va en el lienzo «Design» (secciones 1–6), no en esta página.

## 8. Capturas del «antes» (los dos formatos)

Cada pantalla rediseñada enseña la pantalla real que sustituye. Quien revisa el prototipo compara sin salir de él, y tú compruebas que has rediseñado y no repintado.

**Cuándo.** En la fase 1, mientras recorres la app: una captura por pantalla que vas a rediseñar, y por cada modal o formulario clave. Si un rediseño junta varias pantallas antiguas, captúralas todas. Si una pantalla es nueva y no sustituye a ninguna, no lleva captura: su nota «Antes» dice dónde se hace hoy ese trabajo.

**Cómo se captura** (con Claude in Chrome; en otro agente, con su equivalente):
1. Fija el tamaño de la ventana una sola vez (`resize_window`, por ejemplo 1440×900) y no lo cambies hasta terminar.
2. Deja la pantalla en un estado representativo: con datos, sin cargas a medias ni menús abiertos y con el scroll arriba.
3. Enmascara los datos personales. Pega `assets/mask-pii.js` con `javascript_tool` y llama a `uxMask({ blur: [...], text: [...] })`:
   - tapa siempre correos, teléfonos, IBAN, tarjetas y DNI/NIE;
   - en `blur` van los selectores de lo que identifica a alguien (columna de nombres, avatares, direcciones);
   - en `text` van los nombres sueltos, que pasan a «Persona 1», «Persona 2»…

   Solo cambia lo que se ve en esa pestaña: no guarda nada en el servidor y al recargar vuelve todo. Respeta el modo de solo lectura.
4. Captura con `computer`, acción `screenshot` y `save_to_disk: true`. Mira la imagen: si queda un nombre, un correo, un teléfono, una dirección o la foto de alguien real, añádelo a `uxMask` y vuelve a capturar.
5. Copia el archivo a `<prototipo>/antes/<pantalla>.png`, con el mismo nombre que el tablero o el `id` de la pantalla. Si pesa más de unos 500 KB, conviértelo a JPEG al 80 % (en macOS: `sips -s format jpeg -s formatOptions 80 <captura>.png --out antes/<pantalla>.jpg`).

Sin navegador, pide las capturas al usuario y recuérdale que tape los datos personales.

**En el lienzo.** Un tablero no carga imágenes por nombre de archivo ni como `data:`:
1. Sube las capturas como assets del lienzo: `Artifact` con la `url` del lienzo, `asset: true` y `file_paths` (hasta 25 por llamada). Cada una devuelve una `url` `/_blob/<id>`.
2. Apúntalas en `before` de `layout.json` (ejemplo en `assets/layout-example.json`): `"Main": [{"file": "antes/Main.png", "src": "/_blob/<id>"}]`. `file` es la copia local, para leer sus medidas. `label` nombra cada captura cuando hay varias. Las pantallas nuevas van en `"new"`.
3. `build_canvas.py` escribe `project/Antes-<Tablero>.dc.html` con las capturas a 1440 px de ancho y lo coloca encima de su tablero, con el título «Antes · <título>». Avisa de las pantallas sin captura que no están en `"new"` y de los tableros «Antes» que sobran.
4. Publica los tableros «Antes» con el `canvas.json`. `lint_boards.py` y `scan_ui.py` no los revisan porque los genera el script.

**En la página HTML.** `before: 'antes/<id>.png'` en su `screen({...})`, o una lista `[{ src: 'antes/a.png', label: 'Listado' }, …]` si son varias, o `before: null` si la pantalla es nueva.
- «Ver antes» en la barra lateral (o ⇧A) cambia la pantalla por su captura a ancho completo, y Esc vuelve al rediseño. Se mantiene al cambiar de pantalla, así que se pueden recorrer todos los «antes» seguidos.
- En el panel de notas, la nota «Antes» muestra la miniatura.
- Al desplegar, sube la carpeta `antes/` junto a la página.
