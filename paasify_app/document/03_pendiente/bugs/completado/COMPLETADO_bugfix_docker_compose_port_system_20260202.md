# Registro de Bugs y Mejoras - Sistema de Puertos y Docker Compose

**Fecha:** 2026-02-02  
**Estado:** Completado  
**Módulo:** `containers` (Servicios y Despliegue)

---

## 1. 🐛 Bug: El Puerto Personalizado no se guardaba en la Base de Datos

**Descripción:**  
Al crear un servicio (Dockerfile o DockerHub) especificando un "Puerto personalizado", el valor se procesaba para arrancar el contenedor, pero el campo `assigned_port` del modelo `Service` quedaba como `NULL`. Esto impedía que el sistema "recordara" qué puerto tiene asignado un servicio ya creado.

**Causa:**  
El `ServiceSerializer` no mapeaba el campo de entrada `custom_port` al campo del modelo `assigned_port` en su método `create`.

**Solución:**

- Se modificó `containers/serializers.py` para extraer `custom_port` de los datos validados y asignarlo explícitamente a `assigned_port` antes de guardar.

---

## 2. 🐛 Bug: Los puertos de Docker Compose eran invisibles para el sistema

**Descripción:**  
Al desplegar mediante `docker-compose.yml`, el sistema no guardaba los puertos externos definidos en el YAML. Como resultado, la herramienta de "Verificar disponibilidad" mostraba esos puertos como disponibles cuando en realidad estaban ocupados por el stack de compose.

**Solución:**

- **Modelo:** Se añadió el campo `assigned_ports` (JSONField) al modelo `Service` para almacenar múltiples puertos.
- **Serializer:** Se implementó lógica de extracción automática en el `ServiceSerializer` que parsea el `docker-compose.yml` al crear el servicio y guarda todos los puertos detectados.
- **Sincronización:** Se mejoró la lógica para que los puertos detectados por Docker al arrancar también se reflejen en el sistema.

---

## 3. 🐛 Bug: Verificación de disponibilidad de puertos incompleta

**Descripción:**  
La herramienta de verificación solo consultaba la tabla `Service` buscando el campo `assigned_port`. Ignoraba los puertos reservados actualmente en Docker, los puertos de servicios Compose en ejecución y las reservas activas en la tabla `PortReservation`.

**Solución:**

- Se actualizó la vista `check_port_availability` en `containers/views.py` para realizar una búsqueda exhaustiva en:
  1.  `Service.assigned_port` (Contenedores simples).
  2.  `Service.assigned_ports` (Listas de puertos de stacks Compose).
  3.  `ServiceContainer.assigned_ports` (Puertos de contenedores individuales del stack).
  4.  `PortReservation` (Reservas activas en el motor Docker).

---

## 4. ✨ Mejora UX: Pre-selección de Asignatura y Filtrado de Proyectos

**Descripción:**  
Al crear un servicio desde la página de una asignatura específica, el usuario debía volver a seleccionar la asignatura manualmente. Además, el selector de "Proyecto" mostraba todos los proyectos del usuario sin filtrar por la asignatura elegida.

**Solución:**

- **Backend:** Se modificó la vista `new_service_page` para detectar el `HTTP_REFERER` y pre-seleccionar la asignatura correspondiente.
- **Frontend:** Se añadió lógica JavaScript en `_scripts.html` para filtrar dinámicamente el dropdown de Proyectos basándose en la Asignatura seleccionada.

---

## 5. 🚀 Mejora UX: Redirección Inmediata tras Creación

**Descripción:**  
Tras pulsar "Crear Servicio", el navegador esperaba demasiado tiempo (1.5s) antes de redirigir, dando una sensación de lentitud innecesaria dado que la creación es un proceso asíncrono en segundo plano.

**Solución:**

- Se redujo el retardo de redirección a **500ms** en `new_service.html`, mejorando la fluidez del usuario hacia el panel de control de la asignatura.

---

## Archivos Modificados:

- `containers/models.py`: Nuevo campo `assigned_ports`.
- `containers/serializers.py`: Lógica de mapeo y extracción de puertos YAML.
- `containers/views.py`: Mejora en la API de verificación de puertos y pre-selección de datos.
- `templates/containers/new_service.html`: Ajustes de UI y tiempos de respuesta.
- `templates/containers/_partials/panels/_scripts.html`: Lógica de filtrado de proyectos.
