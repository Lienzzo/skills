# Calidad y coherencia: lista de comprobación

Pasa esta lista antes de dar el prototipo por terminado. Lo que distingue un prototipo «top tier» de uno «decente» es que nada desentona al tocarlo.

Los validadores del bucle (`references/agent-briefs.md`, «Bucle de validación») la usan como guion: el de calidad, las secciones 1, 3, 4 y 5, y el de UX/UI, la 2. La auditoría final del artefacto en el navegador (sección 7) es lo último que haces tú.

## 1. Automática (scripts)

```bash
S=<carpeta de esta skill>/scripts   # la ruta base que indica el agente al cargar la skill
python3 $S/lint_boards.py --project <carpeta>          # antivibecoding, foco, tema oscuro, motion reducido; en el lienzo, también su formato
python3 $S/scan_ui.py --project <carpeta>              # IDs técnicos, anidados, menús abiertos, tokens claro/oscuro, enlaces, plurales
node    $S/check_logic.js <carpeta> <Tablero> […]      # solo lienzo: cada hueco resuelve y cada manejador se ejecuta sin errores
```

Además:
- **Enlaces:** todo `href="X.dc.html"` (lienzo) o `href="#pantalla"` (página) apunta a algo que existe. `scan_ui.py` lo comprueba.
- **Alturas (lienzo):** `$preview.height` igual a la `min-height` del contenedor raíz.
- **Lógica (página HTML):** en el navegador, cada acción, su «Deshacer» y cada atajo.
- **Capturas del «antes»:** en la página, `scan_ui.py` avisa de las pantallas sin `before` y de las capturas que no existen. En el lienzo, `build_canvas.py` avisa de las pantallas sin captura que no están en `"new"`.

## 2. Revisión senior (pantalla por pantalla)

La hace el validador de UX/UI en cada ronda del bucle, o tú si no hay subagentes, mirando la captura de la pantalla y no su código. Si una pantalla no pasa, se rehace; no se pule.

- [ ] **Rediseñada, no repintada.** Ponla al lado de su captura del «antes». Si se reconoce la misma estructura (la misma navegación, el mismo orden, los mismos modales) con otro estilo, no está rediseñada.
- [ ] **Menos coste por tarea.** Cuenta clics, teclas, pantallas y esperas de su tarea principal, antes y ahora. Deben bajar, y en las de uso intensivo, a un clic o una tecla por elemento.
- [ ] **Ocho horas al día.** Imagina a quien la usa toda la jornada. Apunta las tres cosas que aún le molestarían a la décima repetición y quítalas.
- [ ] **Listón Linear.** ¿Pasaría la revisión de diseño de Linear? ¿Hay algo que parezca plantilla, genérico o «vibecoded» (`references/design-language.md`, § 6)?
- [ ] **Cada elemento se gana su sitio.** Quita lo que no ayude a decidir o a actuar.
- [ ] **Estados completos.** Hover, foco, carga, vacío, error y éxito diseñados, no por defecto.

## 3. Visual (a tamaño real, en el navegador, pantalla por pantalla)

- [ ] Ningún texto partido en dos líneas donde no debe: botones, etiquetas, insignias, pestañas.
- [ ] Ningún solapamiento: cabeceras de columna, celdas largas (elipsis), avisos sobre botones, popovers sobre contenido.
- [ ] Espacios correctos entre texto y cifras («Espera 47 min», no «Espera47 min»).
- [ ] Ningún menú abierto por defecto que tape contenido.
- [ ] Las tablas aprietan bien cuando se abre la vista lateral: la columna principal con `minmax(0,1fr)` y elipsis.
- [ ] Los estados de pulsado, hover y foco se ven en filas y botones.
- [ ] Las alturas de evento en calendarios encajan con su texto: una línea si dura menos de 60 min.
- [ ] Modo oscuro: revisa al menos 3 pantallas (con la prop `dark` en el lienzo o el conmutador de tema en la página).
- [ ] Ningún ID técnico visible.
- [ ] Accesibilidad básica:
  - texto secundario con contraste suficiente;
  - foco visible en todo lo interactivo;
  - campos con etiqueta o `aria-label`;
  - botones de solo icono con `aria-label`.

## 4. Interacción (pantallas de uso intensivo)

- [ ] La acción principal ejecuta, muestra el resultado y pasa al siguiente.
- [ ] «Deshacer» devuelve exactamente el estado anterior, contadores incluidos.
- [ ] Los filtros y las vistas filtran de verdad y sus contadores cuadran con la lista.
- [ ] El estado vacío final aparece al vaciar la cola y resume lo hecho.
- [ ] Los atajos visibles funcionan al pulsarlos como botones y, en la página HTML, también con el teclado.

## 5. Coherencia entre pantallas (la que más se olvida)

Haz una tabla mental o un `grep` de cada persona y cifra recurrente:

- [ ] **Un único «ahora».** Las esperas y antigüedades de bandeja, mensajería, leads y agenda salen del mismo reloj. Por ejemplo, el mensaje de las 10:14 sigue esperando 31 min a las 10:45.
- [ ] **Contadores del menú lateral** iguales a la suma de las pestañas de esa sección (por ejemplo, Soporte = Abiertos + En espera + Escalados).
- [ ] **Totales** que suman: los programas suman el total y las vistas guardadas cuadran.
- [ ] **Misma persona, mismos datos:** programa o plan, etapa, responsable, teléfono, pagador, importes.
  - Una persona no puede estar «completada» en un sitio y «sin entrar 9 días» en otro.
  - Tampoco puede estar en un programa y entregar trabajos de otro.
- [ ] **Etapas y nombres idénticos** en todas partes. Si una pantalla dice «Decisión» y otra «Interesado», cámbialo.
- [ ] **Flujos coherentes con el rediseño.** Si el nuevo alta envía la invitación sola al pagar, ninguna bandeja puede tener «invitaciones listas para enviar» sin explicar por qué (por ejemplo, clientes migrados).
- [ ] **Asignaciones coherentes:** lo que está «asignado a mí» en una cola lo está también en la agenda.
- [ ] **Notas «Antes / Ahora»** al día con lo que realmente hace cada tablero, sin cifras antiguas.

## 6. Entrega

- [ ] Lienzo: creado como artefacto del tipo «Design», con `canvas.json` regenerado, sin solapamientos y con `launch` en la primera página. Página HTML: abre en la primera pantalla de uso diario y el panel de notas funciona.
- [ ] Cada pantalla rediseñada tiene su captura del «antes» (encima, en el lienzo; con «Ver antes», en la página), salvo las nuevas, que lo explican en su nota.
- [ ] Ninguna captura muestra datos personales reales: revisadas una a una.
- [ ] Notas de uso intensivo con el bloque «Fricción mínima».
- [ ] Informe y documento actualizados con el enlace al prototipo y la sección de uso intensivo.
- [ ] Bucle de validación cerrado en 3 rondas como mucho: sin P0 ni P1, o con lo que queda abierto explicado.
- [ ] Auditoría final (sección 7) hecha sobre la versión publicada, después del último cambio.
- [ ] Pestañas del navegador que abriste, cerradas.
- [ ] Mensaje final: qué se hizo, enlaces, cuántas rondas de validación hubo y qué quedó abierto, qué se comprobó en el navegador y qué no, y que el prototipo es privado.

## 7. Auditoría final del artefacto publicado (lo último)

Hazla tú, con todo publicado y después del último arreglo, en una pestaña nueva y como lo verá quien lo reciba. No revises tu copia local: revisa el artefacto.

- [ ] **Vista de canvas** (en el lienzo): cada tablero «Antes» encima de su pantalla, con el título correcto; filas, títulos y notas sin solapes; la nota introductoria al principio; `launch` en la primera página.
- [ ] **Modo de juego, pantalla por pantalla:** las comprobaciones visuales de la sección 3 a tamaño real.
- [ ] **Interacción:** cada acción principal con su «Deshacer», los filtros, la vista lateral y los enlaces entre pantallas, incluida la barra lateral.
- [ ] **Uso intensivo:** la tarea principal de cada pantalla, de principio a fin, contando clics y teclas.
- [ ] **Modo oscuro** en al menos tres pantallas.
- [ ] **Capturas del «antes»** visibles, con el tamaño correcto y sin datos personales.

Lo que falle se arregla, se publica y se vuelve a mirar solo esa pantalla. Si aparece algo estructural, no abras otra ronda del bucle sin decírselo al usuario. Al terminar, cierra la pestaña y anota qué no has podido comprobar (por ejemplo, atajos de teclado que el entorno no deja probar).
