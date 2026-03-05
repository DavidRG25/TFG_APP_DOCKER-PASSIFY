# 🚀 Plan Completo: GitHub Action Oficial de PaaSify

## 📌 Estado: DESARROLLO PENDIENTE

Este documento define el plan técnico completo para crear la **GitHub Action oficial
de PaaSify** (`paasify-deploy-action`), que permitirá a cualquier alumno automatizar
el despliegue de su aplicación desde su repositorio de GitHub.

---

## 📋 Índice

1. [Visión General](#1-visión-general)
2. [Arquitectura de 3 Repos](#2-arquitectura-de-3-repos)
3. [Los 3 Modos de Despliegue](#3-los-3-modos-de-despliegue)
4. [Contrato Técnico de la Action](#4-contrato-técnico-de-la-action)
5. [Plan por Repo: PaaSify Backend](#5-plan-por-repo-paasify-backend)
6. [Plan por Repo: paasify-deploy-action](#6-plan-por-repo-paasify-deploy-action)
7. [Plan por Repo: Mini-Repo (Alumno de ejemplo)](#7-plan-por-repo-mini-repo)
8. [Fases de Desarrollo](#8-fases-de-desarrollo)
9. [Decisiones Arquitectónicas](#9-decisiones-arquitectónicas)

---

## 1. Visión General

### Qué se va a construir

Una **Custom GitHub Action reutilizable** que un alumno añade a su workflow con una
sola línea:

```yaml
- uses: DavidRG25/paasify-deploy-action@v1
  with:
    mode: dockerhub
    paasify_api_url: ${{ secrets.PAASIFY_API_URL }}
    paasify_token: ${{ secrets.PAASIFY_TOKEN }}
    name: mi-app
    image: usuario/mi-app:latest
    internal_port: 8000
    project_id: ${{ secrets.PROJECT_ID }}
    subject_id: ${{ secrets.SUBJECT_ID }}
```

### Qué NO hace la Action

- ❌ NO construye imágenes Docker
- ❌ NO hace push a DockerHub
- ❌ NO ejecuta docker-compose
- ❌ NO se autentica contra registries/DockerHub
- ❌ NO guarda estado

### Qué SÍ hace la Action

- ✅ Valida inputs según el modo elegido
- ✅ Se autentica contra la API de PaaSify (con el token del alumno)
- ✅ Busca si el servicio ya existe (GET por nombre)
- ✅ Si existe → PATCH (actualiza)
- ✅ Si no existe → POST (crea)
- ✅ Devuelve `container_id` como output
- ✅ Soporta 3 modos: `dockerhub`, `custom_dockerfile`, `custom_compose`

---

## 2. Arquitectura de 3 Repos

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        FLUJO COMPLETO                                   │
│                                                                         │
│  Repo del Alumno                    paasify-deploy-action               │
│  ┌──────────────────┐              ┌──────────────────────────┐         │
│  │ 1. Push a main   │              │                          │         │
│  │ 2. Workflow se   │──────────────│  3. Valida inputs        │         │
│  │    dispara       │  uses: ...   │  4. GET /containers/     │         │
│  │                  │              │  5. POST o PATCH         │──────┐  │
│  └──────────────────┘              └──────────────────────────┘      │  │
│                                                                      │  │
│                                    PaaSify Backend                    │  │
│                                    ┌──────────────────────────┐      │  │
│                                    │  6. Recibe petición      │◄─────┘  │
│                                    │  7. Crea/actualiza       │         │
│                                    │     servicio             │         │
│                                    │  8. Ejecuta contenedor   │         │
│                                    └──────────────────────────┘         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Los 3 repos

| Repo                        | URL prevista                                    | Responsabilidad                                                |
| --------------------------- | ----------------------------------------------- | -------------------------------------------------------------- |
| **PaaSify Backend**         | `DavidRG25/TFG_APP_DOCKER-PASSIFY`              | API que recibe los despliegues. Validar, documentar endpoints. |
| **paasify-deploy-action**   | `DavidRG25/paasify-deploy-action` (NUEVO)       | La Custom Action. Composite Action en YAML + bash.             |
| **MiniAPP_Paasify_Testing** | `DavidRG25/MiniAPP_Paasify_Testing` (YA EXISTE) | Repo de pruebas que simula un alumno. Workflows de ejemplo.    |

---

## 3. Los 3 Modos de Despliegue

> ⚠️ **PaaSify solo soporta imágenes públicas en modo `dockerhub`.
> Para proyectos privados o código fuente, utilice el modo `custom`
> (Dockerfile o Docker Compose).**

### Modo A: `dockerhub`

El alumno usa una **imagen pública** de DockerHub. El alumno es responsable de
hacer `docker build` + `docker push` en su workflow **antes** de llamar a la
Action. La imagen DEBE ser pública.

| Campo           | Obligatorio | Descripción                                                                                         |
| --------------- | ----------- | --------------------------------------------------------------------------------------------------- |
| `image`         | ✅ Sí       | Imagen pública (ej: `usuario/mi-app:v1.0`)                                                          |
| `internal_port` | ✅ Sí       | Puerto interno de escucha (ej: `8000`)                                                              |
| `env_vars`      | ⭕ No       | Variables de entorno como JSON string. Se pasan desde GitHub Secrets/Variables del repo del alumno. |

**Formato de envío a la API**: `application/json`

**Ejemplo de uso en workflow**:

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build & Push (lo hace el alumno)
        run: |
          echo ${{ secrets.DOCKERHUB_TOKEN }} | docker login -u ${{ secrets.DOCKERHUB_USERNAME }} --password-stdin
          docker build -t ${{ secrets.DOCKERHUB_USERNAME }}/mi-app:${{ github.sha }} .
          docker push ${{ secrets.DOCKERHUB_USERNAME }}/mi-app:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: DavidRG25/paasify-deploy-action@v1
        with:
          mode: dockerhub
          paasify_api_url: ${{ secrets.PAASIFY_API_URL }}
          paasify_token: ${{ secrets.PAASIFY_TOKEN }}
          name: mi-app
          image: ${{ secrets.DOCKERHUB_USERNAME }}/mi-app:${{ github.sha }}
          internal_port: 8000
          project_id: ${{ secrets.PROJECT_ID }}
          subject_id: ${{ secrets.SUBJECT_ID }}
          env_vars: '{"DEBUG": "false", "SECRET_KEY": "${{ secrets.APP_SECRET }}"}'
```

### Modo B: `custom_dockerfile`

El alumno sube su **código fuente + Dockerfile**. PaaSify construye la imagen
internamente. El código nunca se publica en DockerHub → ideal para proyectos privados.

| Campo             | Obligatorio | Descripción                                         |
| ----------------- | ----------- | --------------------------------------------------- |
| `code_path`       | ✅ Sí       | Ruta al directorio del código a comprimir (ej: `.`) |
| `dockerfile_path` | ✅ Sí       | Ruta al Dockerfile (ej: `./Dockerfile`)             |

**Formato de envío a la API**: `multipart/form-data`

La Action se encarga de:

1. Comprimir `code_path` en un `.zip`
2. Enviar `code=@code.zip` + `dockerfile=@Dockerfile` como form-data

**Ejemplo de uso en workflow**:

```yaml
deploy:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: DavidRG25/paasify-deploy-action@v1
      with:
        mode: custom_dockerfile
        paasify_api_url: ${{ secrets.PAASIFY_API_URL }}
        paasify_token: ${{ secrets.PAASIFY_TOKEN }}
        name: mi-app-privada
        code_path: .
        dockerfile_path: ./Dockerfile
        project_id: ${{ secrets.PROJECT_ID }}
        subject_id: ${{ secrets.SUBJECT_ID }}
```

### Modo C: `custom_compose`

El alumno sube su **código fuente + docker-compose.yml**. PaaSify orquesta
múltiples contenedores internamente. Los puertos se autodetectan desde el
fichero `docker-compose.yml` → **NO se requiere `internal_port`**.

| Campo                 | Obligatorio | Descripción                                             |
| --------------------- | ----------- | ------------------------------------------------------- |
| `code_path`           | ✅ Sí       | Ruta al directorio del código (ej: `.`)                 |
| `docker_compose_path` | ✅ Sí       | Ruta al docker-compose.yml (ej: `./docker-compose.yml`) |

**Formato de envío a la API**: `multipart/form-data`

**Ejemplo de uso en workflow**:

```yaml
deploy:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: DavidRG25/paasify-deploy-action@v1
      with:
        mode: custom_compose
        paasify_api_url: ${{ secrets.PAASIFY_API_URL }}
        paasify_token: ${{ secrets.PAASIFY_TOKEN }}
        name: mi-stack-completo
        code_path: .
        docker_compose_path: ./docker-compose.yml
        project_id: ${{ secrets.PROJECT_ID }}
        subject_id: ${{ secrets.SUBJECT_ID }}
```

---

## 4. Contrato Técnico de la Action

### 4.1 Tipo de Action

**Composite Action** (YAML + bash scripts). No requiere Docker ni JavaScript.
Es la más ligera y fácil de mantener.

### 4.2 Estructura del repo `paasify-deploy-action`

```
paasify-deploy-action/
├── action.yml              ← Definición de la Action (inputs, outputs, steps)
├── scripts/
│   ├── validate.sh         ← Validación de inputs por modo
│   ├── deploy.sh           ← Lógica principal (GET + POST/PATCH)
│   └── zip_code.sh         ← Comprime código para modos custom
├── README.md               ← Documentación para el alumno
├── LICENSE
└── .github/
    └── workflows/
        └── test.yml        ← Tests de la propia Action (opcional)
```

### 4.3 Inputs de la Action

#### Comunes (todos los modos)

| Input             | Obligatorio | Descripción                                         |
| ----------------- | ----------- | --------------------------------------------------- |
| `mode`            | ✅ Sí       | `dockerhub`, `custom_dockerfile` o `custom_compose` |
| `paasify_api_url` | ✅ Sí       | URL base de la API (ej: `http://host:8000/api`)     |
| `paasify_token`   | ✅ Sí       | Token de autenticación del alumno                   |
| `name`            | ✅ Sí       | Nombre del servicio                                 |
| `project_id`      | ✅ Sí       | ID del proyecto en PaaSify                          |
| `subject_id`      | ✅ Sí       | ID de la asignatura en PaaSify                      |
| `container_type`  | ⭕ No       | `web` (default), `api`, `database`, `misc`          |
| `is_web`          | ⭕ No       | `true` (default) o `false`                          |
| `keep_volumes`    | ⭕ No       | `true` (default) o `false`                          |

#### Específicos por modo

| Input                 | `dockerhub`                                    | `custom_dockerfile` | `custom_compose`             |
| --------------------- | ---------------------------------------------- | ------------------- | ---------------------------- |
| `image`               | ✅ Obligatorio                                 | ❌                  | ❌                           |
| `internal_port`       | ✅ Obligatorio                                 | ⭕ Opcional         | ❌ No aplica (autodetectado) |
| `env_vars`            | ⭕ Opcional (JSON string desde GitHub Secrets) | ❌                  | ❌                           |
| `code_path`           | ❌                                             | ✅ Obligatorio      | ✅ Obligatorio               |
| `dockerfile_path`     | ❌                                             | ✅ Obligatorio      | ❌                           |
| `docker_compose_path` | ❌                                             | ❌                  | ✅ Obligatorio               |

### 4.4 Outputs de la Action

| Output         | Descripción                                     |
| -------------- | ----------------------------------------------- |
| `container_id` | ID del servicio creado o actualizado en PaaSify |
| `action_taken` | `created` o `patched`                           |

### 4.5 Lógica de Upsert (Create or Patch)

```
1. GET /api/containers/?project={project_id}
2. Filtrar respuesta por name == input.name
3. IF encontrado:
     → PATCH /api/containers/{id}/ (actualizar imagen/archivos)
4. ELSE:
     → POST /api/containers/ (crear servicio nuevo)
5. OUTPUT: container_id + action_taken
```

### 4.6 Formato del request según modo

**Modo `dockerhub`** → JSON:

```bash
curl -X POST "$API_URL/containers/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "mi-app",
    "mode": "dockerhub",
    "image": "usuario/mi-app:v1.0",
    "internal_port": 8000,
    "env_vars": {"KEY": "VALUE"},
    "project": 13,
    "subject": 1,
    "container_type": "web",
    "is_web": true,
    "keep_volumes": true
  }'
```

**Modo `custom_dockerfile`** → Multipart:

```bash
curl -X POST "$API_URL/containers/" \
  -H "Authorization: Bearer $TOKEN" \
  -F "name=mi-app" \
  -F "mode=custom" \
  -F "code=@code.zip" \
  -F "dockerfile=@Dockerfile" \
  -F "project=1" \
  -F "subject=1" \
  -F "container_type=web"
```

**Modo `custom_compose`** → Multipart:

```bash
curl -X POST "$API_URL/containers/" \
  -H "Authorization: Bearer $TOKEN" \
  -F "name=mi-stack" \
  -F "mode=custom" \
  -F "code=@code.zip" \
  -F "docker_compose=@docker-compose.yml" \
  -F "project=1" \
  -F "subject=1"
```

---

## 5. Plan por Repo: PaaSify Backend

### ¿Qué hacer en `TGF_APP_DOCKER-PASSIFY`?

El backend **ya soporta** los 3 modos de despliegue a nivel de API. Las tareas
aquí son de **validación y documentación**, no de desarrollo nuevo.

### Tareas

#### 5.1 Validar endpoints existentes

- [ ] Confirmar que `POST /api/containers/` acepta los 3 modos:
  - `mode=dockerhub` con JSON (`image`, `internal_port`, `env_vars`)
  - `mode=custom` con multipart (`code` + `dockerfile`)
  - `mode=custom` con multipart (`code` + `docker_compose`)
- [ ] Confirmar que `PATCH /api/containers/{id}/` acepta:
  - Cambio de `image` (para dockerhub)
  - Cambio de `code` + `dockerfile` (para custom)
  - Cambio de `code` + `docker_compose` (para custom)
- [ ] Confirmar que `GET /api/containers/?project={id}` filtra correctamente
- [ ] Confirmar que el token del alumno tiene permisos sobre su project_id y subject_id
  - Si el project_id o subject_id no pertenece al usuario → 403

#### 5.2 Validar seguridad

- [ ] No permitir despliegue de imágenes privadas en modo dockerhub
      (nota: PaaSify intenta hacer `docker pull` y si falla porque es privada,
      devuelve error al alumno → esto ya funciona implícitamente)
- [ ] No permitir ejecución de docker-compose externo (PaaSify controla internamente)

#### 5.3 Documentación API

- [ ] Crear `templates/api_docs/partials/08_cicd/04_action_paasify.md`
  - Explicar qué es la Action
  - Los 3 modos con ejemplos
  - Tabla de secrets necesarios
  - Nota de imágenes públicas en dockerhub
  - Enlace al repo de la Action
- [ ] Actualizar `01_intro.md` del bloque 08_cicd para mencionar la Action
- [ ] (Opcional) Crear endpoint `POST /api/deploy/` simplificado que haga upsert
      internamente → reduce lógica en la Action. **Decisión pendiente.**

#### 5.4 Secrets que el alumno necesita configurar

| Secret               | Dónde se obtiene                  | Usado en         |
| -------------------- | --------------------------------- | ---------------- |
| `PAASIFY_API_URL`    | URL del servidor PaaSify          | Todos los modos  |
| `PAASIFY_TOKEN`      | Panel web → Mi Perfil → Token API | Todos los modos  |
| `PROJECT_ID`         | `GET /api/projects/` o panel web  | Todos los modos  |
| `SUBJECT_ID`         | `GET /api/subjects/` o panel web  | Todos los modos  |
| `DOCKERHUB_USERNAME` | DockerHub (solo si build+push)    | Solo `dockerhub` |
| `DOCKERHUB_TOKEN`    | DockerHub (solo si build+push)    | Solo `dockerhub` |

---

## 6. Plan por Repo: paasify-deploy-action

### ¿Qué crear en `DavidRG25/paasify-deploy-action`?

Este es el repo **NUEVO**. Contiene la Custom GitHub Action.

### Tareas

#### 6.1 Estructura inicial

- [ ] Crear repo público `DavidRG25/paasify-deploy-action` en GitHub
- [ ] Crear `action.yml` con todos los inputs definidos
- [ ] Crear `scripts/validate.sh` → validación de inputs por modo
- [ ] Crear `scripts/deploy.sh` → lógica principal GET + POST/PATCH
- [ ] Crear `scripts/zip_code.sh` → comprimir código para modos custom
- [ ] Crear `README.md` con documentación completa para alumnos

#### 6.2 `action.yml` — Esqueleto

```yaml
name: "PaaSify Deploy"
description: "Despliega tu aplicación en PaaSify automáticamente"
author: "DavidRG25"

inputs:
  # --- Comunes ---
  mode:
    description: "Modo de despliegue: dockerhub, custom_dockerfile, custom_compose"
    required: true
  paasify_api_url:
    description: "URL de la API de PaaSify"
    required: true
  paasify_token:
    description: "Token de autenticación de PaaSify"
    required: true
  name:
    description: "Nombre del servicio"
    required: true
  project_id:
    description: "ID del proyecto en PaaSify"
    required: true
  subject_id:
    description: "ID de la asignatura en PaaSify"
    required: true
  container_type:
    description: "Tipo: web, api, database, misc"
    required: false
    default: "web"
  is_web:
    description: "Es servicio web accesible"
    required: false
    default: "true"
  keep_volumes:
    description: "Conservar volúmenes tras reinicios"
    required: false
    default: "true"

  # --- Modo dockerhub ---
  image:
    description: "Imagen pública DockerHub (solo mode=dockerhub)"
    required: false
  internal_port:
    description: "Puerto interno (obligatorio en dockerhub, opcional en custom_dockerfile)"
    required: false
  env_vars:
    description: "Variables de entorno como JSON string (solo mode=dockerhub, opcional)"
    required: false
    default: "{}"

  # --- Modos custom ---
  code_path:
    description: "Ruta al directorio del código (modos custom)"
    required: false
    default: "."
  dockerfile_path:
    description: "Ruta al Dockerfile (solo mode=custom_dockerfile)"
    required: false
  docker_compose_path:
    description: "Ruta al docker-compose.yml (solo mode=custom_compose)"
    required: false

outputs:
  container_id:
    description: "ID del servicio en PaaSify"
    value: ${{ steps.deploy.outputs.container_id }}
  action_taken:
    description: "Acción realizada: created o patched"
    value: ${{ steps.deploy.outputs.action_taken }}

runs:
  using: "composite"
  steps:
    - name: Validate inputs
      shell: bash
      run: ${{ github.action_path }}/scripts/validate.sh
      env:
        INPUT_MODE: ${{ inputs.mode }}
        INPUT_IMAGE: ${{ inputs.image }}
        INPUT_INTERNAL_PORT: ${{ inputs.internal_port }}
        INPUT_CODE_PATH: ${{ inputs.code_path }}
        INPUT_DOCKERFILE_PATH: ${{ inputs.dockerfile_path }}
        INPUT_DOCKER_COMPOSE_PATH: ${{ inputs.docker_compose_path }}

    - name: Prepare code (custom modes)
      if: inputs.mode == 'custom_dockerfile' || inputs.mode == 'custom_compose'
      shell: bash
      run: ${{ github.action_path }}/scripts/zip_code.sh
      env:
        INPUT_CODE_PATH: ${{ inputs.code_path }}

    - name: Deploy to PaaSify
      id: deploy
      shell: bash
      run: ${{ github.action_path }}/scripts/deploy.sh
      env:
        INPUT_MODE: ${{ inputs.mode }}
        INPUT_API_URL: ${{ inputs.paasify_api_url }}
        INPUT_TOKEN: ${{ inputs.paasify_token }}
        INPUT_NAME: ${{ inputs.name }}
        INPUT_PROJECT_ID: ${{ inputs.project_id }}
        INPUT_SUBJECT_ID: ${{ inputs.subject_id }}
        INPUT_IMAGE: ${{ inputs.image }}
        INPUT_INTERNAL_PORT: ${{ inputs.internal_port }}
        INPUT_ENV_VARS: ${{ inputs.env_vars }}
        INPUT_CONTAINER_TYPE: ${{ inputs.container_type }}
        INPUT_IS_WEB: ${{ inputs.is_web }}
        INPUT_KEEP_VOLUMES: ${{ inputs.keep_volumes }}
        INPUT_DOCKERFILE_PATH: ${{ inputs.dockerfile_path }}
        INPUT_DOCKER_COMPOSE_PATH: ${{ inputs.docker_compose_path }}
```

#### 6.3 `scripts/validate.sh` — Lógica

```bash
#!/bin/bash
set -euo pipefail

echo "🔍 Validando inputs para modo: ${INPUT_MODE}"

case "$INPUT_MODE" in
  dockerhub)
    [[ -z "$INPUT_IMAGE" ]] && echo "❌ Error: 'image' es obligatorio en mode=dockerhub" && exit 1
    [[ -z "$INPUT_INTERNAL_PORT" ]] && echo "❌ Error: 'internal_port' es obligatorio en mode=dockerhub" && exit 1
    echo "✅ Modo dockerhub: image=${INPUT_IMAGE}, port=${INPUT_INTERNAL_PORT}"
    ;;
  custom_dockerfile)
    [[ ! -f "$INPUT_DOCKERFILE_PATH" ]] && echo "❌ Error: Dockerfile no encontrado en ${INPUT_DOCKERFILE_PATH}" && exit 1
    [[ ! -d "$INPUT_CODE_PATH" ]] && echo "❌ Error: Directorio de código no encontrado en ${INPUT_CODE_PATH}" && exit 1
    echo "✅ Modo custom_dockerfile: dockerfile=${INPUT_DOCKERFILE_PATH}, code=${INPUT_CODE_PATH}"
    ;;
  custom_compose)
    [[ ! -f "$INPUT_DOCKER_COMPOSE_PATH" ]] && echo "❌ Error: docker-compose.yml no encontrado en ${INPUT_DOCKER_COMPOSE_PATH}" && exit 1
    [[ ! -d "$INPUT_CODE_PATH" ]] && echo "❌ Error: Directorio de código no encontrado en ${INPUT_CODE_PATH}" && exit 1
    echo "✅ Modo custom_compose: compose=${INPUT_DOCKER_COMPOSE_PATH}, code=${INPUT_CODE_PATH}"
    ;;
  *)
    echo "❌ Error: modo '${INPUT_MODE}' no válido. Usar: dockerhub, custom_dockerfile, custom_compose"
    exit 1
    ;;
esac
```

#### 6.4 `scripts/deploy.sh` — Lógica principal

```bash
#!/bin/bash
set -euo pipefail

API_URL="${INPUT_API_URL}"
TOKEN="${INPUT_TOKEN}"
NAME="${INPUT_NAME}"
PROJECT_ID="${INPUT_PROJECT_ID}"
SUBJECT_ID="${INPUT_SUBJECT_ID}"

# ─── Paso 1: Buscar si ya existe ───
echo "🔍 Buscando servicio '${NAME}' en proyecto ${PROJECT_ID}..."
RESPONSE=$(curl -f -sS \
  -H "Authorization: Bearer ${TOKEN}" \
  "${API_URL}/containers/?project=${PROJECT_ID}")

CONTAINER_ID=$(echo "$RESPONSE" | jq -r ".[] | select(.name == \"${NAME}\") | .id" | head -n 1)

# ─── Paso 2: Decidir POST o PATCH ───
if [ -n "$CONTAINER_ID" ] && [ "$CONTAINER_ID" != "null" ]; then
  ACTION="patched"
  echo "📝 Servicio encontrado (ID: ${CONTAINER_ID}). Actualizando..."
  METHOD="PATCH"
  URL="${API_URL}/containers/${CONTAINER_ID}/"
else
  ACTION="created"
  echo "🆕 Servicio no encontrado. Creando..."
  METHOD="POST"
  URL="${API_URL}/containers/"
fi

# ─── Paso 3: Enviar según modo ───
case "$INPUT_MODE" in
  dockerhub)
    # Construir JSON
    JSON_DATA=$(jq -n \
      --arg name "$NAME" \
      --arg mode "dockerhub" \
      --arg image "$INPUT_IMAGE" \
      --argjson port "${INPUT_INTERNAL_PORT}" \
      --argjson project "${PROJECT_ID}" \
      --argjson subject "${SUBJECT_ID}" \
      --arg ctype "${INPUT_CONTAINER_TYPE:-web}" \
      --argjson is_web "${INPUT_IS_WEB:-true}" \
      --argjson keep_volumes "${INPUT_KEEP_VOLUMES:-true}" \
      '{name: $name, mode: $mode, image: $image, internal_port: $port,
        project: $project, subject: $subject, container_type: $ctype,
        is_web: $is_web, keep_volumes: $keep_volumes}')

    # Añadir env_vars si no está vacío
    if [ -n "$INPUT_ENV_VARS" ] && [ "$INPUT_ENV_VARS" != "{}" ]; then
      JSON_DATA=$(echo "$JSON_DATA" | jq --argjson env "$INPUT_ENV_VARS" '. + {env_vars: $env}')
    fi

    # En PATCH solo enviamos la imagen (y env_vars si hay)
    if [ "$METHOD" == "PATCH" ]; then
      PATCH_DATA="{\"image\": \"${INPUT_IMAGE}\"}"
      if [ -n "$INPUT_ENV_VARS" ] && [ "$INPUT_ENV_VARS" != "{}" ]; then
        PATCH_DATA=$(echo "$PATCH_DATA" | jq --argjson env "$INPUT_ENV_VARS" '. + {env_vars: $env}')
      fi
      JSON_DATA="$PATCH_DATA"
    fi

    RESULT=$(curl -f -sS -X "$METHOD" "$URL" \
      -H "Authorization: Bearer ${TOKEN}" \
      -H "Content-Type: application/json" \
      -d "$JSON_DATA")
    ;;

  custom_dockerfile)
    if [ "$METHOD" == "POST" ]; then
      RESULT=$(curl -f -sS -X POST "$URL" \
        -H "Authorization: Bearer ${TOKEN}" \
        -F "name=${NAME}" \
        -F "mode=custom" \
        -F "code=@/tmp/paasify_code.zip" \
        -F "dockerfile=@${INPUT_DOCKERFILE_PATH}" \
        -F "project=${PROJECT_ID}" \
        -F "subject=${SUBJECT_ID}" \
        -F "container_type=${INPUT_CONTAINER_TYPE:-web}" \
        -F "is_web=${INPUT_IS_WEB:-true}" \
        -F "keep_volumes=${INPUT_KEEP_VOLUMES:-true}")
    else
      RESULT=$(curl -f -sS -X PATCH "$URL" \
        -H "Authorization: Bearer ${TOKEN}" \
        -F "code=@/tmp/paasify_code.zip" \
        -F "dockerfile=@${INPUT_DOCKERFILE_PATH}")
    fi
    ;;

  custom_compose)
    if [ "$METHOD" == "POST" ]; then
      RESULT=$(curl -f -sS -X POST "$URL" \
        -H "Authorization: Bearer ${TOKEN}" \
        -F "name=${NAME}" \
        -F "mode=custom" \
        -F "code=@/tmp/paasify_code.zip" \
        -F "docker_compose=@${INPUT_DOCKER_COMPOSE_PATH}" \
        -F "project=${PROJECT_ID}" \
        -F "subject=${SUBJECT_ID}" \
        -F "container_type=${INPUT_CONTAINER_TYPE:-web}" \
        -F "is_web=${INPUT_IS_WEB:-true}" \
        -F "keep_volumes=${INPUT_KEEP_VOLUMES:-true}")
    else
      RESULT=$(curl -f -sS -X PATCH "$URL" \
        -H "Authorization: Bearer ${TOKEN}" \
        -F "code=@/tmp/paasify_code.zip" \
        -F "docker_compose=@${INPUT_DOCKER_COMPOSE_PATH}")
    fi
    ;;
esac

# ─── Paso 4: Extraer ID y reportar ───
DEPLOYED_ID=$(echo "$RESULT" | jq -r '.id // empty')
echo "container_id=${DEPLOYED_ID}" >> $GITHUB_OUTPUT
echo "action_taken=${ACTION}" >> $GITHUB_OUTPUT
echo ""
echo "✅ Despliegue completado:"
echo "   → Action: ${ACTION}"
echo "   → Container ID: ${DEPLOYED_ID}"
echo "   → Servicio: ${NAME}"
```

#### 6.5 `scripts/zip_code.sh`

```bash
#!/bin/bash
set -euo pipefail

echo "📦 Comprimiendo código desde: ${INPUT_CODE_PATH}"

cd "$INPUT_CODE_PATH"

# Excluir directorios innecesarios
zip -r /tmp/paasify_code.zip . \
  -x ".git/*" \
  -x "node_modules/*" \
  -x "__pycache__/*" \
  -x ".venv/*" \
  -x "venv/*" \
  -x ".env"

SIZE=$(du -h /tmp/paasify_code.zip | cut -f1)
echo "✅ Código comprimido: ${SIZE}"
```

#### 6.6 README.md del repo

- [ ] Descripción de la Action
- [ ] Los 3 modos con ejemplos completos
- [ ] Tabla de inputs
- [ ] Tabla de outputs
- [ ] Tabla de secrets necesarios
- [ ] Nota sobre imágenes públicas
- [ ] Badge de versión
- [ ] Licencia MIT

#### 6.7 Versionado

- [ ] Crear tag `v1` apuntando al commit estable
- [ ] Los alumnos usarán `uses: DavidRG25/paasify-deploy-action@v1`

---

## 7. Plan por Repo: Mini-Repo (Alumno de ejemplo)

### ¿Qué hacer en `MiniAPP_Paasify_Testing`?

Actualmente tiene UN workflow que hace build+push+deploy en modo dockerhub
con lógica manual (curl directo). Se debe **migrar** para usar la Action oficial.

### Tareas

#### 7.1 Migrar workflow existente

- [ ] Reemplazar el paso `deploy-paasify` (curl manual) por `uses: DavidRG25/paasify-deploy-action@v1`
- [ ] Mantener los pasos de build+push (eso lo sigue haciendo el alumno)
- [ ] El workflow actual ya tiene la lógica de check-tag → mantenerla

**Workflow migrado**:

```yaml
name: Build, Push and Deploy to PaaSify

on:
  push:
    branches: ["main"]
    paths:
      - "VERSION"
      - ".github/workflows/deploy.yml"
  workflow_dispatch:

env:
  SERVICE_NAME: miniapp-paasify-testing
  PROJECT_ID: 13
  SUBJECT_ID: 1
  INTERNAL_PORT: 8000

jobs:
  check-tag:
    # ... (se mantiene igual) ...

  build-and-push:
    # ... (se mantiene igual) ...

  deploy-paasify:
    name: Deploy to PaaSify
    needs: [check-tag, build-and-push]
    if: needs.check-tag.outputs.should_deploy == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: DavidRG25/paasify-deploy-action@v1
        with:
          mode: dockerhub
          paasify_api_url: ${{ secrets.PAASIFY_API_URL }}
          paasify_token: ${{ secrets.PAASIFY_TOKEN }}
          name: ${{ env.SERVICE_NAME }}
          image: ${{ secrets.DOCKERHUB_USERNAME }}/${{ env.SERVICE_NAME }}:${{ needs.check-tag.outputs.version }}
          internal_port: ${{ env.INTERNAL_PORT }}
          project_id: ${{ env.PROJECT_ID }}
          subject_id: ${{ env.SUBJECT_ID }}
```

#### 7.2 Crear workflows de ejemplo adicionales (opcional)

- [ ] `.github/workflows/deploy-custom-dockerfile.yml` → ejemplo de modo custom
- [ ] `.github/workflows/deploy-custom-compose.yml` → ejemplo de modo compose

Estos sirven como referencia para los alumnos que quieran usar los otros modos.

#### 7.3 Actualizar README

- [ ] Documentar que usa la Action oficial de PaaSify
- [ ] Explicar los secrets necesarios
- [ ] Enlazar al repo de la Action

---

## 8. Fases de Desarrollo

### Fase 1: Preparar PaaSify Backend

1. Validar que la API soporta los 3 modos correctamente
2. Probar con curl manual cada caso (POST y PATCH)
3. Documentar en `08_cicd/04_action_paasify.md`

### Fase 2: Crear repo paasify-deploy-action

1. Crear repo público en GitHub
2. Implementar `action.yml` + scripts
3. Probar localmente con bash simulado
4. Crear tag `v1`

### Fase 3: Migrar Mini-Repo

1. Reemplazar curl manual por `uses: DavidRG25/paasify-deploy-action@v1`
2. Probar el workflow completo end-to-end
3. Verificar que el upsert funciona (crear y actualizar)

### Fase 4: Testing End-to-End

1. Desde el Mini-Repo, hacer push → verificar que se despliega en PaaSify
2. Probar modo dockerhub (ya funciona)
3. Probar modo custom_dockerfile (nuevo workflow)
4. Probar modo custom_compose (nuevo workflow)
5. Probar PATCH (cambiar versión y re-desplegar)

### Orden de trabajo recomendado

```
Fase 1 (PaaSify) → Fase 2 (Action) → Fase 3 (Mini-Repo) → Fase 4 (Testing)
```

Cada fase depende de la anterior. No se puede probar la Action sin que el
backend esté validado, ni migrar el mini-repo sin tener la Action publicada.

---

## 9. Decisiones Arquitectónicas

### 9.1 ¿Por qué Composite Action y no Docker Action?

| Composite (YAML+bash)                | Docker Action              |
| ------------------------------------ | -------------------------- |
| Se ejecuta directamente en el runner | Necesita construir imagen  |
| Más rápido (~2s setup)               | Más lento (~30s setup)     |
| Más fácil de debuggear               | Requiere Dockerfile propio |
| Suficiente para nuestro caso         | Excesivo para curl + jq    |

### 9.2 ¿Por qué NO un endpoint `/api/deploy/`?

Decisión pendiente. Opciones:

- **Sin endpoint nuevo**: La Action hace GET + POST/PATCH → 2-3 llamadas.
  Funciona bien pero más lógica en la Action.
- **Con endpoint `/api/deploy/`**: PaaSify hace el upsert internamente →
  1 sola llamada. Menos lógica en la Action pero más código en el backend.

**Recomendación**: Empezar sin endpoint nuevo (Fase 1). Si la Action funciona
bien, no es necesario. Si se complica, añadirlo como mejora.

### 9.3 ¿Imágenes privadas?

**NO soportadas.** PaaSify solo hace `docker pull` de imágenes públicas.
Si el pull falla → error 500 con mensaje claro al alumno.

Para código privado → modo `custom` (sube zip, PaaSify construye).

### 9.4 ¿env_vars en modos custom?

No aplica. En custom, las variables de entorno se definen dentro del
Dockerfile (`ENV`) o del docker-compose.yml (`environment:`).
El alumno las controla desde su código, no desde la Action.

En modo `dockerhub`, sí aplica: el alumno las pasa como JSON string
construido desde GitHub Secrets/Variables de su repo.
