# ⚠️ Códigos de Error y Solución

Guía rápida para interpretar y solucionar los errores que puedes recibir al usar la API.

---

## 🚦 Códigos de Estado HTTP

<br>

<details>
<summary style="cursor: pointer; font-weight: 600; color: #e74a3b; display: flex; align-items: center;"><span style="font-size: 1.2em; margin-right: 10px;">🔴</span> 400 - Bad Request</summary>
<div style="background: #fdf5f5; border-left: 4px solid #e74a3b; padding: 1rem; border-radius: 0 0.5rem 0.5rem 0; margin-top: 5px;">
    <strong>Significado:</strong> Petición inválida o mal formada.<br>
    <strong>Causas Comunes:</strong>
    <ul>
        <li>Faltan parámetros obligatorios (ej: <code>image</code> en modo DockerHub).</li>
        <li>El JSON tiene errores de sintaxis.</li>
        <li>Intentas modificar un campo inmutable (ej: <code>image</code> en PATCH).</li>
        <li>Nombre de servicio duplicado.</li>
    </ul>
</div>
</details>

<details>
<summary style="cursor: pointer; font-weight: 600; color: #f6c23e; display: flex; align-items: center;"><span style="font-size: 1.2em; margin-right: 10px;">🔒</span> 401 - Unauthorized</summary>
<div style="background: #fffdf0; border-left: 4px solid #f6c23e; padding: 1rem; border-radius: 0 0.5rem 0.5rem 0; margin-top: 5px;">
    <strong>Significado:</strong> No autenticado.<br>
    <strong>Solución:</strong>
    <ul>
        <li>Verifica la cabecera <code>Authorization: Bearer TU_TOKEN</code>.</li>
        <li>Asegúrate de que el token no ha expirado.</li>
        <li>Regenera el token en tu perfil si sospechas que es inválido.</li>
    </ul>
</div>
</details>

<details>
<summary style="cursor: pointer; font-weight: 600; color: #f6c23e; display: flex; align-items: center;"><span style="font-size: 1.2em; margin-right: 10px;">🚫</span> 403 - Forbidden</summary>
<div style="background: #fffdf0; border-left: 4px solid #f6c23e; padding: 1rem; border-radius: 0 0.5rem 0.5rem 0; margin-top: 5px;">
    <strong>Significado:</strong> Acceso denegado.<br>
    <strong>Causas Comunes:</strong>
    <ul>
        <li>Intentas acceder/modificar un servicio que no es tuyo.</li>
        <li>Intentas desplegar en una asignatura donde no estás matriculado.</li>
        <li>Intentas modificar un servicio del Catálogo Oficial.</li>
    </ul>
</div>
</details>

<details>
<summary style="cursor: pointer; font-weight: 600; color: #858796; display: flex; align-items: center;"><span style="font-size: 1.2em; margin-right: 10px;">🔍</span> 404 - Not Found</summary>
<div style="background: #f8f9fc; border-left: 4px solid #d1d3e2; padding: 1rem; border-radius: 0 0.5rem 0.5rem 0; margin-top: 5px;">
    <strong>Significado:</strong> Recurso no encontrado.<br>
    <strong>Causas Comunes:</strong>
    <ul>
        <li>El ID del servicio es incorrecto.</li>
        <li>La URL del endpoint está mal escrita.</li>
        <li>Intentas usar una imagen de DockerHub que no existe.</li>
    </ul>
</div>
</details>

<details>
<summary style="cursor: pointer; font-weight: 600; color: #e74a3b; display: flex; align-items: center;"><span style="font-size: 1.2em; margin-right: 10px;">💥</span> 500 - Server Error</summary>
<div style="background: #fdf5f5; border-left: 4px solid #e74a3b; padding: 1rem; border-radius: 0 0.5rem 0.5rem 0; margin-top: 5px;">
    <strong>Significado:</strong> Error interno del servidor.<br>
    <strong>Qué hacer:</strong> Inténtalo de nuevo en unos minutos. Si persiste, contacta con el soporte técnico.
</div>
</details>

---

## 🕵️‍♂️ Análisis de Problemas Comunes

### 1. El error de la Barra Diagonal (`/`)

Django es estricto con las URLs. Siempre termina tus endpoints con `/`.

- ❌ **Mal**: `.../api/containers`
- ✅ **Bien**: `.../api/containers/`

### 2. Mensajes de error JSON (400)

La API devuelve detalles específicos de validación. Lee el JSON de respuesta:

```json
{
  "name": ["Ya existe un servicio tuyo con este nombre."],
  "image": ["La imagen no se puede modificar en servicios DockerHub."]
}
```

### 3. Error 405 - Method Not Allowed

Usaste el verbo HTTP incorrecto:

- `GET` en lugar de `POST` (o viceversa).
- `PATCH` en un endpoint que solo admite `GET`.

---

## 🛠️ Debugging

Si tu comando no funciona:

1. Agrega `-v` a tu comando `curl` para ver las cabeceras.
2. Verifica que la URL base `{{ PAASIFY_API_URL }}` es correcta.
3. Asegúrate de que tu JSON es válido (sin comas sobrantes).

---
