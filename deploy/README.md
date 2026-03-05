# 🚀 Guía de Despliegue de PaaSify en Producción

Este directorio contiene todo lo necesario para montar la infraestructura completa de **PaaSify** en un servidor o máquina virtual: Django (ASGI), PostgreSQL, Nginx (proxy inverso + TLS) y cAdvisor (monitorización de hardware).

---

## 📋 Requisitos Previos

| Componente         | Versión Mínima  | Instalación                                                               |
| ------------------ | --------------- | ------------------------------------------------------------------------- |
| **Docker Engine**  | 20.10+          | [docs.docker.com/engine/install](https://docs.docker.com/engine/install/) |
| **Docker Compose** | v2.12+ (Plugin) | Incluido con Docker Engine moderno                                        |
| **htpasswd**       | —               | `sudo apt-get install apache2-utils -y`                                   |

> **No se necesita Python, pip ni ninguna dependencia adicional.** Todo el runtime de PaaSify está dentro de la imagen Docker.

---

## 🛠️ Paso 1: Obtener la Configuración

Puedes obtener este directorio de dos formas:

### Opción A: Sparse Checkout (recomendado)

Descarga **solo** la carpeta `deploy/` sin traer todo el código fuente:

```bash
mkdir PaaSify && cd PaaSify
git clone --no-checkout --sparse https://github.com/DavidRG25/TFG_APP_DOCKER-PASSIFY.git .
git sparse-checkout set deploy
git checkout main
cd deploy
```

### Opción B: Descarga directa

Si no tienes git, puedes descargar la carpeta `deploy/` manualmente desde GitHub como ZIP.

---

## 🔐 Paso 2: Configurar Variables de Entorno (.env)

Crea un archivo `.env` a partir de la plantilla:

```bash
cp .env.example .env
nano .env
```

### Variables que DEBES cambiar en producción

| Variable               | Descripción                                                       | Ejemplo                            |
| ---------------------- | ----------------------------------------------------------------- | ---------------------------------- |
| `DJANGO_SECRET_KEY`    | Clave criptográfica única. **Nunca reutilices la de desarrollo.** | _(genera una nueva, ver abajo)_    |
| `DJANGO_ALLOWED_HOSTS` | Dominio/IP del servidor                                           | `paas.tfg.etsii.urjc.es,localhost` |
| `DB_PASSWORD`          | Contraseña de PostgreSQL                                          | `una_password_fuerte_2026!`        |
| `ADMIN_PASSWORD`       | Contraseña del superusuario `admin`                               | `Mi_Clave_Admin_Segura!`           |

> 💡 **Generar una `DJANGO_SECRET_KEY` segura:**
>
> ```bash
> python3 -c "import secrets; import string; chars = string.ascii_letters + string.digits + '+-/_!*()'; print(''.join(secrets.choice(chars) for i in range(50)))"
> ```

### Ejemplo de `.env` completo

```ini
DJANGO_SECRET_KEY=tu_secreto_seguro_y_largo_generado_automaticamente
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=paas.tfg.etsii.urjc.es,localhost,127.0.0.1

ADMIN_PASSWORD=Mi_Clave_Admin_Segura_2026!

PAASIFY_BASE_URL=https://paas.tfg.etsii.urjc.es

DB_NAME=paasify_db
DB_USER=paasify_admin
DB_PASSWORD=mi_password_postgres_fuerte
DB_HOST=db
DB_PORT=5432
```

> **Nota:** El `DB_HOST` debe ser `db` — es el nombre del servicio PostgreSQL dentro de la red del Docker Compose.

---

## 🔒 Paso 3: Certificados TLS (HTTPS)

Para que el dominio funcione por HTTPS, Nginx necesita un certificado y su clave privada.

```bash
# Crear directorio si no existe
mkdir -p nginx/certs

# Copiar certificados proporcionados por la universidad/proveedor
sudo cp /ruta/al/certificado.pem nginx/certs/server.crt
sudo cp /ruta/a/la/clave_privada.key nginx/certs/server.key

# Ajustar permisos
sudo chown -R $(whoami):$(whoami) nginx/certs/
```

> Si los nombres de tus archivos difieren, actualiza las rutas en `nginx/conf.d/paasify.conf`.

---

## 🛡️ Paso 4: Proteger el Panel de Monitorización (cAdvisor)

El panel de métricas de hardware (`/monitorizacion/`) está protegido por contraseña HTTP:

```bash
# Crear directorio y archivo de credenciales
mkdir -p nginx/htpasswd
cd nginx/htpasswd/
htpasswd -c .htpasswd admin   # Te pedirá introducir una contraseña
cd ../../
```

> ⚠️ **No subas** `.htpasswd` al repositorio.

---

## 🚀 Paso 5: Levantar el Ecosistema

```bash
# Desde la carpeta deploy/
docker compose up -d
```

Esto levanta simultáneamente:

- **PaaSify** (Django + Daphne, ASGI con WebSocket)
- **PostgreSQL 15** (base de datos persistente)
- **Nginx** (proxy inverso con TLS)
- **cAdvisor** (monitorización de contenedores)

---

## 🗄️ Paso 6: Inicializar la Base de Datos (Solo la primera vez)

Tras levantar los servicios, espera ~10 segundos y ejecuta:

```bash
# Crear usuarios base (admin, alumno, profesor)
# El admin usará la contraseña definida en ADMIN_PASSWORD del .env
docker compose exec paasify python manage.py create_demo_users

# Poblar catálogo de imágenes Docker
docker compose exec paasify python manage.py populate_example_images
```

### Usuarios creados

| Rol         | Usuario    | Contraseña                      |
| ----------- | ---------- | ------------------------------- |
| 🔧 Admin    | `admin`    | La definida en `ADMIN_PASSWORD` |
| 🎓 Alumno   | `alumno`   | `Alumno!2025`                   |
| 👨‍🏫 Profesor | `profesor` | `Profesor!2025`                 |

---

## 🔍 Verificación y Monitorización

### Comprobar que todo está funcionando

```bash
# Estado de los servicios
docker compose ps

# Logs en tiempo real
docker compose logs -f paasify    # Logs de la aplicación
docker compose logs -f db         # Logs de PostgreSQL
docker compose logs -f nginx      # Logs del proxy
docker compose logs -f            # Todos a la vez
```

### URLs de acceso

| Servicio           | URL                                    |
| ------------------ | -------------------------------------- |
| **PaaSify**        | `https://<tu-dominio>/`                |
| **Panel Admin**    | `https://<tu-dominio>/admin/`          |
| **API Docs**       | `https://<tu-dominio>/api-docs/`       |
| **Monitorización** | `https://<tu-dominio>/monitorizacion/` |

---

## 🔄 Actualizar PaaSify

Para actualizar a una nueva versión:

```bash
# Descargar la nueva imagen
docker compose pull paasify

# Reiniciar solo PaaSify (sin afectar BD ni Nginx)
docker compose up -d paasify

# Verificar logs
docker compose logs -f paasify
```

> Si la nueva versión incluye migraciones de BD, se ejecutarán automáticamente al arrancar.

---

## 🗑️ Mantenimiento

### Backup de la base de datos

```bash
# Crear backup
docker compose exec db pg_dump -U paasify_admin paasify_db > backup_$(date +%Y%m%d).sql

# Restaurar backup
cat backup.sql | docker compose exec -T db psql -U paasify_admin paasify_db
```

### Limpieza de archivos huérfanos

```bash
# Previsualizar qué se borraría
docker compose exec paasify python manage.py cleanup_media --dry-run

# Ejecutar limpieza real
docker compose exec paasify python manage.py cleanup_media
```

---

## ⚠️ Resolución de Problemas

| Síntoma                             | Causa probable                 | Solución                                               |
| ----------------------------------- | ------------------------------ | ------------------------------------------------------ |
| `502 Bad Gateway` en Nginx          | PaaSify aún no ha arrancado    | Esperar ~15s, verificar `docker compose logs paasify`  |
| BD no arranca                       | Permisos en `volumes/db_data/` | `sudo chown -R 999:999 volumes/db_data/`               |
| Contenedores de alumnos no arrancan | Socket Docker no montado       | Verificar `volumes` en docker-compose.yml              |
| Estáticos no cargan (CSS/JS roto)   | `collectstatic` no ejecutado   | Se ejecuta automáticamente al arrancar, verificar logs |
| WebSocket no funciona               | Nginx sin upgrade headers      | Verificar `proxy_set_header Upgrade` en conf de Nginx  |
