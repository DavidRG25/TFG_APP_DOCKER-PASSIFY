# Testing: Verificación Reestructuración Monorepo

**Fecha:** 2026-03-05  
**Plan asociado:** `document/04_planes/plan_reestructuracion_monorepo.md`

---

## 🎯 Objetivo

Verificar que la reestructuración del monorepo no ha roto ninguna funcionalidad del proyecto: servidor Django, rutas estáticas, Docker build, CI/CD y seguridad del repositorio.

---

## ✅ Checklist de Verificación

### 1. Estructura del Repositorio

- [SI] La raíz del repositorio **NO** contiene archivos `.py`.
- [SI] La raíz solo contiene: `.git/`, `.gitattributes`, `.github/`, `.gitignore`, `README.md`, `deploy/`, `paasify_app/`.
- [SI] Todo el código Python está dentro de `paasify_app/`.

### 2. Django (Servidor Local)

Ejecutar desde `paasify_app/`:

```powershell
cd paasify_app
$env:DJANGO_DEBUG="True"
$env:DJANGO_SECRET_KEY="dev-secret-key-for-testing"
python manage.py check
```

- [SI] **Resultado esperado:** `System check identified no issues (0 silenced)`.

```powershell
python manage.py migrate --check
```

- [SI] **Resultado esperado:** Sin migraciones pendientes.

```powershell
python manage.py runserver 0.0.0.0:8000
```

- [SI] **Resultado esperado:** El servidor arranca sin errores.
- [SI] Acceder a `http://localhost:8000` → La interfaz carga correctamente.
- [SI] Los archivos estáticos (CSS, JS, imágenes) se sirven correctamente.
- [SI] Login de usuario funciona.

### 3. Docker Build

Ejecutar desde la **raíz del repositorio**:

```bash
docker build -t paasify-test ./paasify_app
```

- [SI] **Resultado esperado:** La imagen se construye sin errores.
- [SI] El `.dockerignore` dentro de `paasify_app/` excluye correctamente: `venv/`, `.env`, `db.sqlite3`, `document/`, `testing_examples/`, etc.

### 4. Scripts de Utilidad

Ejecutar desde `paasify_app/`:

```bash
# Verificar que run.sh resuelve rutas correctamente
bash run.sh --help
```

- [SI] **Resultado esperado:** Muestra el menú de ayuda sin errores de ruta.

```bash
# Verificar que start.sh resuelve rutas correctamente
bash scripts/start.sh --help
```

- [SI] **Resultado esperado:** Muestra el menú de ayuda o arranca sin errores de ruta.

### 5. Seguridad del Repositorio (.gitignore)

```powershell
# Desde la raíz del repositorio
git ls-files | Select-String -Pattern "\.env$|credentials|secret|\.pem|\.key|\.csr|sqlite3|version\.txt"
```

- [SI] **Resultado esperado:** Solo aparecen archivos `.env.example` (plantillas sin secretos).
- [SI] **NO** aparecen: `.env`, `.docker_credentials`, `db.sqlite3`, `version.txt`, ni certificados.

### 6. GitHub Actions (CI/CD)

Verificar manualmente el archivo `.github/workflows/django_test.yml`:

- [SI] El job `test` tiene `defaults.run.working-directory: ./paasify_app`.
- [SI] `pip install -r requirements.txt` se ejecuta desde `paasify_app/`.
- [SI] `python manage.py test` se ejecuta desde `paasify_app/`.
- [SI] El job `docker-build-check` usa `docker build -t paasify-dry-run ./paasify_app`.

### 7. Deploy de Producción

Verificar que `deploy/docker-compose.yml` **NO ha cambiado**:

- [SI] Sigue usando `image: davidrg25/paasify:latest`.
- [SI] No tiene rutas relativas al código fuente.
- [SI] Solo referencia volúmenes locales (`./volumes/`) y archivos de configuración propios.

---

## 📊 Resumen de Resultados

| #   | Categoría               | Estado |
| --- | ----------------------- | ------ |
| 1   | Estructura repositorio  | ✅     |
| 2   | Django (servidor local) | ✅     |
| 3   | Docker Build            | ✅     |
| 4   | Scripts de utilidad     | ✅     |
| 5   | Seguridad (.gitignore)  | ✅     |
| 6   | GitHub Actions (CI/CD)  | ✅     |
| 7   | Deploy producción       | ✅     |

---

> **Nota:** Marca cada ⬜ con ✅ o ❌ según el resultado de cada prueba.
