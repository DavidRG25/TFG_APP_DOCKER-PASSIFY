# Plan de Rediseño UI/UX - PaaSify

**Fecha de Creación:** 2025-12-13  
**Última Actualización:** 2025-12-13 20:59  
**Prioridad:** ALTA - Mejora de Experiencia de Usuario

---

## REFERENCIA VISUAL

**Maqueta de Diseño:** `uploaded_image_1765655953832.jpg`

Esta maqueta visual define la estética y estructura que debe seguir la aplicación. A continuación se analizan los elementos clave:

### Análisis de la Maqueta

#### 1. Login / Landing Page (Superior Izquierda)
**Elementos observados:**
- **Fondo:** Azul degradado (`#5B9FD8` → `#4A8BC2`)
- **Logo:** Icono de cubo 3D isométrico + texto "PaaSify" en blanco
- **Slogan:** Opciones sugeridas:
  - "Despliega. Aprende. Innova." (corto y directo)
  - "Tu plataforma de contenedores educativa" (descriptivo)
  - "Contenedores Docker simplificados" (técnico)
  - "Despliega contenedores en segundos" (beneficio claro)
- **Decoración:** Cubos 3D flotantes con líneas punteadas conectándolos
- **Modal de Login:** 
  - Fondo blanco flotante
  - Campos: Usuario, Contraseña
  - Botón azul "Entrar"
  - Diseño minimalista y limpio

**Conclusión:** Landing page con fondo azul vibrante, elementos 3D decorativos y formulario blanco flotante centrado.

---

#### 2. Vista General (Superior Derecha)
**Elementos observados:**
- **Topbar:** Azul (`#4A8BC2`) con logo pequeño, título "Vista General" y botón "Salir"
- **Sidebar:** Blanca con iconos de navegación
- **Contenido:**
  - **4 Cards de métricas** en fila superior:
    - CPU Usage (barra de progreso azul)
    - RAM Usage (número + barra)
    - CPU Usage (gráfico circular)
    - CPU Usage (número + barra)
  - Fondo blanco/gris muy claro
  - Tarjetas con sombras sutiles

**Conclusión:** Dashboard con métricas en cards horizontales, diseño limpio y espaciado.

---

#### 3. Nombre de Inicio (Inferior Izquierda)
**Elementos observados:**
- **Título:** "Nombre de Inicio"
- **Sección "Materias Rápida":**
  - 3 cards horizontales con información de materias
  - Cada card muestra: nombre, estado, progreso
  - Iconos circulares de colores
- **Sección "Formatos Iconos":**
  - Lista de items con iconos verdes (check) y rojos (X)
  - Badges de estado (azul)
- **Sección "Mis Tipos de Servicios":**
  - Cards con avatares circulares
  - Nombres y estados
  - Badges azules

**Conclusión:** Vista de inicio con múltiples secciones organizadas en cards, uso de iconos y badges para estados.

---

#### 4. Tests de Isópteros (Centro Derecha)
**Elementos observados:**
- **Título:** "Tests de Isópteros"
- **Sección "Nombre de Inicio":**
  - 3 tarjetas grandes con iconos tecnológicos:
    - **Pythouse:** Icono de engranaje negro
    - **Comitiva Fedora:** Icono de sombrero azul (Fedora)
    - **Raised clip:** Icono de herramientas azul
  - Cada tarjeta muestra:
    - Icono grande centrado
    - Nombre del servicio
    - Descripción breve
    - Badges de estado
    - Botones de acción (azul)

**Conclusión:** Grid de tarjetas grandes con iconos tecnológicos prominentes, similar a un catálogo de servicios.

---

#### 5. Vista el Alumno (Inferior Izquierda)
**Elementos observados:**
- **Título:** "Vista el Alumno"
- **Gráfico de barras:** Actividad o estadísticas
- **Sección "Recién desplegados":**
  - Lista de items con nombres
  - Badges de estado (verde, azul)
- **Sección "Avance Idealistas":**
  - Lista con avatares circulares
  - Nombres y acciones
  - Botón azul "Iniciar"

**Conclusión:** Vista con gráficos de actividad y listas de elementos recientes.

---

#### 6. Profesor Dashboard (Inferior Derecha)
**Elementos observados:**
- **Título:** "profesor /dashboard"
- **Sección "Asignaciones":**
  - Card con icono de cubo 3D grande (azul)
  - Nombre: "Secundarias"
  - Descripción
  - Botón azul "DETALLES"
- **Sección "Ver Detalles":**
  - Lista de asignaturas con iconos de personas (verde, amarillo)
  - Indicadores de estado (semáforos)
  - Badges azules
  - Botón "Ver Detalles"

**Conclusión:** Dashboard de profesor con cards de asignaturas y listas con semáforos de estado.

---

### Elementos Comunes Identificados

**Colores:**
- **Azul primario:** `#4A8BC2` a `#5B9FD8` (topbar, botones, acentos)
- **Blanco:** `#FFFFFF` (cards, fondos)
- **Gris claro:** `#F5F7FA` (fondo general)
- **Verde:** `#10B981` (estados positivos, iconos de check)
- **Rojo:** `#EF4444` (estados negativos, iconos de error)
- **Amarillo/Naranja:** `#F59E0B` (warnings)

**Componentes:**
- **Cards:** Blancas con sombras sutiles, bordes redondeados
- **Botones:** Azules con texto blanco, esquinas redondeadas
- **Badges:** Pequeños, colores según estado, texto blanco
- **Iconos:** Grandes y prominentes (cubos 3D, logos de tecnologías)
- **Topbar:** Azul con logo y título
- **Sidebar:** Blanca con iconos de navegación

**Tipografía:**
- Sans-serif moderna (similar a Inter o Roboto)
- Títulos en negrita
- Texto secundario en gris medio

---

## VISIÓN DE DISEÑO: "Light Tech con Acentos Azules"

### Filosofía
Interfaz **clara, limpia e intuitiva** orientada al entorno educativo y técnico. Basada en la maqueta visual proporcionada, con fondo azul para landing/topbar y contenido en blanco/gris claro. El diseño debe transmitir profesionalismo, simplicidad y facilitar la comprensión rápida de la información mediante iconos grandes y tarjetas visuales.

---

## FASE 2: REDISEÑO UI/UX

### 2.1 Sistema de Diseño "Light Tech" (Basado en Maqueta Visual)

**Paleta de Colores:**

**Fondos:**
- **Landing/Topbar:** Azul degradado `#5B9FD8` → `#4A8BC2`
- **Fondo General:** `#F5F7FA` (Gris muy claro, casi blanco)
- **Paneles/Tarjetas:** `#FFFFFF` (Blanco puro) con sombras sutiles
- **Sidebar:** `#FFFFFF` con borde derecho sutil

**Acentos:**
- **Primario:** `#4A8BC2` (Azul medio) - Topbar, botones principales
- **Primario Claro:** `#5B9FD8` (Azul claro) - Degradados, hover
- **Primario Hover:** `#3A7AB2` (Azul oscuro)
- **Éxito:** `#10b981` (Verde Emerald) - Estados positivos, checks
- **Error:** `#ef4444` (Rojo) - Errores, estados negativos
- **Warning:** `#f59e0b` (Amarillo/Naranja) - Advertencias
- **Info:** `#06b6d4` (Cyan) - Información adicional

**Tipografía:**
- **Principal:** `#0f172a` (Slate 900) - Negro/gris oscuro para alta legibilidad
- **Secundaria:** `#64748b` (Slate 500) - Gris medio para texto secundario
- **Blanco:** `#FFFFFF` - Texto sobre fondos azules (topbar, botones)
- **Fuente:** Inter o Roboto (Google Fonts)
- **Monospace:** Fira Code (para terminal y código)

**Sombras:**
- **Tarjetas:** `box-shadow: 0 2px 4px 0 rgba(0, 0, 0, 0.08), 0 1px 2px 0 rgba(0, 0, 0, 0.04);`
- **Hover:** `box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.12), 0 2px 4px 0 rgba(0, 0, 0, 0.06);`
- **Elevación:** Sombras sutiles y suaves, nunca agresivas

**Bordes:**
- **Color:** `#e2e8f0` (Slate 200) - Gris muy claro
- **Radius:** `0.5rem` (8px) para tarjetas, `0.375rem` (6px) para botones, `0.25rem` (4px) para inputs

**Degradados:**
- **Landing/Topbar:** `linear-gradient(135deg, #5B9FD8 0%, #4A8BC2 100%)`
- **Botones (opcional):** `linear-gradient(135deg, #4A8BC2 0%, #3A7AB2 100%)`

---

### 2.2 Componentes Clave

**Diseño de Componentes:**

**Botones:**
- **Primario:** Fondo azul (`#3b82f6`), texto blanco
- **Hover:** Cambio de color a azul más oscuro (`#2563eb`) + sombra suave
- **Secundario:** Fondo blanco, borde azul, texto azul
- **Peligro:** Fondo rojo (`#ef4444`), texto blanco
- **Sin efecto glow:** Usar transiciones de color y sombra suave

**Tarjetas:**
- Fondo blanco puro
- Bordes sutiles (`#e2e8f0`)
- Sombra suave (elevación)
- Padding generoso (16-24px)
- Border-radius de 6px

**Tablas:**
- Header con fondo gris muy claro (`#f8fafc`)
- Filas alternadas (zebra striping) con `#f9fafb`
- Transformar a Card Grids en móvil

**Terminal:**
- **Excepción al tema claro:** Mantener fondo negro puro (`#000000`)
- Modal fullscreen o drawer lateral
- Fuente Fira Code con ligaduras
- Tema de colores verde neón sobre negro (estilo terminal clásico)

**Inputs:**
- Fondo blanco
- Borde gris claro (`#e2e8f0`)
- Focus: Borde azul (`#3b82f6`) + sombra azul suave
- Floating labels opcionales
- Estados claros (focus, error, success)

**Iconos:**
- Font Awesome 6 (ya integrado)
- Color primario: Azul (`#3b82f6`)
- Tamaño consistente (16px, 20px, 24px)
- Uso generoso para mejorar escaneo visual

**Badges:**
- Fondo con color del estado (verde, rojo, amarillo) al 10% de opacidad
- Texto con color del estado al 100%
- Border-radius de 4px
- Padding: 4px 8px

---

### 2.3 Estructura Base: SB Admin

**Layout Principal:**

```
┌─────────────────────────────────────────────┐
│  Topbar (Header)                            │
│  - Logo + Nombre de la app                  │
│  - Búsqueda (opcional)                      │
│  - Usuario + Notificaciones + Dropdown      │
├──────────┬──────────────────────────────────┤
│          │                                  │
│ Sidebar  │  Área de Contenido               │
│          │  - Breadcrumbs                   │
│ - Nav    │  - Título de página              │
│ - Links  │  - Contenido principal           │
│          │                                  │
│          │                                  │
└──────────┴──────────────────────────────────┘
```

**Topbar:**
- **Fondo:** Azul degradado `linear-gradient(90deg, #4A8BC2 0%, #5B9FD8 100%)`
- **Altura:** 56-60px
- **Logo:** Icono pequeño + texto "PaaSify" (blanco)
- **Título de página:** Centro o izquierda (blanco)
- **Botón "Salir":** Derecha, fondo blanco/transparente, texto blanco
- **Usuario y notificaciones:** Derecha (iconos blancos)
- **Sombra:** Sombra inferior sutil para separar del contenido

**Sidebar:**
- **Fondo:** Blanco
- **Ancho:** 60-80px (solo iconos), expandible a 240px (con texto)
- **Items:** Iconos Font Awesome centrados
- **Hover:** Fondo azul claro (`#E3F2FD`)
- **Item activo:** Fondo azul (`#4A8BC2`), icono blanco
- **Colapsable:** Hamburger menu en móvil

**Área de Contenido:**
- Fondo gris muy suave (`#f8fafc`)
- Padding: 24px
- Contenedores blancos flotantes con sombra

---

### 2.4 Vistas Principales

#### Login (`login.html`) - Basado en Maqueta Visual

**Estructura:**
Pantalla completa con fondo azul degradado

**Fondo Azul Degradado:**
- Degradado: `linear-gradient(135deg, #5B9FD8 0%, #4A8BC2 100%)`
- Altura: 100vh (pantalla completa)

**Elementos Decorativos:**

**Opción 1: Cubos 3D Isométricos (Recomendado - Relacionado con Docker)**
- **Concepto:** Cubos 3D flotantes que representan contenedores Docker
- **Colores:** Tonos de azul (`#4A8BC2`, `#5B9FD8`, `#3A7AB2`)
- **Distribución:** Dispersos por el fondo, diferentes tamaños
- **Conexiones:** Líneas punteadas conectando algunos cubos (efecto de red)
- **Animación:** Movimiento sutil flotante (translate Y lento)
- **Implementación:** CSS + SVG
- **Asset generado:** `login_background_pattern.png` (referencia visual)

**Opción 2: Patrón Geométrico Abstracto**
- **Concepto:** Formas geométricas (hexágonos, triángulos) en degradado
- **Estilo:** Minimalista, moderno
- **Opacidad:** Muy sutil (10-20%)
- **Implementación:** CSS background-image

**Opción 3: Partículas Flotantes**
- **Concepto:** Pequeños puntos o círculos flotando
- **Efecto:** Similar a estrellas o nieve suave
- **Implementación:** JavaScript (particles.js) o CSS

**Opción 4: Sin Decoración (Minimalista)**
- **Concepto:** Solo degradado azul limpio
- **Ventaja:** Más rápido de cargar, más limpio
- **Desventaja:** Menos visual

**Recomendación:** Opción 1 (Cubos 3D) por su relación directa con Docker y contenedores.

**Logo y Branding (Centro Superior):**
- **Logo:** Icono de cubo 3D isométrico (azul más oscuro o blanco)
- **Texto "PaaSify":** Blanco, fuente grande y bold
- **Slogan:** "Despliega. Aprende. Innova." o "Tu plataforma de contenedores educativa" (blanco, fuente más pequeña)
- **Posición:** Centro horizontal, tercio superior vertical

**Modal/Card de Login (Centro):**
- **Fondo:** Blanco puro (`#FFFFFF`)
- **Posición:** Centrado vertical y horizontalmente
- **Tamaño:** ~400px ancho, altura automática
- **Sombra:** Sombra suave y elevada
- **Border-radius:** 8px

**Contenido del Modal:**
1. **Título:** "Iniciar Sesión" (opcional, puede omitirse si el diseño es minimalista)
2. **Campo Usuario:**
   - Placeholder: "Usuario"
   - Icono: Persona (izquierda del input)
   - Borde gris claro, focus azul
3. **Campo Contraseña:**
   - Placeholder: "Contraseña"
   - Icono: Candado (izquierda del input)
   - Borde gris claro, focus azul
4. **Botón "Entrar":**
   - Fondo azul (`#4A8BC2`)
   - Texto blanco
   - Ancho completo
   - Border-radius: 6px
   - Hover: Azul más oscuro (`#3A7AB2`)
5. **Link "¿Olvidaste tu contraseña?":**
   - Debajo del botón
   - Texto azul, pequeño
   - Centrado

**Toast Notifications:**
- Posición: Esquina superior derecha
- Colores según tipo (error=rojo, éxito=verde)
- Auto-dismiss: 5 segundos
- No desplazan contenido

**Responsive:**
- **Desktop (>1024px):** Modal centrado en pantalla azul
- **Tablet (768px-1024px):** Modal centrado, ligeramente más ancho
- **Móvil (<768px):** 
  - Modal ocupa 90% del ancho
  - Logo y slogan más pequeños
  - Mantener fondo azul degradado

**Diferencia con diseño anterior:**
- **Antes:** Pantalla dividida 50/50 (branding izquierda, formulario derecha)
- **Ahora:** Fondo azul completo con modal blanco centrado (más moderno y limpio)

---

#### Dashboard Alumno (`student_panel.html`)

**Estructura Base:** SB Admin

**Topbar:**
- Logo + "PaaSify"
- Saludo: "Hola, [Nombre] 👋" (centrado o derecha)
- Icono de usuario + dropdown

**Sidebar:**
- Inicio (activo)
- Mis Servicios
- Nueva Imagen
- Nuevo Código
- Ayuda

**Área de Contenido:**

**1. Header con Métricas (Cards Row):**
```
┌──────────┬──────────┬──────────┬──────────┐
│ CPU      │ RAM      │ Servicios│ Storage  │
│ 45%      │ 2.1 GB   │ 3 activos│ 1.2 GB   │
│ [Barra]  │ [Barra]  │ [Número] │ [Barra]  │
└──────────┴──────────┴──────────┴──────────┘
```
- 4 tarjetas blancas con sombra
- Icono grande a la izquierda (azul)
- Valor destacado (número grande)
- Barra de progreso o indicador visual
- Responsive: 2x2 en tablet, 1 columna en móvil

**2. Grid de Servicios (Tarjetas Grandes):**

Cada tarjeta representa un servicio/contenedor:

```
┌─────────────────────────────────┐
│  [Icono Grande]  Nombre Servicio│
│  Node.js                        │
│                                 │
│  Estado: 🟢 Running             │
│  Puerto: 44454 [Abrir]          │
│  Asignatura: [Badge]            │
│                                 │
│  [Terminal] [Logs] [⏸️] [🗑️]    │
└─────────────────────────────────┘
```

**Características:**
- **Icono grande:** Detección automática (Node.js, Python, Nginx, Docker)
  - Node.js: Logo verde
  - Python: Logo azul/amarillo
  - Nginx: Logo verde
  - Docker: Logo azul
  - Genérico: Icono de cubo
- **Estado:** Badge con color (verde=running, rojo=stopped, amarillo=building)
- **Puerto:** Enlace clicable que abre en nueva pestaña
- **Asignatura:** Badge azul con nombre
- **Botones de acción:** Iconos grandes, tooltips en hover
  - Terminal: Abre modal fullscreen
  - Logs: Abre modal con logs
  - Parar/Reiniciar: Acción directa con confirmación
  - Eliminar: Confirmación obligatoria

**Grid:**
- 3 columnas en desktop (1200px+)
- 2 columnas en tablet (768px-1199px)
- 1 columna en móvil (<768px)
- Gap de 24px entre tarjetas

**3. Botón Flotante "Nuevo Servicio":**
- Botón azul grande en esquina inferior derecha
- Icono de "+" grande
- Abre drawer lateral (no modal)

**Wizard de Creación (Drawer Lateral):**
- Desliza desde la derecha
- Ancho: 480px (desktop), fullscreen (móvil)
- Fondo blanco
- 3 pasos con indicador de progreso en la parte superior

**Paso 1: Asignatura**
- Selector visual de asignaturas (tarjetas pequeñas)
- Cada tarjeta con icono y nombre

**Paso 2: Tipo de Servicio**
- Dos opciones grandes:
  - "Desde Imagen Docker" (icono de Docker)
  - "Desde Código Fuente" (icono de código)

**Paso 3: Configuración**
- Formulario con campos relevantes:
  - Nombre del servicio
  - Imagen/Archivo (según tipo)
  - Puerto interno (opcional, con valor por defecto)
  - Variables de entorno (expandible, opcional)
- Botón "Crear Servicio" azul, grande

---

#### Dashboard Profesor

**Estructura Base:** SB Admin

**Topbar:**
- Logo + "PaaSify"
- Saludo: "Hola, Profesor [Nombre]"
- Icono de usuario + dropdown

**Sidebar:**
- Inicio (activo)
- Mis Asignaturas
- Alumnos
- Estadísticas
- Configuración

**Área de Contenido:**

**1. Vista General (Página Principal):**

**Métricas Globales (Cards Row):**
```
┌──────────┬──────────┬──────────┬──────────┐
│ Alumnos  │ Servicios│ CPU Total│ RAM Total│
│ 45       │ 123      │ 65%      │ 45 GB    │
└──────────┴──────────┴──────────┴──────────┘
```

**Gráficos de Actividad:**
- Gráfico de barras: Servicios activos por asignatura
- Gráfico de líneas: Actividad en los últimos 7 días
- Librería: Chart.js o similar
- Colores consistentes con paleta (azul primario)

**2. Gestión de Asignaturas (Grid de Tarjetas):**

Cada tarjeta representa una asignatura:

```
┌─────────────────────────────────┐
│  [Imagen de fondo sutil]        │
│                                 │
│  Asignatura 1                   │
│                                 │
│  👥 25 alumnos                  │
│  🐳 45 servicios (38 activos)   │
│  📦 12 proyectos entregados     │
│                                 │
│  [Ver Detalles →]               │
└─────────────────────────────────┘
```

**Características:**
- Imagen de fondo relacionada con la asignatura (opcional, muy sutil)
- Nombre de la asignatura destacado
- Indicadores con iconos
- Botón "Ver Detalles" que lleva a vista de detalle

**Grid:**
- 2 columnas en desktop
- 1 columna en tablet/móvil
- Gap de 24px

**3. Vista de Detalle de Asignatura:**

**Header:**
- Breadcrumbs: Inicio > Asignaturas > [Nombre]
- Título: Nombre de la asignatura
- Botón "Volver"

**Lista de Alumnos (Tabla):**

```
┌──────────────┬─────────┬────────────┬────────────┐
│ Alumno       │ Estado  │ Servicios  │ Actividad  │
├──────────────┼─────────┼────────────┼────────────┤
│ Juan Pérez   │ 🟢 OK   │ 3 (3/3)    │ Hace 2h    │
│ María García │ 🟡 Warn │ 2 (1/2)    │ Hace 1d    │
│ Pedro López  │ 🔴 Error│ 1 (0/1)    │ Hace 3d    │
└──────────────┴─────────┴────────────┴────────────┘
```

**Semáforos de Estado:**
- 🟢 Verde: Todos los servicios running
- 🟡 Amarillo: Algunos servicios stopped o con problemas
- 🔴 Rojo: Todos los servicios stopped o errores críticos

**Vista Expandible:**
- Click en fila expande inline mostrando servicios del alumno
- Misma visualización que en dashboard de alumno (tarjetas pequeñas)

---

## Microinteracciones y Animaciones

**Transiciones:**
- Duración: 200-300ms
- Easing: `ease-in-out`
- Aplicar a: color, background-color, transform, box-shadow

**Hover en Tarjetas:**
- Elevación: Aumentar sombra sutilmente
- Transform: `translateY(-2px)` (levitar ligeramente)
- Sin cambio de color de fondo

**Hover en Botones:**
- Cambio de color de fondo (azul más oscuro)
- Sombra suave
- Sin glow (eliminar efecto de brillo)

**Loading States:**
- Skeleton screens (placeholders grises pulsantes)
- Spinners azules cuando sea necesario
- Nunca bloquear toda la UI

**Estados de Servicio:**
- Running: Punto verde pulsante (animación de pulso)
- Building: Spinner amarillo girando
- Stopped: Punto rojo estático
- Error: Icono de exclamación rojo

**Toasts/Notificaciones:**
- Slide in desde arriba derecha
- Auto-dismiss después de 5 segundos
- Colores según tipo (éxito=verde, error=rojo, info=azul)

---

## SPRINT ÚNICO: IMPLEMENTACIÓN COMPLETA UI/UX (4 semanas)

### Semana 1: Setup y Base Template

**Días 1-2: Setup y Sistema de Diseño**

**Decisión de Framework CSS:**

**Opción 1: Tailwind CSS** ⭐ (Recomendado)
- **Ventajas:**
  - Utility-first, muy flexible
  - Fácil personalización de colores
  - Purge CSS automático (solo incluye clases usadas)
  - Excelente para responsive
  - Documentación extensa
- **Instalación:**
  ```bash
  npm install -D tailwindcss
  npx tailwindcss init
  ```
- **Configuración:** Personalizar `tailwind.config.js` con paleta de colores

**Opción 2: Bootstrap 5** (Si ya está en el proyecto)
- **Ventajas:**
  - Ya puede estar integrado
  - Componentes predefinidos (modals, dropdowns, etc.)
  - Grid system robusto
  - Iconos de Bootstrap Icons disponibles
- **Uso:**
  - Mantener Bootstrap para componentes complejos (modals, tooltips)
  - Personalizar variables SCSS para colores
  - Complementar con CSS custom para diseño específico
- **Recursos adicionales:**
  - Traer assets de Bootstrap según necesidad (JS plugins, iconos)
  - Usar componentes de SB Admin (si es compatible)

**Opción 3: CSS Custom + Variables**
- **Ventajas:**
  - Control total
  - Sin dependencias externas
  - Más ligero
- **Desventajas:**
  - Más trabajo manual
  - Menos componentes predefinidos

**Recomendación Final:**
- **Si el proyecto ya usa Bootstrap:** Mantenerlo y personalizarlo
- **Si es nuevo o se puede migrar:** Usar Tailwind CSS
- **Híbrido:** Bootstrap para componentes complejos + Tailwind para utilidades

**Tareas:**
- [ ] Decidir framework CSS (Tailwind vs Bootstrap vs Custom)
- [ ] Instalar y configurar framework elegido
- [ ] Definir paleta de colores en código (variables CSS o config)
- [ ] Configurar fuentes (Google Fonts: Inter)
- [ ] Crear archivo de variables CSS/Tailwind config
- [ ] Documentar sistema de diseño
- [ ] Si se usa Bootstrap: Identificar assets necesarios (JS, iconos, plugins)

**Días 3-4: Base Template (SB Admin)**
- [ ] Crear `base.html` con estructura SB Admin:
  - Topbar (header) con degradado azul
  - Sidebar de navegación blanca
  - Área de contenido
  - Footer (opcional)
- [ ] Implementar responsive (sidebar colapsable)
- [ ] Hamburger menu en móvil
- [ ] Dropdown de usuario

**Días 5-7: Componentes Base**
- [ ] Sistema de toasts/notificaciones
- [ ] Componentes de botones (primario, secundario, peligro)
- [ ] Componentes de tarjetas
- [ ] Componentes de badges
- [ ] Inputs con estados (focus, error, success)
- [ ] Documentar componentes (Storybook opcional)

---

### Semana 2: Login y Dashboard Alumno

**Días 1-2: Login**
- [ ] Fondo azul degradado completo (100vh)
- [ ] Logo y slogan centrados arriba
- [ ] Elementos decorativos (cubos 3D, opcional)
- [ ] Modal/card de login blanco centrado
- [ ] Inputs con iconos (usuario, contraseña)
- [ ] Botón azul ancho completo
- [ ] Toast notifications para errores
- [ ] Responsive (modal adaptable)

**Días 3-5: Dashboard Alumno - Estructura**
- [ ] Implementar layout SB Admin
- [ ] Topbar azul con saludo personalizado
- [ ] Sidebar blanca con navegación
- [ ] Header con 4 tarjetas de métricas (CPU, RAM, Servicios, Storage)
- [ ] Integrar datos reales desde backend

**Días 6-7: Dashboard Alumno - Grid de Servicios**
- [ ] Grid responsivo de tarjetas (3 cols desktop, 2 tablet, 1 móvil)
- [ ] Tarjeta de servicio con icono grande
- [ ] Detección automática de iconos (Node, Python, Nginx, Docker)
- [ ] Estados visuales (running, stopped, building)
- [ ] Botones de acción (terminal, logs, parar, eliminar)
- [ ] Botón flotante "Nuevo Servicio"

---

### Semana 3: Wizard, Dashboard Profesor y Terminal

**Días 1-3: Wizard de Creación**
- [ ] Drawer lateral deslizante desde derecha
- [ ] Indicador de progreso (3 pasos)
- [ ] Paso 1: Selector de asignatura (tarjetas visuales)
- [ ] Paso 2: Tipo de servicio (Imagen vs Código)
- [ ] Paso 3: Configuración (formulario con validación)
- [ ] Integración con backend
- [ ] Animaciones de transición entre pasos

**Días 4-5: Dashboard Profesor**
- [ ] Vista general con métricas globales (4 cards)
- [ ] Gráficos de actividad (Chart.js)
  - Barras: Servicios por asignatura
  - Líneas: Actividad últimos 7 días
- [ ] Grid de tarjetas de asignaturas (2 cols)
- [ ] Vista de detalle de asignatura
- [ ] Tabla de alumnos con semáforos de estado
- [ ] Vista expandible de servicios por alumno

**Días 6-7: Terminal Mejorada**
- [ ] Modal fullscreen (no drawer)
- [ ] Fondo negro puro (`#000000`)
- [ ] Fuente Fira Code con ligaduras
- [ ] Tema verde neón sobre negro
- [ ] Botones: Copiar, Limpiar, Cerrar
- [ ] Shortcuts de teclado (Ctrl+L limpiar, Esc cerrar)
- [ ] 100% altura disponible
- [ ] Indicador de conexión WebSocket

---

### Semana 4: Polish, Testing y Documentación

**Días 1-2: Animaciones y Microinteracciones**
- [ ] Transiciones suaves en todos los componentes (200-300ms)
- [ ] Hover states en tarjetas y botones
- [ ] Loading skeletons para carga de datos
- [ ] Punto pulsante para estado "running"
- [ ] Animaciones de entrada para modales/drawers
- [ ] Performance optimizado (60fps)

**Días 3-4: Testing Final**
- [ ] Tests de usabilidad con 5+ usuarios reales (alumnos y profesores)
- [ ] Tests responsivos (móvil, tablet, desktop)
- [ ] Tests de accesibilidad (navegación por teclado, screen readers)
- [ ] Performance (Lighthouse > 90)
- [ ] Contraste de colores (WCAG 2.1 AA)
- [ ] Corrección de bugs encontrados

**Días 5-7: Documentación y Entrega**
- [ ] Documentar componentes reutilizables
- [ ] Crear guía de estilos (style guide)
- [ ] Documentar paleta de colores y tipografía
- [ ] Screenshots de todas las vistas
- [ ] Video demo de la aplicación
- [ ] Actualizar README con nuevas features
- [ ] Preparar presentación de resultados

---

## CRITERIOS DE ACEPTACIÓN

**UI/UX:**
- [ ] Tema claro aplicado en todas las vistas (excepto terminal)
- [ ] Paleta de colores "Light Tech" consistente
- [ ] Acentos azules (`#3b82f6`) en botones, enlaces y elementos interactivos
- [ ] Responsive en móvil, tablet y desktop
- [ ] Wizard de creación funcional y usable
- [ ] Terminal fullscreen con tema oscuro personalizado
- [ ] Componentes reutilizables documentados
- [ ] Tipografía correcta (Inter + Fira Code)
- [ ] Iconos grandes y visuales en tarjetas de servicios

**Estructura:**
- [ ] Layout basado en SB Admin (topbar + sidebar + contenido)
- [ ] Login con pantalla dividida
- [ ] Dashboard alumno con grid de tarjetas grandes
- [ ] Dashboard profesor con gráficos y semáforos

**Performance:**
- [ ] Lighthouse Performance > 90
- [ ] Lighthouse Accessibility > 90
- [ ] Tiempo de carga < 3 segundos
- [ ] Animaciones a 60fps
- [ ] Sin jank en scroll

**Usabilidad:**
- [ ] Tests con 5+ usuarios reales (alumnos y profesores)
- [ ] NPS (Net Promoter Score) > 50
- [ ] Reducción del 30% en tiempo de completar tareas
- [ ] 0 errores críticos de usabilidad
- [ ] Feedback positivo sobre claridad visual

**Accesibilidad:**
- [ ] WCAG 2.1 AA cumplido
- [ ] Contraste de colores > 4.5:1 (texto sobre fondo)
- [ ] Navegación por teclado funcional
- [ ] Screen readers compatibles
- [ ] Focus states visibles

---

## NOTAS IMPORTANTES

### Principios de Diseño
- **Claridad sobre complejidad:** Priorizar información clara y escaneable
- **Consistencia:** Mismo patrón de diseño en todas las vistas
- **Feedback inmediato:** Usuario siempre sabe qué está pasando
- **Jerarquía visual:** Elementos importantes destacados (tamaño, color, posición)

### Consideraciones Técnicas
- **Tailwind CSS recomendado:** Facilita implementación rápida y consistente
- **SB Admin como base:** Aprovechar estructura probada y responsive
- **Iconos grandes:** Mejorar escaneo visual y comprensión rápida
- **Sin glow effects:** Usar sombras sutiles y cambios de color

### Testing y Validación
- Testing continuo con usuarios reales (alumnos y profesores)
- Iterar basado en feedback
- Documentar componentes para mantenimiento
- Mantener performance alto (no sacrificar por animaciones)
- Validar accesibilidad en cada componente

### Referencias Visuales
- **Inspiración:** GitHub (modo claro), VS Code (tema claro), SB Admin
- **Paleta:** Colores suaves, acentos azules vibrantes
- **Tipografía:** Clara, legible, profesional
- **Espaciado:** Generoso, respirable, no apretado

---

## RECURSOS EXTERNOS Y FRAMEWORKS

### Bootstrap 5 (Si se usa)

**Componentes útiles de Bootstrap:**
- **Modals:** Para terminal, logs, confirmaciones
- **Dropdowns:** Menú de usuario, filtros
- **Tooltips:** Información adicional en hover
- **Toasts:** Notificaciones temporales
- **Progress bars:** Barras de progreso para CPU/RAM
- **Badges:** Estados de servicios
- **Cards:** Contenedores de información
- **Grid system:** Layout responsive

**Assets de Bootstrap a traer:**
```html
<!-- CSS -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

<!-- JS Bundle (incluye Popper) -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

<!-- Bootstrap Icons (opcional) -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
```

**Personalización de Bootstrap:**
```scss
// Sobrescribir variables de Bootstrap
$primary: #4A8BC2;
$success: #10b981;
$danger: #ef4444;
$warning: #f59e0b;

@import "bootstrap/scss/bootstrap";
```

---

### SB Admin (Plantilla de referencia)

**Recursos de SB Admin:**
- **Repositorio:** [https://github.com/StartBootstrap/startbootstrap-sb-admin-2](https://github.com/StartBootstrap/startbootstrap-sb-admin-2)
- **Demo:** [https://startbootstrap.com/theme/sb-admin-2](https://startbootstrap.com/theme/sb-admin-2)

**Componentes reutilizables:**
- Layout de topbar + sidebar
- Cards de métricas
- Tablas responsivas
- Gráficos con Chart.js
- Dropdown de usuario

**Assets a considerar:**
- `sb-admin-2.css` (personalizar colores)
- `sb-admin-2.js` (funcionalidad de sidebar)
- Estructura HTML de componentes

---

### Otras Librerías Útiles

**Chart.js** (Para gráficos del dashboard de profesor)
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
```

**Font Awesome 6** (Ya integrado, pero confirmar versión)
```html
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
```

**Google Fonts**
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
```

---

### Decisión de Stack Tecnológico

**Opción Recomendada (Híbrida):**
- **Bootstrap 5:** Para componentes complejos (modals, dropdowns, tooltips)
- **Tailwind CSS:** Para utilidades y diseño custom
- **CSS Custom:** Para animaciones y estilos específicos
- **Chart.js:** Para gráficos
- **Font Awesome:** Para iconos

**Ventajas del enfoque híbrido:**
- Aprovechar componentes robustos de Bootstrap
- Flexibilidad de Tailwind para diseño custom
- No reinventar la rueda
- Mejor productividad

**Nota:** Si Bootstrap ya está en el proyecto, mantenerlo y complementar con Tailwind o CSS custom según necesidad.

---

## ASSETS VISUALES GENERADOS

Para facilitar la implementación del diseño, se han generado y guardado los siguientes assets visuales en `paasify/static/assets/img/`:

### Fondos para Login (3 opciones)

**1. login_background_containers.png** ⭐ (Recomendado)
- **Descripción:** Cubos 3D isométricos como elemento principal, ballena Docker muy sutil en el fondo
- **Uso:** Fondo decorativo para página de login
- **Estilo:** Minimalista, enfocado en contenedores
- **Ubicación:** `paasify/static/assets/img/login_background_containers.png`

**2. login_background_pattern.png**
- **Descripción:** Patrón geométrico de cubos 3D en tonos azules
- **Uso:** Alternativa de fondo para login
- **Estilo:** Más abstracto y geométrico
- **Ubicación:** `paasify/static/assets/img/login_background_pattern.png`

**3. login_background_docker.png**
- **Descripción:** Ballenas Docker sutiles con contenedores
- **Uso:** Opción con más presencia de Docker (si se desea)
- **Estilo:** Más relacionado directamente con Docker
- **Ubicación:** `paasify/static/assets/img/login_background_docker.png`

---

### Logos e Iconos

**4. paasify_logo_icon.png**
- **Descripción:** Icono de cubo 3D isométrico en azul
- **Uso:** Logo/icono principal de la aplicación
- **Tamaño:** 512x512px
- **Formatos sugeridos:** Convertir a SVG para mejor escalabilidad
- **Ubicación:** `paasify/static/assets/img/paasify_logo_icon.png`

**5. docker_whale_icon.png**
- **Descripción:** Icono minimalista de ballena Docker en azul
- **Uso:** Elemento decorativo secundario, icono de Docker
- **Nota:** Usar con moderación, no como elemento principal
- **Ubicación:** `paasify/static/assets/img/docker_whale_icon.png`

---

### Ilustraciones

**6. hero_illustration_containers.png**
- **Descripción:** Stack de contenedores con flechas de despliegue
- **Uso:** Hero section, landing page, o header de dashboard
- **Estilo:** Flat design, profesional
- **Ubicación:** `paasify/static/assets/img/hero_illustration_containers.png`

**7. empty_state_illustration.png**
- **Descripción:** Ilustración amigable para estado vacío (sin servicios)
- **Uso:** Cuando el alumno no tiene servicios desplegados
- **Mensaje:** "No hay servicios desplegados aún" (agregar texto en HTML)
- **Ubicación:** `paasify/static/assets/img/empty_state_illustration.png`

---

### Iconos de UI

**8. service_card_icons.png**
- **Descripción:** Set de iconos de tecnologías (Node.js, Python, Nginx, Docker)
- **Uso:** Referencia para tarjetas de servicios
- **Nota:** En producción, usar logos oficiales de cada tecnología
- **Ubicación:** `paasify/static/assets/img/service_card_icons.png`

**9. service_status_icons.png**
- **Descripción:** Iconos de estado (running, stopped, building)
- **Uso:** Indicadores de estado de servicios
- **Colores:** Verde (running), Rojo (stopped), Amarillo (building)
- **Ubicación:** `paasify/static/assets/img/service_status_icons.png`

---

### Logo Existente

**10. logo.png** (Original del proyecto)
- **Descripción:** Logo actual de PaaSify
- **Tamaño:** 47KB
- **Ubicación:** `paasify/static/assets/img/logo.png`

---

## Notas sobre staticfiles

**Directorio `staticfiles/`:**
- Es generado automáticamente por Django con `python manage.py collectstatic`
- Recopila todos los archivos estáticos de todas las apps para producción
- **NO editar archivos aquí directamente**
- Siempre editar en `paasify/static/` y luego ejecutar `collectstatic`
- Archivo obsoleto `images.jpg` eliminado ✅

---

### Próximos Assets a Crear

**Para Sprint 2:**
- [ ] Logo completo (icono + texto "PaaSify") en SVG
- [ ] Favicon en múltiples tamaños (16x16, 32x32, 180x180, 512x512)
- [ ] Iconos de navegación para sidebar en SVG
- [ ] Convertir `paasify_logo_icon.png` a SVG vectorial

**Para Sprint 3:**
- [ ] Gráficos de ejemplo para dashboard de profesor (Chart.js templates)
- [ ] Ilustraciones para cada paso del wizard de creación
- [ ] Iconos animados de estado (CSS animations)
- [ ] Imágenes de fondo sutiles para cards de asignaturas

---

**Plan actualizado:** 2025-12-13 21:16  
**Versión:** 3.0 - Sprint Único + Recursos Bootstrap + 9 Assets Visuales  
**Duración:** 4 semanas (1 sprint consolidado)  
**Próxima revisión:** Al finalizar Semana 2 (mitad del sprint)
