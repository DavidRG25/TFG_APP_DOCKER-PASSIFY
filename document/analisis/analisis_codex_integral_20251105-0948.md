# Análisis integral Codex — PaaSify (rama develop)

## 1. Resumen Ejecutivo
- Entorno Django 5.x funcional, pero con configuraciones sensibles expuestas (`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS="*"`), lo que reduce la seguridad base.
- Arquitectura modular con apps `paasify`, `containers` y `security`; se observan dependencias cruzadas controladas, aunque persisten acoplamientos fuertes entre vistas y modelos legacy.
- Flujo de autenticación diferenciado por rol funciona conceptualmente, pero la navegación expone rutas de alumnos y profesores simultáneamente generando redirecciones forzadas.
- Gestión de contenedores operativa a nivel de código, aunque ejecuta builds y `docker compose` en el hilo web sin aislamiento, elevando riesgo de bloqueos.
- Terminal interactiva valida pertenencia del servicio, pero el cliente HTMX reintenta conexiones incluso tras cierres por permisos, lo que puede saturar sesiones.
- `manage.py showmigrations` revela namespaces duplicados y valores por defecto estáticos; ningún esquema ha sido aplicado al SQLite local.
- Pruebas automatizadas limitadas (`pytest`), sólo cubren reserva de puertos y ciclo básico del contenedor; resto de flujos sin test formal.
- Estabilidad estimada: **65 %** (depende de Docker externo, ausencia de colas y validaciones adicionales).

## 2. Errores Críticos
### 2.1 Configuración insegura en producción
- **Archivo/Línea:** `app_passify/settings.py` líneas 11-20. 【F:app_passify/settings.py†L11-L20】
- **Impacto:** Exposición de `SECRET_KEY`, `DEBUG=True` y `ALLOWED_HOSTS=["*"]` permite secuestro de sesión, cross-site scripting y despliegues inseguros.
- **Causa raíz:** Uso de valores hardcodeados para simplificar desarrollo.
- **Propuesta:** Externalizar variables a `.env`/Docker secrets y condicionar `DEBUG` por entorno.

### 2.2 Namespaces duplicados en URLs
- **Archivo/Línea:** `paasify/urls.py` líneas 1-19; `app_passify/urls.py` líneas 23-48. 【F:paasify/urls.py†L1-L19】【F:app_passify/urls.py†L23-L48】
- **Impacto:** Warnings `urls.W005`, riesgo de `NoReverseMatch` y resoluciones ambiguas (`admin`, `containers`).
- **Causa raíz:** Inclusión doble de `admin/` y del namespace `containers` sin diferenciar nombres.
- **Propuesta:** Mantener `admin/` sólo en `app_passify/urls.py` y declarar `app_name` + namespace consistente en `paasify/urls.py`.

### 2.3 Reserva de puertos no atómica
- **Archivo/Línea:** `containers/services.py` líneas 13-60 y 172-185. 【F:containers/services.py†L13-L185】
- **Impacto:** Condición de carrera: dos solicitudes simultáneas pueden reservar mismo puerto provocando `IntegrityError` o colisiones Docker.
- **Causa raíz:** Consulta + creación sin transacción ni bloqueo (`PortReservation.objects.filter(...)`).
- **Propuesta:** Ejecutar dentro de `transaction.atomic()` con `select_for_update` o usar `PortReservation.reserve_free_port()` centralizando lógica.

### 2.4 Procesos Docker bloqueantes y sin sandbox
- **Archivo/Línea:** `containers/services.py` líneas 186-286. 【F:containers/services.py†L186-L286】
- **Impacto:** Llamadas a `subprocess.run` (`docker compose`, `docker build`) bloquean el worker y ejecutan YAML/Dockerfile suministrado por alumno sin controles; riesgo de DoS y escalada.
- **Causa raíz:** Ejecución directa desde la vista síncrona sin colas ni límites.
- **Propuesta:** Delegar builds en jobs asíncronos (Celery/RQ), validar Dockerfile/compose y ejecutar en runner aislado.

### 2.5 Duplicación de helpers de rol
- **Archivo/Línea:** `containers/views.py` líneas 50-80. 【F:containers/views.py†L50-L80】
- **Impacto:** Funciones `user_is_student/teacher` duplicadas tres veces pueden divergir en futuros merges y dificultan mantenimiento.
- **Causa probable:** Conflictos de merge no resueltos.
- **Estrategia de solución:** Consolidar helpers en `paasify.roles`, importar funciones únicas.

### 2.6 Reintentos infinitos en terminal HTMX
- **Archivo/Línea:** `templates/containers/terminal.html` líneas 31-60; `containers/consumers.py` líneas 67-133. 【F:templates/containers/terminal.html†L31-L60】【F:containers/consumers.py†L67-L133】
- **Impacto:** Tras `close(4403)` o caída del exec, el front-end reconecta indefinidamente, creando hilos daemon adicionales y posibles fugas de sockets.
- **Causa raíz:** `setTimeout(connectSocket, 3000)` sin evaluar motivo del cierre.
- **Propuesta:** Manejar códigos de cierre en JS y detener reintento en errores permanentes; unir hilo en `disconnect`.

## 3. Incoherencias o riesgos
- **Repetición de constantes:** `MAX_UPLOAD_SIZE`, `COMPOSE_EXTENSIONS` duplicados en `containers/services.py`. 【F:containers/services.py†L16-L26】
- **Validación de JSON manual:** `ast.literal_eval` en `edit_service` permite errores 500 al introducir estructuras no válidas; falta sanitización. 【F:containers/views.py†L624-L646】
- **Valores por defecto estáticos:** `UserProject.time` usa `datetime.now().time()` fijo, genera warning W161. 【F:paasify/models/ProjectModel.py†L1-L30】
- **Dependencias cruzadas:** `containers/views` consulta modelos `paasify` directamente (p. ej. `Sport`, `UserProject`), elevando acoplamiento.
- **Plantillas con caracteres mojibake:** `student_panel.html` contiene caracteres UTF-8 mal codificados (“Â·”), indica guardado con BOM. 【F:templates/containers/student_panel.html†L6-L78】
- **Reutilización de plantilla alumno para profesores:** `post_login` redirige correctamente, pero menú en `base.html` expone enlaces de ambos roles según flags, generando redirecciones innecesarias. 【F:templates/base.html†L16-L68】【F:containers/views.py†L331-L387】
- **Terminal sin control de salida:** `TerminalConsumer` cierra socket pero no invalida `reader_thread`, potencial fuga en reconexiones rápidas. 【F:containers/consumers.py†L67-L133】
- **Requisitos sin versionado:** `requirements.txt` lista paquetes sin pins; riesgo de incompatibilidades futuras con Django 5.x. 【F:requirements.txt†L1-L48】

## 4. Testing de flujos
- **Login y roles:** Código de `post_login` cubre admin→`/admin/`, profesor→dashboard, alumno→mis asignaturas; falta test automatizado que valide redirecciones y permisos (`student_panel` retorna 403 a usuarios sin grupo). 【F:containers/views.py†L331-L440】
- **Gestión de contenedores:** `ServiceViewSet.create` valida modo default/custom y ejecuta `run_container`; no hay pruebas unitarias para fallos de build (`subprocess.CalledProcessError`) ni para `custom_port`. 【F:containers/views.py†L132-L220】【F:containers/services.py†L186-L286】
- **Terminal interactiva:** Seguridad por owner confirmada (`get_object_or_404(... owner=user)`); no existen tests de WebSocket (`connect/receive`). 【F:containers/consumers.py†L19-L95】
- **PortReservation/Service lifecycle:** Único test `tests/test_containers.py` verifica unicidad y ciclo run-stop-remove con Docker disponible; ausencia de mocks dificulta CI sin daemon. 【F:tests/test_containers.py†L1-L60】
- **Migraciones:** `showmigrations` ejecutado → múltiples pendientes, warnings por namespaces. 【3b978a†L1-L58】
- **Cobertura HTMX/UI:** No se simulan eventos HX ni render de `_service_rows.html`; potencial `TemplateDoesNotExist` no detectado en pipeline actual.
- **Resultado global de pruebas:** `pytest` → 1 pasado, 1 omitido (Docker no disponible). 【0f624d†L1-L5】

## 5. Recomendaciones Técnicas
- Externalizar configuración sensible y parametrizar `ALLOWED_HOSTS`, habilitar lectura desde variables de entorno.
- Resolver warnings de URLs creando namespaces únicos (`app_name = "paasify"`, prefijo `/paasify/containers/` exclusivo) y eliminando duplicidades.
- Reescribir gestión de puertos usando `PortReservation.reserve_free_port()` dentro de transacción o bloque optimista.
- Introducir cola de trabajos (Celery/RQ) para `run_container`/`remove_container`, con límites de tiempo y entornos aislados.
- Refactorizar helpers de rol para reutilizar `paasify.roles` y eliminar duplicaciones.
- Ajustar terminal HTMX para detener reconexiones tras códigos ≥4400 y cerrar hilo explícitamente.
- Validar y normalizar JSON en `edit_service` (usar `json.loads` y esquemas) evitando `literal_eval`.
- Normalizar codificación de plantillas (`student_panel.html`) y centralizar scripts para evitar recarga periódica de librerías.
- Pinnear versiones mínimas compatibles en `requirements.txt` (e.g., `Django==5.0.3`, `channels==4.x`) tras verificar compatibilidad.
- Añadir pruebas: redirecciones de roles, validación de `custom_port`, manejo de errores HTMX, WebSocket (`communicator`), parsing de env/volúmenes, y escenarios `docker compose` fallidos mediante mocks.

## Módulos afectados
- `app_passify.settings`
- `app_passify.urls`
- `paasify.urls`
- `paasify.models.ProjectModel`
- `containers.services`
- `containers.views`
- `containers.consumers`
- `templates/base.html`
- `templates/containers/*.html`
- `tests/test_containers.py`
- `requirements.txt`

## Tabla de priorización
| Prioridad | Acción | Área |
| --- | --- | --- |
| Alta | Externalizar configuraciones sensibles y corregir namespaces duplicados | Seguridad / Routing |
| Alta | Serializar puertos de forma atómica y aislar ejecución Docker en tareas asíncronas | Contenedores |
| Media | Refactorizar helpers de rol, validar JSON en edición de servicios, mejorar terminal HTMX | Roles / UX |
| Media | Normalizar plantillas y navegación por rol, corregir codificación UTF-8 | UI |
| Baja | Pinnear dependencias y ampliar cobertura de tests (HTMX, WebSocket, compose fallido) | Tooling / QA |
| Baja | Revisar default `UserProject.time` y aplicar migraciones pendientes en entornos controlados | Datos |
