# 🏗️ Ejemplo: Stack de Base de Datos y Adminer (Compose Solo)

Este ejemplo demuestra la capacidad de **PaaSify** para desplegar un stack completo de microservicios utilizando **solamente un archivo `docker-compose.yml`**, sin necesidad de subir archivos de código fuente o un ZIP adicional.

## 📄 Contenido del Stack

El archivo `docker-compose.yml` define dos servicios que interactúan entre sí dentro de la red interna de PaaSify:

1.  **db (PostgreSQL 15)**:
    - Una base de datos persistente.
    - Configurada con usuario `admin` y contraseña `root`.
    - **Seguridad**: No expone puertos al exterior; solo es accesible por otros servicios del mismo stack.
2.  **adminer**:
    - Interfaz web para gestionar la base de datos.
    - Expone el puerto **8080** (PaaSify lo mapeará automáticamente a un puerto de host entre 40000-50000).
    - Se conecta automáticamente al servicio `db`.

## 🚀 Cómo desplegarlo en PaaSify

### Opción A: Desde la Interfaz Web (Panel de Control)

1.  Ve a **Nuevo Servicio**.
2.  Selecciona **Configuración personalizada (Dockerfile o docker-compose)**.
3.  En la pestaña que aparece, selecciona **Docker Compose**.
4.  Sube el archivo `docker-compose.yml` de esta carpeta.
5.  **IMPORTANTE**: Deja el campo de **Código fuente (.zip)** vacío. PaaSify detectará que no es necesario.
6.  Haz clic en **Crear servicio**.

### Opción B: Mediante la API (Terminal)

Puedes desplegar este stack con un solo comando `curl` sin necesidad de enviar archivos ZIP:

```bash
curl -X POST https://tu-paasify.com/api/containers/ \
  -H "Authorization: Bearer <TU_TOKEN>" \
  -F "name=mi-stack-db" \
  -F "mode=custom" \
  -F "compose=@docker-compose.yml" \
  -F "project=<ID_PROYECTO>" \
  -F "subject=<ID_ASIGNATURA>"
```

## 💡 Ventajas de este método

- **Rapidez**: No pierdes tiempo empaquetando código si solo quieres desplegar servicios de catálogo orquestados.
- **Simplicidad**: Ideal para entornos de base de datos, herramientas de administración o proxies.
- **Configuración centralizada**: Todo el stack se gestiona desde un único fichero YAML.
