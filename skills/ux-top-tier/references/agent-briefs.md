# Encargos para subagentes

Para 20 o más pantallas, reparte el trabajo en oleadas de 6–8 subagentes (en Claude Code, `fork`, que hereda el contexto). Tú integras, validas, publicas y revisas en el navegador. Cada encargo es autosuficiente y lleva tres bloques fijos: **propiedad de archivos**, **hoja de verdad** y **reglas aprendidas**.

## Bloque fijo 1 · Propiedad y verificación

```
Raíz: <ruta local del prototipo>. Lee primero <tableros de referencia ya hechos, p. ej. Main.dc.html y Sidebar.dc.html> y copia EXACTAMENTE su sistema visual (helmet, tokens, barra lateral, cabecera de 44 px, Geist 13 px).
Solo puedes escribir: <lista de archivos> y notes/<agente>.json. Nada de publicar, navegador ni Docs.
Antes de terminar:
  python3 <carpeta de la skill>/scripts/lint_boards.py --project <raíz>/project <Tableros>
  python3 <carpeta de la skill>/scripts/scan_ui.py --project <raíz>/project <Tableros>
  node <carpeta de la skill>/scripts/check_logic.js <raíz>/project <Tableros>
Responde con un resumen breve y la altura final de cada tablero.
```

Si el prototipo es la página HTML, cambia las dos primeras líneas por:

```
Raíz: <ruta local del prototipo>. Lee primero index.html (motor, tokens y pantallas de ejemplo) y copia EXACTAMENTE su sistema visual.
Solo puedes escribir: screens/<id>.js (una llamada a screen({...}) por pantalla, con sus notas «Antes / Ahora» en notes). Nada de publicar, navegador ni Docs.
```

y verifica con `lint_boards.py` y `scan_ui.py` sobre la raíz (`check_logic.js` no aplica).

## Bloque fijo 2 · Hoja de verdad (ejemplo)

```
Coherencia de datos (obligatoria):
- «Ahora» es martes 6 oct, 10:45. Calcula todas las esperas y antigüedades desde ahí.
- Tú eres Ana G. (AG, Operaciones). Compañeros: Pablo S. (PS, Ventas), Marta L. (ML, Soporte).
- Totales: Clientes 1.240 = Básico 780 + Pro 360 + Empresa 100. Leads 215. Conversaciones esperando 9 (6 tuyas).
- Personas recurrentes: Lucas Romero (alta ayer, plan Pro, 49 €/mes + 120 € de puesta en marcha = 169 €), …
- Etapas del pipeline: Nuevo, Contactado, Interesado, Enlace de pago enviado. No inventes otras.
```

Amplíala cada vez que un agente fije un dato que otros vayan a mostrar.

## Bloque fijo 3 · Reglas aprendidas

```
- La UI actual (repo y app) es evidencia de tareas y datos, NO la referencia. No calques su navegación, jerarquía, componentes, modales ni orden de campos: rediseña desde la tarea, con Linear y v0 como dirección. La captura del «antes» es para saber de dónde partes, no una plantilla.
- Diseña para alguien que pasa 6–8 h al día en esta pantalla: cada clic, espera, modal o dato que recordar se multiplica por cientos de veces al día. Quita toda fricción que no sea imprescindible.
- Listón: que pase la revisión de diseño de Linear. Antes de terminar, revisa cada tablero como el diseñador de producto más exigente, apunta lo que aún molestaría y arréglalo. «Decente» no vale.
- Lenguaje Linear/v0. PROHIBIDO: tarjetas con icono decorativo, banners de color, emoji, degradados, antetítulos en mayúsculas, titulares grandes, sombras gruesas.
- Ningún ID técnico visible (nada tipo «CLS-218», «PER-0931»); usa una ruta legible.
- En un contenedor display:flex, no mezcles texto literal y {{hueco}} como hijos directos (se pierde el espacio): envuelve el texto completo en <span> o calcúlalo entero.
- <textarea> con value="{{x}}" onChange="{{fn}}", nunca con contenido.
- Botones en una línea (white-space: nowrap) que quepan; si no, acorta el texto.
- Menús y popovers cerrados por defecto.
- Nada de <a> o <button> anidados.
- Plurales correctos («1 entrega»).
- Avisos con «Deshacer» que no tapen el compositor ni los botones.
- Motion ≤ 200 ms, ease-out. Copy en <idioma>, sin jerga.
- onKeyDown puede no estar soportado: todo atajo también como botón.
```

## Encargo · Oleada de pantallas (fase 3)

```
PANTALLAS · <Sección>: <Tablero1>, <Tablero2>, <Tablero3>.
Contexto del producto: <qué hace la sección, quién la usa>.
Hallazgos del informe que deben resolverse aquí: <C3, T4, J1… con una línea cada uno>.
Capturas del «antes» (míralas para saber de dónde partes, no para copiarlas): <Tablero1: antes/Tablero1.png, …>.
Para cada tablero:
- Diseño completo a 1440×900 con datos ficticios coherentes (hoja de verdad) y estados funcionales (pestañas, filtros, vista lateral, selección).
- Enlaces reales a los tableros relacionados: <lista>.
- Sidebar con active="<clave>" sub="<subclave>".
En el lienzo, escribe notes/<agente>.json = {"<Tablero>.dc.html": {"title": "<n · Sección › Pantalla>", "antes": "ANTES · …\n\n• …", "ahora": "AHORA · …\n\n• …"}}
  - «Antes»: lo observado en el producto real, con evidencia concreta y cifras.
  - «Ahora»: qué resuelve el rediseño y cómo, en 4–6 viñetas.
<Bloques fijos 1, 2 y 3>
```

## Encargo · Pulido de uso intensivo (fase 4)

```
PULIDO PROFUNDO · <Tablero> (<quién lo usa y cuánto: «el equipo de atención responde mensajes durante horas cada día»>).
Objetivo: fricción mínima en una pantalla de uso intensivo. Ponte en la piel de quien la usa toda la jornada y cuenta lo que cuesta cada repetición. Reescribe <Tablero> manteniendo EXACTAMENTE el sistema visual, los datos coherentes y los enlaces existentes. Léelo primero.
Qué debe tener (todo funcional con estado):
- <Lista concreta según el patrón de references/intensive-use.md: trabajo en serie, deshacer, atajos, acciones en línea, valores por defecto, contadores vivos, estado vacío con resumen…>
Añade 3–5 viñetas sobre la fricción eliminada. En el lienzo, en notes/polish-<nombre>.json = {"<Tablero>.dc.html": {"ahora_extra": "• …\n• …"}}; en la página HTML, al final de notes.ahora, bajo «FRICCIÓN MÍNIMA · uso intensivo».
<Bloques fijos 1, 2 y 3>
```

## Durante la ejecución

- **Coherencia en caliente.** Si un agente termina y fija datos que otro agente en marcha mostrará, mándaselos (en Claude Code, con `SendMessage`), por ejemplo: «Nueva alta propone a tres leads concretos en la etapa Interesado; muéstralos con los mismos datos». Escríbelo como un ajuste concreto y verificable.
- **Revisa cada entrega:** linter, `scan_ui.py`, `check_logic.js`, publicación de ese tablero y revisión a tamaño real en el navegador.
- **Al terminar, comprueba tus propias ediciones.** Si un agente retoma el trabajo tras tu mensaje, puede reescribir el archivo después de que tú lo hayas tocado.
- **No delegues la revisión final.** La pasada de coherencia entre pantallas la haces tú, con todo el contexto.
