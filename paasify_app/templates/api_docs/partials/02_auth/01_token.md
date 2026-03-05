# 🔑 Uso del Token API

El token es tu "llave" para la API de PaaSify.

---

### Obtener tu Token

1.  👤 Entra en PaaSify con tu cuenta habitual.
2.  🔒 Ve a tu **Perfil de Usuario** (esquina superior derecha).
3.  🔄 En la pestaña **"Seguridad"**, podrás ver, copiar o regenerar tu Token de API.

> ⚠️ **¡Súper Importante!** Trata tu token como si fuera una contraseña. **NUNCA** lo subas a GitHub o GitLab en texto plano. Usa "Secrets" de tu plataforma CI/CD.

---

### Cómo usar el Token en peticiones

Debes enviar la cabecera `Authorization` con el prefijo `Bearer`.

#### Ejemplo de Cabecera:

`Authorization: Bearer <TU_TOKEN>`

#### Ejemplo CURL:

```bash
# Sustituye <TU_TOKEN> por el valor de tu perfil
# La URL de PaaSify en este entorno es: {{ PAASIFY_API_URL }}
CURL -X GET "{{ PAASIFY_API_URL }}/containers/" \
  -H "Authorization: Bearer <TU_TOKEN>"
```

---

### Gestión de Errores

| Código               | Razón                        | Solución                                                |
| :------------------- | :--------------------------- | :------------------------------------------------------ |
| **401 Unauthorized** | Token ausente o mal copiado. | Verifica que el token sea el actual de tu perfil.       |
| **403 Forbidden**    | Token válido, recurso ajeno. | No tienes permisos sobre ese ID de contenedor/proyecto. |
