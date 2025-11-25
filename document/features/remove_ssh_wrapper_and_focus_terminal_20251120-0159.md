# Retiro del wrapper SSH e impulso de la terminal integrada

## Motivos técnicos para retirar SSH
- El wrapper basado en plantillas generaba fallos con imágenes oficiales (mysql, alpine, oraclelinux) y no funcionaba en distroless/scratch.
- El mantenimiento del entrypoint duplicaba lógica para cada stack y provocaba falsas alarmas en Docker (servicios detenidos nada más iniciar).
- Las dependencias de PAM/shadow no están disponibles de forma homogénea; la autenticación nunca fue fiable.
- La nueva política es priorizar un único punto de entrada (docker exec vía WebSocket) para evitar puertos adicionales y credenciales efímeras.

## Detalles de eliminación
- Se eliminaron `docker_templates/ssh/` y toda referencia a `wrapper_Dockerfile.template`, `entrypoint_ssh.sh` y `sshd_config`.
- El modelo `Service` ya no incluye `enable_ssh`, `ssh_port` ni `ssh_password`; se añadió la migración `0011_remove_service_enable_ssh_and_more`.
- La API y el frontend dejan de exponer toggles o el botón “SSH”; solo permanecen las acciones Iniciar/Detener/Eliminar/Logs/Dockerfile/Compose/Terminal.
- Scripts auxiliares (`scripts/run.sh`, `scripts/start.sh`) dejaron de descargar imágenes SSH externas.
- Se purgó la documentación y guías internas relacionadas con sidecars o wrappers SSH.

## Estabilidad de la terminal basada en docker exec
- `TerminalConsumer` ahora trabaja directamente con el `PipeSocket` devuelto por Docker sin recurrir a atributos internos (`_sock`).
- La conexión WebSocket reporta “Conexión establecida con el contenedor” al abrirse, reenvía stdin/stdout/stderr en binario y cierra de forma elegante con mensaje informativo.
- Se controla la vida del socket (lectura/escritura con `send`/`recv` nativos) y el cierre del contenedor provoca un aviso en el cliente en lugar del error `[ERROR OUTPUT]: 'PipeSocket' object has no attribute '_sock'`.
- Si Docker no está disponible o el contenedor no existe, la terminal devuelve mensajes claros y evita cierres 1000 inesperados.

## Riesgos y futuras mejoras
- Ya no hay acceso SSH directo; toda interacción debe pasar por la terminal integrada, por lo que conviene reforzar controles de cuota y auditoría.
- Usuarios avanzados que dependían de túneles SSH deberán migrar a herramientas basadas en `docker exec` o exponer puertos manualmente en su aplicación.
- La eliminación del wrapper simplifica el despliegue, pero limita compatibilidad con herramientas que solo soportan SFTP; podría evaluarse una alternativa HTTP (p.ej., archivos mediante la API) en el futuro.
- Se recomienda agregar pruebas automáticas del consumidor WebSocket (Channels) para cubrir escenarios de contenedor detenido o binarios que envían UTF-8 inválido.
