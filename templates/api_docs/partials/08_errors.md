# Códigos de Error

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

---

### Análisis de Errores Habituales

Además de los códigos estándar, aquí tienes una guía para solucionar los problemas más frecuentes al integrar la API:

#### 1. El error de la Barra Diagonal (`/`)

Django es estricto con las URLs. Si olvidas poner la barra al final de un endpoint, puedes recibir un error de redirección o un `404`.

- **Mal**: `.../api/containers`
- **Bien**: `.../api/containers/` (Siempre añade la `/` al final).

#### 2. Error 400 - Validación de Datos

Si recibes un `400`, revisa el cuerpo de la respuesta JSON. Te dirá exactamente qué campo ha fallado:

- `"name": ["Ya existe un servicio tuyo con este nombre."]`: El nombre debe ser único.
- `"internal_port": ["Debe estar entre 1 y 65535."]`: Revisa que el puerto interno sea válido.
- `"image": ["La imagen 'xxx' no existe en DockerHub."]`: En modo DockerHub, la imagen debe ser pública y el nombre correcto.

#### 3. Error 401 - Token Incorrecto o Expirado

Si el token no funciona:

1.  Verifica que el formato sea exactamente `Authorization: Bearer <TU_TOKEN>`.
2.  Asegúrate de que no haya espacios extra o caracteres invisibles.
3.  Si ha pasado más de un mes desde que lo generaste, probablemente haya expirado. Genéralo de nuevo en tu **Perfil**.

#### 4. Error 405 - Método No Permitido

Este error ocurre cuando usas el verbo HTTP equivocado:

- Usar `GET` en lugar de `POST` para crear o realizar acciones (start, stop).
- Usar `POST` en lugar de `GET` para listar o ver información.

---

### Solución de Problemas (Troubleshooting)

Si tu comando `curl` falla sin dar mucha información:

1.  Añade el flag `-v` (verbose) a tu comando curl para ver las cabeceras completas de la petición y respuesta.
2.  Verifica que el servidor PaaSify sea accesible desde tu red actual.
3.  Revisa la sintaxis correcta en la sección de **Despliegue API/Terminal** de la interfaz web para asegurar que tu comando sigue la estructura de las plantillas oficiales.
