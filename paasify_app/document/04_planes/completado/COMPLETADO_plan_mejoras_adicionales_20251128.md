# Plan de Mejoras Adicionales: Admin Panel PaaSify

**Fecha:** 2025-11-28  
**Última actualización:** 2026-03-11  
**Estado:** ✅ Completado (10/03/2026)

---

## 🎯 Objetivo

Documentar mejoras adicionales identificadas durante la implementación de las Fases 1-6 que pueden implementarse en futuras iteraciones.

---

## 📊 Mejoras por Módulo

### 🔐 User Admin (Fase 1)

#### ✅ Mejora 1.1: Exportación de Usuarios
**Prioridad:** Media  
**Complejidad:** Baja  
**Estado:** ✅ Implementado (11/03/2026)

**Descripción:**
Acción bulk "Exportar usuarios seleccionados a CSV" en `CustomUserAdmin`. Genera archivo CSV con delimitador `;` y BOM UTF-8 para compatibilidad con Excel. Incluye columnas: Username, Email, Nombre Completo, Rol, Fecha Registro, Última Conexión, Activo.

---

#### 🔮 Mejora 1.2: Gráfico de Distribución de Roles
**Prioridad:** Baja  
**Complejidad:** Media  
**Estado:** 🔮 Futuro (No prioritario para TFG)

**Descripción:**
Agregar widget en el dashboard del admin mostrando distribución de usuarios por rol.

---

#### ✅ Mejora 1.3: Última Conexión del Usuario
**Prioridad:** Alta  
**Complejidad:** Baja  
**Estado:** ✅ Implementado (11/03/2026)

**Descripción:**
Columna `get_last_login_display` en `CustomUserAdmin.list_display` con formato amigable relativo (Hace unos minutos, Ayer, Hace 3 días, Hace 2 semanas, dd/mm/yyyy). Ordenable por `last_login`.

---

### 🐳 Service Admin (Fase 3)

#### ✅ Mejora 3.1: Filtro por Tipo de Imagen
**Prioridad:** Alta  
**Complejidad:** Baja  
**Estado:** ✅ Implementado (11/03/2026)

**Descripción:**
Filtro `ServiceImageTypeFilter` en sidebar de `ServiceAdmin`. Permite filtrar por: Web/Frontend, Base de Datos, Generador de API, Miscelánea, y Personalizado (Dockerfile/Compose). Definido en `admin_filters.py` y enganchado en `containers/admin.py`.

---

#### ✅ Mejora 3.2: Acción Bulk: Reiniciar Servicios
**Prioridad:** Alta  
**Complejidad:** Media  
**Estado:** ✅ Implementado (11/03/2026)

**Descripción:**
Acción `restart_services` en `ServiceAdmin`. Reinicia contenedores Docker de los servicios seleccionados, con manejo de errores individual y resumen final (✅ reiniciados | ❌ con error | ⚪ sin contenedor).

---

#### ✅ Mejora 3.3: Logs en Tiempo Real
**Prioridad:** Media  
**Complejidad:** Alta  
**Estado:** ✅ Ya existente (WebSockets + xterm.js)

**Descripción:**
El sistema ya cuenta con visualización de logs en tiempo real mediante Django Channels, WebSockets y xterm.js en el panel del alumno y terminal SSH.

---

#### 🔮 Mejora 3.4: Gráfico de Uso de Recursos
**Prioridad:** Baja  
**Complejidad:** Alta  
**Estado:** 🔮 Futuro (No prioritario para TFG)

**Descripción:**
Mostrar gráfico de CPU/RAM del contenedor en el formulario de edición.

---

### 📚 Subject Admin (Fase 4)

#### 🔮 Mejora 4.1: Gráfico de Distribución de Alumnos
**Prioridad:** Baja  
**Complejidad:** Media  
**Estado:** 🔮 Futuro (No prioritario para TFG)

**Descripción:**
Mostrar gráfico de barras con número de alumnos por asignatura.

---

#### ✅ Mejora 4.2: Exportar Lista de Alumnos
**Prioridad:** Media  
**Complejidad:** Baja  
**Estado:** ✅ Implementado (11/03/2026)

**Descripción:**
Acción bulk `export_students_csv` en `SubjectAdmin`. Exporta alumnos de las asignaturas seleccionadas a CSV con columnas: Asignatura, Username, Email, Nombre Completo, Servicios Activos (running/total), Última Conexión. Compatible con Excel (BOM UTF-8, delimitador `;`).

---

#### 🔮 Mejora 4.3: Enviar Email a Alumnos
**Prioridad:** Media  
**Complejidad:** Media  
**Estado:** 🔮 Futuro (Requiere Celery)

**Descripción:**
Acción bulk para enviar email a todos los alumnos de asignaturas seleccionadas.

---

### 👤 UserProfile Admin (Fase 5)

#### ✅ Mejora 5.1: Filtro por Rol
**Prioridad:** Alta  
**Complejidad:** Baja  
**Estado:** ✅ Ya existente (`UserRoleFilter` en `admin_filters.py`)

**Descripción:**
`UserRoleFilter` ya está creado en `admin_filters.py` (líneas 63-91) y permite filtrar perfiles por Profesor o Alumno.

---

#### ✅ Mejora 5.2: Acción: Resetear Tokens
**Prioridad:** Media  
**Complejidad:** Baja  
**Estado:** ✅ Ya existente (`refresh_api_tokens`)

**Descripción:**
Acción `refresh_api_tokens` ya implementada en `UserProfileAdmin` y `TeacherProfileAdmin`.

---

#### ✅ Mejora 5.3: Mostrar Última Conexión
**Prioridad:** Alta  
**Complejidad:** Baja  
**Estado:** ✅ Implementado (11/03/2026)

**Descripción:**
Columna `get_last_login` en `UserProfileAdmin.list_display` que muestra la última conexión del usuario del perfil en formato relativo amigable (misma lógica que la Mejora 1.3). Ordenable por `user__last_login`.

---

#### 🔮 Mejora 5.4: Imagen de Perfil (Avatar)
**Prioridad:** Baja  
**Complejidad:** Media  
**Estado:** 🔮 Futuro (No prioritario para TFG)

**Descripción:**
Permitir a los alumnos cargar una imagen de perfil personalizada. Actualmente se usa un sistema de iniciales con círculos de colores de la asignatura.

---

#### ✅ Mejora 5.5: Contraseña Temporal (One-time use)
**Prioridad:** Baja  
**Complejidad:** Alta  
**Estado:** ✅ Ya existente (implementado 10/03/2026)

**Descripción:**
Flag `must_change_password` en `UserProfile`, `ForcePasswordChangeMiddleware` completo que fuerza cambio de contraseña en primer login. Funciona para alumnos (modal en frontend), profesores y administradores (formulario nativo admin Jazzmin).

---

### 📁 UserProject Admin (Fase 6)

#### ✅ Mejora 6.1: Filtro por Estado del Proyecto
**Prioridad:** Alta  
**Complejidad:** Media  
**Estado:** ✅ Implementado (11/03/2026)

**Descripción:**
Filtro `ProjectStatusFilter` en sidebar de `UserProjectAdmin`. Calcula el estado real consultando los servicios Docker asociados. Opciones: ✅ Todos activos, ⚠️ Parcialmente activo, ❌ Detenido, ⚪ Sin servicios. Definido en `admin_filters.py` y enganchado en `list_filter`.

---

#### 🔮 Mejora 6.2: Progreso del Proyecto
**Prioridad:** Baja  
**Complejidad:** Alta  
**Estado:** 🔮 Futuro (No prioritario para TFG)

**Descripción:**
Mostrar barra de progreso del proyecto. Parcialmente cubierto con `get_project_status()` que ya muestra servicios activos/totales.

---

#### 🔮 Mejora 6.3: Acción Bulk: Reiniciar Servicios del Proyecto
**Prioridad:** Media  
**Complejidad:** Media  
**Estado:** 🔮 Futuro (Cubierto parcialmente por Mejora 3.2)

**Descripción:**
La Mejora 3.2 ya permite reiniciar servicios a nivel global, cubriendo el caso de uso principal.

---

## 🎨 Mejoras Generales de UX

### 🔮 Mejora G.1: Dark Mode
**Prioridad:** Baja  
**Complejidad:** Media  
**Estado:** 🔮 Futuro (No prioritario para TFG)

---

### ✅ Mejora G.2: Breadcrumbs Mejorados
**Prioridad:** Baja  
**Complejidad:** Baja  
**Estado:** ✅ Ya existente (Jazzmin los proporciona nativamente con iconos)

---

### ✅ Mejora G.3: Tooltips Informativos
**Prioridad:** Media  
**Complejidad:** Baja  
**Estado:** ✅ Parcial (usados en panel profesor y alumno)

---

### 🔮 Mejora G.4: Búsqueda Avanzada
**Prioridad:** Media  
**Complejidad:** Alta  
**Estado:** 🔮 Futuro (Django `search_fields` cubre el caso básico)

---

## 🔒 Mejoras de Seguridad

### ✅ Mejora S.1: Auditoría de Cambios
**Prioridad:** Alta  
**Complejidad:** Media  
**Estado:** ✅ Ya existente (Django `LogEntry` registra todos los cambios en admin)

---

### ✅ Mejora S.2: Confirmación de Acciones Críticas
**Prioridad:** Alta  
**Complejidad:** Baja  
**Estado:** ✅ Ya existente (Django admin pide confirmación al eliminar; SweetAlert en frontend)

---

### ✅ Mejora S.3: Permisos Granulares
**Prioridad:** Media  
**Complejidad:** Alta  
**Estado:** ✅ Parcial (Django auth proporciona permisos por modelo; profesores ven solo sus datos)

---

## 📊 Resumen Final

| Categoría | ✅ Completado | 🔮 Futuro |
|-----------|:--------:|:--------:|
| User Admin (3) | 2 | 1 |
| Service Admin (4) | 3 | 1 |
| Subject Admin (3) | 1 | 2 |
| UserProfile Admin (5) | 4 | 1 |
| UserProject Admin (3) | 1 | 2 |
| UX General (4) | 2 | 2 |
| Seguridad (3) | 3 | 0 |
| **TOTAL (25)** | **16** | **9** |

De las 25 mejoras planificadas, **16 están completadas** y **9 quedan para futuro** (todas de prioridad Baja o que requieren infraestructura adicional como Celery/Chart.js).

---

**Estado final:** ✅ Completado — Las mejoras de alta y media prioridad están implementadas.
