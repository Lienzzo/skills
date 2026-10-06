# Plantilla del informe de auditoría UX

Estructura probada en una auditoría real de un back-office grande. Adáptala al tamaño del producto, pero conserva el orden: primero el porqué (problemas de fondo), luego lo urgente (P0) y al final el cómo y el cuándo.

Estilo:
- Frases cortas.
- Cifras concretas («212 tickets abiertos», «7 pasos en 3 pantallas»).
- Cada hallazgo con **dónde**, **qué se ve** y **qué hacer**.
- En las fricciones que se repiten a diario, su coste: segundos × veces al día × personas («≈ 25 min al día por persona»).
- Nada de adjetivos vacíos («mejorar la experiencia»).
- Anonimiza a las personas reales.

---

```markdown
# Auditoría UX de <área> (<fecha>)

<Párrafo de 3–4 frases: por qué es difícil (no son pantallas sueltas, son N causas de fondo), qué cambios estructurales se proponen y cuántos arreglos rápidos caben en 1–2 semanas.>

<Párrafo de método: entorno recorrido (y que fue solo lectura), cuántas entradas de menú, pantallas de detalle, formularios y flujos completos; con qué se contrastó (código, transcripciones, feedback).>

Prototipo visual navegable con <N> pantallas rediseñadas, cada una con la captura del producto real que sustituye y notas «Antes / Ahora»: <enlace>

## 1. Diagnóstico: los <N> problemas de fondo

| # | Problema de fondo | Evidencia principal | Efecto en el equipo | Solución estructural |
| --- | --- | --- | --- | --- |
| 1 | **<p. ej. La persona está fragmentada>** | <Hay siete representaciones sin enlaces entre sí…> | <Hay que buscar en 3 sitios para saber quién escribe> | <Ficha 360 única> |

## 2. Hallazgos críticos (P0)

<Una frase: impacto operativo directo o pérdida de confianza; van antes que cualquier mejora estética.>

| # | Hallazgo | Dónde | Evidencia | Acción |
| --- | --- | --- | --- | --- |
| C1 | <Los pagos fallidos no avisan a nadie> | <Facturación › Cobros> | <Qué se ve exactamente, con cifras> | <Qué hacer> |

## 3. Problemas transversales

### T1 · <Título corto>
- <Viñetas con evidencia concreta>
- **Propuesta:** <una línea>

<Transversales típicos:
- persona fragmentada;
- pendientes dispersos en muchas colas;
- navegación y contexto que se pierde;
- vocabulario inconsistente;
- cifras contradictorias;
- fugas técnicas (IDs, enums, errores de API);
- callejones sin salida;
- densidad y maquetación;
- acciones destructivas a mano;
- rendimiento percibido (carga frente a vacío);
- datos de prueba en producción;
- ortografía y microcopy;
- feedback marcado como hecho que no lo está.>

## 4. Flujos de principio a fin: hoy frente al objetivo

| Flujo | Hoy | Fricciones | Objetivo |
| --- | --- | --- | --- |
| **J1 · <Dar de alta a un cliente>** | <Pasos y pantallas actuales> | <Qué falla> | <Cómo debería ser, en una pantalla> |

## 5. Hallazgos por módulo

### <Módulo>
| Hallazgo | Sev. | Recomendación |
| --- | --- | --- |
| <…> | P0/P1/P2 | <…> |

## 6. Propuesta de arquitectura de información

| Nueva entrada | Qué agrupa (hoy) | Abre por defecto en |
| --- | --- | --- |
| **<Hoy>** | <Inicio + todas las colas> | <Mis pendientes> |

<Una frase: de N a M entradas de primer nivel; las más usadas arriba; ⌘K para saltar a cualquier cosa.>

## 7. Principios para un producto de primer nivel

1. **La cola primero.** Cada módulo abre en «qué requiere acción», no en el catálogo.
2. **Una persona, una ficha.** Cualquier nombre abre la ficha 360 en panel lateral.
3. **Cada número se puede pulsar y explicar.**
4. **Nada de datos internos.** Sin IDs, slugs, enums ni errores crudos; cada error dice qué pasó y qué hacer.
5. **El contexto viaja.** Filtros y selección en la URL; «Volver» regresa al punto exacto.
6. **Teclado.** ⌘K, J/K, E, A, /.
7. **Lo destructivo, escondido y reversible.**
8. **Cargando no es vacío.**
9. **Un patrón por problema.** Lista → vista lateral → página completa solo si el trabajo es profundo.
10. **Todo pendiente tiene dueño y edad.**

## 8. Pantallas de uso intensivo: fricción mínima

<N> pantallas concentran la mayor parte de las horas del equipo. <Una frase sobre por qué merecen un listón más alto.>

| Pantalla | Quién la usa y cuánto | Qué se repite | Coste de la fricción hoy | Cómo se quita la fricción |
| --- | --- | --- | --- | --- |
| **<Bandeja>** | <Atención, varias horas al día> | <Leer, responder, cerrar> | <3 clics y 2 pantallas × 150 al día ≈ 25 min por persona> | <Borrador con Tab; plantillas con /; resolver abre la siguiente…> |

Reglas comunes, como criterios de aceptación para desarrollo:
<Copia las 10 reglas de `intensive-use.md`.>

## 9. Plan por fases

### Fase 0 · Arreglos rápidos (1–2 semanas)
- [ ] <Arreglo concreto> (<referencia al hallazgo: C1, T6…>)

### Fase 1 · Flujos núcleo (3–6 semanas)
- [ ] <…>

### Fase 2 · Estructura (6–10 semanas)
- [ ] <…>

### Cómo sabremos que funciona

| Métrica | Hoy (estimado) | Objetivo |
| --- | --- | --- |
| <Tiempo para dar de alta> | <7 pasos en 3 pantallas> | << 2 min en 1 pantalla> |
| <Pendientes con responsable> | <~0 %> | <100 %> |
| <Cifras contradictorias entre pantallas> | <≥ 4 casos> | <0> |
| <SUS con el equipo> | <Sin medir> | <≥ 80> |

Validación: test de usabilidad con <perfiles> y <N> tareas cronometradas, antes y después de la Fase 1.
```

---

## Comprobaciones antes de entregar

- Las cifras anunciadas en la introducción coinciden con las listas («18 arreglos rápidos» → 18 casillas).
- Cada P0 aparece en el plan de la Fase 0 o la Fase 1.
- Las referencias cruzadas (C1, T6, J4, «sección 8») apuntan a secciones que existen.
- Ningún dato personal real.
- El enlace al prototipo funciona y se avisa de que es privado hasta compartirlo.
