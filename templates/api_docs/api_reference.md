# Documentación API REST

## Introducción

La API de PaaSify permite a los alumnos interactuar con la plataforma de forma programática. Todo lo que puedes hacer a través de la interfaz web (crear contenedores, reiniciarlos, ver logs) está disponible mediante peticiones HTTP.

> **URL Base de la API**: `{{ PAASIFY_API_URL }}`

Esta guía detalla el uso de los endpoints disponibles. Los comandos mostrados están listos para ser usados como plantillas.

---

## Autenticación

PaaSify utiliza un sistema de **Bearer Tokens** para la autenticación. Debes utilizar tu token personal que puedes encontrar y gestionar en tu **Perfil de Usuario**.

**Formato de cabecera:**

```bash
Authorization: Bearer <TU_API_TOKEN>
```

> 💡 **Seguridad**: Nunca compartas tu token ni lo subas a repositorios públicos de GitHub. Si el token se ve comprometido, puedes regenerarlo en tu perfil.

---

## Listar Servicios

Recupera la lista detallada de todos tus servicios activos y sus estados actuales.

**Endpoint:** `GET /containers/`

```bash
curl -X GET {{ PAASIFY_API_URL }}/containers/ \
  -H "Authorization: Bearer <TU_API_TOKEN>"
```

---

## Crear Servicio

Este es el endpoint para desplegar aplicaciones. Permite crear servicios usando imágenes del catálogo o configuraciones personalizadas.

**Endpoint:** `POST /containers/`

### Parámetros del Body (JSON)

| Campo             | Tipo   | Descripción                                           |
| :---------------- | :----- | :---------------------------------------------------- |
| **name\***        | string | Nombre único para el servicio (minúsculas y guiones). |
| **image**         | string | Imagen de DockerHub o del catálogo.                   |
| **mode**          | string | `default`, `dockerhub` o `custom`.                    |
| **internal_port** | int    | Puerto que usa la app internamente (por defecto 80).  |
| **environment**   | object | (Opcional) Mapa de variables de entorno.              |

### Ejemplo: Imagen del Catálogo

```bash
curl -X POST {{ PAASIFY_API_URL }}/containers/ \
  -H "Authorization: Bearer <TU_API_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "mi-app-api",
    "image": "nginx:latest",
    "mode": "default"
  }'
```

---

## Control de Servicios

| Acción      | Endpoint                       |
| :---------- | :----------------------------- |
| **Iniciar** | `POST /containers/{id}/start/` |
| **Detener** | `POST /containers/{id}/stop/`  |

---

## Ver Logs

Obtén la salida estándar (stdout/stderr) de tu contenedor en tiempo real.

**Endpoint:** `GET /containers/{id}/logs/`

```bash
curl -X GET {{ PAASIFY_API_URL }}/containers/{id}/logs/ \
  -H "Authorization: Bearer <TU_API_TOKEN>"
```

---

## Integración CI/CD

Automatiza tus despliegues cada vez que hagas un push a tu repositorio.

### GitHub Actions Ejemplo (.github/workflows/deploy.yml)

```yaml
name: Deploy to PaaSify
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Notify PaaSify API
        run: |
          curl -X POST {{ PAASIFY_API_URL }}/containers/{ID_SERVICIO}/restart/ \
            -H "Authorization: Bearer ${{ secrets.PAASIFY_TOKEN }}"
```

---

## Códigos de Error

| Código | Significado                                                |
| :----- | :--------------------------------------------------------- |
| `401`  | **Unauthorized**: Token faltante o inválido.               |
| `400`  | **Bad Request**: Parámetros incorrectos o puerto ocupado.  |
| `404`  | **Not Found**: El servicio especificado no existe.         |
| `500`  | **Server Error**: Error interno al levantar el contenedor. |
