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

---

## **Instalación y Configuración** 

### **Pre-requisitos**

- 📦 **Docker Desktop** debe estar instalado y ejecutándose.  
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
source venv/bin/activate  # En Windows sin "source": venv\Scripts\activate
```

### 3. Instala las Dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecuta las Migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Inicia el servidor ASGI con Daphne

```bash
python3 -m daphne -b 0.0.0.0 -p 8080 app_passify.asgi:application
```
#### Dependiendo de la versión
```bash
python -m daphne -b 0.0.0.0 -p 8080 app_passify.asgi:application
```
