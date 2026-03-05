# Plan: Reestructuración de Arquitectura Monorepo (PaaSify)

**Estado:** COMPLETADO ✅
**Fecha:** 2026-03-02
**Objetivo:** Transicionar el repositorio actual hacia una estructura de "Monorepo" profesional, donde la raíz del repositorio de GitHub actúe como un índice limpio (Despliegue, DevOps y Documentación), encapsulando todo el código fuente del backend y desarrollo en un único subdirectorio.

---

## 1. Motivación y Beneficios

- **Impacto Visual y Profesionalidad:** El repositorio mostrará al tribunal y futuros empleadores una estructura limpia y orientada a microservicios/monorepos.
- **Separación de Responsabilidades:** Separa claramente qué es "Infraestructura/Despliegue" (Deploy, CI/CD) de qué es "Aplicación/Desarrollo" (Backend Django).
- **Seguridad en Rutas:** Django no sufrirá cambios en su `settings.py` ya que su directorio base simplemente será la nueva carpeta encapsulada.

---

## 2. Estructura Propuesta

```text
TFG_APP_DOCKER-PASSIFY/    <-- (Raíz del Repositorio Limpia)
│
├── .github/               # Workflows de CI/CD (GitHub Actions)
├── deploy/                # Producción (VM URJC, docker-compose, nginx)
├── docs/                  # (Opcional - Futuro) Documentación oficial del Repo
├── .gitignore             # Gitignore global (actualizado)
├── README.md              # README global (Índice y vitrina del proyecto) # Debería de tener un quickstart (Descargar en el ordenador rápidamente.)
│
└── paasify_app/           # <-- (NUEVO DIRECTORIO: Aquí va la aplicación actual)
    ├── app_passify/       # Código backend
    ├── containers/        # Apps de contenedores
    ├── document/          # Planes, memorias y recursos de desarrollo
    ├── scripts/           # build_and_push.sh, utilidades, etc.
    ├── Dockerfile         # Dockerfile de la aplicación
    ├── manage.py
    ├── requirements.txt
    ├── venv/              # Entorno virtual local (ignorado)
    └── ... (todo el resto de archivos y carpetas actuales)
```

---

## 3. Fases de Ejecución

### Fase 1: Movimiento de Ficheros Base

1. Crear el nuevo directorio principal: `mkdir paasify_app` (o `source`, `src`, el nombre a elegir).
2. Seleccionar cuidadosamente los archivos de la raíz que **SÍ** se quedan:
   - `.github/`
   - `deploy/`
   - `README.md`
   - `.gitignore` (para modificarlo)
3. Mover usando Git (para no perder el historial de commits):
   `git mv <carpetas_y_archivos> paasify_app/`

### Fase 2: Actualización de Referencias DevOps (Rutas rotas)

Al mover el núcleo de la app, algunos scripts de CI/CD o despliegue en la nueva raíz perderán la pista de dónde está el código:

1. **GitHub Actions (`.github/workflows/django_test.yml`):**
   - Actualizar el directorio de trabajo (`working-directory: ./paasify_app`) para que los tests pasen.
2. **`docker-compose.yml` de Producción (`deploy/`):**
   - No sufre daños graves porque descarga la imagen de DockerHub, pero hay que revisar rutas relativas de volumen si aplicaran.
3. **`.gitignore` y `.dockerignore`:**
   - Asegurar que las rutas aplican correctamente a los archivos dentro de la nueva carpeta.

### Fase 3: Build & Push Script

El script `build_and_push.sh` (actualmente en `scripts/`) se moverá a `paasify_app/scripts/`.

- Validar que al ejecutar `docker build .` desde dentro de `paasify_app`, el contexto sea correcto y el `version.txt` / `.docker_credentials` se lean bien.

### Fase 4: Pruebas Finales antes del Commit

1. Arrancar el entorno local (dentro de `paasify_app`): `python manage.py runserver`
2. Construir imagen Docker local (dentro de `paasify_app`): `docker build -t test .`
3. Validar que la interfaz web (PaaSify) carga sin rutas estáticas rotas.

---

## 4. Criterios de Éxito

- [ ] La raíz del repositorio en GitHub no contiene archivos de código Python (`.py`).
- [ ] El framework GitHub Actions ejecuta los tests correctamente buscando en el nuevo subdirectorio.
- [ ] El script local `build_and_push.sh` genera la imagen de la aplicación con éxito.
- [ ] El `deploy/docker-compose.yml` levanta el ecosistema de producción intacto.
