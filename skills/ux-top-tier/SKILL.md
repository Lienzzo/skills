---
name: ux-top-tier
description: "Senior UX/UI audit and «top tier» redesign of any software (admin, back-office, CRM, SaaS, dashboard, app or website), in the spirit of Linear and v0: frictionless, dense and calm, never the «vibecoding» look. It gathers context first (URL and environment, repo, roles, most-used screens, pains, brand), walks the real app and its code, and delivers a prioritised report, a clickable prototype with Before/After notes and a minimal-friction pass on high-use screens. Use it whenever someone asks to review, audit, improve or redesign a UX or UI, says flows are complex or confusing, asks for a mock or prototype, or mentions Linear, v0, top tier, frictionless or senior UX. Spanish triggers: «revisa la UX del admin», «audita la UI», «hazme un mock de cómo quedaría», «sin fricción», «que no parezca vibecoding». Instructions are written in Spanish; deliverables follow the user's language."
license: MIT
compatibility: "Needs a browser the agent can drive (e.g. Claude in Chrome) to walk the app, plus Python 3 and Node for the QA scripts. The prototype is a single HTML page that works anywhere; on Claude Code with claude.ai artifacts it can use the Design canvas (.dc.html) instead."
metadata:
  author: Lienzzo
  version: "1.0.0"
---

# UX top tier: auditoría senior, prototipo y fricción mínima

Convierte «los usuarios dicen que esto es complicado» en entregables que un equipo puede ejecutar, en cualquier software:

1. **Informe de auditoría** priorizado, con evidencia, causas de fondo, flujos de principio a fin, plan por fases y métricas.
2. **Prototipo visual navegable** de todas las pantallas rediseñadas, con una nota «Antes / Ahora» en cada una.
3. **Pulido de fricción mínima** en las pantallas donde el equipo o los clientes pasan más horas.

El listón es explícito: **no basta con «decente»**. Se busca la sensación de Linear y v0: densa, calmada, rápida, con teclado y sin adornos, con un pequeño toque de la identidad del producto. Piensa como un diseñador de UX senior: **tareas y causas raíz**, no gustos.

Responde y escribe los entregables en el idioma del usuario, aunque estas instrucciones estén en español.

## Modo rápido (petición acotada)

Si piden revisar una sola pantalla, un componente o un detalle («revisa este formulario», «¿qué le falta a este botón?»), no lances el proceso completo:

1. Pregunta solo lo imprescindible: dónde verlo y quién lo usa.
2. Aplica a esa pieza la mirada de la fase 1 y la lista de la fase 5.
3. Entrega los hallazgos en el chat, con la forma **qué se ve → por qué importa → acción**, y una propuesta concreta (código o un mock pequeño).
4. Ofrece en una línea el paquete completo (informe, prototipo y pulido) por si lo quieren.

## Proceso

| Fase | Qué produces | Lee |
|---|---|---|
| 0. Contexto | Brief del software: URL y entorno, repo, roles, pantallas clave, dolores, marca | `references/intake.md` |
| 1. Descubrimiento | Recorrido real por tareas, con fricción medida y evidencias | `references/senior-lens.md` |
| 2. Informe | Informe en el repo + documento compartible | `references/report-template.md` |
| 3. Prototipo | Página HTML o lienzo con todas las pantallas y notas «Antes / Ahora» | `references/design-language.md`, `references/prototype-canvas.md` |
| 4. Uso intensivo | Pantallas clave con trabajo en serie, deshacer, teclado, acciones en línea… | `references/intensive-use.md` |
| 5. Calidad | Ningún fallo visual ni dato contradictorio | `references/qa-checklist.md`, `scripts/` |

Con más de unas 15 pantallas, reparte las fases 3 y 4 entre subagentes con `references/agent-briefs.md`.

Las rutas `references/`, `scripts/` y `assets/` son relativas a la carpeta de esta skill. Claude Code indica esa ruta base al cargarla, y la skill puede estar en `~/.claude/skills/`, en `.claude/skills/` del repo o dentro de un plugin. En los encargos a subagentes, usa siempre la ruta absoluta.

Al empezar cada fase y cuando algo tarde, avisa al usuario en una línea.

**Herramientas.** La skill nombra las de Claude Code: navegador con Claude in Chrome, `AskUserQuestion`, artefactos, subagentes y `SendMessage`. En otro agente, usa su equivalente. Si no hay navegador, pide capturas o un vídeo del recorrido y avisa de que la evidencia es indirecta. Si no hay artefactos, el prototipo es una página HTML local o desplegada, a partir de `assets/prototype-template.html`.

## Fase 0 · Contexto del software (obligatoria)

Cada software es distinto. **No empieces el recorrido sin contexto.** Sigue `references/intake.md`:

1. **Deduce** del repo, la documentación y la pestaña abierta del navegador lo que puedas:
   - producto y usuarios;
   - stack y rutas de la UI;
   - navegación y roles;
   - sistema de diseño y marca;
   - contratos de UX;
   - URLs de entornos;
   - dolores documentados.
2. **Pregunta lo que falte en un solo mensaje**, enseñando lo que has deducido para que solo confirme. Imprescindibles:
   - la URL y si es producción;
   - el repo;
   - los roles y en qué pantallas pasan más horas;
   - qué problemas han reportado.

   Útiles:
   - la marca;
   - las restricciones;
   - los entregables (por defecto, todo);
   - otras fuentes de información.

   Para las decisiones cerradas, usa la herramienta de preguntas del agente (en Claude Code, `AskUserQuestion`).
3. **Escribe el brief** (`<carpeta de documentación>/ux-brief-<área>.md`, o en una carpeta temporal si no se puede escribir en el repo). Lo usarás tú y se lo pasarás a cada subagente.
4. **Adapta el enfoque** al tipo de producto: back-office, SaaS, móvil, web pública o analítica (tabla en `intake.md`).

**Seguridad, siempre:**
- **Producción es de solo lectura.** No crees, guardes, envíes, archives ni borres nada. Puedes abrir formularios y modales para verlos, pero ciérralos sin enviar. Un error en una consulta de solo lectura es un hallazgo, no algo que «arreglar».
- **Credenciales.** La sesión la abre el usuario: nunca escribas contraseñas.
- **Datos personales.** Anonimiza en el informe a las personas reales. El prototipo usa datos ficticios.
- **Sistema de diseño del repo.** Si el repo tiene uno (o un presupuesto de motion o contratos de UX), **manda sobre el lenguaje por defecto de esta skill**.

## Fase 1 · Descubrimiento con mirada senior

Objetivo: entender el producto mejor que quien lo diseñó, con evidencia y fricción medida. Sigue `references/senior-lens.md`.

1. **Código.**
   - Rutas, navegación (cuenta entradas y niveles) y componentes de tabla, formulario, modal y estado vacío.
   - Textos de error, enums visibles y contratos de UX.
2. **Contexto humano.** Transcripciones, feedback, tickets y notas: ahí están el vocabulario y los dolores reales.
3. **Recorrido en el navegador**, por **tareas de cada rol** de principio a fin y luego entrada por entrada del menú. Mide:
   - pasos y pantallas;
   - saltos de contexto y esperas;
   - decisiones sin información y datos que hay que recordar;
   - incertidumbre y capacidad de recuperar un error.

   Anota también:
   - carga frente a vacío;
   - cifras que se contradicen;
   - fugas técnicas (IDs, enums, errores crudos);
   - callejones sin salida;
   - acciones destructivas a mano;
   - datos de prueba;
   - ortografía;
   - accesibilidad básica: contraste, foco visible, etiquetas en los campos y uso con teclado.
4. **Clasifica** cada hallazgo:
   - **P0:** impacto operativo o pérdida de confianza;
   - **P1:** fricción frecuente;
   - **P2:** pulido.

   Prioriza por impacto × frecuencia y agrupa en **3–6 causas raíz**. Para cada causa, propone un cambio estructural y sus arreglos rápidos.
5. **Confirma o corrige** la lista de pantallas de uso intensivo del brief con lo que has visto.

## Fase 2 · Informe

Sigue `references/report-template.md`:
1. Causas de fondo.
2. P0.
3. Transversales.
4. Flujos hoy frente a objetivo.
5. Hallazgos por módulo.
6. Nueva arquitectura de información.
7. Principios.
8. Estándar de uso intensivo.
9. Plan por fases con arreglos rápidos y métricas.

Cada hallazgo sigue la forma: **qué se ve → por qué importa → evidencia → acción**.

- **Dónde guardarlo:** en el repo, en la carpeta de documentación del proyecto.
- **Documento compartible:** si hay un conector de documentos de primera parte (por ejemplo, Claude Docs), créalo también.
- **Enlace al prototipo:** cuando esté publicado, añádelo en los dos sitios.
- **Revisión final:** comprueba que las cifras cuadran («18 arreglos rápidos» son 18 casillas) y que las referencias cruzadas existen.

## Fase 3 · Prototipo visual

Un mock independiente del software: sin lógica real, pero **navegable y con estado**, para que el equipo vea y toque cómo sería lo «top».

- **Formato.** Elige uno de los dos (detalle en `references/prototype-canvas.md`):
  - **Página HTML, en cualquier agente.** Parte de `assets/prototype-template.html`: una sola página sin dependencias, con barra lateral, pantallas por `#ruta`, estado, deshacer, atajos de teclado y panel de notas «Antes / Ahora». Añade una entrada a `screens` por cada pantalla.
  - **Lienzo de diseño, en Claude Code con artefactos de claude.ai (tipo «Design»).** Llama primero a `Artifact` con `action: "quickstart"` e `intent: "design"` y parte de `assets/board-template.dc.html` y `assets/sidebar-template.dc.html`. Es un formato del propio producto y puede cambiar: si algo no cuadra con esta skill, mandan las instrucciones del tipo.
- **Lenguaje visual.** Sigue `references/design-language.md`:
  - grises neutros, tipografía de 13 px y barra lateral fija;
  - paneles con vista lateral, filtros en píldora y barra flotante de selección;
  - ⌘K y atajos visibles;
  - el color primario de la marca solo en la acción principal, y el acento de marca solo en el logo y en la marca del asistente.

  **Prohibido el «vibecoding»:**
  - tarjetas con icono decorativo;
  - banners de color;
  - emoji y degradados;
  - antetítulos en mayúsculas;
  - titulares enormes;
  - sombras gruesas.
- **Cobertura.** Todas las pantallas del área, incluidos los detalles, formularios y modales clave. No basta con una muestra.
- **Hoja de verdad.** Antes de dibujar, fija:
  - un único «ahora», por ejemplo martes a las 10:45;
  - las personas recurrentes con sus datos;
  - los totales y sus desgloses;
  - las etapas y los nombres de las secciones.

  Añádela al brief y pásasela a cada subagente.
- **Notas «Antes / Ahora»** en cada pantalla (bajo el tablero en el lienzo y en el panel de notas en la página HTML).
  - «Antes»: lo observado en el producto real, con evidencia.
  - «Ahora»: qué resuelve el rediseño y cómo.

  En las pantallas intensivas, el «Ahora» suma el bloque «Fricción mínima · uso intensivo».
- **Orden.** Primero las pantallas de uso diario y después el resto, por temas.
  - En la página HTML, con grupos en la barra lateral.
  - En el lienzo, con páginas temáticas, un título por fila y una nota introductoria. Genera el `canvas.json` con `scripts/build_canvas.py` (ejemplo en `assets/layout-example.json`).

## Fase 4 · Pantallas de uso intensivo

Rehaz las 8–14 pantallas donde más horas se pasan, con `references/intensive-use.md`:

- **trabajo en serie:** al resolver se abre solo lo siguiente;
- **deshacer en vez de confirmar;**
- **teclado visible:** J/K, E, A, H, ⌘⏎ y /;
- **acciones en línea:** sin modales para lo que se hace diez veces al día;
- **valores por defecto útiles;**
- **contadores vivos;**
- **estados vacíos** que cierran el día con un resumen.

Todo funciona con estado en el prototipo. Márcalas con «· uso intensivo» en el prototipo y añade su sección al informe: la tabla de pantallas, las 10 reglas como criterios de aceptación y sus métricas.

## Fase 5 · Calidad y coherencia (no la saltes)

Aquí se separa «decente» de «top tier». Sigue `references/qa-checklist.md`:

```bash
S=<carpeta de esta skill>/scripts   # la ruta base que indica el agente al cargar la skill
python3 $S/lint_boards.py --project <carpeta> [archivos…]   # reglas antivibecoding y formato (.html y .dc.html)
python3 $S/scan_ui.py --project <carpeta> [archivos…]       # IDs técnicos, anidados, menús abiertos, tokens, enlaces, plurales
node    $S/check_logic.js <carpeta> <Tableros…>             # solo lienzo: huecos que resuelven y manejadores sin errores
```

Sin nombres de archivo, revisan todos los `.html` de la carpeta. En la página HTML, la lógica se comprueba en el navegador.

Después:
- **Revisión a tamaño real en el navegador**, pantalla por pantalla (en el lienzo, en su modo de juego): textos partidos, solapes, popovers que tapan contenido, avisos encima de botones.
- **Pasada de coherencia entre pantallas:**
  - contadores del menú iguales a la suma de las pestañas;
  - la misma persona con los mismos datos en todas partes;
  - horas compatibles con el mismo «ahora»;
  - etapas idénticas;
  - totales que suman.

## Trabajo con subagentes

Con `references/agent-briefs.md`:
- **Propiedad estricta de archivos.** Cada agente escribe solo sus tableros y su archivo de notas.
- **Contexto en cada encargo.** Brief, hoja de verdad y reglas aprendidas.
- **Verificación antes de terminar,** con los scripts.
- **Integración tuya.** Tú validas, corriges las incoherencias entre tableros, publicas y revisas en el navegador.
- **Coherencia en caliente.** Si un agente fija datos que otro, todavía en marcha, va a mostrar, avísale (en Claude Code, con `SendMessage`).
- **La revisión final de coherencia la haces tú.**

## Lecciones aprendidas (evita repetirlas)

**Al construir las pantallas** (los huecos `{{…}}` y `onKeyDown` son del lienzo):
- **Texto junto a un hueco en un contenedor flex.** Pierde el espacio («Espera47 min»). Envuelve el texto completo en un `<span>` o calcúlalo entero en la lógica.
- **Fondos en línea.** Anulan `.hov:hover`. Declara el hover con `!important`.
- **Textareas.** `<textarea>{{x}}</textarea>` muestra «[object Object]». Usa `value="{{x}}" onChange="{{fn}}"`.
- **IDs técnicos.** No muestres ninguno («CLS-218»). Usa rutas legibles. Los códigos editoriales del negocio sí pueden verse.
- **Menús.** Ciérralos por defecto.
- **Botones.** Que quepan en una línea; si no, acorta el texto («Mover…»).
- **Anidación.** Ni `<a>` ni `<button>` dentro de otro.
- **Datos.**
  - Plurales correctos («1 entrega»).
  - Un único «ahora» en todo el prototipo.
  - Etapas con el mismo nombre en todas las pantallas.
- **Avisos.** No deben tapar el compositor ni los botones.
- **Atajos reales (`onKeyDown`).** Pueden no funcionar en el prototipo: ofrece cada atajo también como botón y di al usuario qué no se ha comprobado.

**En el navegador:**
- **Coordenadas.** Cambian si cambia el tamaño de la ventana. Haz una captura nueva antes de cada tanda de clics. Antes de concluir que «no responde», comprueba que la captura no tenía otro tamaño.
- **Clics en el lienzo.** En la vista de lienzo no llegan a los tableros: usa el modo de juego.
- **`find`.** No ve dentro de un iframe (el lienzo o una página publicada); usa capturas y `zoom`.

**Al publicar en el lienzo:**
- **Publicación rechazada** porque el lienzo cambió (el editor normaliza las notas): lee la versión publicada, fusiona y vuelve a publicar.
- **Por tandas.** Publica solo los tableros cambiados y nunca uno que otro agente esté escribiendo.
- **Al terminar,** deja `launch` en la primera página del lienzo.

## Entrega final

Breve y en el idioma del usuario:
- qué se ha hecho;
- enlaces al informe, al documento y al prototipo;
- qué pantallas son de uso intensivo y qué cambió en ellas;
- qué se ha comprobado en el navegador y qué no;
- cómo compartir el prototipo: por ejemplo, un artefacto de claude.ai es privado hasta compartirlo desde «Compartir».

Si hay memoria persistente, guarda dónde quedan el informe, el brief y el prototipo.
