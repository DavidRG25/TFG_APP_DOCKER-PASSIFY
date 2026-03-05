# 🛑 Errores de la API de PaaSify

PaaSify sigue estrictamente los estándares REST. Si recibes un error, el cuerpo de la respuesta contendrá un JSON con detalles técnicos para ayudarte a solucionarlo rápidamente.

---

### 📋 Guía de Referencia de Errores

| Código  | Estado       | Causa Probable                                | Solución Sugerida                                    |
| :------ | :----------- | :-------------------------------------------- | :--------------------------------------------------- |
| **400** | Bad Request  | Parámetros faltantes o JSON mal formado.      | Valida tu sintaxis JSON y campos obligatorios.       |
| **401** | Unauthorized | Token ausente, caducado o mal copiado.        | Regenera el token en tu perfil de usuario.           |
| **403** | Forbidden    | Intentas acceder a un recurso que no es tuyo. | Verifica que el ID del contenedor te pertenezca.     |
| **404** | Not Found    | El recurso (ID) no existe en la DB.           | Asegúrate de que el contenedor no haya sido borrado. |
| **500** | Server Error | Error crítico en el nodo de Docker.           | Contacta con el administrador del sistema.           |

---

### 📝 Ejemplo de Respuesta de Error

Si intentas consultar un proyecto que no te pertenece (403 Forbidden):

#### Comando CURL:

```bash
CURL -X GET "{{ PAASIFY_API_URL }}/projects/999/" \
  -H "Authorization: Bearer <TOKEN_INVALIDO>"
```

#### Respuesta JSON:

```json
{
  "detail": "No tienes permisos para realizar esta acción.",
  "code": "permission_denied"
}
```

---

### ✅ Checklist de Depuración

- [ ] ¿He incluido la barra final `/` en la URL? (Django la requiere).
- [ ] ¿He puesto la palabra `Bearer` seguida de un espacio antes del Token?
- [ ] ¿El `Content-Type` es `application/json` en peticiones POST/PATCH?
