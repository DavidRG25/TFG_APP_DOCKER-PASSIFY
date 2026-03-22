# Implementación: Feedback Tutor – Optimización, Documentación y Fix UI (v10.14.0)

**Fecha**: 22-03-2026
**Versión**: v10.14.0
**Estado**: Completado

---

## 📋 Resumen de Cambios

Esta versión aborda los cinco puntos de feedback recibidos del tutor el 20/03/2026, incluyendo optimización de despliegue, limpieza de warnings, documentación de seguridad, y corrección de bugs en la interfaz de usuario.

---

### 1. Optimizar Git Sparse-Checkout

Se detectó que el comando de clonación del README y la guía de despliegue descargaba todo el historial del repositorio en lugar de solo los ficheros necesarios.

- **Corrección**: Se añadió el flag `--filter=blob:none` al comando `git clone`, que evita descargar blobs innecesarios del historial y reduce drásticamente el tamaño de la descarga.
- **Comando optimizado**:
  ```bash
  git clone --filter=blob:none --no-checkout --sparse <URL> .
  git sparse-checkout set deploy
  git checkout main
  ```

**Archivos modificados**:
- `README.md` — Sección "Despliegue rápido".
- `docs/DEPLOYMENT.md` — Sección 2 "Clonar el repositorio".

---

### 2. Limpiar Warnings Docker Compose

Docker Compose v2 marca como obsoleta la directiva `version: "3.8"` y emite un warning amarillo en cada ejecución. Se ha eliminado esta línea de **todos** los archivos compose del proyecto.

**Archivos modificados** (9 ficheros):
- `deploy/docker-compose.yml`
- `testing_examples/docker-compose/02_compose_redis_nginx/docker-compose.yml`
- `testing_examples/docker-compose/03_compose_node_mariadb/docker-compose.yml`
- `testing_examples/docker-compose/04_compose_mega_stack/docker-compose.yml`
- `testing_examples/docker-compose/05_compose_persistence/v1/docker-compose.yml`
- `testing_examples/docker-compose/05_compose_persistence/v2/docker-compose.yml`
- `testing_examples/docker-compose/05_compose_persistence/docker-compose-invalido.yml`
- `testing_examples/docker-compose/06_compose_solo/docker-compose.yml`

---

### 3. Documentación de Certificados TLS y Nginx

Se amplió la sección 5 de `docs/DEPLOYMENT.md` para incluir una guía paso a paso de:

- **Generar certificados autofirmados** para pruebas locales con `openssl`.
- **Integrar certificados válidos** (Let's Encrypt o de una CA comercial).
- **Configurar `server_name`** en `deploy/nginx/conf.d/default.conf` para asociar el dominio correcto al proxy inverso.

---

### 4. Requisito apache2-utils / httpd-tools

Se documentó en `docs/DEPLOYMENT.md` (sección 6) que el comando `htpasswd` usado para generar credenciales de acceso requiere la instalación previa del paquete:

- `apache2-utils` en Debian/Ubuntu.
- `httpd-tools` en CentOS/RHEL/Fedora.

---

### 5. Fix UI: Spinner infinito en errores de despliegue

**Bug original**: Al crear un servicio Docker Compose que fallaba durante el despliegue, el spinner de "Creando servicio..." se quedaba visible indefinidamente, bloqueando la interfaz sin mostrar el error.

**Corrección** (en `templates/containers/new_service.html`):
- El listener `htmx:afterRequest` ahora resetea **incondicionalmente** el overlay de carga y el botón de envío, independientemente de si la petición fue exitosa o fallida.
- Se añadió lógica para extraer y mostrar el mensaje de error real:
  1. Primero intenta leer el header `HX-Trigger` (donde el backend Django envía los toasts).
  2. Luego intenta parsear el cuerpo JSON de la respuesta (formato DRF).
  3. Muestra el error en una alerta roja (`alert-danger`) con scroll automático al mensaje.

---

### 6. Validación estricta de Docker Compose (Mejora adicional)

Durante las pruebas del punto 5, se identificó que el sistema aceptaba archivos `docker-compose.yml` con errores de sintaxis o estructura (ej. `servicos:` en vez de `services:`), creando servicios que fallaban inevitablemente.

**Corrección** (en `containers/serializers.py`):
- Se integró una validación usando `docker compose -f - config -q`, que pasa el contenido del archivo por stdin al motor de Docker para verificar la sintaxis y la estructura antes de aceptarlo.
- **Bug corregido**: `value.read()` devuelve `bytes`, pero `subprocess.run(..., text=True)` esperaba `str`. Esto causaba un `TypeError` silencioso que anulaba toda la validación CLI. Se solucionó decodificando `content` a UTF-8.
- Se añadió `CREATE_NO_WINDOW` para Windows y un `timeout=15s` para evitar bloqueos.

**Resultado**: Si el archivo es inválido, el sistema bloquea la creación mostrando el error de Docker al usuario antes de tocar la base de datos.

---

### 7. Prioridad de archivos en workspace (Mejora adicional)

Se reordenó la función `prepare_service_workspace` en `containers/services.py` para que:

1. Primero se descomprime el ZIP de código fuente (si existe).
2. Después se copia el `Dockerfile` o `docker-compose.yml` subido explícitamente en el formulario.

Esto garantiza que el archivo subido por el usuario **siempre prevalece** sobre cualquier homónimo que pueda existir dentro del ZIP.

---

## 🛠 Resumen de Archivos Modificados

| Archivo | Cambio |
|---|---|
| `README.md` | Optimización comando sparse-checkout |
| `docs/DEPLOYMENT.md` | Guía TLS, Nginx, apache2-utils, sparse-checkout |
| `deploy/docker-compose.yml` | Eliminado `version: "3.8"` |
| `testing_examples/.../docker-compose.yml` (×7) | Eliminado `version: "3.8"` |
| `containers/serializers.py` | Validación Docker CLI + fix bytes→str |
| `containers/services.py` | Reorden workspace: ZIP → Dockerfile/Compose |
| `containers/views.py` | Mejora mensaje error en create() |
| `templates/containers/new_service.html` | Fix spinner + notificación de errores |

---
