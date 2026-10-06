# Prototipo: página HTML o lienzo de diseño

Dos formatos con la misma disciplina:

- **Página HTML** (sección 7): funciona en cualquier agente y se publica en cualquier sitio. Es la opción por defecto.
- **Lienzo de diseño** (secciones 1–6): `.dc.html` + `canvas.json`, el tipo de artefacto «Design» de claude.ai, disponible en Claude Code con artefactos. **Las instrucciones del tipo mandan.** Léelas tras el `quickstart` (intent `design`). Estas secciones resumen lo que funcionó en un proyecto real con 52 tableros y las trampas que conviene evitar. Es un formato del propio producto y puede cambiar.

## Índice
1. Crear el artefacto y la carpeta local
2. Anatomía de un tablero
3. Huecos, control de flujo y eventos
4. Componentes compartidos (barra lateral)
5. `canvas.json`: tableros, notas, páginas, lanzamiento
6. Publicar y revisar
7. Página HTML (cualquier agente)

## 1. Crear el artefacto y la carpeta local

1. Llama a `Artifact` con `action: "quickstart"` e `intent: "design"`, y crea el artefacto desde el `type_url` que te devuelva, con un `title`.
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

## 7. Página HTML (cualquier agente)

Parte de `assets/prototype-template.html`. Es una sola página sin dependencias (solo la fuente Geist de Google Fonts) que ya trae:

- barra lateral con grupos y contadores, ⌘K para ir a cualquier pantalla y conmutador de tema claro u oscuro;
- rutas por `#pantalla`, de modo que cada pantalla tiene su enlace;
- estado por pantalla, avisos con «Deshacer» (también ⌘Z) y atajos de teclado reales (J/K, E, Esc, /, ⌘⏎);
- el panel «Notas Antes / Ahora», que se abre como tercera columna sin tapar la pantalla;
- dos pantallas de ejemplo: una bandeja de uso intensivo con vista lateral y trabajo en serie, y un directorio con tabla.

**Cómo se añade una pantalla.** Una llamada a `screen({...})` con `id`, `title`, `group`, `initial`, `render(s)`, `actions`, `keys` y `notes`. El comentario del motor explica cada campo.

- `render` devuelve `` h`…` ``: las interpolaciones se escapan solas y las listas se pintan con `.map(...)`. Para atributos booleanos, escribe `'true'` o `'false'` explícitamente.
- Los botones lanzan acciones con `data-act="nombre"` y `data-arg="…"`. Los campos guardan su valor con `data-model="clave"`, y el buscador con `data-search` se enfoca con «/».
- Para lo reversible usa `ctx.flash(patch, texto)`: aplica el cambio, avisa y permite deshacer. `ctx.say(texto)` avisa sin deshacer.
- Los datos, ficticios y coherentes con la hoja de verdad. Si varias pantallas muestran a la misma persona, que coincida en todas.

**Con subagentes.** Cada uno escribe solo `screens/<id>.js` (una o varias llamadas a `screen`), y tú añades `<script src="screens/<id>.js"></script>` después del motor. Así se respeta la propiedad de archivos.

**Revisión.**
- `lint_boards.py` y `scan_ui.py` funcionan sobre la página (y leen `screens/*.js` para comprobar los enlaces `#pantalla`).
- La lógica se prueba en el navegador: abre cada pantalla, pulsa cada acción y deshaz, prueba los atajos y mira el modo oscuro y el ancho de móvil.

**Publicación.** Como artefacto (si el entorno lo ofrece, carga antes su guía de diseño: la plantilla ya sigue el contrato de tokens claro/oscuro), en un despliegue estático o como archivo para abrir en local.
