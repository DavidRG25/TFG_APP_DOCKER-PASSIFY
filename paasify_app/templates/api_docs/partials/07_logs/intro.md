# 📄 7. Logs del Servicio

Visualiza el flujo de datos y mensajes de diagnóstico de tus aplicaciones en tiempo real. Los logs son la ventana principal para entender qué sucede dentro de tus contenedores Docker.

---

### 🔍 ¿Qué puedes encontrar en los Logs?

PaaSify captura tanto la **Salida Estándar (STDOUT)** como la **Salida de Errores (STDERR)** de tu proceso principal:

| Tipo de Mensaje | Ejemplo Típico                     | Importancia                                         |
| :-------------- | :--------------------------------- | :-------------------------------------------------- |
| **🚀 Startup**  | `Server listening on port 3000...` | Confirma que tu app ha arrancado bien.              |
| **📡 Tráfico**  | `GET /api/users 200 15ms`          | Monitorización de peticiones en tiempo real.        |
| **🛑 Errores**  | `Error: Connection refused to DB`  | Identifica fallos de configuración o código.        |
| **⚙️ Config**   | `DEBUG_MODE is enabled`            | Verifica que las variables de entorno se aplicaron. |

---

### 🛠️ Herramientas de Diagnóstico

Consulta la sección **7.1 Logs** para aprender a:

- Extraer registros mediante comandos **CURL**.
- Filtrar información relevante para no saturar tu terminal.
- Depurar fallos de despliegue mediante el historial de eventos.

Haz clic en el menú lateral para ver los ejemplos técnicos de consulta.
