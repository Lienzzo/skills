# Fase 0 · Contexto del software

Cada software es distinto. Antes de auditar nada, reúne su contexto: **deduce todo lo que puedas** y **pregunta solo lo que falte**, en un único mensaje. No empieces a recorrer pantallas hasta tener al menos los campos marcados como imprescindibles.

## 1. Deduce primero (sin preguntar)

Si hay un repo abierto, léelo en 2–3 minutos:

| Dato | Dónde mirarlo |
|---|---|
| Qué es el producto y para quién | `README`, `AGENTS.md`, `CLAUDE.md`, `docs/`, landing en el repo |
| Stack y dónde vive la UI | `package.json`, estructura de `app/`, `src/`, `pages/`, `routes/` |
| Áreas y navegación | archivos de menú o navegación (`*navigation*`, `*sidebar*`, `*menu*`, `routes`) |
| Roles y permisos | enums o tablas de roles, middleware de autorización |
| Sistema de diseño y marca | `DESIGN.md`, tokens (`tailwind.config`, `theme`, `globals.css`), logo en `public/` |
| Contratos de UX | reglas en `AGENTS.md` o `CLAUDE.md` (p. ej. «sin IDs en la UI»), presupuesto de motion |
| URLs de entornos | `.env.example`, configuración de despliegue, README |
| Dolores reales | transcripciones, actas, feedback, issues, tickets en `docs/` o similar |
| Idioma de la interfaz | archivos de traducción y textos en los componentes |

Si el navegador ya tiene la app abierta, mira sus pestañas (en Claude in Chrome, `tabs_context_mcp`): muchas veces el usuario ya ha dejado la URL.

## 2. Pregunta lo que falte (un solo mensaje)

Presenta lo deducido como propuesta («He visto que… ¿es así?») y pide solo los huecos. Para decisiones cerradas (alcance, entregables, entorno) usa `AskUserQuestion`. Para URLs y descripciones, pídelas en texto.

**Imprescindibles:**
1. **Qué auditamos.** URL de la app (y de qué entorno), y la sección o el producto entero.
2. **Entorno y permisos.** ¿Es producción? Si lo es, el recorrido es de solo lectura. ¿Hay entorno de pruebas donde se pueda crear y enviar? Si hay que iniciar sesión, la sesión la abre el usuario: nunca escribas sus credenciales.
3. **Repo.** Ruta local o enlace, si no es el directorio actual.
4. **Usuarios.** Qué roles lo usan, qué hace cada uno a diario y **en qué pantallas pasan más horas**.
5. **El dolor.** Qué les ha llegado («los flujos se hacen complejos», «no encuentran X»…) y de quién.

**Útiles (si no se deducen):**
6. **Marca.** Color primario y acento, logo y tono («sin perder un toque de identidad»).
7. **Restricciones.** Sistema de diseño obligatorio, accesibilidad, dispositivos (escritorio o móvil), idiomas.
8. **Entregables.** Informe, prototipo visual, pulido de pantallas de uso intensivo o todo. Por defecto, todo.
9. **Fuentes extra.** Grabaciones, transcripciones, feedback, analítica de uso.
10. **Dónde guardar.** Carpeta del informe en el repo y si quiere un documento compartible.

Ejemplo de mensaje:

> Antes de empezar necesito el contexto. Esto es lo que he deducido del repo: <producto> para <usuarios>; el admin vive en `<ruta>`, tiene <N> entradas de menú y la marca usa <color>.
> Me falta:
> 1. La URL que quieres que recorra y si es producción (en ese caso, solo leo, no creo ni borro nada).
> 2. Qué roles lo usan a diario y en qué pantallas pasan más horas.
> 3. Qué problemas os han reportado.
> 4. ¿Quieres el paquete completo (informe, prototipo y pulido de las pantallas clave) o solo una parte?

Si el usuario ya dio parte del contexto en su petición, no se lo vuelvas a preguntar.

## 3. Deja el contexto por escrito

Guarda un brief corto. Si se puede escribir en el repo, en `<carpeta de documentación>/ux-brief-<área>.md`; si no, en una carpeta temporal. Lo usarás tú y se lo pasarás a cada subagente:

```markdown
# Brief UX · <producto / área> (<fecha>)
- Producto y propósito:
- URL y entorno (solo lectura: sí/no):
- Repo y rutas de la UI:
- Roles y tareas diarias:
- Pantallas de uso intensivo (hipótesis inicial):
- Dolores reportados y fuentes:
- Marca (primario, acento, logo, tono):
- Restricciones (sistema de diseño, a11y, dispositivos, idioma):
- Entregables acordados:
- Hoja de verdad del prototipo («ahora», personas, totales): se completa en la fase 3
```

## 4. Adapta el enfoque al tipo de producto

| Tipo | Ajuste |
|---|---|
| Back-office, CRM, admin, herramienta interna | Densidad Linear y el estándar de uso intensivo completo. Es el caso base. |
| SaaS para clientes | Igual, más onboarding, estados vacíos que enseñan y planes o límites visibles. |
| App móvil | Pulgar primero, acciones en la parte baja, gestos con alternativa visible. Tableros de 390×844. |
| Web pública o marketing | Más expresividad (motion de hasta unos 600 ms), con la misma disciplina antivibecoding y foco en la conversión. |
| Panel con datos o analítica | Una definición por métrica, cada número pulsable y explicado, y comparativas en una línea. |
