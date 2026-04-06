# Plan de Testing - GitHub Action Oficial de PaaSify

**Fecha Inicio**: 05/04/2026  
**Fecha Finalización**: 07/04/2026  
**Tipo**: Testing de Integración CI/CD — GitHub Action  
**Estado**: ✅ COMPLETADO

---

## 📋 **ALCANCE DE ESTE DOCUMENTO**

Este documento cubre el testing de la GitHub Action oficial `DavidRG25/paasify-deploy-action@v1`, que permite desplegar aplicaciones en PaaSify desde un workflow de GitHub Actions.

- ✅ Modo `dockerhub` — crear servicio nuevo
- ✅ Modo `dockerhub` — actualizar servicio existente (upsert)
- ✅ Modo `custom_dockerfile` — crear desde código + Dockerfile
- ✅ Modo `custom_compose` — crear desde código + docker-compose.yml
- ✅ Errores esperados (token inválido, project_id incorrecto)

**Repositorio de pruebas**: `DavidRG25/MiniAPP_Paasify_Testing`  
**Repositorio de la Action**: `DavidRG25/paasify-deploy-action`

---

## 🔧 CONFIGURACIÓN PREVIA

Antes de ejecutar los tests, verificar que los siguientes secrets están configurados en `MiniAPP_Paasify_Testing`:

| Secret               | Valor esperado                     |
| -------------------- | ---------------------------------- |
| `PAASIFY_API_URL`    | URL base de la API sin `/` final   |
| `PAASIFY_TOKEN`      | Token válido del usuario de prueba |
| `PROJECT_ID`         | ID de un proyecto propio           |
| `SUBJECT_ID`         | ID de una asignatura propia        |
| `DOCKERHUB_USERNAME` | Usuario de DockerHub               |
| `DOCKERHUB_TOKEN`    | Token de acceso de DockerHub       |

---

## 🧪 TESTING MODO DOCKERHUB

### **Test 1.1: Crear Servicio Nuevo (Modo dockerhub)**

**Objetivo**: Verificar que la Action crea un servicio desde cero cuando no existe

**Pasos**:

1. Asegurarse de que no existe ningún servicio llamado `miniapp-paasify` en el proyecto
2. Hacer `push` a la rama `main` del repo `MiniAPP_Paasify_Testing`
3. Observar la ejecución en la pestaña **Actions** de GitHub

**Verificar**:

- [SI] El workflow se dispara automáticamente al hacer push
- [SI] El step `🚀 Deploy to PaaSify` completa sin errores
- [SI] En los logs aparece: `Creando nuevo servicio...` o similar
- [SI] El output `action_taken` es `created`
- [SI] El output `container_id` tiene un valor numérico
- [SI] El servicio aparece en el panel de PaaSify con estado `running` o `creating`

**Resultado Esperado**: ✅ Servicio creado correctamente desde la Action

---

### **Test 1.2: Actualizar Servicio Existente (Upsert)**

**Objetivo**: Verificar que si el servicio ya existe, la Action lo actualiza (PATCH) en lugar de crear uno nuevo

**Pasos**:

1. Partir del estado con el servicio ya creado (Test 1.1 completado)
2. Hacer un segundo `push` a `main` (por ejemplo, cambiar cualquier línea del código)
3. Observar la ejecución en GitHub Actions

**Verificar**:

- [SI] El workflow se dispara
- [SI] Los logs muestran que encontró el servicio existente
- [SI] El output `action_taken` es `updated`
- [SI] El `container_id` coincide con el del Test 1.1
- [SI] No se crea un servicio duplicado en PaaSify

**Resultado Esperado**: ✅ Servicio actualizado sin duplicados

---

## 🧪 TESTING MODO CUSTOM DOCKERFILE

### **Test 2.1: Despliegue con Dockerfile Personalizado**

**Objetivo**: Verificar que la Action comprime el código, lo sube y PaaSify construye la imagen

**Pasos**:

1. Ir a la pestaña **Actions** → workflow `Deploy Custom Dockerfile to PaaSify`
2. Ejecutar manualmente con **Run workflow**
3. Observar la ejecución

**Verificar**:

- [SI] El step `📦 Prepare code (zip)` se ejecuta (solo en modos custom)
- [SI] El step `🚀 Deploy to PaaSify` completa sin errores
- [SI] Los logs no muestran error en el zip ni en el upload
- [SI] El servicio `miniapp-custom-dockerfile` aparece en PaaSify

**Datos de Prueba**:

```
Workflow: deploy-custom-dockerfile.yml
Modo: custom_dockerfile
Nombre del servicio: miniapp-custom-dockerfile
Dockerfile: ./examples/dockerfile/Dockerfile
```

**Resultado Esperado**: ✅ Servicio creado desde Dockerfile personalizado

---

## 🧪 TESTING MODO CUSTOM COMPOSE

### **Test 3.1: Despliegue con Docker Compose**

**Objetivo**: Verificar que la Action sube el compose y PaaSify orquesta los contenedores

**Pasos**:

1. Ir a la pestaña **Actions** → workflow `Deploy Custom Compose to PaaSify`
2. Ejecutar manualmente con **Run workflow**
3. Observar la ejecución

**Verificar**:

- [SI] El step de zip se ejecuta correctamente
- [SI] El step de deploy completa sin errores
- [SI] El servicio `miniapp-custom-compose` aparece en PaaSify
- [SI] PaaSify detecta los servicios del compose (`web` + `redis`)

**Datos de Prueba**:

```
Workflow: deploy-custom-compose.yml
Modo: custom_compose
Nombre del servicio: miniapp-custom-compose
Compose: ./examples/compose/docker-compose.yml
```

**Resultado Esperado**: ✅ Servicio multi-contenedor creado desde docker-compose.yml

---

## 🧪 TESTING DE ERRORES

### **Test 4.1: Token Inválido**

**Objetivo**: Verificar que la Action falla de forma clara cuando el token es incorrecto

**Pasos**:

1. Cambiar temporalmente el secret `PAASIFY_TOKEN` a un valor inválido (`token-falso`)
2. Ejecutar el workflow manualmente
3. Observar el error

**Verificar**:

- [SI] El workflow falla con error visible
- [SI] Los logs muestran `401` o `Unauthorized`
- [SI] El step falla con código de salida distinto de 0 (gracias a `set -e`)
- [SI] No se crea ningún servicio en PaaSify

**Resultado Esperado**: ✅ Fallo claro y controlado ante token inválido

---

### **Test 4.2: Project ID Incorrecto**

**Objetivo**: Verificar que la API devuelve 403 cuando el proyecto no pertenece al usuario

**Pasos**:

1. Cambiar el secret `PROJECT_ID` a un ID que no pertenezca al usuario
2. Ejecutar el workflow manualmente
3. Observar el error

**Verificar**:

- [SI] El workflow falla
- [SI] Los logs muestran `403` o `Forbidden`
- [SI] No se crea ningún servicio

**Resultado Esperado**: ✅ Fallo claro ante proyecto no autorizado

---

## 📊 RESUMEN DE TESTING

### **Total de Tests**: 6

**Por Categoría**:

- Modo dockerhub: 2 tests
- Modo custom_dockerfile: 1 test
- Modo custom_compose: 1 test
- Errores: 2 tests

**Estado**:

- Tests ejecutados: 6/6
- Tests pasados: 6/6
- Tests fallidos: 0/6

---

## 🎯 CRITERIOS DE ACEPTACIÓN

### **Funcionalidad**:

- [SI] Los 3 modos crean el servicio correctamente en PaaSify
- [SI] El upsert detecta servicios existentes y hace PATCH (no crea duplicados)
- [SI] Los outputs `container_id` y `action_taken` se escriben correctamente
- [SI] El step de zip solo se ejecuta en modos `custom_dockerfile` y `custom_compose`

### **Manejo de Errores**:

- [SI] Token inválido → fallo claro con código 401
- [SI] Project ID incorrecto → fallo claro con código 403
- [SI] El workflow de GitHub muestra el error en rojo, no pasa silenciosamente

---

## 🔗 REFERENCIAS

**Repositorios**:

- Action: `github.com/DavidRG25/paasify-deploy-action`
- Mini-repo de pruebas: `github.com/DavidRG25/MiniAPP_Paasify_Testing`

**Workflows de prueba**:

- `.github/workflows/deploy.yml` — modo dockerhub (push a main)
- `.github/workflows/deploy-custom-dockerfile.yml` — modo custom_dockerfile (manual)
- `.github/workflows/deploy-custom-compose.yml` — modo custom_compose (manual)

**Documentación**:

- API Docs: sección `8. Integración CI/CD` del panel de PaaSify

---

## 🐛 BUGS ENCONTRADOS Y CORREGIDOS DURANTE EL TESTING

| # | Componente | Bug | Fix |
|---|-----------|-----|-----|
| 1 | `deploy.sh` | Auth usaba `Token` en lugar de `Bearer` | Cambiado a `Authorization: Bearer ${TOKEN}` |
| 2 | `deploy.sh` | jq fallaba al parsear respuesta de la API (array vs paginado) | Añadido `if type == "array" then . else .results end` |
| 3 | `deploy.sh` | Faltaba `mode: "dockerhub"` en el payload POST de dockerhub | Añadido al payload jq |
| 4 | `deploy.sh` | Faltaba `-F "mode=custom"` en POST de custom_dockerfile y custom_compose | Añadido a ambos modos |
| 5 | `deploy.sh` | `internal_port` no se enviaba en modos custom | Añadido `-F "internal_port=${INTERNAL_PORT}"` en POST y PATCH |
| 6 | `deploy.sh` | `INTERNAL_PORT` era unbound variable en modos custom | Movida la definición al bloque global al inicio del script |
| 7 | `deploy.sh` | Campo `docker_compose` incorrecto; la API espera `compose` | Renombrado a `-F "compose=@${COMPOSE_PATH}"` |
| 8 | `deploy.sh` | `internal_port` no se actualizaba en PATCH de dockerhub | Añadido `internal_port` al payload PATCH |
| 9 | `serializers.py` | En PATCH, `internal_port` se reseteaba siempre a 80 | Fix: solo aplicar default 80 en POST (`not is_update`) |
| 10 | Workflows | `${{ env.INTERNAL_PORT }}` (entero YAML) no se expandía en `with:` | Cambiado a valor literal `8000` directamente en `with:` |
