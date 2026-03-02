# ⚙️ 6. Acciones del Servicio

Toma el control manual sobre el estado de ejecución de tus aplicaciones. Estos endpoints son ideales para realizar reinicios rápidos o liberar recursos del servidor de PaaSify.

---

### 🕹️ Centro de Control REST

Mediante un `POST` a las URLs de acción correspondientes, puedes enviar comandos directos al motor de Docker de la universidad:

| Operación     | URL (Sufijo) | Acción Real | Uso Recomendado                                    |
| :------------ | :----------- | :---------- | :------------------------------------------------- |
| **Levantar**  | `/start/`    | Encender    | Activar servicios tras un periodo de inactividad.  |
| **Detener**   | `/stop/`     | Apagar      | Apagar apps que ya no uses para ahorrar memoria.   |
| **Reiniciar** | `/restart/`  | Refrescar   | Solucionar bloqueos o fugas de memoria del código. |
| **Eliminar**  | `/remove/`   | Borrar      | Limpieza definitiva del contenedor y volúmenes.    |

---

### 📡 Respuesta del Servidor

Al ejecutar una acción, la API te devolverá un mensaje confirmando el envío del comando:
`{"status": "queued", "message": "Servicio encolado para iniciar."}`

Consulta **6.1 Acciones** para ver ejemplos de comandos **CURL** completos listos para copiar y pegar.
