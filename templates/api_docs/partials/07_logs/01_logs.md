# 📄 Consulta de Logs

Este recurso es fundamental para depurar errores de arranque o fallos en la lógica de negocio de tu aplicación. PaaSify almacena las últimas líneas emitidas por el contenedor para un acceso rápido.

**URL de Logs en este entorno:** `{{ PAASIFY_API_URL }}/containers/{id}/logs/`

---

### 📝 Ejemplos de CURL para Logs

A continuación se presentan diferentes formas de interactuar con el endpoint de logs:

#### 1️⃣ Consulta Básica (Últimos registros)

```bash
# Obtener el bloque de logs más reciente del contenedor 123
CURL -X GET "{{ PAASIFY_API_URL }}/containers/123/logs/" \
  -H "Authorization: Bearer <TU_TOKEN>"
```

#### 2️⃣ Filtrado Avanzado (Búsqueda de Errores)

Puedes combinar la salida de la API con herramientas de procesamiento de texto en tu terminal local:

```bash
# Filtrar solo las líneas que contienen la palabra "ERROR"
CURL -s -X GET "{{ PAASIFY_API_URL }}/containers/123/logs/" \
  -H "Authorization: Bearer <TU_TOKEN>" | jq -r ".logs" | grep "ERROR"
```

#### 3️⃣ Monitorización de Arranque

Si acabas de lanzar un servicio y quieres ver si falla al inicio:

```bash
# Consultar logs y limpiar la salida para facilitar la lectura
CURL -s -X GET "{{ PAASIFY_API_URL }}/containers/123/logs/" \
  -H "Authorization: Bearer <TU_TOKEN>" | jq -r ".logs"
```

---

### 📊 Estructura de la Respuesta JSON

Al realizar una petición de logs, recibirás un objeto con este formato:

```json
{
  "logs": "2026-02-26 21:00:00 [INFO] Starting Node.js...\n2026-02-26 21:00:05 [ERROR] Port 3000 already in use\n",
  "container_id": 123,
  "status": "active"
}
```

### ✅ Consejos de Depuración

- **Vacío de Logs**: Si la respuesta está vacía (`"logs": ""`), puede que tu aplicación no esté imprimiendo nada por consola o que el contenedor no haya arrancado todavía.
- **Formato**: Asegúrate de que tu aplicación no use prefijos de colores extraños (caracteres ANSI) que puedan dificultar la lectura en crudo del JSON.
