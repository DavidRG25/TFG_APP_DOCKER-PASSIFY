# Plan de Testing: Análisis Inteligente de Docker Compose y Tipado de Servicios

**Fecha:** 15/02/2026  
**Autor:** David RG  
**Objetivo:** Validar que el sistema de análisis inteligente de Docker Compose, el tipado de servicios y el control de visibilidad web funcionan correctamente en todas las capas (Frontend, Backend, API y Docs).

---

## 🖥️ FASE 1: FRONTEND Y FORMULARIO (INTERFAZ DE USUARIO)

### **Test 01: Análisis Dinámico de Compose**

1. Ir a **"Crear Nuevo Servicio"** -> **"Configuración Personalizada"** -> **"Docker Compose"**.
2. Subir un archivo `docker-compose.yml` (ej: el de Mega Stack).
3. **Verificar**:
   - [SI] Aparece el indicador de "Analizando...".
   - [SI] Se despliega la tabla con todos los contenedores detectados.
   - [SI] Los nombres de imagen y mapped ports coinciden con el archivo.
   - [SI] Desaparecen los campos de "Puerto Personalizado" e "Interno" (para evitar redundancia).

### **Test 02: Overrides y Personalización**

1. En la tabla de análisis:
2. Cambiar el **Tipo de Contenedor** de un servicio (ej: de Web a API).
3. Desactivar el interruptor de **Modo Web** de un servicio (ej: la base de datos).
4. **Verificar**:
   - [SI] Al crear el servicio, los cambios se mantienen en la vista principal.

### **Test 03: Modo Simple (Acceso Rápido)**

1. Seleccionar **"Imagen desde DockerHub"** o **"Dockerfile Único"**.
2. **Verificar**:
   - [SI] Aparece la nueva sección de "Configuracion de Acceso y Tipo".
   - [SI] Se puede seleccionar el tipo (Web, API, DB) y el interruptor de visibilidad inicial.

---

## ⚙️ FASE 2: BACKEND Y LÓGICA DE NEGOCIO

### **Test 04: Motor de Análisis (Parser)**

1. Enviar un archivo YAML corrupto.
   - [SI] **Verificar**: El sistema muestra un error de sintaxis descriptivo (línea/columna).
2. Enviar un archivo con más de 5 servicios.
   - [SI] **Verificar**: Mensaje de error limitando el despliegue.

### **Test 05: Persistencia de Configuración (container_configs)**

1. Crear un servicio multi-contenedor con ajustes personalizados en la tabla.
2. Ir a la base de datos o revisar la respuesta del servidor.
3. **Verificar**:
   - [sI] Cada `ServiceContainer` tiene el `container_type` y `is_web` asignados por el usuario.

---

## 🎨 FASE 3: VISTA DE SERVICIOS Y EXPERIENCIA VISUAL

### **Test 06: Iconografía Dinámica**

1. En el Panel de Control, observar los servicios creados.
2. **Verificar**:
   - [SI] Servicios tipo **Web** muestran el icono de Globo (🌐).
   - [SI] Servicios tipo **API** muestran el icono de Microchip (⚙️).
   - [SI] Servicios tipo **Database** muestran el icono de Base de Datos (🗄️).

### **Test 07: Control de Botón "Acceder"**

1. Revisar un servicio donde se desactivó "Permitir acceso vía web".
2. **Verificar**:
   - [SI] El botón de **flecha externa (Acceder)** NO aparece en la tarjeta del servicio.
   - [SI] El botón de terminal y otros controles siguen visibles.

---

## 🔌 FASE 4: API REST Y DOCUMENTACIÓN

### **Test 08: Endpoint de Análisis Independiente**

1. Realizar una petición `POST /api/containers/analyze-compose/` con un archivo yaml.
2. **Verificar**:
   - [SI] Devuelve JSON con el array de `containers`, sus puertos detectados y tipos sugeridos.

### **Test 09: Creación vía API con Configuración Refinada**

1. Realizar un `POST /api/containers/` pasando el JSON `container_configs` en el body.
2. **Verificar**:
   - [SI] El servicio se crea respetando las preferencias de visibilidad y tipado enviadas.

### **Test 10: Validación de Documentación**

1. Ir a la página de **Documentación de la API** (`/paasify/containers/api-docs/`).
2. Entrar en la sección **"Crear Servicio"**.
3. **Verificar**:
   - [SI] Aparecen documentados los campos `container_type` e `is_web`.
   - [SI] Aparece la nueva sección detallando el endpoint de **Análisis Previo**.

---

## ✅ CRITERIOS DE ACEPTACIÓN FINAL

- [SI] El análisis de Compose es no-bloqueante (asíncrono en frontend).
- [SI] La iconografía mejora la legibilidad del stack tecnológico del alumno.
- [SI] No es necesario configurar puertos a mano cuando se usa Compose.
- [SI] La documentación refleja el 100% de las nuevas capacidades.
