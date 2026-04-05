# 🚀 Guía de Despliegue y Administración — PaaSify

## Índice

1. [Requisitos del Sistema](#1-requisitos-del-sistema)
2. [Despliegue Rápido (Producción)](#2-despliegue-rápido-producción)
3. [Arquitectura de Producción](#3-arquitectura-de-producción)
4. [Configuración de Variables de Entorno](#4-configuración-de-variables-de-entorno)
5. [Certificados TLS y Seguridad](#5-certificados-tls-y-seguridad)
6. [Monitorización (cAdvisor)](#6-monitorización-cadvisor)
7. [Administración del Día a Día](#7-administración-del-día-a-día)
8. [Mantenimiento y Backups](#8-mantenimiento-y-backups)
9. [Resolución de Problemas](#9-resolución-de-problemas)

---

## 1. Requisitos del Sistema

| Componente            | Versión Mínima             | Notas                                                       |
| --------------------- | -------------------------- | ----------------------------------------------------------- |
| **Docker**            | 20.10+                     | Requerido en la máquina host                                |
| **Docker Compose**    | v2.12+                     | Plugin de Docker CLI                                        |
| **Sistema Operativo** | Ubuntu 22.04+ / Debian 12+ | Recomendado Linux para producción                           |
| **RAM**               | 4 GB mínimo                | 8 GB recomendado según número de alumnos                    |
| **Disco**             | 20 GB libres               | Las imágenes Docker de alumnos consumirán espacio adicional |
| **Red**               | Puerto 80 y 443 abiertos   | + rango 40000-50000 para servicios de alumnos               |

> **Nota:** PaaSify **NO necesita Python ni pip en la máquina de producción**. Todo el runtime se ejecuta dentro de un contenedor Docker.

---

## 2. Despliegue Rápido (Producción)

El despliegue usa **Sparse Checkout** para descargar solo la carpeta `deploy/` del repositorio (la imagen de la aplicación se descarga desde DockerHub):

```bash
# 1. Clonar solo la configuración de deploy
mkdir Paasify && cd Paasify
git clone --filter=blob:none --no-checkout --sparse https://github.com/DavidRG25/TFG_APP_DOCKER-PASSIFY.git .
git sparse-checkout set deploy
git checkout main

# 2. Preparar entorno
cd deploy
cp .env.example .env
nano .env  # Configura DJANGO_SECRET_KEY, credenciales BD, etc.

# 3. (Opcional) Configurar certificados TLS
# Copia tus certificados a deploy/nginx/certs/

# 4. Crear red externa para Traefik (Obligatorio)
docker network create traefik-net

# 5. Levantar todo el ecosistema
docker compose up -d
```

**Resultado:** En menos de 5 minutos tendrás PaaSify, PostgreSQL, Nginx (con TLS) y cAdvisor ejecutándose.

---

## 3. Arquitectura de Producción

PaaSify en producción se compone de **5 servicios orquestados** que se levantan con un solo `docker compose up -d`:

```mermaid
graph TB
    subgraph "Internet / DNS"
        USER["👨‍🎓 Usuarios"]
        DNS["🌐 Wildcard DNS<br/>*.paasify.com"]
    end

    subgraph "Servidor / VM"
        subgraph "Docker Compose (deploy/)"
            TRAEFIK["🚀 Traefik v3<br/>Entrypoint + DNS Dinámico<br/>:80 / :443"]
            NGINX["🔒 Nginx<br/>Proxy App Principal<br/>(Interno)"]
            APP["⚙️ PaaSify Core<br/>Django + Daphne (ASGI)<br/>:8000 (interno)"]
            DB["🗄️ PostgreSQL 15<br/>Base de datos<br/>:5432 (interno)"]
            CADV["📊 cAdvisor<br/>Monitorización HW<br/>/monitorizacion"]
        end

        subgraph "Contenedores de Alumnos (Red traefik-net)"
            C1["📦 App Alumno 1<br/>sub-1.paasify.com"]
            C2["📦 App Alumno 2<br/>sub-2.paasify.com"]
            CN["📦 ...más servicios"]
        end

        SOCK["/var/run/docker.sock"]
    end

    USER --> DNS
    DNS --> TRAEFIK
    TRAEFIK -->|Host Rule| NGINX
    TRAEFIK -->|Dynamic Rule| C1
    TRAEFIK -->|Dynamic Rule| C2
    NGINX -->|proxy_pass| APP
    NGINX -->|proxy_pass| CADV
    APP -->|SQL| DB
    APP -->|Docker API| SOCK
    SOCK -->|Gestiona| C1
    SOCK -->|Gestiona| C2
    SOCK -->|Gestiona| CN
```

### Docker-outside-of-Docker (DooD)

PaaSify **no ejecuta Docker dentro de Docker**. En su lugar, monta el socket del host (`/var/run/docker.sock`) para crear contenedores "hermanos" directamente en la máquina anfitriona. Esto proporciona:

- **Rendimiento nativo:** los contenedores de alumnos no tienen overhead de virtualización adicional.
- **Acceso por Subdominio:** Traefik detecta automáticamente cada contenedor y le asigna un subdominio (ej: `mi-app-5.paasify.com`).
- **Acceso por puerto real:** el acceso directo por puerto host (rango 40000-50000) sigue disponible como fallback.
- **Gestión centralizada:** PaaSify puede arrancar, parar, inspeccionar y eliminar contenedores directamente.

---

## 4. Configuración de Variables de Entorno

El archivo `.env` dentro de `deploy/` configura **todos** los servicios. Variables principales:

| Variable               | Requerida   | Descripción                                                                                                                                            |
| ---------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `DJANGO_SECRET_KEY`    | ✅          | Clave secreta criptográfica. Generar con: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DJANGO_DEBUG`         | ✅          | **Siempre `False`** en producción                                                                                                                      |
| `DJANGO_ALLOWED_HOSTS` | ✅          | Dominio del servidor (ej: `paas.tfg.etsii.urjc.es`)                                                                                                    |
| `DB_NAME`              | ✅          | Nombre de la base de datos PostgreSQL                                                                                                                  |
| `DB_USER`              | ✅          | Usuario de PostgreSQL                                                                                                                                  |
| `DB_PASSWORD`          | ✅          | Contraseña de PostgreSQL                                                                                                                               |
| `DB_HOST`              | ✅          | `db` (nombre del servicio en compose)                                                                                                                  |
| `DB_PORT`              | ✅          | `5432`                                                                                                                                                 |
| `PAASIFY_BASE_URL`     | Recomendada | URL base pública (ej: `https://paas.tfg.etsii.urjc.es`)                                                                                                |

---

## 5. Certificados TLS y Seguridad

PaaSify divide la responsabilidad del HTTPS en dos partes:
- **Nginx**: Certificado estático proporcionado por tu institución para el dominio principal (`paas.tu-dominio.com`).
- **Traefik**: Certificados dinámicos automáticos (Let's Encrypt) para los contenedores de los alumnos (`app-1.paas.tu-dominio.com`).

### 5.1. Certificado del Dominio Principal (Nginx)

Para HTTPS en tu dominio base, coloca los certificados estáticos en `deploy/nginx/certs/`:

```
deploy/nginx/certs/
├── server.crt      # Certificado del servidor
└── server.key      # Clave privada
```

**Opción A: Certificados Autofirmados (Para pruebas locales)**
```bash
cd deploy/nginx/certs/
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout server.key -out server.crt -subj "/CN=localhost"
```

**Opción B: Certificados válidos (Let's Encrypt externo / Entidad Autorizada)**
1. Cópialos a la carpeta `nginx/certs/` respetando los nombres `server.crt` y `server.key`.
2. Opcional: edita `server_name` en `deploy/nginx/conf.d/paasify.conf` a tu dominio real.

### 5.2. HTTPS Automático para Subdominios (Traefik / Let's Encrypt)

Traefik es capaz de pedir certificados automáticamente a Let's Encrypt a medida que los alumnos crean contenedores.

1. Abre `deploy/docker-compose.yml`.
2. Busca la sección del servicio `traefik`.
3. Descomenta y configura tu email en las siguientes líneas:
   ```yaml
   - "--entrypoints.websecure.address=:443"
   - "--certificatesresolvers.letsencrypt.acme.email=tu-correo@institucion.es" # Cambia esto
   - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
   - "--certificatesresolvers.letsencrypt.acme.tlschallenge=true"
   ```
4. Descomenta el puerto HTTPS exportado al host:
   ```yaml
   ports:
     - "80:80"
     - "443:443" # <-- Descomentar
   ```
5. Esto creará automáticamente certificados válidos cada vez que un servicio nuevo arranca en PaaSify.

---

---

## 6. Monitorización (cAdvisor)

PaaSify incluye **cAdvisor** para monitorizar los recursos de hardware de todos los contenedores:

- **URL:** `https://<tu-dominio>/monitorizacion`
- **Protegido** por contraseña HTTP Basic (configurar con `htpasswd`)
- Muestra CPU, RAM, red y disco por contenedor en tiempo real

```bash
# Requiere instalar apache2-utils (Ubuntu/Debian) o httpd-tools (CentOS/RHEL) para usar htpasswd:
# sudo apt-get install apache2-utils

# Generar contraseña para cAdvisor
cd deploy/nginx/htpasswd/
htpasswd -c .htpasswd admin
```

---

## 7. Administración del Día a Día

### Primer inicio — Crear datos base

Al levantar PaaSify por primera vez, ejecuta los comandos de inicialización **dentro del contenedor**:

```bash
# Entrar al contenedor de PaaSify
docker compose exec paasify bash

# Crear usuarios de demostración
python manage.py create_demo_users

# Poblar catálogo de imágenes Docker
python manage.py populate_example_images
```

### Gestión de usuarios

| Acción              | Cómo                                                                  |
| ------------------- | --------------------------------------------------------------------- |
| Crear admin         | `python manage.py createsuperuser` (dentro del contenedor)            |
| Crear alumnos       | Desde el panel de admin → Perfiles de alumnos → Añadir                |
| Crear profesores    | Desde el panel de admin → Perfiles de profesores → Añadir             |
| Resetear contraseña | Desde el panel de admin → Usuarios → Seleccionar → Cambiar contraseña |

### Ver logs

```bash
# Logs de PaaSify
docker compose logs -f paasify

# Logs de todos los servicios
docker compose logs -f

# Logs de un contenedor de alumno específico
docker logs <container_id>
```

---

## 8. Mantenimiento y Backups

### Backup de la base de datos

```bash
# Crear backup
docker compose exec db pg_dump -U ${DB_USER} ${DB_NAME} > backup_$(date +%Y%m%d).sql

# Restaurar backup
cat backup_20260305.sql | docker compose exec -T db psql -U ${DB_USER} ${DB_NAME}
```

### Limpiar archivos huérfanos

```bash
docker compose exec paasify python manage.py cleanup_media --dry-run  # Previsualizar
docker compose exec paasify python manage.py cleanup_media            # Ejecutar
```

### Actualizar PaaSify

```bash
cd deploy
docker compose pull paasify   # Descargar nueva versión
docker compose up -d paasify  # Reiniciar solo PaaSify
```

---

## 9. Resolución de Problemas

| Problema                                | Solución                                                                                      |
| --------------------------------------- | --------------------------------------------------------------------------------------------- |
| Los contenedores de alumnos no arrancan | Verificar que `/var/run/docker.sock` está montado y es accesible                              |
| Error de puerto en uso                  | Un servicio previo puede haber dejado un puerto reservado. Revisar `PortReservation` en admin |
| Archivos estáticos no cargan            | Ejecutar `docker compose exec paasify python manage.py collectstatic --noinput`               |
| Base de datos no arranca                | Verificar permisos de la carpeta `deploy/volumes/db_data/`                                    |
| WebSocket no funciona                   | Verificar que Nginx tiene configurado `proxy_set_header Upgrade` y `Connection`               |
