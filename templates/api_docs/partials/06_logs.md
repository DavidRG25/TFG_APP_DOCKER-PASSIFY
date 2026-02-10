# Logs del Servicio

Endpoint dedicado para monitorear la salida de tus contenedores en tiempo real o consultar el historial de despliegue.

---

### Ver Logs

Obtiene la salida estándar (stdout) y de error (stderr) del contenedor. Es la herramienta principal para depurar fallos en tus aplicaciones.

**Endpoint:** `GET /api/containers/{id}/logs/`

```bash
curl -X GET "{{ PAASIFY_API_URL }}/containers/{id}/logs/" \
  -H "Authorization: Bearer <TU_API_TOKEN>"
```

#### Tip: Formato de salida

Este endpoint devuelve texto plano (`text/plain`), lo que facilita su lectura directa en la terminal sin necesidad de procesar JSON.

---

### Escenarios de uso

1. **Error de arranque**: Si el estado del servicio es `error`, consulta este endpoint para ver el mensaje de error de Docker o de tu aplicación.
2. **Depuración**: Puedes añadir `print()` o logs en tu código y verlos aquí instantáneamente.
3. **Multi-contenedor (Compose)**: Si usas Docker Compose, puedes filtrar los logs de un contenedor específico añadiendo el parámetro `?container={id_contenedor}`.

---

<details class="api-errors">
<summary>Códigos de error de este endpoint</summary>
<div class="api-error-content">
    <strong>401 Unauthorized:</strong> Permiso denegado. Token inválido.<br>
    <strong>403 Forbidden:</strong> No tienes permiso para ver los logs de este servicio.<br>
    <strong>404 Not Found:</strong> El servicio no existe.<br>
    <strong>500 Internal Server Error:</strong> El contenedor no está disponible o Docker ha fallado al recuperar los registros.
</div>
</details>
