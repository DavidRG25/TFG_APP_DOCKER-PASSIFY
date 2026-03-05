# Resumen de Desarrollo e Implementación - v10.1.0 (Despliegue y DooD)

**Fecha:** 2026-03-02
**Objetivo principal:** Preparar la infraestructura de contenedores para el pase a producción (Máquina anfitriona URJC) utilizando la arquitectura Docker-in-Docker (DooD) y automatizar el flujo de Integración y Entrega Continua (CI/CD).

## 1. Gestión de Ramas y Versiones

- Se realizó un volcado completo de la rama `dev2` hacia `develop`.
- Sincronización final desde `develop` hacia la rama principal `main`.
- Etiquetado de la versión estable en Git como `v10.0`.

## 2. Infraestructura como Código (IoC) y Empaquetado

- **Dockerfile:** Creada la receta de construcción de la imagen de PaaSify.
  - Basada en `python:3.10-slim-bullseye`.
  - Instalación del cliente `docker.io` interno para habilitar la capacidad DooD.
  - Reutilización inteligente de los scripts nativos (`run.sh --production`) como _entrypoint_ del contenedor.
- **.dockerignore:** Creado para excluir archivos innecesarios de la construcción (p. ej., `venv`, bases de datos SQLite locales y archivos de documentación), disminuyendo drásticamente el peso de la imagen resultante.
- Archivos locales confidenciales como `.env` y `.docker_credentials` asegurados a través del repositorio con `.gitignore`.
- Eliminado archivo `versiones.txt` obsoleto.

## 3. Entorno de Producción (`deploy/`)

- Mapeo de puertos `40000-50000` y zócalo de Docker local posibilitando a PaaSify orquestar sus propios contenedores adyacentes.
- **`docker-compose.yml` (Producción):** Configurado con 4 servicios clave:
  1. `paasify_core`: Ejecutando la app con soporte DooD y ASGI.
  2. `paasify_db`: Contenedor PostgreSQL nativo y aislado.
  3. `paasify_proxy`: Proxy Nginx.
  4. `paasify_cadvisor`: Recolector de métricas de Hardware expuesto de forma segura y centralizada.
- **Nginx Config (`deploy/nginx/conf.d/paasify.conf`):**
  - Gestión del tráfico SSL/TLS para el dominio real (`paas.tfg.etsii.urjc.es`).
  - Upgrade de proxy para WebSockets (obligatorio para las terminales y logs interactivos en Daphne).
  - Protección activa de cAdvisor vía autenticación básica (`htpasswd`).

## 4. Workflows de CI/CD (Automatización)

- **GitHub Actions (`django_test.yml`):** Creado flujo en `.github/workflows/` para correr de manera automatizada los tests de la plataforma al recibir `push` o `Pull Requests` en las ramas `main` o `develop`, orquestando un contenedor Postgres efímero para ello.
- **Script Local Segurizado (`scripts/build_and_push.sh`):** Creada herramienta de Build & Push que:
  1. Lee del nuevo control de versiones plano `version.txt` (Empezando en `1.0.0`).
  2. Inyecta credenciales locales desde el `.docker_credentials` invisible.
  3. Comprueba preemptivamente el API de _Docker Hub_ evitando el re-etiquetado involuntario.
  4. Levanta el Docker build y limpia las capas basura tras la subida exitosa.

## Siguientes Pasos (Pendientes por el Administrador)

- Ejecutar el script `build_and_push.sh` en local para alojar públicamente en la nube del registro el primer build (`1.0.0`).
- Realizar los Git Push en `main` referenciando el salto de versionado en los Commits (`v10.1.0`).
