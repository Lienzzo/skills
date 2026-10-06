# Lenguaje visual «top tier» (Linear / v0)

Lo que hace que una interfaz se sienta como Linear o v0, y lo que la hace parecer «vibecoding». **Si el repo tiene su propio sistema de diseño (`DESIGN.md`, tokens, presupuesto de movimiento), ese manda.** Esto es el punto de partida cuando no hay nada o lo que hay es pobre.

## Índice
1. Principios
2. Tokens
3. Estructura de pantalla
4. Patrones de interacción
5. Componentes
6. Lista negra «vibecoding»
7. Identidad de marca
8. Movimiento
9. Microcopy

## 1. Principios

- **Densidad calmada.** Mucha información, poco ruido: grises neutros y un solo color de acción.
- **La tarea manda.** Cada pantalla responde «¿qué requiere acción?» antes que «¿qué hay?».
- **Nada se rompe sin aviso.** Estados de carga, vacío, error y éxito diseñados a propósito.
- **Teclado y ratón valen lo mismo.** Los atajos se ven en los botones.
- **El color significa algo:**
  - rojo para bloqueo o error;
  - naranja para fuera de plazo;
  - ámbar para atención;
  - verde para listo;
  - azul o violeta para categorías.
  Nunca decora.

## 2. Tokens

Declara los tokens en el tema claro y en el oscuro, y **usa siempre variables**, sin colores a fuego en los componentes, salvo el acento de marca. En la página HTML van en `:root` y `:root[data-theme="dark"]` (más `prefers-color-scheme`), como en `assets/prototype-template.html`; en el lienzo, en `.pp` y `.pp.dark`. Los valores son los mismos:

```css
.pp{--bg:#F6F6F7;--panel:#FFFFFF;--panel2:#FAFAFA;--border:#E4E4E7;--line:#EEEEF0;
--text:#18181B;--text2:#5E5E68;--text3:#8B8B95;--hover:#F4F4F5;--active:#EBEBED;--sel:#F0F1F8;
--primary:<COLOR_PRIMARIO_MARCA>;--primaryFg:#FFFFFF;--link:<COLOR_PRIMARIO_MARCA>;
--red:#E5484D;--orange:#F06A1D;--orangeText:#AE4A0E;--green:#30A46C;--amber:#E2A336;--blue:#3E63DD;--violet:#8E4EC6;
--kbd:#F4F4F5;--overlay:rgba(24,24,27,.24);--inv:#18181B;--invText:#FAFAFA;
--shadow:0 0 0 1px rgba(0,0,0,.04),0 4px 8px rgba(0,0,0,.04),0 24px 48px rgba(0,0,0,.10)}
.pp.dark{--bg:#0B0B0D;--panel:#121214;--panel2:#161618;--border:#252528;--line:#1C1C1F;
--text:#EDEDEF;--text2:#A0A0A8;--text3:#6E6E76;--hover:#1A1A1D;--active:#202024;--sel:#191C2C;
--primary:<PRIMARIO_CLARO_PARA_OSCURO>;--primaryFg:#0A0F2C;--link:<PRIMARIO_CLARO>;
--red:#F2555A;--orange:#FF8A3D;--orangeText:#FFAE78;--green:#3DD68C;--amber:#F0B44C;--blue:#7B9BFF;--violet:#B98AE6;
--kbd:#1F1F23;--overlay:rgba(0,0,0,.55);--inv:#EDEDEF;--invText:#0B0B0D;
--shadow:0 0 0 1px rgba(255,255,255,.06),0 24px 48px rgba(0,0,0,.6)}
.pp a{color:inherit}
.pp :focus-visible{outline:2px solid <PRIMARIO_SUAVE>;outline-offset:2px}
.pp .hov:hover{background:var(--hover) !important}
.pp .navitem:hover{background:var(--active) !important}
.pp button,.pp a{transition:background-color .12s ease-out,border-color .12s ease-out}
```

- **Tipografía:** Geist y Geist Mono (Google Fonts), o Inter y JetBrains Mono.
  - Cuerpo a 13 px con interlineado 1,5.
  - Secundario a 12 px.
  - Títulos de pantalla a 13 px y peso 500.
  - Títulos de vista lateral a 17 px y peso 600.
  - Cifras con `font-variant-numeric: tabular-nums`.
- **Radios:** 6 px en botones e inputs, 8 px en tarjetas y menús, 10 px en paneles.
- **Alturas:**
  - botones de 28 px (26 px en barras y 32 px para el primario de un formulario);
  - filas de 36–40 px;
  - cabeceras de grupo de 32 px;
  - cabecera de panel de 44 px.

## 3. Estructura de pantalla

```
┌──────────┬──────────────────────────────────────────────┐
│ Sidebar  │ ┌ panel (margin 8, radius 10, borde 1) ─────┐ │
│ 232 px   │ │ cabecera 44: título · pestañas · acciones  │ │
│          │ │ barra de filtros en píldora                │ │
│ búsqueda │ ├────────────────────────────┬──────────────┤ │
│ ⌘K       │ │ lista / tablero / hilo     │ vista lateral│ │
│ secciones│ │ (grupos con contador,      │ 300–380 px   │ │
│ vistas   │ │  «Mostrar N más»)          │              │ │
│ usuario  │ └────────────────────────────┴──────────────┘ │
└──────────┴──────────────────────────────────────────────┘
```

- **Barra lateral:**
  - logo y espacio de trabajo;
  - botón «+» de crear;
  - búsqueda «Buscar o preguntar… ⌘K», con el texto en una línea y cortado con elipsis;
  - entradas principales con contador;
  - grupos plegables;
  - vistas guardadas con punto de color;
  - usuario abajo.

  Pocas entradas, ordenadas por tarea.
- **Pestañas de sección** en la cabecera, con contador en `--text3`. La activa con fondo `--active` y peso 500.
- **Vista lateral (peek)** para ver y actuar sin salir de la lista. Un botón abre la página completa.

## 4. Patrones de interacción

- **Lista → vista lateral → página completa**, solo si el trabajo es profundo.
- **Filtros en píldora**: `Campo | es | valor ▾` y «+ Filtro».
- **Selección múltiple** con barra flotante abajo y al centro: «3 seleccionados · Acción · Acción · ×».
- **⌘K**: acciones, personas e «Ir a…».
- **Estado con iconos SVG pequeños**: círculo vacío, medio lleno, check o aviso. **Prioridad** con barras.
- **Aviso («toast») con «Deshacer»**: oscuro (`--inv`), abajo y al centro, durante 6 s. No debe tapar la zona de trabajo.
- **Atajos en `<kbd>`** dentro del propio botón: `Resolver E`, `Enviar ⌘⏎`.
- **Estados vacíos** con una frase, el resumen de lo hecho y la siguiente acción. Nada de ilustraciones grandes.

## 5. Componentes

- **Botón primario:** fondo `--primary`, texto `--primaryFg`, 28 px, peso 500, con un `<kbd>` opcional.
- **Botón secundario:** borde `--border`, fondo `--panel`.
- **Botón fantasma:** sin borde ni fondo, con la clase `hov`.
- **Insignia o etiqueta:** 20 px, radio 999, borde `--border`, punto de color de 6 px y texto `--text2`.
- **Avatar:** iniciales a 8,5–9 px dentro de un círculo de 18–20 px con un tono suave por persona.
- **Campo:** 28–32 px, borde `--border`, al enfocar contorno de 2 px en el primario suave.
- **Tabla:** cabecera a 12 px en `--text3` sin mayúsculas, filas con `border-bottom: 1px solid var(--line)` y la columna principal con `minmax(0,1fr)` y elipsis.

## 6. Lista negra «vibecoding»

Si aparece algo de esto, la pantalla deja de parecer Linear:

- tarjetas con un icono grande de color y un titular;
- banners de color a todo lo ancho («Bienvenido 👋»);
- emoji en la interfaz;
- degradados en botones, fondos o textos;
- antetítulos en mayúsculas con tracking ancho;
- titulares de 28 px o más dentro del producto;
- sombras gruesas en cada tarjeta;
- bordes de 2 px de color;
- botones «píldora» gigantes;
- cuadrículas de KPI con iconos;
- fondos decorativos («blobs», ruido);
- textos de marketing dentro de una herramienta de trabajo;
- más de un botón primario por zona.

Lo que sí:
- avisos en línea discretos, con un icono de 14 px y una frase en `--text`, sin fondo de color;
- KPI como «número + etiqueta + variación» en una línea;
- jerarquía con peso y color de texto, no con tamaño.

## 7. Identidad de marca

Un «pequeño toque»:
- el **color primario** de la marca en la acción principal y los enlaces;
- el **acento** de la marca (un amarillo, por ejemplo) solo en el logo y en la marca del asistente (por ejemplo, «✦»);
- el **nombre del asistente** con su avatar cuadrado de 16–18 px en los resúmenes y propuestas.

El resto, neutro.

## 8. Movimiento

- **Herramienta interna:** 200 ms o menos, `ease-out` o `linear`. Sin parallax, partículas ni animaciones de entrada «cinematográficas».
- **Aparición de popovers y avisos:** opacidad más `translateY(4px)` en 120–160 ms.
- **Respeta `prefers-reduced-motion`.**
- **Superficies de marca** (web pública, emails): hasta unos 600 ms, solo con justificación.

## 9. Microcopy

- En el idioma del usuario, sin jerga técnica.
- Verbos de acción en los botones («Crear sala», «Enviar enlace»), no «OK» ni «Submit».
- Cada error dice qué pasó y qué hacer.
- Cantidades con su plural correcto («1 entrega», «2 entregas»).
- Fechas y horas humanas («hace 2 d», «Hoy, 16:30»), coherentes con el «ahora» del prototipo.
