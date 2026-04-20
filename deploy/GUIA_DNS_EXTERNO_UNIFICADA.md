# PaaSify — Guía de Despliegue con DNS Externo y Certificados Automáticos

**Autor:** David Rodríguez García  
**Fecha:** Abril 2026  
**Versión:** v12.1.0  

---

## 1. Introducción

Este documento describe el procedimiento completo para desplegar PaaSify cuando el dominio DNS se gestiona **externamente** (ej: Cloudflare) y **no se dispone de certificados SSL/TLS propios** en la máquina del servidor.

En este escenario, Traefik (el reverse proxy ya incluido en la arquitectura) se encarga de obtener certificados SSL de **Let's Encrypt** automáticamente, renovarlos cada 90 días y generar certificados individuales para cada subdominio de alumno de forma dinámica.

### Caso real documentado

El profesor registra el dominio `*.paasify.maes.dev` en Cloudflare apuntando a la IP de la máquina de la universidad (`193.147.60.40`). El alumno despliega PaaSify en esa máquina sin tener ningún certificado SSL de mano.

### Ubicación de la documentación en el repositorio

Toda la documentación generada para esta operativa se encuentra en el repositorio de GitHub en las siguientes rutas:

| Archivo | Ruta en el repositorio | Descripción |
|---------|----------------------|-------------|
| Guía operativa detallada | `deploy/DNS_EXTERNO_SIN_CERTIFICADOS.md` | Paso a paso completo con bloques de código, tablas comparativas y troubleshooting |
| Referencia rápida | `docs/DNS_EXTERNO.md` | Resumen ejecutivo con arquitectura, cambios por archivo y errores frecuentes |
| Este documento (PDF) | `deploy/GUIA_DNS_EXTERNO_UNIFICADA.md` | Versión unificada para distribución |

---

## 2. Arquitectura resultante

Con esta configuración, el flujo de tráfico funciona así:

```
Usuario (HTTPS con candado verde)
      │
      ▼
┌──────────────────────────────────────────────┐
│  CLOUDFLARE (DNS Only - nube gris)           │
│  *.paasify.maes.dev → IP del servidor        │
└──────────────────┬───────────────────────────┘
                   │
      ┌────────────▼────────────────┐
      │      TRAEFIK v3.0           │
      │  • Puertos 80 y 443        │
      │  • Let's Encrypt (TLS)     │
      │  • Redirección HTTP→HTTPS  │
      │  • Enrutamiento dinámico   │
      └───┬──────────────────┬─────┘
          │                  │
          │ paasify.maes.dev │ app-5.paasify.maes.dev
          ▼                  ▼
   ┌────────────┐    ┌──────────────┐
   │   NGINX    │    │  Contenedor  │
   │  (HTTP:80) │    │  del alumno  │
   │  → Django  │    │ (cert auto)  │
   └─────┬──────┘    └──────────────┘
         │
         ▼
   ┌────────────┐
   │  DJANGO    │
   │  (Daphne)  │
   │  :8000 int │
   └────────────┘
```

**Punto clave:** Traefik **termina el TLS** (descifra la conexión HTTPS) y le pasa tráfico HTTP plano a Nginx. Esto elimina la necesidad de que Nginx tenga certificados físicos (`.crt` / `.key`).

---

## 3. Prerrequisitos

| Requisito | Detalle |
|-----------|---------|
| Dominio configurado | El Wildcard DNS (`*.paasify.maes.dev`) debe apuntar a la IP pública de tu servidor mediante un **registro A** (Address), que vincula el nombre de dominio con la dirección IPv4 física de la máquina. |
| Puerto 443 abierto | Let's Encrypt necesita acceso al puerto 443 desde Internet |
| Docker + Docker Compose | Versión 20.10+ de Docker Engine |
| Red externa de Traefik | `docker network create traefik-net` (ejecutar una sola vez) |
| Cloudflare en DNS Only | La nube debe estar **gris** (no naranja/proxy) |

---

## 4. Archivos modificados

Se necesitan cambios en **3 archivos** dentro de la carpeta `deploy/`:

### 4.1. Archivo `deploy/.env` — Variables de entorno de Django

Las variables críticas que hay que configurar son:

```ini
# === Django / Backend ===
DJANGO_SECRET_KEY=<genera_una_clave_secreta_larga_y_aleatoria>
DJANGO_DEBUG=False

# El punto (.) delante permite TODOS los subdominios automáticamente
# Ejemplo: .paasify.maes.dev acepta "app-5.paasify.maes.dev", etc.
DJANGO_ALLOWED_HOSTS=.paasify.maes.dev,paasify.maes.dev,localhost,127.0.0.1

# NUEVO Y CRÍTICO: Sin esta línea, el login devuelve error 403 "CSRF Forbidden"
# Django 4.0+ requiere autorizar explícitamente los orígenes HTTPS
DJANGO_CSRF_TRUSTED_ORIGINS=https://paasify.maes.dev,https://*.paasify.maes.dev

# URL base pública con HTTPS para que los enlaces de subdominio sean correctos
PAASIFY_BASE_URL=https://paasify.maes.dev

# === Base de Datos ===
DB_NAME=paasify_db
DB_USER=paasify_admin
DB_PASSWORD=<contraseña_segura>
DB_HOST=db
DB_PORT=5432
```

**¿Por qué cada variable?**

| Variable | Propósito | Qué pasa si falta |
|----------|-----------|-------------------|
| `.paasify.maes.dev` en `ALLOWED_HOSTS` | Permite que Django acepte subdominios | Error 400 "Bad Request" |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Autoriza formularios POST desde HTTPS | Error 403 "CSRF verification failed" al hacer login |
| `PAASIFY_BASE_URL` con `https://` | Genera URLs correctas para servicios | Los enlaces apuntarán a HTTP en vez de HTTPS |

---

### 4.2. Archivo `deploy/nginx/conf.d/paasify.conf` — Proxy inverso Nginx

#### El problema con la configuración original

La configuración original tenía **dos bloques server**: uno redirigiendo HTTP a HTTPS y otro escuchando en el puerto 443 con `listen 443 ssl` que **requería certificados físicos**. Sin esos archivos (`.crt` y `.key`), Nginx se niega a arrancar:

```
nginx: [emerg] no "ssl_certificate" is defined for the "listen ... ssl" directive
```

#### La solución

Como Traefik termina el TLS, Nginx **nunca recibe tráfico cifrado**. Solo necesita escuchar en el puerto 80. El archivo debe quedar así:

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
        # Traefik le habla a Nginx por HTTP (puerto 80), pero el usuario
        # original entró por HTTPS. Si dejamos $scheme, Django recibe
        # "http" y rechaza los formularios CSRF por no coincidir.
        proxy_set_header X-Forwarded-Proto https;

        # WebSockets support (para Daphne/ASGI)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 2. Monitorización (cAdvisor)
    location /monitorizacion/ {
        auth_basic "Restricted Access";
        auth_basic_user_file /etc/nginx/htpasswd/.htpasswd;

        proxy_pass http://paasify_cadvisor:8080;
        proxy_redirect default;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
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

#### Resumen de cambios respecto a la configuración original

| Cambio | Antes | Después | Motivo |
|--------|-------|---------|--------|
| Bloques server | 2 (puerto 80 + 443) | 1 (solo puerto 80) | Traefik maneja TLS |
| `ssl_certificate` | Requerido | Eliminado | No hay archivos `.crt`/`.key` |
| `X-Forwarded-Proto` | `$scheme` (dinámico) | `https` (fijo) | Django necesita saber que el usuario usó HTTPS |
| Redirección HTTP→HTTPS | En Nginx | En Traefik (global) | Traefik lo hace antes |

---

### 4.3. Archivo `deploy/docker-compose.yml` — Orquestación

#### Cambios en el servicio Traefik

Se activa Let's Encrypt con `tlschallenge` (validación por puerto 443) y la redirección global HTTP→HTTPS:

```yaml
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
```

#### ¿Por qué `tlschallenge` y no `httpchallenge`?

| Método | Puerto | Funciona con firewall en puerto 80 |
|--------|--------|------------------------------------|
| `httpchallenge` | 80 | No — el firewall de la universidad lo bloquea |
| `tlschallenge` | 443 | Sí — el puerto 443 suele estar abierto |

#### Cambios en las labels del servicio Nginx

Se eliminan las labels TCP (que forzaban a Nginx a tener certificados) y se sustituyen por HTTP (donde Traefik descifra el TLS):

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
```

#### Comparativa de labels — Antes vs Después

| Antes (TLS Passthrough) | Después (HTTP Router) |
|--------------------------|----------------------|
| `traefik.tcp.routers.*.rule=HostSNI(...)` | `traefik.http.routers.*.rule=Host(...)` |
| `traefik.tcp.routers.*.tls.passthrough=true` | `traefik.http.routers.*.tls.certresolver=letsencrypt` |
| `loadbalancer.server.port=443` | `loadbalancer.server.port=80` |

---

## 5. Certificados automáticos para subdominios de alumnos

PaaSify genera automáticamente las labels de Traefik para cada contenedor de alumno (en `containers/services.py`). Cuando un alumno crea un servicio, el código inyecta:

```python
labels.extend([
    f"traefik.http.routers.{router_name}.entrypoints=web,websecure",
    f"traefik.http.routers.{router_name}.tls.certresolver=letsencrypt",
])
```

Esto hace que Traefik solicite un certificado individual a Let's Encrypt para cada subdominio nuevo (ej: `mi-app-5.paasify.maes.dev`), de forma **completamente automática** y sin intervención del administrador ni del alumno.

---

## 6. Pasos de despliegue

```bash
# 1. Crear la red de Traefik (solo la primera vez)
docker network create traefik-net

# 2. Limpiar certificados antiguos si los hubiera
sudo rm -f volumes/traefik_certs/acme.json

# 3. Levantar todos los servicios
docker-compose down
docker-compose up -d

# 4. Verificar que Traefik obtuvo el certificado
docker logs paasify_traefik
# (No debería haber líneas "ERR" para paasify.maes.dev)

# 5. Verificar que Nginx arrancó sin errores
docker logs paasify_proxy
# (Debe mostrar "Configuration complete; ready for start up")
```

---

## 7. Resolución de problemas encontrados

Durante la configuración real de este despliegue nos encontramos con varios problemas que quedan documentados para futuras referencias:

### 7.1. Nginx no arranca — `no "ssl_certificate" is defined`

**Causa:** El bloque `listen 443 ssl` en `paasify.conf` requiere certificados físicos que no existen.

**Solución:** Eliminar el bloque SSL completo. Nginx solo escucha en el puerto 80 porque Traefik gestiona el TLS.

### 7.2. Error 403 al hacer login — `Verificación CSRF fallida`

**Causa:** Dos problemas simultáneos:
1. Django no reconoce `https://paasify.maes.dev` como origen de confianza.
2. Nginx envía `X-Forwarded-Proto: http` (por usar `$scheme`) cuando el usuario realmente entró por HTTPS.

**Solución:**
- Añadir `DJANGO_CSRF_TRUSTED_ORIGINS=https://paasify.maes.dev,https://*.paasify.maes.dev` al `.env`.
- Cambiar `proxy_set_header X-Forwarded-Proto $scheme;` por `proxy_set_header X-Forwarded-Proto https;` en `paasify.conf`.

### 7.3. Let's Encrypt falla — `Timeout during connect (firewall)`

**Causa:** El firewall de la red de la universidad bloquea el puerto 80. Let's Encrypt no puede completar el HTTP Challenge.

**Solución:** Usar `tlschallenge` en vez de `httpchallenge` en el `docker-compose.yml`, ya que valida por el puerto 443 que sí está abierto.

### 7.4. Let's Encrypt bloqueado — `rateLimited :: too many failed authorizations`

**Causa:** Demasiados intentos fallidos en poco tiempo. Let's Encrypt bloquea temporalmente (1 hora).

**Solución:**
1. Borrar el archivo de caché: `sudo rm volumes/traefik_certs/acme.json`
2. Esperar el tiempo indicado en el mensaje de error.
3. Reiniciar Traefik: `docker-compose restart traefik`

### 7.5. Navegador muestra error SSL tras arreglar el servidor

**Causa:** Chrome cachea agresivamente los fallos de certificado durante varios minutos.

**Solución:** Abrir una **pestaña de incógnito** para verificar el estado real de la web.

### 7.6. Contenedores antiguos generan errores continuos en logs

**Causa:** Contenedores del dominio anterior (`*.paas.tfg.etsii.urjc.es`) siguen corriendo y Traefik intenta pedirles certificados.

**Solución:** Parar y eliminar esos contenedores que ya no son necesarios:
```bash
docker ps
docker stop <nombre_contenedor>
docker rm <nombre_contenedor>
```

---

## 8. Checklist de verificación

- [x] DNS Wildcard (`*.paasify.maes.dev`) apuntando a la IP del servidor
- [x] Cloudflare en modo DNS Only (nube gris)
- [x] Puerto 443 abierto en el firewall del servidor
- [x] Red Docker `traefik-net` creada
- [x] `.env` con `DJANGO_CSRF_TRUSTED_ORIGINS` y `PAASIFY_BASE_URL`
- [x] `paasify.conf` sin bloques SSL (solo puerto 80) y con `X-Forwarded-Proto https`
- [x] `docker-compose.yml` con `tlschallenge=true` y labels HTTP (no TCP)
- [x] Certificados Let's Encrypt obtenidos automáticamente por Traefik
- [x] Acceso exitoso a `https://paasify.maes.dev` con candado verde
- [x] Login funcional sin error CSRF
