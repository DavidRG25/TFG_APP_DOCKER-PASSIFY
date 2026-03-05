# Resumen: Reestructuración Monorepo PaaSify

**Fecha:** 2026-03-05  
**Estado:** ✅ COMPLETADO  
**Plan asociado:** `document/04_planes/plan_reestructuracion_monorepo.md`

---

## 📋 Objetivo

Transicionar el repositorio hacia una estructura de "Monorepo" profesional donde la raíz actúe como un índice limpio (Despliegue, DevOps y Documentación), encapsulando todo el código fuente del backend/desarrollo dentro de `paasify_app/`.

---

## 🏗 Estructura Final del Repositorio

```text
TFG_APP_DOCKER-PASSIFY/          <-- Raíz limpia del repositorio
│
├── .git/                        # Control de versiones
├── .gitattributes               # Normalización de finales de línea
├── .github/                     # Workflows CI/CD (GitHub Actions)
│   └── workflows/
│       └── django_test.yml      # ← Actualizado con working-directory
├── .gitignore                   # ← Actualizado con patrones de seguridad
├── README.md                    # README global / vitrina del proyecto
├── deploy/                      # Producción (docker-compose de VM URJC, nginx)
│   ├── .env.example
│   ├── docker-compose.yml
│   ├── README.md
│   └── nginx/
│
└── paasify_app/                 # ← TODO el código de la aplicación
    ├── .docker_credentials      # (ignorado por git)
    ├── .dockerignore            # ← Actualizado
    ├── .env                     # (ignorado por git)
    ├── .env.example             # Plantilla de variables de entorno
    ├── Dockerfile               # Dockerfile de la aplicación
    ├── app_passify/             # Settings y configuración Django
    ├── asgi.py                  # Punto de entrada ASGI (Daphne/WebSockets)
    ├── containers/              # App Django de gestión de contenedores
    ├── db.sqlite3               # (ignorado por git)
    ├── docker-compose.yml       # Compose de desarrollo local
    ├── docker_templates/        # Plantillas Docker (futuro)
    ├── document/                # Documentación de desarrollo
    ├── manage.py                # CLI de Django
    ├── media/                   # (ignorado por git)
    ├── paasify/                 # App Django principal (modelos, vistas, etc.)
    ├── requirements.txt         # Dependencias Python
    ├── routing.py               # Routing de WebSockets
    ├── run.bat                  # Lanzador rápido Windows
    ├── run.sh                   # Wrapper para scripts/run.sh
    ├── scripts/                 # build_and_push.sh, run.sh, start.sh
    ├── security/                # Configuración y utilidades de seguridad
    ├── start.sh                 # Wrapper para scripts/start.sh
    ├── staticfiles/             # (ignorado por git)
    ├── templates/               # Plantillas HTML (Django templates)
    ├── testing_examples/        # Ejemplos de Dockerfile, Compose para testing
    ├── venv/                    # (ignorado por git)
    ├── vercel.json              # Config Vercel (legacy)
    └── version.txt              # (ignorado por git)
```

---

## 📝 Cambios Realizados

### Fase 1: Movimiento de Ficheros

| Acción               | Detalle                                                                                                                                                 |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Creado**           | Directorio `paasify_app/`                                                                                                                               |
| **Movido (git mv)**  | `app_passify/`, `containers/`, `document/`, `scripts/`, `paasify/`, `templates/`, `security/`, `testing_examples/`                                      |
| **Movido (git mv)**  | `Dockerfile`, `manage.py`, `requirements.txt`, `asgi.py`, `routing.py`, `run.bat`, `run.sh`, `start.sh`, `vercel.json`, `.dockerignore`, `.env.example` |
| **Movido (manual)**  | `version.txt`, `.docker_credentials`, `.env`, `db.sqlite3`, `media/`, `staticfiles/`, `docker_templates/`, `venv/`                                      |
| **Se queda en raíz** | `.git/`, `.gitattributes`, `.github/`, `.gitignore`, `README.md`, `deploy/`                                                                             |

> ✅ Se usó `git mv` para todos los archivos rastreados, preservando el historial de commits.

### Fase 2: Actualización de Referencias DevOps

| Archivo                                 | Cambios                                                                                                                                                                          |
| --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`.github/workflows/django_test.yml`** | Añadido `defaults.run.working-directory: ./paasify_app` al job `test`. Docker build ahora usa `./paasify_app` como contexto.                                                     |
| **`.gitignore`**                        | Reescrito con patrones globales de seguridad: `.env`, `.docker_credentials`, `*.pem`, `*.key`, `*.csr`, `*.p12`, `*.pfx`, `version.txt` se ignoran en cualquier nivel del árbol. |
| **`paasify_app/.dockerignore`**         | Eliminadas referencias a `deploy/` y `.github/` que ya no existen dentro del contexto de build.                                                                                  |

### Fase 3: Verificación de Scripts

| Script                      | Estado                                                                        |
| --------------------------- | ----------------------------------------------------------------------------- |
| `scripts/build_and_push.sh` | ✅ Sin cambios — `ROOT_DIR` se calcula relativamente (`../` desde `scripts/`) |
| `scripts/run.sh`            | ✅ Sin cambios — misma lógica relativa de `ROOT_DIR`                          |
| `scripts/start.sh`          | ✅ Sin cambios — misma lógica relativa de `ROOT_DIR`                          |
| `deploy/docker-compose.yml` | ✅ Sin cambios — usa imágenes de DockerHub, no rutas relativas                |

### Fase 4: Pruebas

| Prueba                                        | Resultado                                           |
| --------------------------------------------- | --------------------------------------------------- |
| `python manage.py check` desde `paasify_app/` | ✅ "System check identified no issues (0 silenced)" |
| `git ls-files` buscar archivos sensibles      | ✅ Solo `.env.example` (plantillas sin secretos)    |
| `git status` verificar integridad             | ✅ Solo renombrados (R) y modificaciones esperadas  |

---

## ⚠️ Notas Importantes

1. **Para desarrollo local:** Ahora hay que ejecutar `python manage.py runserver` desde **dentro de `paasify_app/`**, no desde la raíz del repositorio.
2. **Para Docker build:** El contexto de build es `paasify_app/` → `docker build -t paasify ./paasify_app`.
3. **El `venv/` es local:** Si se reinstala, ejecutar `python -m venv venv` desde dentro de `paasify_app/`.
4. **El historial de git se preserva** gracias al uso de `git mv`.
