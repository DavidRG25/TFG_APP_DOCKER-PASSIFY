# Códigos de Error

## Códigos de Error

Estos son los códigos de estado HTTP más comunes que puedes recibir en tus respuestas:

<br>
<details>
<summary style="cursor: pointer; font-weight: 600; color: #e74a3b;">400 - Bad Request</summary>
<div style="background: #fdf5f5; border: 1px solid #e74a3b; padding: 1rem; border-radius: 0.5rem; margin-top: 5px;">
    <strong>Significado:</strong> Petición inválida.<br>
    <strong>Causas Comunes:</strong> Faltan parámetros obligatorios, nombre de servicio duplicado, puerto ocupado ilegalmente, o JSON mal formado.
</div>
</details>

<details>
<summary style="cursor: pointer; font-weight: 600; color: #f6c23e;">401 - Unauthorized</summary>
<div style="background: #fffdf0; border: 1px solid #f6c23e; padding: 1rem; border-radius: 0.5rem; margin-top: 5px;">
    <strong>Significado:</strong> No autenticado.<br>
    <strong>Causas Comunes:</strong> Token faltante, formato de cabecera inválido, o token expirado/regenerado. Verifica Authorization: Bearer.
</div>
</details>

<details>
<summary style="cursor: pointer; font-weight: 600; color: #f6c23e;">403 - Forbidden</summary>
<div style="background: #fffdf0; border: 1px solid #f6c23e; padding: 1rem; border-radius: 0.5rem; margin-top: 5px;">
    <strong>Significado:</strong> Permiso denegado.<br>
    <strong>Causas Comunes:</strong> Intentas acceder a recursos de otro alumno o asignaturas donde no estás matriculado.
</div>
</details>

<details>
<summary style="cursor: pointer; font-weight: 600; color: #858796;">404 - Not Found</summary>
<div style="background: #f8f9fc; border: 1px solid #d1d3e2; padding: 1rem; border-radius: 0.5rem; margin-top: 5px;">
    <strong>Significado:</strong> Recurso no encontrado.<br>
    <strong>Causas Comunes:</strong> ID de servicio incorrecto, imagen de DockerHub inexistente, o endpoint mal escrito.
</div>
</details>

<details>
<summary style="cursor: pointer; font-weight: 600; color: #e74a3b;">500 - Server Error</summary>
<div style="background: #fdf5f5; border: 1px solid #e74a3b; padding: 1rem; border-radius: 0.5rem; margin-top: 5px;">
    <strong>Significado:</strong> Error interno.<br>
    <strong>Causas Comunes:</strong> Fallo en Docker Daemon, problemas de red en el servidor, o bug en la lógica de PaaSify. Contacta con el administrador.
</div>
</details>
