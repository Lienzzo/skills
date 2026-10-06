# Mirada de UX senior: cómo encontrar y medir la fricción

Un análisis senior no lista «cosas feas». Explica **por qué** la gente se pierde, **cuánto** le cuesta cada tarea y **qué cambio estructural** elimina la causa. Usa esta guía en la fase 1 (descubrimiento) y para justificar cada propuesta.

## 0. Siéntate en su silla

- **La UI actual es evidencia, no referencia.** Recórrela para entender las tareas, los datos y los dolores, no para copiarla. Lo que hay casi nunca es lo óptimo: pregúntate siempre cómo lo resolverían Linear o v0 desde cero.
- **Piensa en la persona que pasa ocho horas al día aquí.** Para ella una fricción pequeña no existe: un clic de más, una espera o un modal se repiten cientos de veces al día, todos los días, durante años.
- **Pon cifra al dolor.** Coste = segundos perdidos × veces al día × personas × días laborables. Por ejemplo, 3 s de más × 200 veces al día son 10 min diarios por persona, unas 40 h al año. Esa cifra ordena las prioridades y convence más que cualquier adjetivo.
- **Repite la tarea diez veces seguidas.** Lo que a la primera parece aceptable, a la décima molesta. Eso es lo que hay que eliminar.

## 1. Analiza por tareas, no por pantallas

Para cada rol, lista sus 5–8 tareas diarias («responder a un cliente», «dar de alta», «corregir una entrega»). Recorre cada una de principio a fin en la app real y anota:

| Medida | Qué cuenta |
|---|---|
| Pasos | Clics, teclas y campos hasta terminar |
| Pantallas | Cambios de pantalla o de pestaña |
| Saltos de contexto | Veces que hay que ir a otro módulo a buscar un dato para decidir |
| Esperas | Cargas, procesos en segundo plano, «actualiza y vuelve a intentarlo» |
| Decisiones | Cuántas veces el usuario tiene que elegir sin la información para hacerlo |
| Memoria | Datos que debe recordar o copiar de una pantalla a otra |
| Incertidumbre | ¿Sabe si funcionó? ¿Sabe qué pasará al pulsar? |
| Recuperación | ¿Puede deshacer? ¿El error explica qué hacer? |

Este recuento alimenta la tabla «Flujos de principio a fin» del informe y las métricas de antes y después. En las tareas que se repiten a diario, añade cuántas veces al día se hacen: sin eso no se puede calcular el coste.

Mientras recorres, captura el «antes» de cada pantalla que vas a rediseñar, con los datos personales enmascarados (`references/prototype-canvas.md`, § 8).

## 2. Taxonomía de fricción

Clasifica cada hallazgo. Las causas raíz suelen agruparse aquí:

1. **Fragmentación.** La misma entidad (persona, pedido) vive en varios sitios sin enlaces.
2. **Trabajo invisible.** Lo pendiente está repartido en colas sin bandeja común, responsable ni antigüedad.
3. **Navegación profunda.** Muchos niveles (menú, pestaña, subpestaña, botón) y lo frecuente por debajo del pliegue.
4. **Vocabulario.** Un término con dos significados, o dos términos para lo mismo.
5. **Desconfianza.** Cifras que se contradicen, «sin resultados» mientras carga, datos de prueba en producción.
6. **Fugas técnicas.** IDs, slugs, enums, claves y errores crudos de API en la interfaz.
7. **Callejones sin salida.** Ves el problema pero no puedes actuar desde ahí.
8. **Confirmaciones y modales innecesarios** para lo reversible y frecuente.
9. **Falta de valores por defecto.** Formularios en blanco cuando el sistema ya sabe la respuesta.
10. **Estados sin diseñar.** Carga, vacío, error, éxito, permisos.

## 3. Heurísticas que sí importan en herramientas de trabajo

- **Reconocer mejor que recordar.** Muestra en contexto lo necesario para decidir (quién es, qué pagó, qué pidió).
- **Visibilidad del estado.** Cada elemento dice en qué punto está y qué falta.
- **Prevención de errores.** Mejor que un buen mensaje de error: evita que ocurra. Valida en línea, bloquea duplicados y propone.
- **Control y libertad.** Deshacer siempre. Nada irreversible a un clic.
- **Consistencia.** Un patrón por problema en todo el producto (lista → vista lateral → página).
- **Eficiencia para expertos.** Teclado, acciones masivas, vistas guardadas y ⌘K, sin estorbar al novato.
- **Ley de Hick.** Pocas opciones por decisión: lo frecuente arriba y el resto en «…».
- **Ley de Fitts.** Las acciones frecuentes, grandes y cerca de donde está la vista. Las destructivas, lejos.
- **Rastro de información.** Cada enlace y cada cifra dicen adónde llevan; los contadores llevan a la lista filtrada.

## 4. Prioriza con impacto × frecuencia

| | Frecuencia alta | Frecuencia baja |
|---|---|---|
| **Impacto alto** (bloquea, pierde dinero o confianza) | P0: arreglar ya | P0/P1 |
| **Impacto medio** (fricción, tiempo) | P1: pantallas de uso intensivo | P2 |
| **Impacto bajo** (pulido) | P2, en lote | Backlog |

Una fricción pequeña en una pantalla que se usa 200 veces al día vale más que un gran defecto en una pantalla que se abre una vez al mes.

## 5. Cómo escribir cada hallazgo

Usa cuatro partes: **qué se ve → por qué importa → evidencia → acción**.

- Mal: «La bandeja es confusa».
- Bien: «La bandeja no distingue quién ya es cliente: alguien con suscripción activa que pregunta por su pedido aparece como "Lead nuevo · Sin asignar". El equipo tiene que buscarlo en otras dos pantallas antes de responder. Acción: cruzar teléfono y correo con la base de clientes y mostrar "Cliente activo" con su contexto en el hilo».

## 6. Diseña la solución, no el parche

No partas de la pantalla actual para retocarla: parte de la tarea y del estándar de Linear y v0, y solo después mira qué se puede aprovechar. Para cada causa raíz propone un **cambio estructural** (bandeja única, ficha 360, navegación por tareas, glosario) **y** sus **arreglos rápidos**, que se pueden hacer ya y no contradicen la estructura. El informe debe permitir empezar el lunes por los arreglos rápidos sin esperar al rediseño.
