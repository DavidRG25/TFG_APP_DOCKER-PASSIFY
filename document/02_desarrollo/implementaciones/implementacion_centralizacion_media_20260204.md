# Implementación: Centralización y Limpieza de Media

**Fecha:** 04 de Febrero de 2026  
**Estado:** ✅ COMPLETADO

---

## 📝 Descripción

Se ha rediseñado por completo la gestión de almacenamiento de archivos del sistema para centralizar todos los activos de los servicios en una estructura única, profesional y fácil de mantener. Se han eliminado las dependencias de carpetas temporales dispersas y se ha optimizado el rendimiento de acceso a archivos.

## 🛠️ Cambios Realizados

### 1. Modelo `Service` (containers/models.py)

- **Unificación de Rutas**: Se ha creado la función `get_service_upload_path` que centraliza todas las subidas en `services/<id>/`.
- **Gestión de Temporales**: Se implementó una ruta `services/tmp/` para archivos subidos antes de que el objeto tenga un ID definitivo.
- **Compatibilidad**: Se mantuvieron aliases de las funciones antiguas (`get_dockerfile_path`, etc.) para no romper las migraciones de Django existentes.

### 2. Lógica de Servicio (containers/services.py)

- **Corrección de Error Crítico**: Se eliminó el error _"The file cannot be reopened"_ optimizando la lectura de archivos (lectura única en memoria y volcado a disco).
- **Refactorización de Workspaces**: `prepare_service_workspace` ahora mueve automáticamente los archivos desde `tmp/` a la carpeta definitiva del servicio durante el primer despliegue.
- **Descompresión Optimizada**: La función `_unpack_code_archive_to` ahora puede trabajar con rutas físicas, evitando re-abrir objetos de archivo de Django.
- **Limpieza Robusta**: Se simplificó `cleanup_service_workspace` para borrar recursivamente la carpeta del servicio, incluyendo lógica específica para Windows que gestiona permisos de archivos bloqueados.

### 3. Operaciones de Mantenimiento (containers/management/commands/cleanup_media.py)

- **Barredora Legacy**: El comando ahora identifica y elimina los directorios antiguos (`user_code/`, `dockerfiles/`, `compose_files/`) y borra las carpetas raíz una vez vaciadas.
- **Mantenimiento de Temporales**: Se añadió lógica para limpiar la carpeta `services/tmp/` borrando archivos de más de una hora de antigüedad.

### 4. Interfaz de Usuario (Templates)

- **Éxito Visual**: Se rediseñó el banner de éxito al crear servicios, mejorando el espaciado y sustituyendo el botón de cierre por una "X" estética de FontAwesome.

## 📂 Nueva Estructura de Directorios

```text
media/
└── services/
    ├── <id_servicio>/
    │   ├── Dockerfile (u otros archivos de configuración)
    │   ├── source.zip / source.rar
    │   └── [archivos_del_servidor_descomprimidos]
    └── tmp/
        └── [archivos_subidios_pendiente_de_id]
```

## 🧪 Pruebas Realizadas

- Creación de servicios con Dockerfile y ZIP: **OK**
- Creación de servicios con Docker Compose: **OK**
- Eliminación de servicios (borrado físico de carpeta): **OK**
- Ejecución de `cleanup_media` (limpieza de carpetas legacy): **OK**
- Gestión de permisos en Windows: **OK**
