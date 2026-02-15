# Logs del Servicio

Endpoint dedicado para monitorear la salida de tus contenedores en tiempo real o consultar el historial de despliegue.

---

### Ver Logs

Obtiene la salida estándar (`stdout`) y de error (`stderr`) del contenedor. Si el servicio ha fallado al crearse (por ejemplo, error al descomprimir o en el `Dockerfile`), este endpoint devolverá los logs del sistema para ayudarte a depurar.

**Endpoint:** `GET /api/containers/{id}/logs/`

#### Parámetros opcionales (Query Params)

| Parámetro   | Descripción                        | Valores ejemplo                      |
| :---------- | :--------------------------------- | :----------------------------------- |
| `tail`      | Número de líneas finales a mostrar | `10`, `100`, `all` (por defecto 200) |
| `since`     | Filtrar por antigüedad             | `5m`, `1h`, `24h`, `7d`              |
| `container` | ID del contenedor (solo Compose)   | `1`, `2`                             |

---

### Ejemplos Prácticos

Usa estos comandos en tu terminal para verificar el funcionamiento:

#### 1. Modo Dockerfile (mi-app-passify-example-dockerfile)

Para ver las últimas 10 líneas de actividad:

```bash
curl -X GET "{{ PAASIFY_API_URL }}/containers/{ID_SERVICIO}/logs/?tail=10" \
  -H "Authorization: Bearer <TU_API_TOKEN>"
```

#### 2. Modo Docker Compose (stack-completo-passify)

Para ver los logs de la última hora de todo el stack:

```bash
curl -X GET "{{ PAASIFY_API_URL }}/containers/{ID_SERVICIO}/logs/?since=1h" \
  -H "Authorization: Bearer <TU_API_TOKEN>"
```

#### 3. Filtrar un contenedor específico en Compose

Si quieres ver solo los logs de un servicio hijo (ej. el contenedor de la base de datos):

```bash
curl -X GET "{{ PAASIFY_API_URL }}/containers/{ID_SERVICIO}/logs/?container={ID_CONTENEDOR_HIJO}" \
  -H "Authorization: Bearer <TU_API_TOKEN>"
```

---

#### Tip: Depuración de errores de aplicación

Si tu servicio está en estado `ERROR`, consulta este endpoint para identificar fallos en tu código o en la configuración del entorno. Los logs te mostrarán el _stacktrace_ exacto del error.

**Ejemplo de error por dependencia faltante (Python):**

```text
Traceback (most recent call last):
  File "app.py", line 1, in <module>
    import flask
ModuleNotFoundError: No module named 'flask'
```

_Solución: Verifica que has incluido todas las dependencias en tu archivo `requirements.txt`._

**Ejemplo de error en Dockerfile:**

```text
[DOCKER] Step 4/6 : RUN pip install -r missing_file.txt
[DOCKER] ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'missing_file.txt'
```

_Solución: Asegúrate de que los nombres de los archivos en tu Dockerfile coinciden exactamente con los de tu código subido._

---

<details class="api-errors">
<summary>Códigos de error de este endpoint</summary>
<div class="api-error-content">
    <strong>401 Unauthorized:</strong> Permiso denegado. Token inválido.<br>
    <strong>403 Forbidden:</strong> No tienes permiso para ver los logs de este servicio.<br>
    <strong>404 Not Found:</strong> El servicio no existe.<br>
    <strong>500 Internal Server Error:</strong> El contenedor no está disponible o Docker ha fallado al recuperar los registros.
</div>
</details>
