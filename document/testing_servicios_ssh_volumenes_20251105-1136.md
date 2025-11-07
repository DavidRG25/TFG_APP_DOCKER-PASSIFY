# Testing — Servicios, SSH y Volúmenes (2025-11-05 23:25)

## 1. Prerrequisitos
1. Docker en ejecución con acceso al socket utilizado por Django.
2. Imagen necesaria para el sidecar SSH descargada (`SERVICE_SSH_IMAGE`, por defecto `linuxserver/openssh-server`). Los scripts `scripts/run.sh` y `scripts/start.sh` la obtienen automáticamente, pero puede verificarse manualmente con `docker image inspect`.
3. Entorno virtual activo (`source venv/Scripts/activate` o equivalente) y dependencias instaladas (`scripts/start_app.sh`).

## 2. Pruebas automatizadas
1. **Unitarias / API**  
   - Comando: `pytest containers/tests.py -k "TestServiceCreation"`  
   - Resultado esperado: pasan las pruebas de creación de servicios en los modos catálogo y custom.
2. **Interacción Docker (entorno con permisos)**  
   - Comando: `pytest containers/tests.py -k "container_lifecycle or terminal_websocket"`  
   - Precondición: Docker accesible.  
   - Resultado esperado: los tests marcados con `@pytest.mark.skipif` sólo se ejecutan si `DOCKER_AVAILABLE` es `True`; al completarse, los servicios quedan eliminados y los puertos liberados.

## 3. Pruebas manuales funcionales
1. **Creación de servicio (modo catálogo)**  
   - Pasos: iniciar sesión como alumno → “Mis servicios” → “Nuevo servicio” → seleccionar imagen permitida → crear.  
   - Validaciones: la fila aparece con estado `running`; en la BD (`Service`) se asigna `volume_name=svc_{id}` y `ssh_port`/`ssh_password` tienen valor.
2. **Modal SSH**  
   - Pasos: en la tabla, pulsar “SSH”.  
   - Validaciones: el modal muestra comando, usuario (`SERVICE_SSH_USER`) y contraseña generada; el botón “Copiar” funciona (ver consola del navegador).  
   - Extra: comprobar que el comando `ssh usuario@host -p puerto` permite conectar usando la contraseña indicada.
3. **Terminal web**  
   - Pasos: pulsar “Terminal”, ejecutar `whoami` y `ls ~/data`.  
   - Validaciones: la sesión responde inmediatamente; los comandos reflejan el contenido del volumen persistente.
4. **Logs**  
   - Pasos: botón “Logs” → confirmar que se abre el modal genérico con el tail de Docker.  
   - Validaciones: los errores se muestran con prefijo `(error ...)`.
5. **Eliminación**  
   - Pasos: botón “Eliminar” → aceptar.  
   - Validaciones: la fila desaparece; `docker volume ls` no muestra `svc_{id}`; `PortReservation` no contiene el puerto liberado.

## 4. Pruebas de permisos
1. Alumno sólo ve y opera sus servicios (`Service.owner`).  
   - Intentar acceder a `/api/containers/{otro_id}/logs/` debería devolver 404/403.
2. Profesor/Admin puede inspeccionar servicios de terceros (vistas `professor_dashboard`, modal logs).  
3. Alumnos sin matrícula en una asignatura reciben 403 al acceder a `containers:student_services_in_subject`.

## 5. Checklist post despliegue
1. Ejecutar `scripts/run.sh` o `scripts/start.sh`; confirmar que el log muestra “Verificando imagen SSH requerida (…)” y, si no existía, que la descarga finaliza correctamente.
2. Lanzar `python manage.py create_test_user --username qa_admin` si se necesita un superusuario rápido.
3. Registrar en `document/` cualquier bloqueo relacionado con permisos Docker o descargas de imágenes para trazabilidad.
