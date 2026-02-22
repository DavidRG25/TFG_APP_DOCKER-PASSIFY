# Plan de Testing: Edición de Servicios (UI Re-Test v2 - Casuística Completa)

**ESTADO:** ✅ COMPLETADO
**FECHA DE FINALIZACIÓN:** 2026-02-22

Este documento detalla las pruebas exhaustivas necesarias para validar la funcionalidad de modificación de servicios en la interfaz de PaaSify, abarcando todos los modos de despliegue, errores y casos límite.

## 1. Escenario: Servicio del Catálogo (Modo Default)

**Objetivo**: Validar que la edición está bloqueada para garantizar la integridad del catálogo gestionado.

- [SI] **Acceso a la ruta de edición**: Intentar entrar directamente en la URL `/paasify/containers/edit/{id}/` de un servicio oficial.
- [SI] **Resultado**: El sistema debe redirigir a un listado general o mostrar una página de error 403 Forbidden clara, indicando que este servicio no es modificable por su naturaleza de catálogo.

## 2. Escenario: Servicio DockerHub

**Objetivo**: Validar cambios dinámicos en configuración de red, metadatos y variables de entorno para imágenes públicas.

- [SI] **Caso A: Cambio de Puertos**:
  - Modificar el valor de `Puerto Interno` de 80 a 8080.
  - Alternar el `Puerto Externo` entre asignación libre (Auto) y un puerto específico permitido (ej. 50080).
- [SI] **Caso B: Variables de Entorno y Configuración Avanzada**:
  - Añadir un bloque JSON válido: `{"DEBUG": "True", "APP_ENV": "dev"}`.
  - Guardar, volver a entrar en la pantalla de edición y verificar que el JSON se ha persistido correctamente.
- [SI] **Caso C: Alteración de Metadatos**:
  - Modificar el campo `Tipo de Contenedor` de "Web" a "API" o "Database".
  - Desactivar el interruptor "¿Es una web accesible?".
- [SI] **Caso D: Actualización de la Imagen**:
  - Habilitar la edición de la imagen pública (ej: modificar `nginx:1.19` a `nginx:latest`). Verificando que al guardar, el contenedor se reconstruye basándose en la nueva imagen.
- [SI] **Caso E: Conflictos de Configuración (Edge Case)**:
  - Intentar asignar un nombre de servicio que ya existe o tiene espacios.
  - Intentar cambiar el "modo" (el formulario debería tenerlo bloqueado u oculto).
- [SI] **Resultado Final**: Tras pulsar "Guardar", la UI debe reflejar el spinner de carga. Tras el éxito, el contenedor debe recrearse, y si se desactivó "¿Es una web accesible?", el botón de enlace web (🌐) debe desaparecer del listado.

## 3. Escenario: Servicio Personalizado (Dockerfile)

**Objetivo**: Validar todo el flujo de actualización de código fuente, sobreescritura de archivos y el consiguiente proceso de reconstrucción (Build).

- [SI] **Caso A: Reemplazo Total de Archivos**:
  - Subir un nuevo archivo `Dockerfile` (modificando por ejemplo la imagen base de python:3.9 a python:3.10).
  - Subir un nuevo archivo `.zip` con código actualizado.
- [SI] **Caso B: Reemplazo Parcial**:
  - Subir solo un nuevo `.zip` sin alterar el `Dockerfile`. Verificar que el build se ejecuta correctamente utilizando el Dockerfile persistido anterior.
- [SI] **Caso C: Metadatos y Accesibilidad**:
  - Activar "Acceso Web" y cambiar tipo a "Web", garantizando concordancia con un puerto de red expuesto en el Dockerfile.
- [SI] **Resultado Final**: El sistema debe vaciar o sobreescribir correctamente el workspace (`media/services/{id}`) e invocar transparentemente `docker build`. Refrescar la vista de logs para garantizar que reflejan la salida del nuevo código temporal.

## 4. Escenario: Servicio Personalizado (Docker Compose)

**Objetivo**: Validar la gestión, alteración y autodetección de parámetros en stacks auto-desplegables.

- [SI] **Caso A: Persistencia y Análisis Pormenorizado de Sub-servicios**:
  - En el formulario edit, marcar el componente `frontend` como "Web" y activar `is_web: true`.
  - Marcar el componente `api` o `db` estricto a "API" o "Database" y con `is_web: false`.
- [SI] **Caso B: Inyección / Modificación del Stack Root**:
  - Subir una nueva iteración del archivo `docker-compose.yml` que incluya un nuevo volumen persistente o añada un contenedor de Redis. El sistema debe adaptarse en la siguiente pantalla de recálculo (si la hay) o internamente.
- [SI] **Caso C: Comprobación de Adherencia en UI**:
  - Navegar fuera de la página y volver a `/paasify/containers/edit/{id}/`.
  - Validar fehacientemente que la tabla de análisis de sub-contenedores conserva su configuración (checkboxes y menús desplegables per-service).
- [SI] **Resultado Final**: Al volver al listado general, única y exclusivamente el sub-servicio designado como "Web" (ej. `frontend`) debe proveer el botón/enlace de acceso al puerto exterior expuesto.

## 5. Pruebas de Persistencia de Volúmenes de Datos (Transversal)

**Objetivo**: Confirmar que el usuario puede elegir a través de la interfaz (Switch: "Preservar Volúmenes") si mantener o destruir el almacenamiento secundario / persistente asociado a un contenedor o stack durante su reconstrucción.

- [SI] **Prueba de Persistencia Activada (Toggle ON / `keep_volumes: true`)**:
  - Crear e iniciar una base de datos o stack y guardar algún dato real en ella (ej. una tabla MySQL).
  - En la vista de Edición, asegurarse de tener activado el switch "Preservar Volúmenes de Datos". Aplicar un cambio (nueva imagen, puerto) y guardar.
  - **Resultado Esperado**: El contenedor se reconstruye y las modificaciones toman efecto. Sin embargo, al inspeccionar el servicio de nuevo (ej. hacer query en la BD), los datos antiguos siguen estando ahí.
- [SI] **Prueba de Persistencia Desactivada (Toggle OFF / `keep_volumes: false`)**:
  - En la vista de Edición, desactivar explícitamente el switch de "Preservar Volúmenes" con su debido warning. Aplicar cambio y guardar.
  - **Resultado Esperado**: El contenedor o stack se destruye en su totalidad. Al levantar la nueva versión, la base de datos o almacenamiento vuelve a su estado _vacío / limpio_.

## 6. Pruebas Transversales de Robustez, Errores y UX

- [SI] **Conflicto de Nombres Duplicados**: Cambiar el nombre a uno existente en otro proyecto (Debería lanzar error al Guardar).
- [SI] **Interacciones de Estado y Ciclo de Vida**:
  - Detener y pausar el servicio desde la vista general.
  - Entrar en la edición, cambiar configuración y guardar.
  - Verificar que el servicio mantiene el estado lógico correcto (arranca si la edición lo requería, o sigue detenido pero reconstruido).
- [SI] **Prevención de Sintaxis Inválida**: Subir un archivo de Docker Compose malformado (YAML inválido). El backend debe escupir un toast o aviso rojo interceptando el guardado.
- [ ] **Previsualización de Documentos Actuales**: Utilizar el botón "Ver archivo actual" para confirmar que un archivo `.yml` o `.Dockerfile` servido es exactamente la última iteración enviada.
- [SI] **Feedback de Interfaz en Esperas**: Confirmar que durante el guardado de recursos pesados se inhabilita el botón "Guardar" y aparece un spinner minimalista para evitar dobles envíos.
- [SI] **Restricción de Permisos entre Usuarios**: Iniciar sesión como un profesor `A`. Intentar abrir con la URL de edición directa el contenedor pertenenciente a profesor `B`. Esperado: `404 Not Found` o `403 Forbidden`.

---

**Firmado:** PaaSify QA Team  
**Fecha de Revisión:** 2026-02-21
