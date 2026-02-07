# Autenticación

## Autenticación

PaaSify utiliza un sistema de **Bearer Tokens** para la autenticación. Debes utilizar tu token personal que puedes encontrar y gestionar en tu **Perfil de Usuario** en la sección "Seguridad".

### ¿Cómo usarlo?

Debes incluir tu token en la cabecera `Authorization` de **todas** tus peticiones HTTP.

**Formato de cabecera:**

```bash
Authorization: Bearer <TU_API_TOKEN>
```

> 💡 **Seguridad**: Este token actúa como tu contraseña. **Nunca** compartas tu token ni lo subas a repositorios públicos de GitHub. Si sospechas que tu token se ha visto comprometido, regeneralo inmediatamente desde tu panel de usuario.

---
