# 🌐 Guía: Despliegue con DNS Externo (sin certificados propios)

## Contexto

Esta guía documenta el procedimiento completo para desplegar PaaSify cuando:

- El **dominio** está gestionado externamente (ej: Cloudflare, Namecheap, Google Domains…).
- El proveedor DNS apunta un **Wildcard** (`*.tu-dominio.com`) a la IP de tu servidor.
- **No dispones de certificados SSL/TLS** (`.crt` / `.key`) en tu máquina.
- Quieres obtener certificados **automáticamente** con Let's Encrypt a través de Traefik.

> **Ejemplo real:** Un profesor registra el dominio `*.paasify.maes.dev` en Cloudflare y lo apunta a la máquina de la universidad (`193.147.60.40`). El alumno necesita desplegar PaaSify en esa máquina sin tener ningún certificado de mano.

---

## Índice

1. [Arquitectura resultante](#1-arquitectura-resultante)
2. [Prerrequisitos](#2-prerrequisitos)
3. [Paso 1 — Configuración DNS externa (Cloudflare)](#3-paso-1--configuración-dns-externa-cloudflare)
4. [Paso 2 — Configurar `.env`](#4-paso-2--configurar-env)
5. [Paso 3 — Configurar `nginx/conf.d/paasify.conf`](#5-paso-3--configurar-nginxconfdpaasifyconf)
6. [Paso 4 — Configurar `docker-compose.yml`](#6-paso-4--configurar-docker-composeyml)
7. [Paso 5 — Desplegar y verificar](#7-paso-5--desplegar-y-verificar)
8. [Resolución de problemas](#8-resolución-de-problemas)
9. [Referencia rápida de archivos modificados](#9-referencia-rápida-de-archivos-modificados)

---

## 1. Arquitectura resultante

Con esta configuración, el flujo de tráfico funciona así:

```
Usuario (HTTPS)
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  TRAEFIK (:80 / :443)                               │
│  • Recibe TODO el tráfico entrante                   │
│  • Redirige HTTP → HTTPS automáticamente             │
│  • Gestiona certificados Let's Encrypt (TLS Challenge)│
│  • Enruta subdominios de alumnos dinámicamente       │
└──────┬───────────────────────────┬──────────────────┘
       │                           │
       │ Host(`paasify.maes.dev`)  │ Host(`app-5.paasify.maes.dev`)
       ▼                           ▼
┌────────────┐            ┌──────────────────┐
│   NGINX    │            │ Contenedor Alumno│
│  (:80 int) │            │   (Traefik auto) │
│  proxy →   │            └──────────────────┘
│  Django    │
└─────┬──────┘
      │
      ▼
┌────────────┐
│  DJANGO    │
│  (Daphne)  │
│  :8000 int │
└────────────┘
```

**Punto clave:** Traefik termina el TLS (descifra HTTPS) y le pasa tráfico HTTP plano a Nginx. Nginx ya **no necesita certificados** porque nunca ve tráfico cifrado directamente.

---

## 2. Prerrequisitos

| Requisito | Detalle |
|-----------|---------|
| **Dominio configurado** | El Wildcard DNS (`*.paasify.maes.dev`) debe apuntar a la IP pública de tu servidor mediante un **registro A** (Address), que vincula el nombre de dominio con la dirección IPv4 física de la máquina. |
| **Puerto 443 abierto** | Let's Encrypt necesita que el puerto 443 esté accesible desde Internet |
| **Docker + Docker Compose** | Versión 20.10+ de Docker Engine |
| **Red externa de Traefik** | `docker network create traefik-net` (ejecutar una sola vez) |

> ⚠️ **Importante sobre Cloudflare:** Si usas Cloudflare como DNS, el registro debe estar en modo **"DNS Only" (nube gris)**. Si la nube está naranja (Proxy activado), Cloudflare intercepta el tráfico y Let's Encrypt no puede completar la validación del certificado.

---

## 3. Paso 1 — Configuración DNS externa (Cloudflare)

### 3.1. Crear los registros DNS

En el panel de Cloudflare (o tu proveedor DNS), crea estos dos registros:

| Tipo | Nombre | Contenido | Proxy |
|------|--------|-----------|-------|
| `A` | `paasify` | `<IP_DE_TU_SERVIDOR>` | **DNS only** (🔘 gris) |
| `A` | `*.paasify` | `<IP_DE_TU_SERVIDOR>` | **DNS only** (🔘 gris) |

> El registro Wildcard (`*.paasify`) permite que **cualquier subdominio** (como `mi-app-5.paasify.maes.dev`) apunte automáticamente a tu servidor sin crear registros adicionales.

### 3.2. Verificar la resolución DNS

Desde cualquier máquina, comprueba que el dominio resuelve correctamente:

```bash
# Debe devolver la IP de tu servidor
nslookup paasify.maes.dev

# También debe funcionar con subdominios aleatorios
nslookup test123.paasify.maes.dev
```

---

## 4. Paso 2 — Configurar `.env`

El archivo `.env` se encuentra en `deploy/.env`. Si no existe, créalo a partir de `.env.example`:

```bash
cp .env.example .env
nano .env
```

### Variables críticas para DNS externo

Estas son las variables que **debes modificar** respecto a una instalación local:

```ini
# === Django / Backend ===
DJANGO_SECRET_KEY=<tu_clave_secreta_larga_y_aleatoria>
DJANGO_DEBUG=False

# ALLOWED_HOSTS: El punto (.) delante permite TODOS los subdominios automáticamente
# Esto es necesario para que Django acepte peticiones de los servicios de los alumnos
# Ejemplo: .paasify.maes.dev acepta "app-5.paasify.maes.dev", "web-12.paasify.maes.dev", etc.
DJANGO_ALLOWED_HOSTS=.paasify.maes.dev,paasify.maes.dev,localhost,127.0.0.1

# CSRF_TRUSTED_ORIGINS: Django 4.0+ requiere esta variable para aceptar formularios
# enviados desde HTTPS. Sin esto, el login y cualquier POST devolverán error 403 "CSRF Forbidden".
# El wildcard https://*.paasify.maes.dev cubre los subdominios de los alumnos.
DJANGO_CSRF_TRUSTED_ORIGINS=https://paasify.maes.dev,https://*.paasify.maes.dev

# URL base pública: Determina cómo se generan los subdominios de los servicios de alumnos.
# DEBE incluir https:// para que los enlaces generados sean correctos.
PAASIFY_BASE_URL=https://paasify.maes.dev
```

### Ejemplo de `.env` completo

```ini
# === Django / Backend ===
DJANGO_SECRET_KEY=<genera_una_clave_secreta_larga_y_aleatoria>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=.paasify.maes.dev,paasify.maes.dev,localhost,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=https://paasify.maes.dev,https://*.paasify.maes.dev

# === Contraseña del Administrador ===
ADMIN_PASSWORD=MiClaveAdminSegura2026!

# === PaaSify Configuration ===
PAASIFY_BASE_URL=https://paasify.maes.dev

# === Base de Datos ===
DB_NAME=paasify_db
DB_USER=paasify_admin
DB_PASSWORD=mi_password_postgres_segura
DB_HOST=db
DB_PORT=5432

# === Docker Hub (Opcional) ===
DOCKER_HUB_USERNAME=
DOCKER_HUB_PASSWORD=
```

### ¿Por qué cada variable?

| Variable | Propósito | ¿Qué pasa si falta? |
|----------|-----------|---------------------|
| `.paasify.maes.dev` en `ALLOWED_HOSTS` | Permite que Django acepte peticiones a subdominios | Error 400 "Bad Request" al acceder por subdominio |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Autoriza formularios POST desde HTTPS | Error 403 "CSRF verification failed" al hacer login |
| `PAASIFY_BASE_URL` con `https://` | Genera URLs correctas para los servicios de alumnos | Los enlaces de subdominio apuntarán a HTTP en vez de HTTPS |

---

## 5. Paso 3 — Configurar `nginx/conf.d/paasify.conf`

### El problema con la configuración original

La configuración original de Nginx tenía **dos bloques server**:
1. Uno escuchando en el puerto 80 que redirigía a HTTPS.
2. Otro escuchando en el puerto 443 con `listen 443 ssl` que **requería certificados físicos** (`.crt` y `.key`).

**Sin esos certificados, Nginx se niega a arrancar** con el error:
```
nginx: [emerg] no "ssl_certificate" is defined for the "listen ... ssl" directive
```

### La solución: Nginx solo escucha en HTTP (puerto 80)

Como Traefik es quien se encarga de terminar el TLS (descifrar HTTPS), Nginx **nunca recibe tráfico cifrado directamente**. Solo necesita escuchar en el puerto 80.

### Configuración completa de `paasify.conf`

Reemplaza **todo** el contenido de `deploy/nginx/conf.d/paasify.conf` por:

```nginx
server {
    listen 80;
    server_name paasify.maes.dev;

    # 1. Aplicación Principal (PaaSify)
    location / {
        proxy_pass http://paasify_core:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # IMPORTANTE: Forzar "https" en vez de "$scheme"
        # Traefik le habla a Nginx por HTTP (puerto 80), pero el usuario original
        # entró por HTTPS. Si dejamos $scheme, Django recibe "http" y rechaza
        # los formularios CSRF por no coincidir el protocolo.
        proxy_set_header X-Forwarded-Proto https;

        # WebSockets support (para Daphne/ASGI)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 2. Monitorización (cAdvisor) protegido por usuario y contraseña
    location /monitorizacion/ {
        auth_basic "Restricted Access";
        auth_basic_user_file /etc/nginx/htpasswd/.htpasswd;

        proxy_pass http://paasify_cadvisor:8080;
        proxy_redirect default;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # IMPORTANTE: Mismo cambio que arriba
        proxy_set_header X-Forwarded-Proto https;
    }

    # 3. Archivos estáticos de Django
    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
    }

    # 4. Archivos media/subidos
    location /media/ {
        alias /app/media/;
        expires 30d;
    }
}
```

### Cambios clave respecto a la configuración original

| Cambio | Antes | Después | Motivo |
|--------|-------|---------|--------|
| Bloques server | 2 (puerto 80 + puerto 443) | 1 (solo puerto 80) | Traefik maneja TLS, Nginx no necesita certificados |
| `ssl_certificate` | Requerido | **Eliminado** | No hay archivos `.crt`/`.key` |
| `X-Forwarded-Proto` | `$scheme` (dinámico) | `https` (fijo) | Django necesita saber que el usuario original usó HTTPS |
| Redirección HTTP→HTTPS | En Nginx | **En Traefik** (global) | Traefik lo hace antes de que el tráfico llegue a Nginx |

---

## 6. Paso 4 — Configurar `docker-compose.yml`

### Cambios en el servicio `traefik`

La configuración original tenía las líneas de Let's Encrypt **comentadas**. Ahora las activamos y usamos `tlschallenge` en vez de `httpchallenge`:

```yaml
  traefik:
    image: traefik:v3.0
    container_name: paasify_traefik
    restart: unless-stopped
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"

      # Entrypoints: Puerto 80 (HTTP) y 443 (HTTPS)
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"

      # Redirección global: Todo HTTP → HTTPS automáticamente
      # Traefik es lo bastante inteligente para excluir las rutas internas
      # de validación de Let's Encrypt de esta redirección.
      - "--entrypoints.web.http.redirections.entrypoint.to=websecure"
      - "--entrypoints.web.http.redirections.entrypoint.scheme=https"

      # Let's Encrypt: Obtención automática de certificados
      # tlschallenge usa el puerto 443 (no el 80), lo que permite funcionar
      # incluso en redes universitarias donde el puerto 80 está bloqueado
      # por el firewall institucional.
      - "--certificatesresolvers.letsencrypt.acme.email=tu-email@ejemplo.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
      - "--certificatesresolvers.letsencrypt.acme.tlschallenge=true"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./volumes/traefik_certs:/letsencrypt
    networks:
      - traefik-net
```

### ¿Por qué `tlschallenge` y no `httpchallenge`?

Let's Encrypt ofrece varios métodos para verificar que eres dueño de un dominio:

| Método | Puerto | Funcionamiento | Limitación |
|--------|--------|---------------|------------|
| `httpchallenge` | 80 | Let's Encrypt accede a `http://tu-dominio/.well-known/acme-challenge/...` | ❌ No funciona si el firewall bloquea el puerto 80 |
| `tlschallenge` | 443 | Let's Encrypt establece una conexión TLS directa al puerto 443 | ✅ Funciona en redes que bloquean el 80 (universidades) |
| `dnschallenge` | — | Let's Encrypt comprueba un registro TXT en tu zona DNS | ❌ Requiere acceso a la API del proveedor DNS |

En entornos universitarios, el firewall institucional suele **bloquear el puerto 80** pero dejar abierto el 443. Por eso usamos `tlschallenge`.

### Cambios en las labels del servicio `nginx`

La configuración original usaba **TCP routers con TLS passthrough**, que pasan la conexión TLS cruda directamente a Nginx (obligándole a tener certificados). Ahora usamos **HTTP routers** donde Traefik descifra el TLS:

```yaml
  nginx:
    image: nginx:alpine
    container_name: paasify_proxy
    restart: unless-stopped
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./nginx/certs:/etc/nginx/certs:ro
      - ./nginx/htpasswd:/etc/nginx/htpasswd:ro
      - ./volumes/staticfiles:/app/staticfiles:ro
      - ./volumes/media:/app/media:ro
    labels:
      - "traefik.enable=true"
      - "traefik.docker.network=traefik-net"

      # Tráfico HTTPS: Traefik termina el TLS con el certificado de Let's Encrypt
      # y pasa la petición descifrada a Nginx por el puerto 80.
      - "traefik.http.routers.paasify_https.rule=Host(`paasify.maes.dev`)"
      - "traefik.http.routers.paasify_https.entrypoints=websecure"
      - "traefik.http.routers.paasify_https.tls=true"
      - "traefik.http.routers.paasify_https.tls.certresolver=letsencrypt"
      - "traefik.http.services.paasify_https.loadbalancer.server.port=80"
    depends_on:
      - paasify
      - cadvisor
    networks:
      - traefik-net
      - default
```

### Comparativa de labels: Antes vs Después

| Antes (TLS Passthrough) | Después (HTTP Router) | Motivo |
|--------------------------|----------------------|--------|
| `traefik.tcp.routers.*.rule=HostSNI(...)` | `traefik.http.routers.*.rule=Host(...)` | TCP pasa el TLS crudo a Nginx; HTTP lo descifra en Traefik |
| `traefik.tcp.routers.*.tls.passthrough=true` | `traefik.http.routers.*.tls.certresolver=letsencrypt` | Antes Nginx necesitaba cert; ahora Traefik lo gestiona |
| `loadbalancer.server.port=443` | `loadbalancer.server.port=80` | Nginx ya solo escucha en 80 |
| Labels de redirección HTTP→HTTPS (middleware) | Redirección global en entrypoint | Más limpio y no interfiere con Let's Encrypt |

### `docker-compose.yml` completo

```yaml
services:
  # =========================================================
  # 0. TRAEFIK (Reverse Proxy Dinámico para Subdominios)
  # =========================================================
  traefik:
    image: traefik:v3.0
    container_name: paasify_traefik
    restart: unless-stopped
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      
      # Entrypoints y Redirección global a HTTPS
      - "--entrypoints.web.address=:80"
      - "--entrypoints.web.http.redirections.entrypoint.to=websecure"
      - "--entrypoints.web.http.redirections.entrypoint.scheme=https"
      - "--entrypoints.websecure.address=:443"
      
      # Let's Encrypt (TLS Challenge - funciona con puerto 80 bloqueado)
      - "--certificatesresolvers.letsencrypt.acme.email=tu-email@ejemplo.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
      - "--certificatesresolvers.letsencrypt.acme.tlschallenge=true"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./volumes/traefik_certs:/letsencrypt
    networks:
      - traefik-net

  # =========================================================
  # 1. PAASIFY CORE (Backend Django / ASGI)
  # =========================================================
  paasify:
    image: davidrg25/paasify:3.0.0
    container_name: paasify_core
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./volumes/media:/app/media
      - ./volumes/staticfiles:/app/staticfiles
    depends_on:
      db:
        condition: service_healthy
    networks:
      - traefik-net
      - default

  # =========================================================
  # 2. BASE DE DATOS (PostgreSQL)
  # =========================================================
  db:
    image: postgres:15-alpine
    container_name: paasify_db
    restart: unless-stopped
    env_file:
      - .env
    environment:
      POSTGRES_DB: ${DB_NAME:-paasify_db}
      POSTGRES_USER: ${DB_USER:-paasify_admin}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-mypassword}
    volumes:
      - ./volumes/db_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-paasify_admin} -d ${DB_NAME:-paasify_db}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - default

  # =========================================================
  # 3. PROXY INVERSO (Nginx — solo HTTP interno)
  # =========================================================
  nginx:
    image: nginx:alpine
    container_name: paasify_proxy
    restart: unless-stopped
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./nginx/certs:/etc/nginx/certs:ro
      - ./nginx/htpasswd:/etc/nginx/htpasswd:ro
      - ./volumes/staticfiles:/app/staticfiles:ro
      - ./volumes/media:/app/media:ro
    labels:
      - "traefik.enable=true"
      - "traefik.docker.network=traefik-net"
      
      # Tráfico HTTPS → Traefik descifra y pasa a Nginx por puerto 80
      - "traefik.http.routers.paasify_https.rule=Host(`paasify.maes.dev`)"
      - "traefik.http.routers.paasify_https.entrypoints=websecure"
      - "traefik.http.routers.paasify_https.tls=true"
      - "traefik.http.routers.paasify_https.tls.certresolver=letsencrypt"
      - "traefik.http.services.paasify_https.loadbalancer.server.port=80"
    depends_on:
      - paasify
      - cadvisor
    networks:
      - traefik-net
      - default

  # =========================================================
  # 4. MONITORIZACIÓN (cAdvisor)
  # =========================================================
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:v0.47.2
    container_name: paasify_cadvisor
    command: -url_base_prefix=/monitorizacion
    restart: unless-stopped
    privileged: true
    devices:
      - /dev/kmsg:/dev/kmsg
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    networks:
      - traefik-net
      - default

networks:
  traefik-net:
    external: true
  default:
    driver: bridge
```

---

## 7. Paso 5 — Desplegar y verificar

### 7.1. Crear la red de Traefik (solo la primera vez)

```bash
docker network create traefik-net
```

### 7.2. Limpiar certificados antiguos (si existían intentos previos)

Si Traefik ya intentó pedir certificados antes y falló, el archivo `acme.json` puede contener datos corruptos o rate-limited. Bórralo para empezar limpio:

```bash
sudo rm -f volumes/traefik_certs/acme.json
```

### 7.3. Levantar los servicios

```bash
docker-compose down
docker-compose up -d
```

### 7.4. Verificar que Traefik obtuvo el certificado

```bash
# Ver los logs de Traefik (buscar errores de ACME/Let's Encrypt)
docker logs paasify_traefik

# Si todo va bien, NO debería haber líneas "ERR" para tu dominio.
# Traefik es silencioso cuando obtiene el certificado correctamente.
```

### 7.5. Verificar que Nginx está funcionando

```bash
docker logs paasify_proxy
# Debe mostrar: "Configuration complete; ready for start up"
# Sin errores de "ssl_certificate"
```

### 7.6. Probar el acceso

```bash
# Desde el propio servidor:
curl -I https://paasify.maes.dev

# Debe devolver HTTP/2 200 y las cabeceras de Django
```

> 💡 **Tip:** Si acabas de hacer cambios y el navegador sigue mostrando error SSL, abre una **pestaña de incógnito**. Chrome cachea agresivamente los fallos de certificado durante varios minutos.

---

## 8. Resolución de problemas

### Error: `nginx: [emerg] no "ssl_certificate" is defined`

**Causa:** Nginx tiene un bloque `listen 443 ssl` pero no encuentra los archivos de certificado.

**Solución:** Elimina todo el bloque SSL de `paasify.conf`. Con esta guía, Nginx solo debe escuchar en el puerto 80. Traefik maneja el TLS.

---

### Error: `403 Forbidden — Verificación CSRF fallida`

**Causa:** Django no reconoce `https://paasify.maes.dev` como origen de confianza.

**Solución:** Añade en el `.env`:
```ini
DJANGO_CSRF_TRUSTED_ORIGINS=https://paasify.maes.dev,https://*.paasify.maes.dev
```
Y asegúrate de que en `paasify.conf` tienes:
```nginx
proxy_set_header X-Forwarded-Proto https;
```
(No `$scheme`, que enviaría "http" porque Traefik habla por el 80 con Nginx.)

---

### Error: `Timeout during connect (likely firewall problem)`

**Causa:** Let's Encrypt no puede alcanzar tu servidor por el puerto 80.

**Solución:** Usa `tlschallenge` en vez de `httpchallenge` en el docker-compose:
```yaml
# ❌ No funciona con firewall en puerto 80:
- "--certificatesresolvers.letsencrypt.acme.httpchallenge=true"
- "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"

# ✅ Funciona por el puerto 443:
- "--certificatesresolvers.letsencrypt.acme.tlschallenge=true"
```

---

### Error: `rateLimited :: too many failed authorizations`

**Causa:** Has intentado pedir certificados demasiadas veces y Let's Encrypt te ha bloqueado temporalmente (1 hora).

**Solución:**
1. Borra el archivo de caché: `sudo rm volumes/traefik_certs/acme.json`
2. Espera el tiempo indicado en el mensaje de error (generalmente 1 hora).
3. Reinicia Traefik: `docker-compose restart traefik`

---

### Error: `ERR_SSL_UNRECOGNIZED_NAME_ALERT` en el navegador

**Causa:** Traefik no tiene un certificado válido listo para presentar al navegador.

**Solución:**
1. Comprueba los logs de Traefik: `docker logs paasify_traefik`
2. Si no hay errores, espera 30 segundos y recarga la página en modo incógnito.
3. Si hay errores de ACME, sigue las instrucciones del error correspondiente en esta sección.

---

### Los contenedores antiguos generan errores en los logs

**Causa:** Contenedores de un dominio anterior (ej: `adminer-9.paas.tfg.etsii.urjc.es`) siguen corriendo y Traefik intenta pedirles certificado.

**Solución:** Para o elimina esos contenedores que ya no son necesarios:
```bash
# Ver qué contenedores están corriendo
docker ps

# Parar los que ya no necesitas
docker stop adminer-9_ctr
docker rm adminer-9_ctr
```

---

## 9. Referencia rápida de archivos modificados

### Resumen de cambios por archivo

| Archivo | Cambio principal |
|---------|-----------------|
| `deploy/.env` | Añadir `DJANGO_CSRF_TRUSTED_ORIGINS`, prefijo `.` en `ALLOWED_HOSTS`, `PAASIFY_BASE_URL` con `https://` |
| `deploy/nginx/conf.d/paasify.conf` | Eliminar bloque SSL 443, dejar solo puerto 80, cambiar `$scheme` → `https` |
| `deploy/docker-compose.yml` | Activar Let's Encrypt con `tlschallenge`, cambiar labels TCP → HTTP, redirección global en entrypoint |

### Checklist de despliegue

- [ ] DNS Wildcard (`*.tu-dominio.com`) apuntando a la IP del servidor
- [ ] Cloudflare en modo **DNS Only** (nube gris), no Proxy
- [ ] Puerto **443** abierto en el firewall del servidor
- [ ] Red Docker `traefik-net` creada
- [ ] `.env` con `DJANGO_CSRF_TRUSTED_ORIGINS` y `PAASIFY_BASE_URL` configurados
- [ ] `paasify.conf` sin bloques SSL (solo puerto 80)
- [ ] `docker-compose.yml` con `tlschallenge=true` y labels HTTP (no TCP)
- [ ] Archivo `acme.json` limpio (borrado si hubo intentos previos fallidos)
- [ ] `docker-compose up -d` ejecutado
- [ ] Verificación con `docker logs paasify_traefik` sin errores ACME
- [ ] Acceso exitoso a `https://tu-dominio.com` en navegador (modo incógnito)
