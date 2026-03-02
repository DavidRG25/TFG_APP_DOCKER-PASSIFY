# **PaaSify**

---

### Plataforma Educativa para el Despliegue de Aplicaciones con Docker

---

**PaaSify** es una plataforma web educativa que permite a estudiantes desplegar, visualizar y gestionar aplicaciones Docker en contenedores desde una interfaz gráfica. Pensada para facilitar el aprendizaje de tecnologías de virtualización y despliegue, ofrece funciones avanzadas como subida de código, terminal web embebida y soporte completo para Dockerfile y Compose.

---

## **Características Principales**

- **Despliegue de Aplicaciones en Contenedores Docker** desde la interfaz, usando `Dockerfile`, `docker-compose.yml` o un archivo `.zip` con código fuente.
- **Gestión de Asignaturas y Proyectos** para organizar el trabajo de los estudiantes por profesor.
- **Asignación de Roles**:
  - `ADMIN`: gestiona usuarios, asignaturas y permisos.
  - `TEACHER`: asigna proyectos y revisa servicios desplegados.
  - `STUDENT`: despliega servicios, sube código y administra contenedores.
- **Puerto Personalizado**: permite declarar manualmente un puerto dentro del rango permitido.
- **Subida de Archivos**: `Dockerfile`, `docker-compose.yml` y `.zip` del código fuente.
- **Visualización de Archivos y Logs** con resaltado de sintaxis (Prism.js).
- **Terminal Web Interactiva** (basada en WebSocket y xterm.js) para ejecutar comandos en tiempo real dentro del contenedor.
- **Interfaz Reactiva con HTMX** para actualización de paneles, estados y acciones sin recargar la página.
- **Sincronización Inteligente**: Sistema de **Throttling (Cooldown)** y **Atomic Transactions** para garantizar la estabilidad de la base de datos incluso con múltiples usuarios realizando polling.
- **Persistencia de Estado**: Los puertos y configuraciones de servicios Docker Compose se mantienen visibles en la interfaz incluso cuando los contenedores están detenidos.
- **Despliegue Flexible**: Permite desplegar proyectos complejos subiendo un único archivo `.zip` que contenga el `docker-compose.yml` o `Dockerfile` en la raíz.
- **Aislamiento y Seguridad**: Validación estricta de archivos de orquestación, prohibiendo `bind mounts` y configuraciones privilegiadas para proteger el host.

---

## **Tecnologías Utilizadas**

### **Frontend**

- **Bootstrap** para diseño responsivo.
- **HTMX** para interacciones dinámicas sin JavaScript explícito.
- **Prism.js** para resaltado de código fuente.
- **xterm.js** para emulación de terminal en el navegador.

### **Backend**

- **Django** como framework principal.
- **Django REST Framework** para la API.
- **Django Channels** para soporte WebSocket en terminal interactiva.
- **Docker SDK for Python** para interacción directa con el motor Docker.

### **Base de Datos**

- **Híbrida**: Configurada para detectar automáticamente el entorno.
- **SQLite** (por defecto): Ideal para desarrollo local y pruebas rápidas. Incluye optimizaciones de **WAL (Write-Ahead Logging)** y **Throttling** para evitar bloqueos.
- **PostgreSQL**: Recomendado para entornos de producción dockerizados o con alta concurrencia.

---

## **Requisitos del Sistema**

Asegúrate de tener instalado:

- **Python 3.8 o superior**
- **Docker**
- **Docker Compose**
- **Pip** (gestor de paquetes de Python)
- **Daphne** (para entorno de producción con WebSocket)
- **Extractor RAR** (7-Zip, unrar, bsdtar o unar en el PATH) cuando se usen archivos .rar
- **UNRAR_TOOL_PATH** apuntando al ejecutable de 7-Zip/unrar, por ejemplo `C:\Program Files\7-Zip\7z.exe`, para descomprimir RAR

---

## **Instalación y Configuración**

### **Pre-requisitos**

- 📦 **Docker Desktop** debe estar instalado y ejecutándose.
- 🗜️ **Extractor RAR** (solo si usaras archivos .rar): instala y deja en PATH uno de estos binarios:
  - Windows (Chocolatey): `choco install 7zip -y` o `choco install unrar -y`
  - Ubuntu/WSL: `sudo apt-get install p7zip-full` (o `sudo apt-get install unrar`)
  - Si ya tienes 7-Zip, agrega su ruta (p. ej. `C:\Program Files\7-Zip`) al PATH y define `UNRAR_TOOL_PATH` apuntando al ejecutable.

> Nota RAR: define `UNRAR_TOOL_PATH` en tu entorno o `.env` con la ruta al binario de 7-Zip/unrar. El sistema testea y extrae RAR mediante ese comando; si falta, la extraccion fallara con mensaje indicando la ausencia o ruta invalida.

- **Si trabajas en Windows**, para evitar errores con named-pipe y `docker.from_env()`:
  1. Instala y habilita WSL 2 en tu máquina:
     ```powershell
     # Ejecuta en PowerShell como Administrador
     wsl --install
     wsl --set-default-version 2
     ```
  2. Abre Docker Desktop → **Settings → Resources → WSL Integration**.
     - Activa **Enable integration with my default WSL distro**.
     - Pulsa **Refetch distros** y asegúrate de que tu distro Ubuntu aparece marcada.
     - Aplica y reinicia Docker Desktop.
  3. **Abre VS Code dentro de WSL**:
     - Instala la extensión **Remote – WSL** de Microsoft.
     - Pulsa `Ctrl+Shift+P` → **Remote-WSL: Open Folder in WSL…**.
     - Navega a `/mnt/c/Users/david/…/PaaSify/Fase2.4/PaaSify` y abre la carpeta.
     - En la terminal integrada (ya en Ubuntu), instala el entorno y dependencias:
       ```bash
       sudo apt update
       sudo apt install python3-venv python3-pip
       python3 -m venv venv
       source venv/bin/activate
       pip install --upgrade pip
       pip install -r requirements.txt
       ```
     - Ejecuta migraciones y arranca el servidor ASGI:
       ```bash
       python manage.py makemigrations
       python manage.py migrate
       python3 -m daphne -b 0.0.0.0 -p 8080 app_passify.asgi:application
       ```
     - Navega en tu Windows a `http://127.0.0.1:8000/` para ver la app.

---

### 1. Clona el Repositorio

```bash
git clone https://github.com/tu-usuario/paasify.git
cd paasify
```

### 2. Configura el Entorno Virtual

```bash
python -m venv venv
source venv/Scripts/activate  # En Windows sin "source": venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Ejecuta las Migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. (Opcional) Poblar Datos de Ejemplo

#### 4.1. Crear Usuarios de Demostración

Para facilitar las pruebas, puedes crear usuarios de ejemplo con credenciales predefinidas:

```bash
python manage.py create_demo_users
```

Este comando crea 3 usuarios:

- 👤 **Admin:** `admin` / `Admin!123` (Superusuario)
- 👨‍🎓 **Alumno:** `alumno` / `Alumno!2025` (Estudiante)
- 👨‍🏫 **Profesor:** `profesor` / `Profesor!2025` (Profesor)

**Nota:** Este comando es idempotente (puedes ejecutarlo múltiples veces sin duplicar usuarios).

#### 4.2. Crear Imágenes Docker de Ejemplo

Para facilitar el uso de la plataforma, puedes crear imágenes de ejemplo pre-clasificadas por tipo:

```bash
python manage.py populate_example_images
```

Este comando crea 11 imágenes de ejemplo:

- 🌐 **Web/Frontend:** nginx, httpd
- 🗄️ **Base de Datos:** mysql, postgres, mongo, redis
- 🚀 **Generador de API:** strapi, hasura, postgrest
- 📦 **Miscelánea:** python, node

Cada imagen está clasificada con su tipo correspondiente, lo que habilitará funcionalidades específicas a nivel de servicio en futuras versiones.

#### 4.3. Crear Datos de Prueba (Asignaturas, Proyectos y Servicios)

Para tener un entorno con datos realistas listos para interactuar (ideal para testear la API y la interfaz), ejecuta:

```bash
python manage.py create_test_data
```

Este script asume que los usuarios demo ya están creados y genera:

- 🎓 **2 Asignaturas** ("Desarrollo Web Fullstack" y "Sistemas Cloud y Contenedores") asignadas a `profesor`.
- 📂 **2 Proyectos** asignados a `alumno` dentro de dichas asignaturas.
- 📦 **3 Servicios Docker** (React, API Node/Python y Postgres) en estado "creado pero detenido" (`stopped`).

**Nota:** Todos los comandos de población de datos (4.1 y 4.2) se ejecutan automáticamente al usar `bash scripts/start.sh`. El script `create_test_data` se debe invocar manualmente cuando necesites volumen de pruebas.

### 5. Arranca la app

```bash
# Desarrollo
python manage.py runserver 0.0.0.0:8000

# Produccion ASGI
python -m daphne -b 0.0.0.0 -p 8080 app_passify.asgi:application
```

### 6. Variables de entorno (archivo .env)

```bash
# Configuración Básica
DJANGO_SECRET_KEY=pon_aqui_una_clave_segura
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Herramientas Externas
UNRAR_TOOL_PATH="C:/Program Files/7-Zip/7z.exe"

# Base de Datos Híbrida
# Si DB_NAME está vacío, PaaSify usa SQLite automáticamente.
# Para usar PostgreSQL, rellena estos campos:
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
```

### 6. Crear un servicio (resumen)

- **Modo imagen por defecto**: Selecciona una imagen del catálogo, puerto opcional entre 40000-50000.
- **Modo DockerHub**: Introduce cualquier imagen pública y el puerto interno que use (ej: `python:3.9` puerto `5000`).
- **Modo Custom**:
  - **Estructura flexible**: Puedes subir el `Dockerfile` / `docker-compose.yml` por separado O incluirlo dentro del archivo `.zip` del código fuente.
  - El sistema detectará automáticamente la orquestación dentro del paquete.
  - Soporta arquitecturas multi-contenedor complejas (ver ejemplo Mega Stack).

### 7. Pruebas rapidas

```bash
python manage.py test
# o con pytest
pytest
```

## 🚀 Scripts de Ejecución

PaaSify incluye dos scripts principales para facilitar el desarrollo:

### 📦 Primera vez o entorno limpio: `start.sh`

Inicializa el proyecto completo (crea venv, instala dependencias, configura BD y datos de ejemplo):

```bash
bash start.sh
```

**El script realiza:**

1. ✅ Detecta Python disponible (python/py/python3)
2. ✅ Crea entorno virtual en `./venv` (si no existe)
3. ✅ Instala/actualiza dependencias desde `requirements.txt`
4. ✅ Ejecuta `makemigrations` y `migrate`
5. ✅ Crea usuarios de demostración (admin, alumno, profesor)
6. ✅ Pobla imágenes Docker de ejemplo
7. ✅ Recolecta archivos estáticos
8. ✅ Arranca Daphne (servidor ASGI) en `0.0.0.0:8000`

**Opciones disponibles:**

```bash
bash start.sh --skip-install              # No reinstala dependencias
bash start.sh --skip-migrate              # No ejecuta migraciones
bash start.sh --skip-setup                # No crea usuarios ni datos de ejemplo
bash start.sh --port 8080                 # Puerto personalizado
bash start.sh --host 127.0.0.1            # Host personalizado
bash start.sh --help                      # Muestra ayuda completa
```

**Ejemplo combinado:**

```bash
bash start.sh --skip-install --skip-setup --port 9000
```

---

### ⚡ Desarrollo diario: `run.sh`

Ejecuta el servidor rápidamente (asume que el entorno ya está configurado):

```bash
bash run.sh                    # Modo desarrollo (runserver)
bash run.sh --production       # Modo producción (Daphne)
```

**El script realiza:**

1. ✅ Carga variables de entorno desde `.env`
2. ✅ Ejecuta migraciones (rápido si no hay cambios)
3. ✅ Recolecta archivos estáticos
4. ✅ Arranca servidor:
   - **Sin flags**: `runserver` en `127.0.0.1:8000` (desarrollo)
   - **Con `--production`**: Daphne en `0.0.0.0:8000` (producción)

**Opciones disponibles:**

```bash
bash run.sh --production              # Usa Daphne (ASGI) en lugar de runserver
bash run.sh --port 9000               # Puerto personalizado
bash run.sh --host 0.0.0.0            # Host personalizado
bash run.sh --help                    # Muestra ayuda completa
```

**Ejemplos:**

```bash
bash run.sh                                      # Desarrollo local
bash run.sh --production --host 0.0.0.0 --port 8080  # Producción
```

---

### 📝 ¿Cuándo usar cada script?

| Situación                                         | Script     | Comando                    |
| ------------------------------------------------- | ---------- | -------------------------- |
| 🆕 Primera vez que clonas el proyecto             | `start.sh` | `bash start.sh`            |
| 🔄 Actualizaste dependencias (`requirements.txt`) | `start.sh` | `bash start.sh`            |
| 🗑️ Borraste el entorno virtual                    | `start.sh` | `bash start.sh`            |
| ⚙️ Necesitas recrear usuarios/datos de ejemplo    | `start.sh` | `bash start.sh`            |
| 💻 Desarrollo diario (código ya configurado)      | `run.sh`   | `bash run.sh`              |
| 🚀 Prueba rápida en modo producción               | `run.sh`   | `bash run.sh --production` |

> **Nota:** Ambos scripts están disponibles en la raíz del proyecto (`start.sh`, `run.sh`) y en `scripts/` (`scripts/start.sh`, `scripts/run.sh`). Puedes ejecutarlos desde cualquier ubicación.

---

## **Uso de la API con Tokens JWT**

PaaSify incluye autenticación mediante tokens JWT para acceder a la API de forma programática.

### **Generar un Token**

1. Inicia sesión y ve a **Mi Perfil**.
2. En la sección **Bearer Token API**, haz clic en **"Generar Token"**.

### **Usar el Token**

Incluye el token en el header `Authorization`:

```bash
curl -X GET http://localhost:8000/api/containers/ \
  -H "Authorization: Bearer TU_TOKEN_AQUI"
```

---

## **Comandos de Gestión Adicionales**

### **1. Usuarios de Demostración**

Para generar usuarios base (`admin`, `alumno` y `profesor`):

```bash
python manage.py create_demo_users
```

| Rol          | Usuario    | Contraseña      | Detalles              |
| ------------ | ---------- | --------------- | --------------------- |
| **Admin**    | `admin`    | `Admin!123`     | Superusuario (staff). |
| **Alumno**   | `alumno`   | `Alumno!2025`   | Grupo `Student`.      |
| **Profesor** | `profesor` | `Profesor!2025` | Grupo `Teacher`.      |

### **2. Imágenes de Catálogo y Ejemplos**

Para restaurar las imágenes por defecto del catálogo:

```bash
python manage.py populate_example_images
```

#### **Ejemplos de Validación Sugeridos (Carpeta `testing_examples`):**

1. **Simple**: `02_dockerfile_flask_api` (Flask con dashboard Tailwind).
2. **Orquestación**: `02_compose_redis_nginx` (Nginx + Redis).
3. **Mega Stack**: `04_compose_mega_stack` (Stack completo: Gateway + API + Redis + Postgres con flujo de datos interactivo).

### **3. Mantenimiento y Purga**

Para limpiar archivos huérfanos en `media/` de servicios eliminados:

```bash
# Previsualizar (recomendado)
env DJANGO_DEBUG=True python manage.py cleanup_media --dry-run

# Ejecutar limpieza real
env DJANGO_DEBUG=True python manage.py cleanup_media
```

> **⚠️ Nota:** El sistema realiza limpieza automática al borrar servicios. Usa este comando solo para mantenimiento general o depuración.

---

## 🌩️ Despliegue en Producción (Docker-in-Docker)

PaaSify está diseñado para funcionar en entornos de producción orquestando contenedores en la misma máquina anfitriona donde se ejecuta. Esto se logra mediante la arquitectura **Docker-in-Docker (DooD)**.

### **¿Cómo funciona el Docker-in-Docker en PaaSify?**

PaaSify se ejecuta dentro de un contenedor Docker, pero necesita lanzar y gestionar _otros_ contenedores (los proyectos de los alumnos). En lugar de crear contenedores "dentro" del contenedor de PaaSify (lo cual es ineficiente y problemático), se monta el socket de Docker de la máquina anfitriona (`/var/run/docker.sock`) dentro del contenedor de PaaSify.
De esta forma, cuando PaaSify da la orden de arrancar un servicio, este nace como un "contenedor hermano" directamente en la máquina anfitriona, utilizando la red y los puertos reales del servidor.

### **Pasos para Desplegar en una Máquina Virtual (VM)**

Para desplegar PaaSify en un entorno de producción (como una VM de la universidad o proveedor cloud):

1. **Descargar configuración en la VM (Sparse Checkout)**:
   Para no descargar todo el código fuente del backend (que ya está dentro de la imagen Docker), usaremos un clonado disperso para traer únicamente la carpeta `deploy/`:

   ```bash
   mkdir Paasify && cd Paasify
   git clone --no-checkout --sparse https://github.com/DavidRG25/TFG_APP_DOCKER-PASSIFY.git .
   git sparse-checkout set deploy
   git checkout main
   ```

2. **Preparar el entorno de despliegue**:
   Toda la configuración de producción se encuentra encapsulada en la carpeta que acabas de descargar.

   ```bash
   cd deploy
   cp .env.example .env
   # Edita el archivo .env configurando una clave secreta fuerte y contraseñas de BD
   nano .env
   ```

3. **Configurar Certificados TLS y Seguridad**:
   - Copia tus certificados SSL institucionales (`paas.tfg.etsii.urjc.es.crt` y `.key`) en `deploy/nginx/certs/`.
   - Genera una contraseña para proteger el panel de monitorización de hardware (`cAdvisor`):
     ```bash
     cd nginx/htpasswd/
     htpasswd -c .htpasswd admin
     cd ../../
     ```

4. **Levantar la Infraestructura**:
   El sistema desplegará simultáneamente PaaSify (con ASGI habilitado), PostgreSQL, Proxy Nginx y cAdvisor.
   ```bash
   docker compose up -d
   ```

⭐ **Para más información detallada, consulta la guía completa en [deploy/README.md](deploy/README.md).**
