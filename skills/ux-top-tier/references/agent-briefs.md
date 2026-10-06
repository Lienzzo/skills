# Encargos para subagentes

Si el entorno tiene subagentes, reparte el trabajo para ir más rápido (tabla «Multiagente» en `SKILL.md`):

- **Descubrimiento (fase 1):** dos lectores en paralelo mientras tú recorres la app.
- **Construcción (fases 3 y 4):** oleadas de 6–8 agentes, con 2–3 pantallas cada uno, o una pantalla de uso intensivo. En Claude Code, `fork`, que hereda el contexto.
- **Validación (fase 5):** validadores nuevos en cada ronda del bucle. En Claude Code, un agente nuevo y no `fork`, para que no herede tu sesgo de autor.

Tú integras, decides, publicas y manejas el navegador; ningún subagente lo toca. Cada encargo es autosuficiente. Los de construcción llevan tres bloques fijos: **propiedad de archivos**, **hoja de verdad** y **reglas aprendidas**.

## Encargo · Descubrimiento en paralelo (fase 1)

```
LECTURA DEL CÓDIGO · <producto>. Repo: <ruta>. UI en: <rutas>. No edites nada.
Devuelve, en menos de 400 palabras:
- mapa de navegación: entradas de menú, niveles y rutas de cada pantalla;
- componentes de tabla, formulario, modal y estado vacío, y dónde se repiten o se contradicen;
- textos de error, enums o IDs que llegan a la interfaz, con archivo y línea;
- contratos de UX y sistema de diseño (tokens, presupuesto de motion, reglas en AGENTS.md o CLAUDE.md);
- sospechas de fricción que el código deja ver (pasos de más, modales para lo frecuente, formularios sin valores por defecto).
```

```
LECTURA DEL CONTEXTO HUMANO · <producto>. Fuentes: <transcripciones, tickets, feedback, notas>. No edites nada.
Devuelve, en menos de 400 palabras:
- los dolores reportados, con quién lo dice y una cita corta (personas anonimizadas: «una persona de soporte»);
- las tareas diarias de cada rol y cuántas veces al día se repiten, si se dice;
- el vocabulario del negocio y los términos que se confunden;
- lo que ya se ha prometido o descartado.
```

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

## Bucle de validación (fase 5)

Validadores que no han construido las pantallas las revisan, tú arreglas y se repite hasta el nivel top tier, **sin excederse**.

### Encargo · Validador de calidad

```
VALIDACIÓN DE CALIDAD · ronda <n> de 3 · <Tableros>.
Eres un revisor externo: no has construido estas pantallas y tu trabajo es encontrar lo que impide el nivel top tier, no aprobarlas.
Raíz: <ruta local del prototipo>. Lee <carpeta de la skill>/references/qa-checklist.md (§ 1, 3, 4 y 5) y references/design-language.md.
Ejecuta lint_boards.py, scan_ui.py y check_logic.js sobre tus tableros y revisa a mano:
- datos frente a la hoja de verdad: personas, cifras, contadores, totales, horas y etapas;
- estados: vacío, carga, error, éxito, hover y foco;
- accesibilidad básica, textos, plurales y enlaces entre pantallas;
- capturas actuales (<rutas .png>): textos partidos, solapes, popovers o avisos que tapan algo.
No edites nada. Responde SOLO con la lista de hallazgos, de más a menos grave:
  [P0|P1|P2] <Tablero> · <qué falla, con el texto o la línea exacta> → <arreglo concreto>
P0 = rompe algo o impide el top tier; P1 = se nota y molesta; P2 = pulido. Si no hay nada: «Sin hallazgos».
Ya descartado (no lo repitas): <lista con motivo, o «nada»>.
<Bloque fijo 2 · Hoja de verdad>
```

### Encargo · Validador de UX/UI senior

```
VALIDACIÓN UX/UI SENIOR · ronda <n> de 3 · <Tableros>.
Eres el diseñador de producto más exigente de Linear revisando el trabajo de otro. No lo has hecho tú: busca por qué todavía no es top tier.
Producto y usuarios: <qué hace, roles y cuántas horas pasan en cada pantalla>.
Para cada tablero tienes su código (<ruta>), su captura actual (<ruta .png>), la captura del «antes» (<ruta .png>) y los hallazgos del informe que debía resolver (<C3, T4…>). Mira las imágenes.
Aplica <carpeta de la skill>/references/qa-checklist.md § 2, references/design-language.md y, en las de uso intensivo, references/intensive-use.md:
- ¿Rediseñada o repintada respecto al «antes»? ¿Copia la navegación, el orden o los modales de la UI actual?
- Clics, teclas, pantallas y esperas de la tarea principal, antes y ahora.
- Qué molestaría a quien la usa ocho horas al día a la décima repetición, con su coste (segundos × veces al día).
- ¿Algo parece plantilla, genérico o «vibecoded»? ¿Pasaría la revisión de diseño de Linear?
- Jerarquía, densidad, alineación, copy y estados.
No edites nada. Responde con la lista de hallazgos en el mismo formato que el validador de calidad. Nada de gustos sin una tarea detrás: cada hallazgo dice a quién le cuesta qué.
Ya descartado (no lo repitas): <lista con motivo, o «nada»>.
```

### Cómo gira cada ronda

1. **Prepara.** Publica los tableros y captura cada pantalla que se va a validar (modo de juego, `save_to_disk`). Sin navegador, los validadores trabajan solo sobre el código y lo dicen.
2. **Lanza en paralelo.** Un validador de calidad y uno de UX/UI por cada grupo de hasta unas 8 pantallas.
3. **Tría.** Acepta lo que mejora la tarea o acerca al listón. Descarta, con motivo, lo que contradice el brief, el sistema de diseño del repo o la hoja de verdad. Junta los duplicados.
4. **Arregla** los P0 y P1, tú o el agente que construyó la pantalla (con `SendMessage` si sigue disponible, o con un encargo nuevo con la lista exacta). Respeta la propiedad de archivos.
5. **Siguiente ronda,** con validadores nuevos y solo las pantallas que han cambiado. Añade una pasada de coherencia si los arreglos tocan datos compartidos.

### Cuándo parar (sin excederse)

- Como mucho **3 rondas**.
- Para antes si una ronda no deja P0 ni P1.
- Para también si los hallazgos nuevos son de gusto, repiten lo descartado o le dan la vuelta a lo ya arreglado: eso es ruido, no calidad.
- Los P2 se arreglan en lote tras la última ronda, sin volver a validar.
- Lo que siga abierto tras la tercera ronda va a la entrega, con el motivo.

## Durante la ejecución

- **Coherencia en caliente.** Si un agente termina y fija datos que otro agente en marcha mostrará, mándaselos (en Claude Code, con `SendMessage`), por ejemplo: «Nueva alta propone a tres leads concretos en la etapa Interesado; muéstralos con los mismos datos». Escríbelo como un ajuste concreto y verificable.
- **Revisa cada entrega:** linter, `scan_ui.py`, `check_logic.js`, publicación de ese tablero y revisión a tamaño real en el navegador.
- **Al terminar, comprueba tus propias ediciones.** Si un agente retoma el trabajo tras tu mensaje, puede reescribir el archivo después de que tú lo hayas tocado.
- **No delegues el final.** La pasada de coherencia entre pantallas y la auditoría final del artefacto en el navegador las haces tú, con todo el contexto.
