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
- **Sincronización con Docker en tiempo real**: detecta contenedores borrados manualmente y actualiza su estado en la base de datos.

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
- **SQLite** para desarrollo.
- **MySQL** o **PostgreSQL** recomendados en producción.

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

### 4. Arranca la app

```bash
# Desarrollo
python manage.py runserver 0.0.0.0:8000

# Produccion ASGI
python -m daphne -b 0.0.0.0 -p 8080 app_passify.asgi:application
```

### 5. Variables de entorno (ejemplo .env)

```
DJANGO_SECRET_KEY=pon_aqui_una_clave_segura
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

### 6. Crear un servicio (resumen)
- Modo imagen por defecto: selecciona una imagen del catalogo, puerto opcional entre 40000-50000 (o dejalo vacio para auto-asignar).
- Modo custom:
  - Dockerfile o docker-compose (exclusivos).
  - Codigo fuente obligatorio en .zip o .rar. Para .rar necesitas la herramienta externa (ver requisitos).

### 7. Pruebas rapidas

```bash
python manage.py test
# o con pytest
pytest
```

### 🛠️ Ejecución rápida con el script `start_app.sh`

Si prefieres automatizar los pasos anteriores, puedes usar el script incluido:

```bash
bash scripts/start_app.sh
```

El script realiza:
1. Crea (si es necesario) el entorno virtual en `./venv` usando el Python disponible en tu sistema.
2. Instala dependencias (`pip install -r requirements.txt`).
3. Ejecuta `python manage.py makemigrations` y `python manage.py migrate`.
4. Arranca Daphne en `0.0.0.0:8080`.

Opciones útiles:
```bash
bash scripts/start_app.sh --skip-install --skip-migrate       # Reutiliza dependencias y migraciones existentes
bash scripts/start_app.sh --port 9000                         # Arranca Daphne en otro puerto
HOST=127.0.0.1 bash scripts/start_app.sh                      # Cambia el host de escucha
```

> Antes de usar el script, asegúrate de tener Python 3 instalado y accesible desde la terminal (`python --version`).

### 👥 Usuarios de ejemplo

Para generar usuarios base (admin, alumno y profesor) ejecuta el comando:

```bash
python manage.py create_demo_users
```

Credenciales creadas:

| Rol        | Usuario    | Contraseña     | Detalles                          |
|------------|------------|----------------|-----------------------------------|
| Admin      | `admin`    | `Admin!123`    | Usuario con `is_staff` + `is_superuser`. |
| Alumno     | `alumno`   | `Alumno!2025`  | Pertenece al grupo `Student`.     |
| Profesor   | `profesor` | `Profesor!2025`| Pertenece al grupo `Teacher`.     |

El comando es idempotente: si los usuarios ya existen, actualizará permisos, email y contraseñas.
