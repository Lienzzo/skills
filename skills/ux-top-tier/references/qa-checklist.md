# Calidad y coherencia: lista de comprobación

Pasa esta lista antes de dar el prototipo por terminado. Lo que distingue un prototipo «top tier» de uno «decente» es que nada desentona al tocarlo.

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

## 2. Visual (a tamaño real, en el navegador, pantalla por pantalla)

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

## 3. Interacción (pantallas de uso intensivo)

- [ ] La acción principal ejecuta, muestra el resultado y pasa al siguiente.
- [ ] «Deshacer» devuelve exactamente el estado anterior, contadores incluidos.
- [ ] Los filtros y las vistas filtran de verdad y sus contadores cuadran con la lista.
- [ ] El estado vacío final aparece al vaciar la cola y resume lo hecho.
- [ ] Los atajos visibles funcionan al pulsarlos como botones y, en la página HTML, también con el teclado.

## 4. Coherencia entre pantallas (la que más se olvida)

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

## 5. Entrega

- [ ] Lienzo: `canvas.json` regenerado, sin solapamientos y con `launch` en la primera página. Página HTML: abre en la primera pantalla de uso diario y el panel de notas funciona.
- [ ] Notas de uso intensivo con el bloque «Fricción mínima».
- [ ] Informe y documento actualizados con el enlace al prototipo y la sección de uso intensivo.
- [ ] Pestañas del navegador que abriste, cerradas.
- [ ] Mensaje final: qué se hizo, enlaces, qué se comprobó en el navegador y qué no, y que el prototipo es privado.
