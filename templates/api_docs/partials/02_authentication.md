# 🔐 Autenticación

PaaSify utiliza **Bearer Tokens** (OAuth2 simplificado) para la autenticación. Este token acredita tu identidad y te da acceso **SOLO** a tus recursos y los de tus asignaturas.

---

## 🔑 Obtener tu Token

1. 👤 Ve a tu **Perfil de Usuario** en PaaSify.
2. 🔒 Haz clic en la pestaña "Seguridad".
3. 🔄 Genera o copia tu Token de API.

> ⚠️ **¡CUIDADO!** Este token es personal e intransferible. Actúa como tu contraseña. **NUNCA** lo compartas ni lo subas a repositorios públicos (GitHub, GitLab). Si sospechas que tu token se ha filtrado, **regeneralo inmediatamente**.

---

## 📤 Cómo usar el Token

Debes incluirlo en la cabecera `Authorization` de **todas** tus peticiones HTTP.

**Formato:** `Authorization: Bearer <TU_TOKEN>`

### 📝 Ejemplo cURL:

```bash
curl -X GET {{ PAASIFY_API_URL }}/containers/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

### 🐍 Ejemplo Python (Requests):

```python
import requests

headers = {
    "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
response = requests.get("{{ PAASIFY_API_URL }}/containers/", headers=headers)
```

### 💻 Ejemplo JavaScript (Fetch):

```javascript
fetch("{{ PAASIFY_API_URL }}/containers/", {
  headers: {
    Authorization: "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  },
});
```

---

## 🛑 Errores de Autenticación

| Código               | Razón                           | Solución                                                                       |
| :------------------- | :------------------------------ | :----------------------------------------------------------------------------- |
| **401 Unauthorized** | Token inválido o ausente.       | Verifica que copiaste bien el token y que la cabecera es correcta.             |
| **403 Forbidden**    | Token válido pero sin permisos. | Intentas acceder a un recurso (ej: asignatura o servicio) que no te pertenece. |

---
