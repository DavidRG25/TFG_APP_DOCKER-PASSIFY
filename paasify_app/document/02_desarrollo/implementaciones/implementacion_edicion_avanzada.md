# Plan de Implementación: Edición Avanzada y Persistencia de Volúmenes

Este documento centraliza todas las fases del desarrollo para permitir la edición en-sitio de servicios reteniendo sus valores (volúmenes, puertos, etc.) y posibilitando la modificación de imágenes (DockerHub) o reconstrucción de código (Dockerfile/Compose).

## Fase 1: Implementación de Lógica Backend (Serializadores y Dockerd)

**Estado: Completada**

- **Serializadores (`containers/serializers.py`):**
  - Desbloqueo de edición del campo `image` para modo `dockerhub`.
  - Integración del campo write-only (virtual) `keep_volumes` mapeado en DRF a `instance._keep_volumes`, permitiendo persistencia granular sin ensuciar el schema de la DB.
- **Vistas (`containers/views.py`):**
  - Recuperación de `_keep_volumes` (defaults a `True`) al invocar `remove_container` en el método `perform_update`.
- **Servicios Docker (`containers/services.py`):**
  - Refuerzo en `remove_container` para acatar `keep_volumes`.
  - En Compose: condicional que omite la bandera `--volumes` y la purga si `keep_volumes` es verdadero.
  - En Simples: condicional que omite sentencias `volume.remove(force=True)`.

## Fase 2: Implementación Frontend (Interfaz de Edición y Switch de Volumen)

**Estado: En progreso (A continuación)**

1. **Modificación de Campos (DockerHub Image):** Desbloquear el `input` de la imagen en los templates de "Configuración actual" cuando el servicio sea de tipo DockerHub.
2. **Selector de Persistencia (`keep_volumes`):** Integrar un "Switch" UI amistoso en la ventana de edición. Este switch vendrá activado (`On`) por defecto para proteger los datos, y solo si el usuario interactúa explícitamente y lo apaga (`Off`), perderá la data durante la actualización del servicio. Textos de advertencias claros y rojos se revelarán entonces.
3. **Control Cautelar (Javascript):** Ajustes en lógica de eventos. Cuando ocurra una recarga HTMX con PATCH, el interruptor viaja embutido en el form `formData`.

## Fase 3: Pruebas y Post-QA

**Estado: Pendiente**

- Ajustar tests automatizados o flujos de comprobación end-to-end con cURL.
- Verificación del comportamiento del contenedor tras la sustitución de imagen.
- Inspección manual para corroborar que los "named volumes" siguen anclándose.
- Chequear el modal en UI para confirmar flujos visuales libres de bugs.
