# ⚙️ Acciones Disponibles

Controla el ciclo de vida de tus servicios directamente desde la API de PaaSify. Estos comandos se envían directamente al motor de Docker que gestiona tu instancia mediante endpoints específicos.

---

### 🕹️ Lista de Operaciones

Cada acción dispone de su propia URL dedicada a la que debes enviar una petición `POST` (sin necesidad de cuerpo de mensaje):

| Acción      | Emoticono | Endpoint (Relativo) | Descripción                                    |
| :---------- | :-------: | :------------------ | :--------------------------------------------- |
| **start**   |    🚀     | `/start/`           | Arranca el servicio si está detenido.          |
| **stop**    |    🛑     | `/stop/`            | Detiene el servicio y libera recursos.         |
| **restart** |    🔄     | `/restart/`         | Reinicia el servicio (Stop -> Start).          |
| **remove**  |    🗑️     | `/remove/`          | Elimina el servicio y sus volúmenes asociados. |

---

### 📝 Ejemplos de CURL por Acción

A continuación se muestran los comandos específicos para interactuar con cada recurso:

#### 1️⃣ Arrancar Servicio (Start)

```bash
# Encender el contenedor 123
CURL -X POST "{{ PAASIFY_API_URL }}/containers/123/start/" \
  -H "Authorization: Bearer <TU_TOKEN>" \
  -H "Content-Type: application/json"
```

#### 2️⃣ Detener Servicio (Stop)

```bash
# Apagar el contenedor 123
CURL -X POST "{{ PAASIFY_API_URL }}/containers/123/stop/" \
  -H "Authorization: Bearer <TU_TOKEN>" \
  -H "Content-Type: application/json"
```

#### 3️⃣ Reiniciar Servicio (Restart)

```bash
# Reinicio completo del contenedor 123
CURL -X POST "{{ PAASIFY_API_URL }}/containers/123/restart/" \
  -H "Authorization: Bearer <TU_TOKEN>" \
  -H "Content-Type: application/json"
```

#### 4️⃣ Eliminar Servicio (Remove)

**⚠️ Atención:** Esta acción es irreversible. Elimina el contenedor y sus archivos.

```bash
# Eliminar definitivamente el contenedor 123
CURL -X POST "{{ PAASIFY_API_URL }}/containers/123/remove/" \
  -H "Authorization: Bearer <TU_TOKEN>" \
  -H "Content-Type: application/json"
```

---

### ✅ Recomendaciones de Uso

1.  **Ahorra Recursos**: Detén (`stop`) los servicios que no estés usando activamente.
2.  **Verificación**: Tras lanzar una acción, puedes consultar el estado con un `GET` a `/api/containers/123/`.
