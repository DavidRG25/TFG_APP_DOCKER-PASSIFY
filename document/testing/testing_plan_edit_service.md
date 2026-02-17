# Plan de Testing: Edición de Servicios (UI Re-Test v2 - Casuística Completa)

Este documento detalla las pruebas necesarias para validar la funcionalidad de modificación de servicios en PaaSify para cada uno de los modos de despliegue admitidos.

## 1. Escenario: Servicio del Catálogo (Modo Default)

**Objetivo**: Validar que la edición está bloqueada para garantizar la integridad del catálogo.

- [ ] **Acceso**: Intentar entrar en `/paasify/containers/edit/{id}/` de un servicio oficial (ej: MySQL o Nginx oficial).
- [ ] **Resultado**: El sistema debe redirigir con un mensaje de error o mostrar un error 403 Forbidden indicando que no es editable.

## 2. Escenario: Servicio DockerHub

**Objetivo**: Validar cambios en configuración de red y entorno para imágenes públicas.

- [ ] **Caso A: Cambio de Puertos**:
  - Cambiar `Puerto Interno` de 80 a 8080.
  - Cambiar `Puerto Externo` de "Auto" a 50080.
- [ ] **Caso B: Variables de Entorno**:
  - Añadir un JSON válido: `{"DEBUG": "True", "APP_ENV": "dev"}`.
- [ ] **Caso C: Metadatos**:
  - Cambiar `Tipo de Contenedor` de "Web" a "API".
  - Desactivar switch "¿Es una web accesible?".
- [ ] **Resultado**: Tras pulsar "Guardar", el contenedor debe recrearse. Verificar que el botón 🌐 ha desaparecido en la tabla general.

## 3. Escenario: Servicio Personalizado (Dockerfile)

**Objetivo**: Validar el reemplazo de archivos y reconstrucción (Build).

- [ ] **Caso A: Reemplazo de Archivos**:
  - Subir un nuevo archivo `Dockerfile` (ej: cambiar imagen base).
  - Subir un nuevo `.zip` de código.
- [ ] **Caso B: Cambio de Visibilidad**:
  - Activar "Acceso Web" y cambiar tipo a "Web".
  - Definir un puerto interno que coincida con el nuevo código.
- [ ] **Resultado**: El sistema debe purgar el workspace (`media/services/{id}`) y ejecutar `docker build`. Verificar que el nuevo código está en ejecución.

## 4. Escenario: Servicio Personalizado (Docker Compose)

**Objetivo**: Validar la gestión de stacks multi-contenedor y su autodetección.

- [ ] **Caso A: Gestión de Sub-servicios**:
  - En la tabla de análisis de Compose, marcar el contenedor `frontend` como "Web" + `is_web: true`.
  - Marcar el contenedor `api` como "API" + `is_web: false`.
- [ ] **Caso B: Modificación del Stack**:
  - Subir un nuevo `docker-compose.yml` que incluya un nuevo volumen o una red diferente.
- [ ] **Caso C: Persistencia de Configs**:
  - Guardar y volver a entrar a editar. Verificar que los checkboxes de la tabla de análisis mantienen su estado.
- [ ] **Resultado**: En la tabla general de contenedores, solo el sub-servicio `frontend` debe mostrar el botón azul de acceso web.

## 5. Pruebas Transversales (UX)

- [ ] **Overlay de Carga**: Confirmar que al guardar solo aparece el spinner minimalista (sin textos).
- [ ] **Mensajes de Error**: Intentar subir un archivo que no sea un YAML válido en Compose y verificar que el sistema avisa del error.
- [ ] **Visualización**: Usar el botón "Ver" para confirmar que el contenido mostrado corresponde a la última versión subida del archivo.

---

**Firmado:** PaaSify QA Team
**Fecha:** 2026-02-18
