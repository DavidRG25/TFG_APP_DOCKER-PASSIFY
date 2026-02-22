# 📄 Logs del Servicio

Endpoint dedicado para monitorear la salida de tus contenedores en tiempo real o consultar el historial de despliegue.

---

## 👁️ Ver Logs

Obtiene la salida estándar (`stdout`) y de error (`stderr`) del contenedor.

**Endpoint:** `GET /api/containers/{id}/logs/`

> 💡 **Nota:** Si tu servicio falla al crearse (ej: error en `Dockerfile`), este endpoint devolverá los logs de construcción para ayudarte a depurar.

### ⚙️ Parámetros Opcionales (Query Params)

| Parámetro     | Descripción                  | Valores ejemplo                            |
| :------------ | :--------------------------- | :----------------------------------------- |
| **tail**      | Nº líneas finales a mostrar. | `10`, `100`, `all` (default: 200).         |
| **since**     | Filtrar por antigüedad.      | `5m` (minutos), `1h` (horas), `24h`, `7d`. |
| **container** | ID (solo para Compose).      | Nombre del servicio hijo en el stack.      |

---

## 📝 Ejemplos Prácticos

### 1. Ver últimas 10 líneas

Ideal para verificar que el servicio arrancó correctamente.

```bash
curl -X GET "{{ PAASIFY_API_URL }}/containers/{ID}/logs/?tail=10" \
  -H "Authorization: Bearer <TU_TOKEN>"
```

### 2. Ver logs de la última hora

Útil para diagnosticar problemas recientes.

```bash
curl -X GET "{{ PAASIFY_API_URL }}/containers/{ID}/logs/?since=1h" \
  -H "Authorization: Bearer <TU_TOKEN>"
```

### 3. Filtrar servicio específico (Compose)

Si tu stack tiene `db` y `frontend`, puedes ver solo los logs de la base de datos.

```bash
curl -X GET "{{ PAASIFY_API_URL }}/containers/{ID}/logs/?container=db" \
  -H "Authorization: Bearer <TU_TOKEN>"
```

---

## 🐛 Guía de Depuración

Si tu servicio está en estado ⚠️ **ERROR**, los logs son tu mejor herramienta.

### Caso A: Error de Dependencia (Python)

```text
Traceback (most recent call last):
  File "app.py", line 1, in <module>
    import flask
ModuleNotFoundError: No module named 'flask'
```

✅ **Solución:** Verifica que `flask` está en tu `requirements.txt`.

### Caso B: Error en Dockerfile

```text
[DOCKER] Step 4/6 : RUN pip install -r missing_file.txt
[DOCKER] ERROR: Could not open requirements file: ... No such file or directory
```

✅ **Solución:** Asegúrate de que el nombre del archivo en el `Dockerfile` coincide con el archivo en tu `.zip`.

---

## 📬 Códigos de Respuesta

<details class="api-errors">
<summary>ℹ️ Posibles respuestas en logs</summary>
<div class="api-error-content">
    <strong>401 Unauthorized:</strong> 🔒 Token inválido.<br>
    <strong>403 Forbidden:</strong> 🚫 No tienes permiso para ver estos logs.<br>
    <strong>404 Not Found:</strong> 🔍 El servicio no existe.<br>
    <strong>500 Internal Server Error:</strong> 💥 El contenedor no está disponible o Docker falló.
</div>
</details>

---
