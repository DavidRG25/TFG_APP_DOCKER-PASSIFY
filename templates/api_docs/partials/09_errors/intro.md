# 🛑 9. Códigos de Error

Comprender la respuesta de la API es clave para depurar tus integraciones. PaaSify utiliza el estándar de la comunidad para que tus scripts puedan manejar fallos de forma robusta.

---

### 🔍 Anatomía de un Error

Cuando una petición falla, PaaSify siempre devuelve un objeto JSON estructurado:

```json
{
  "detail": "Descripción humana del problema",
  "code": "slug_tecnico_para_programadores"
}
```

---

### 🛠️ Tabla de Primeros Auxilios

| Familia de Error   | Qué está pasando             | Qué revisar                                            |
| :----------------- | :--------------------------- | :----------------------------------------------------- |
| **400 - Client**   | Formato de datos incorrecto. | Revisa que el JSON esté bien cerrado o falte una coma. |
| **401/403 - Auth** | Problema de identidad.       | Regenera el token o comprueba los IDs de proyecto.     |
| **404 - Logic**    | Recurso no encontrado.       | ¿Has borrado el servicio recientemente?                |
| **500 - Server**   | Error interno de Docker.     | Intenta re-desplegar o contacta con soporte técnico.   |

Consulta **9.1 Errores** para ver la lista completa de códigos y sus significados específicos.
