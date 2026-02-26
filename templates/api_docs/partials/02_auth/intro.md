# 🔐 2. Autenticación

PaaSify utiliza **Bearer Tokens** (tokens de portador) para asegurar que cada alumno acceda únicamente a sus propios recursos y a los de las asignaturas en las que está matriculado.

---

### 🛡️ Esquema de Seguridad

La autenticación sigue un flujo de "Token de Larga Duración":

1.  **Generación**: El token se genera en tu perfil web y es único para ti.
2.  **Transmisión**: Se envía en la cabecera `Authorization` de cada petición HTTP.
3.  **Validación**: PaaSify verifica que el token sea vigente y que el usuario tenga permisos sobre el `id` solicitado.

| Característica    | Detalle                                       |
| :---------------- | :-------------------------------------------- |
| **Tipo de Token** | Portador (Bearer)                             |
| **Ámbito**        | Acceso completo a tus proyectos y servicios   |
| **Cabecera**      | `Authorization: Bearer <TU_TOKEN>`            |
| **Expiración**    | Permanente hasta que decidas **Re-generarlo** |

---

### 💡 Recomendaciones Pro

- **Secrets CI/CD**: Si usas GitHub Actions, guarda este token como un `SECRET`. Nunca lo pongas en el código.
- **Pruebas Locales**: Usa herramientas como `Insomnia` o `Postman` para probar tus tokens antes de programar tu script.

Consulta el apartado **2.1 Token API** para ver el tutorial paso a paso de cómo obtenerlo.
