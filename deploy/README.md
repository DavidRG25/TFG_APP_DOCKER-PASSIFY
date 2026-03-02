# 🚀 Guía de Despliegue de PaaSify a Producción

Este directorio contiene todo lo necesario para montar la infraestructura final de **PaaSify** en la máquina virtual o servidor de producción (Docker-in-Docker, PostgreSQL, Nginx para proxy/TLS, y cAdvisor para monitorización).

## 📋 Requisitos Previos en la Máquina Destino

Asegúrate de tener instalados en el servidor:

- **Docker Engine** (y permisos de ejecución sin sudo, o lanzar comandos con root)
- **Docker Compose** (V2 recomendada: `docker compose`)
- Herramienta para generar contraseñas HTTP: `htpasswd` (parte de `apache2-utils` en Ubuntu).

---

## 🛠️ Paso 1: Configurar Variables de Entorno (.env)

El archivo `docker-compose.yml` depende de un archivo `.env` que debe estar **en la misma carpeta** o en el directorio raíz del proyecto al pasarlo a producción.

Crea un archivo `.env` tomando como base el `.env.example`. Las variables críticas de Base de Datos deben estar así:

> **💡 Tip:** Para generar una `DJANGO_SECRET_KEY` segura y aleatoria directamente desde la terminal de tu servidor, ejecuta este comando y copia el resultado:
>
> ```bash
> python3 -c "import secrets; import string; chars = string.ascii_letters + string.digits + '+-/_!*()'; print(''.join(secrets.choice(chars) for i in range(50)))"
> ```

```ini
# Pega aquí el resultado del comando anterior
DJANGO_SECRET_KEY=tu_secreto_seguro_y_distinto_a_desarrollo
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=paas.tfg.etsii.urjc.es,localhost,127.0.0.1

# Estas 3 variables las leerá PostgreSQL al crearse por primera vez
# y también PaaSify para conectarse a ella
DB_NAME=paasify_db
DB_USER=paasify_admin
DB_PASSWORD=tu_password_fuerte
DB_HOST=db
DB_PORT=5432
```

_Nota importante:_ El host de la DB debe ser `db` porque así se llama el servicio de Postgres en la red del `docker-compose`.

---

## 🔒 Paso 2: Certificados SSL (TLS) para Nginx

Para que el dominio `paas.tfg.etsii.urjc.es` funcione por HTTPS, Nginx necesita el certificado y la clave que provea la universidad.

1. Dentro de la carpeta `deploy/nginx/certs/`, coloca directamente los archivos finales cuando te los den:
   - `paas.tfg.etsii.urjc.es.crt` (O el archivo del certificado completo `.pem` / `.cer`)
   - `paas.tfg.etsii.urjc.es.key` (Tu clave privada actual)
2. Asegúrate de que los nombres de los archivos correspondan exactamente a lo declarado en `deploy/nginx/conf.d/paasify.conf`.

---

## 🛡️ Paso 3: Proteger el Panel de cAdvisor (Usuario y Clave)

El servicio de métricas de hardware (`cAdvisor`) es interceptado por Nginx para evitar acceso público. Necesitas generar un archivo de credenciales.

En tu máquina anfitriona (Linux), ejecuta:

```bash
# Entra a la carpeta de htpasswd
cd deploy/nginx/htpasswd/

# Crea el archivo con el usuario 'admin' (te pedirá ingresar una clave por terminal)
htpasswd -c .htpasswd admin
```

_Importante:_ No subas el archivo `.htpasswd` al repositorio de git.

---

## 🚀 Paso 4: Levantar la Arquitectura (Arrancar)

Cuando hayas publicado la imagen de PaaSify en Docker Hub (ej: `davidrg25/paasify:v10.1.0`), actualiza la línea `image:` en el `docker-compose.yml` para que apunte a la versión correcta en lugar de `latest`, o asegúrate de haber hecho push del tag `latest`.

Finalmente dirígete a la carpeta `deploy/` y ejecuta:

```bash
docker-compose up -d
```

### Comprobaciones posteriores:

- Ver el estado vital de los servicios: `docker compose ps`
- Leer logs de Daphne/Django: `docker compose logs -f paasify`
- Leer logs de la BD: `docker compose logs -f db`
- Leer logs del proxy: `docker compose logs -f nginx`

¡PaaSify estará sirviendo en `https://paas.tfg.etsii.urjc.es` y monitorizado en la ruta `/monitorizacion/`!
