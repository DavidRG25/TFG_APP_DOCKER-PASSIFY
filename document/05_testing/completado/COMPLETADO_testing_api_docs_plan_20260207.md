# Estado: COMPLETADO (2026-02-07)

# 🏆 Plan Maestro de Testing: API Docs & Funcionalidad REST (v5.12)

**Fecha**: 07/02/2026  
**Objetivo**: Validar la experiencia de usuario en la documentación y la integridad técnica de los nuevos filtros y endpoints de la API.
**Estado**: COMPLETADO

---

## 🏗️ FASE 1: UI/UX Y NAVEGACIÓN (DOCS BROWSER)

### **Test 01: Navegación de Extremos**

- [SI] El botón **"← Anterior"** aparece deshabilitado en Introducción.
- [SI] El botón **"Siguiente →"** aparece deshabilitado en Códigos de Error.

### **Test 02: Sidebar Dinámico (Sub-secciones H3)**

- [SI] En "Crear Servicio", verificar sub-menú: Catálogo, DockerHub, ZIP.
- [SI] En "Consultas (GETs)", verificar sub-menú: Proyectos, Asignaturas, Servicios.
- [SI] Botón **Expandir Todo**: Probar que abre/cierra todos los submenus del sidebar.

### **Test 03: Diseño Responsive y Menú Móvil**

1. Reducir el ancho del navegador (< 992px).
2. **Verificar**:
   - [SI] El sidebar desaparece y aparece la cabecera móvil.
   - [SI] El botón **"Menú"** abre el sidebar lateralmente.
   - [SI] Al seleccionar una sección en móvil, el sidebar se cierra automáticamente tras navegar.

### **Test 04: Feedback Visual (Spinner & Performance)**

1. Pulsar secciones rápidamente.
2. **Verificar**:
   - [SI] Aparece el spinner azul central durante la carga.
   - [SI] El contenido actual se vuelve translúcido (`nav-loading`) para evitar clics fantasma.
   - [SI] Las páginas cargan rápido gracias al `prefetch` configurado en el `<head>`.

### **Test 05: Atajos de Teclado y Copiado**

1. Usar flechas del teclado `←` y `→`. Verificar cambio de página.
2. Hacer click en el icono de **"Copiar"** de los bloques de comando `curl`.
3. **Verificar**: El icono cambia a un tick `check` y el comando está en el portapapeles.

---

## ⚡ FASE 2: FUNCIONALIDAD DE CONSULTAS (GET)

### **Test 06: Obtención de IDs (Comandos Genéricos)**

1. Ejecutar `GET /api/subjects/`.
   - [SI] Verificar que devuelve una lista de objetos con `id` y `name`.
2. Ejecutar `GET /api/projects/`.
   - [SI] Verificar que devuelve mis proyectos y que incluye el campo `subject_name`.

### **Test 07: Filtrado Especializado (Query Params)**

1. Ejecutar `GET /api/containers/?project={ID_DE_UN_PROYECTO}`.
   - [SI] Verificar que SOLO se devuelven los servicios de ese proyecto.
2. Ejecutar `GET /api/projects/?subject={ID_DE_UNA_ASIGNATURA}`.
   - [SI] Verificar que SOLO se devuelven los proyectos de esa asignatura.
3. Ejecutar `GET /api/containers/?status=running`.
   - [SI] Verificar que no aparecen servicios detenidos.

### **Test 08: Consulta de Recurso Único**

1. Ejecutar `GET /api/containers/{id}/`.
   - [SI] Verificar que devuelve el objeto completo (no una lista), incluyendo `env_vars` y `assigned_port`.

---

## 🚀 FASE 3: CREACIÓN Y ACCIONES (POST)

### **Test 09: Creación en Modo Custom (ZIP)**

1. Usar comando `POST` con `-F` (Multipart).
2. Probar enviar **ambos** (Dockerfile y Compose).
   - [SI] Verificar que el servidor devuelve **400 Bad Request** (solo se permite uno).
3. Probar enviar **ninguno**.
   - [SI] Verificar que devuelve **400 Bad Request**.

### **Test 10: Control de Ciclo de Vida**

1. Ejecutar `POST /api/containers/{id}/stop/`.
   - [SI] Verificar que el servicio cambia a estado `stopped`.
2. Ejecutar `GET /api/containers/{id}/logs/`.
   - [SI] Verificar que devuelve texto plano con la salida del contenedor.

---

## � FASE 4: SEGURIDAD Y ERRORES

### **Test 11: Validación de Token (Bearer)**

1. Intentar cualquier petición sin cabecera `Authorization`.
   - [SI] Verificar: **401 Unauthorized**.
2. Intentar petición con token de otro usuario o expirado.
   - [SI] Verificar: **401 Unauthorized**.

### **Test 12: Aislamiento (Multi-tenant)**

1. Intentar acceder a un `{id}` de un servicio que NO me pertenece.
   - [SI] Verificar: **404 Not Found** o **403 Forbidden** (el sistema no debe revelar la existencia del servicio de otro).

---

## ✅ CRITERIOS DE ACEPTACIÓN FINAL

- [SI] La documentación coincide exactamente con el comportamiento de la API.
- [SI] No existen tokens de ejemplo "hardcoded" (se usa la variable del usuario).
- [SI] Todas las URLs base apuntan a `/api/` de forma consistente.
- [SI] Los filtros de proyecto y asignatura funcionan correctamente.
