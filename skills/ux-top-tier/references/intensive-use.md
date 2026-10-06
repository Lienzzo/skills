# Estándar de uso intensivo: fricción mínima

Las pantallas donde el equipo pasa horas multiplican cada clic por cientos de repeticiones al día. Aquí no basta con un flujo correcto: cada acción frecuente debe costar un clic o una tecla, y nunca obligar a volver a la lista.

Diseña cada una sentado en la silla de quien la usa ocho horas al día, cinco días a la semana. Lo que para ti es «un clic más» para esa persona son cientos de clics al día y un dolor que no se acaba. No partas de cómo es hoy la pantalla: parte de la tarea y de cómo la resolverían Linear o v0, y pon en el informe el coste de la fricción que quitas (segundos × veces al día × personas).

## Cómo identificarlas

Pregunta o deduce del contexto (roles, transcripciones, feedback) qué hace cada rol todo el día. Suelen ser:

| Tipo de pantalla | Ejemplos | Patrón |
|---|---|---|
| Bandeja del día | Hoy, Inicio, Mis pendientes | Lista agrupada + vista lateral + trabajo en serie |
| Mensajería | Conversaciones, tickets, soporte | Tres columnas: lista, hilo y contexto |
| Cola de revisión | Corrección, moderación, aprobaciones, triaje de errores | Cola + visor + panel de decisión con «Enviar y siguiente» |
| Seguimiento / CRM | Leads, clientes en riesgo, cobros | Vista «Para hoy» + acción en línea por fila |
| Ficha 360 | Cliente, paciente, lead | Resumen, siguiente paso, compositor, actividad filtrable y anterior/siguiente de la cola |
| Pipeline | Altas, oportunidades, pedidos | Tablero con la acción siguiente en cada tarjeta, que avanza sola |
| Alta / creación frecuente | Nueva alta, nuevo pedido | Un solo buscador que rellena, resumen vivo y «Crear otro» sin cerrar |
| Directorio | Clientes, pacientes, productos | Búsqueda instantánea + vista lateral con la acción según el estado |
| Agenda / planificación | Agenda, clases, turnos | Día y semana, vencidas arriba, reprogramar con huecos propuestos |
| Catálogo editable | Productos, base de conocimiento, plantillas | Filtros, edición en la vista lateral con guardado implícito y acciones masivas |

Elige entre 8 y 14. En el lienzo, márcalas con «· uso intensivo» y llévalas a la primera página.

## Las 10 reglas (criterios de aceptación)

1. **Trabajo en serie.** Tras resolver, enviar o corregir se abre el siguiente elemento de la cola. Volver a la lista nunca es obligatorio.
2. **Deshacer en vez de confirmar.** Lo reversible se ejecuta al momento y muestra un aviso con «Deshacer» durante 6–8 s. Solo lo irreversible (cobros, borrados definitivos) pide confirmación.
3. **Teclado completo y visible.** Cada acción frecuente tiene atajo, y el atajo se ve en el botón o en una barra discreta al pie: J/K moverse, E resolver, A asignar, H posponer, R responder, N nota, / plantillas, ⌘⏎ enviar, Esc cerrar.
4. **Acción en línea.** Lo que se hace más de diez veces al día no abre un modal ni cambia de pantalla. Usa popovers pequeños anclados a la fila o tiras que se despliegan dentro de ella.
5. **Valores por defecto útiles.** Plantillas con el nombre y el motivo ya puestos, responsable por defecto quien lo usa, tarifa y programa ya elegidos, huecos libres propuestos.
6. **Contadores vivos.** Cada acción actualiza al instante los contadores del grupo, de la pestaña y del ámbito («Mío 14 → 13»).
7. **Sin esperas visibles.** Respuesta optimista en menos de 100 ms y sincronización en segundo plano. Si algo falla, el aviso lo explica y ofrece reintentar.
8. **Un estado vacío que cierra el día.** «Todo al día» con lo hecho (resueltas, tiempo medio) y lo siguiente en la agenda.
9. **El contexto se conserva.** Filtro, selección y borrador sobreviven a navegar y a recargar.
10. **Densidad estable.** Filas de 36–40 px y sin saltos de maquetación al cambiar de elemento. Un elemento resuelto puede quedarse atenuado hasta que el usuario se mueva, para que la lista no salte bajo el ratón.

## Detalle por patrón

### Bandeja del día
- Grupos por tipo o por urgencia, con un menú «Vista» para cambiarlo. Ámbitos Mío / Equipo / Todo con datos distintos.
- Cada fila lleva icono de prioridad, título, contexto en gris, etiqueta de tipo, avatar del responsable y antigüedad, en naranja si pasa del plazo.
- La vista lateral tiene:
  - una ruta legible («Clases › Hoy, 16:30»), nunca un ID;
  - la posición en la cola («3 de 14»);
  - ‹ › para moverse;
  - una **acción principal contextual** (crear la sala, responder con el borrador, enviar las invitaciones) cuyo resultado se ve en la propia vista lateral antes de pasar al siguiente («Sala creada · 214 invitados · Siguiente: … ⏎ · Deshacer»);
  - Resolver (E), Asignar (A) y Posponer (H: «Mañana 9:00», «El lunes», «Elegir fecha…»).
- Arriba, un resumen de una línea del asistente con enlaces que actúan.

### Mensajería
- Vistas «Esperan / No leídas / Mías / Todas» que filtran de verdad, cada una con su contador.
- El objetivo de respuesta va visible («menos de 30 min · 3 fuera de plazo»). La espera de cada conversación se pone naranja cuando lo supera.
- El compositor tiene:
  - el borrador del asistente, que se acepta con Tab;
  - plantillas con «/»;
  - un conmutador «Respuesta / Nota interna», donde la nota se pinta con un fondo distinto para no enviarla por error;
  - envío con ⌘⏎;
  - la firma.
- Al enviar, el mensaje aparece en el hilo como «ahora · Enviado» y la conversación sale de «Esperan», con «Deshacer».
- Resolver (E) archiva y abre la siguiente que espera.
- El panel de contexto tiene acciones que cambian el estado: reenviar la invitación, marcar el pedido como enviado, enviar el enlace de pago.

### Cola de revisión (corrección, moderación)
- Una cola con su estado: pendiente, borrador (medio lleno) o enviada (check y nota). El visor tiene pestañas del documento.
- Rúbrica con la nota calculada al momento. «Enviar» se activa solo cuando está completa y dice cuántos criterios faltan.
- Propuesta del asistente aplicable con un clic. Frases frecuentes en chips y anotaciones ancladas a líneas.
- «Enviar y siguiente» (⌘⏎), «Borrador», un modo foco que oculta la cola, y el tiempo frente al objetivo (por ejemplo, 48 h).
- Si la cola queda vacía, un resumen (corregidas, tiempo medio, nota media) y un enlace a la siguiente cola.

### Triaje de errores reportados en el contenido
- Decisión 1 / 2 / 3: corregir, está bien o retirar. Cada una cambia la plantilla de respuesta y el texto del botón.
- El impacto se ve antes de resolver («afecta a 1.200 registros: 260 cambian de estado»).
- Edición en línea del contenido afectado. Resolver avisa a quienes lo reportaron y abre el siguiente. Con «Saltar» se pasa al siguiente sin resolver.

### Seguimiento / CRM
- La vista «Para hoy» es la de por defecto: atrasados arriba y el resto ordenado por hora.
- Registrar el resultado de la llamada desde la fila con un clic: interesado, no contesta, volver a llamar el… o no le interesa con su motivo. El siguiente seguimiento se programa solo y la selección pasa a la siguiente fila.
- «Contactar» abre en la fila un mensaje ya personalizado con el motivo. Al enviar, la fila pasa a «Contactados hoy».
- La barra de selección múltiple ejecuta de verdad: plantilla a todos, asignar, posponer 7 días o marcar como contactado.

### Ficha 360
- Arriba, un resumen narrativo y un **siguiente paso** destacado y ejecutable («Programar mensaje · hoy 12:00»).
- Compositor de nota o mensaje, actividad filtrable con contadores y propiedades editables en línea con menús pequeños.
- Anterior y siguiente dentro de la cola de la que se vino («1 / 12»).

### Pipeline
- Cada tarjeta muestra su **acción siguiente**, que se ejecuta sin abrir nada: «Recordar pago» pasa a «Recordado hace un momento», y «Llamada hecha» pide el resultado en un popover.
- Al completar el último paso, la tarjeta pasa sola a la columna siguiente, con aviso y «Deshacer».
- Franja «Necesitan atención» que filtra al pulsarla. Conmutador Tablero / Lista y columnas vacías explicadas.

### Alta frecuente
- Un único campo «Nombre, teléfono o correo» que busca en todo:
  - elegir a alguien lo rellena todo;
  - si ya existe archivado, ofrece «Reincorporar» en vez de duplicar;
  - si ya está activo, lo bloquea y ofrece abrir su ficha.
- Valores por defecto según el origen, validación en línea discreta y resumen vivo de lo que pasará al confirmar, con el importe.
- ⌘⏎ confirma. El éxito se muestra en el propio modal, con «Crear otro» y «Ver en…».

### Directorio
- Búsqueda instantánea por nombre, teléfono o correo, que también se abre con «/».
- Vistas guardadas con cifras que suman y filtros en píldora con recuento.
- La vista lateral trae la acción según el estado: reenviar la invitación, cambiar la tarjeta, reincorporar.

### Agenda / sesiones
- Día y semana, la línea de «ahora» y las vencidas arriba con «Hacer ahora / Reprogramar».
- Reprogramar propone 2–3 huecos libres en un clic. Crear se puede hacer en lenguaje natural mostrando antes cómo se ha interpretado.
- Las sesiones (clases, citas, turnos) van ordenadas por estado: sin sala, sin responsable o sin contenido, con el arreglo en un clic por fila. Al resolver una, la selección pasa a la siguiente con problema.

## Métricas para el informe

| Métrica | Objetivo típico |
|---|---|
| Clics para resolver un elemento de la bandeja y abrir el siguiente | 1 clic o 1 tecla |
| Tiempo de primera respuesta en mensajería (horario laboral) | < 30 min |
| Clics para enviar una corrección y abrir la siguiente | 1 clic o ⌘⏎ |
| Acciones hechas con teclado en las pantallas de mayor uso | > 50 % al mes |
| Tiempo para dar de alta | < 2 min en 1 pantalla |
| Pendientes con responsable asignado | 100 % |

## En el prototipo

Todo debe funcionar con estado: filtrar filtra, enviar añade el mensaje, resolver mueve la selección, deshacer devuelve exactamente el estado anterior y los contadores cambian. Patrón de deshacer que funciona:

```js
flash(patch, text, undoable) {
  const id = Date.now() + Math.random();
  const snapshot = undoable ? this.snapshotOf(this.state) : null; // copia de las claves que la acción toca
  this.setState({ ...patch, snapshot, toast: { id, text, undo: Boolean(undoable) } });
  clearTimeout(this.toastTimer);
  this.toastTimer = setTimeout(() => {
    if (this.state.toast && this.state.toast.id === id) this.setState({ toast: null });
  }, 6000);
}
// en renderVals: undo: () => this.state.snapshot && this.setState({ ...this.state.snapshot, snapshot: null, toast: null })
```

Los atajos de teclado reales (`onKeyDown`) pueden no estar soportados por el entorno del prototipo. Ofrece siempre el mismo atajo también como botón pulsable, y dile al usuario qué atajos no has podido comprobar.
