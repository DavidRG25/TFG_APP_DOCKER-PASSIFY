# Análisis integral Codex – PaaSify (rama develop)

## 1. Resumen Ejecutivo
- Entorno Django 5.x funcional, pero con configuraciones sensibles expuestas (`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS="*"`), lo que reduce la seguridad base.
- Arquitectura modular con apps `paasify`, `containers` y `security`; se observan dependencias cruzadas controladas, aunque persisten acoplamientos fuertes entre vistas y modelos legacy.
- Flujo de autenticación diferenciado por rol funciona conceptualmente, pero la navegación expone rutas de alumnos y profesores simultáneamente generando redirecciones forzadas.
- Gestión de contenedores operativa a nivel de código, aunque ejecuta builds y `docker compose` en el hilo web sin aislamiento, elevando riesgo de bloqueos.
- Terminal interactiva valida pertenencia del servicio, pero el cliente HTMX reintenta conexiones incluso tras cierres por permisos, lo que puede saturar sesiones.
- `manage.py showmigrations` revela namespaces duplicados y valores por defecto estáticos; ningún esquema ha sido aplicado al SQLite local.
- Pruebas automatizadas limitadas (`pytest`), sólo cubren reserva de puertos y ciclo básico del contenedor; resto de flujos sin test formal.
- Estabilidad estimada: **65‑70 %** (depende de Docker externo, ausencia de colas y validaciones adicionales).

## 2. Errores Críticos
### 2.1 Configuración insegura en producción
- **Archivo/Línea:** `app_passify/settings.py` líneas 11-20.
- **Impacto:** Exposición de `SECRET_KEY`, `DEBUG=True` y `ALLOWED_HOSTS=["*"]` permite secuestro de sesión, cross-site scripting y despliegues inseguros.
- **Causa raíz:** Uso de valores hardcodeados para simplificar desarrollo.
- **Propuesta:** Externalizar variables a `.env`/Docker secrets y condicionar `DEBUG` por entorno.

### 2.2 Namespaces duplicados en URLs
- **Archivo/Línea:** `paasify/urls.py` líneas 1-19; `app_passify/urls.py` líneas 23-48.
- **Impacto:** Warnings `urls.W005`, riesgo de `NoReverseMatch` y resoluciones ambiguas (`admin`, `containers`).
- **Causa raíz:** Inclusión doble de `admin/` y del namespace `containers` sin diferenciar nombres.
- **Propuesta:** Mantener `admin/` sólo en `app_passify/urls.py` y declarar `app_name` + namespace consistente en `paasify/urls.py`.

### 2.3 Reserva de puertos no atómica
- **Archivo/Línea:** `containers/services.py` líneas 13-60 y 172-185.
- **Impacto:** Condición de carrera: dos solicitudes simultáneas pueden reservar mismo puerto provocando `IntegrityError` o colisiones Docker.
- **Causa raíz:** Consulta + creación sin transacción ni bloqueo (`PortReservation.objects.filter(...)`).
- **Propuesta:** Ejecutar dentro de `transaction.atomic()` o usar `PortReservation.reserve_free_port()` centralizando lógica.

### 2.4 Procesos Docker bloqueantes y sin sandbox
- **Archivo/Línea:** `containers/services.py` líneas 186-286.
- **Impacto:** Llamadas a `subprocess.run` (`docker compose`, `docker build`) bloquean el worker y ejecutan YAML/Dockerfile suministrado por alumno sin controles; riesgo de DoS y escalada.
- **Causa raíz:** Ejecución directa desde la vista síncrona sin colas ni límites.
- **Propuesta:** Delegar builds en jobs asíncronos (Celery/RQ), validar Dockerfile/compose y ejecutar en runner aislado.

### 2.5 Duplicación de helpers de rol
- **Archivo/Línea:** `containers/views.py` líneas 50-80.
- **Impacto:** Funciones `user_is_student/teacher` duplicadas tres veces pueden divergir en futuros merges y dificultan mantenimiento.
- **Causa probable:** Conflictos de merge no resueltos.
- **Propuesta:** Consolidar helpers en `paasify.roles`, importar funciones únicas.

### 2.6 Reintentos infinitos en terminal HTMX
- **Archivo/Línea:** `templates/containers/terminal.html` líneas 31-60; `containers/consumers.py` líneas 67-133.
- **Impacto:** Tras `close(4403)` o caída del exec, el front-end reconecta indefinidamente, creando hilos daemon adicionales y posibles fugas de sockets.
- **Causa raíz:** `setTimeout(connectSocket, 3000)` sin evaluar motivo del cierre.
- **Propuesta:** Manejar códigos de cierre en JS y detener reintento en errores permanentes; unir hilo en `disconnect`.

## 3. Incoherencias o riesgos
- **Repetición de constantes:** `MAX_UPLOAD_SIZE`, `COMPOSE_EXTENSIONS` duplicados en `containers/services.py`.
- **Validación de JSON manual:** `ast.literal_eval` en `edit_service` permite errores 500 al introducir estructuras inválidas; falta sanitización.
- **Valores por defecto estáticos:** `UserProject.time` usa `datetime.now()` fijo, genera warning W161.
- **Dependencias cruzadas:** `containers/views` consulta modelos `paasify` directamente, elevando acoplamiento.
- **Plantillas con mojibake:** `student_panel.html` contiene caracteres UTF-8 mal codificados (indica guardado con BOM).
- **Reutilización de plantilla alumno para profesores:** Menú en `base.html` expone enlaces de ambos roles generando redirecciones innecesarias.
- **Terminal sin control de salida:** Reader thread no se cierra tras desconectar, riesgo de fugas.
- **Requisitos sin versionado:** `requirements.txt` lista paquetes sin pins; riesgo de incompatibilidades futuras.

## 4. Testing de flujos
- **Login y roles:** `post_login` cubre escenarios pero falta test automatizado.
- **Gestión de contenedores:** `ServiceViewSet.create` valida modos, sin pruebas unitarias para fallos.
- **Terminal interactiva:** Seguridad por owner confirmada; no existen tests WebSocket.
- **PortReservation/Service lifecycle:** Único test verifica puerto y ciclo run-stop-remove con Docker disponible.
- **Migraciones:** `showmigrations` indica pendientes y warnings.
- **Cobertura HTMX/UI:** No se simulan eventos HX.
- **Resultado global de pruebas:** `pytest` → 1 pasada, 1 omitida.

## 5. Recomendaciones Técnicas
- Externalizar configuración sensible y parametrizar `ALLOWED_HOSTS`.
- Resolver warnings de URLs creando namespaces únicos.
- Reescribir gestión de puertos con reservas atómicas.
- Introducir cola de trabajos para contenedores.
- Refactorizar helpers de rol y validar JSON en ediciones.
- Ajustar terminal HTMX para detener reconexiones tras códigos de error.
- Normalizar codificación de plantillas.
- Pinnear dependencias y ampliar cobertura de tests.

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

## 7. Resumen de ajustes aplicados (2025-11-05)
- Configuraciones sensibles delegadas a variables de entorno (`app_passify/settings.py`) y namespaces saneados (`paasify/urls.py`, `app_passify/urls.py`).
- Reserva de puertos atómica y modelos sin mojibake (`containers/models.py`, `paasify/models/ProjectModel.py`, `paasify/models/StudentModel.py`).
- Ejecución de contenedores encolada mediante `ThreadPoolExecutor`, validación JSON segura y pruebas actualizadas (`containers/services.py`, `containers/views.py`, `tests/test_containers.py`).
- Vistas HTMX sin duplicados y con permisos coherentes, incluyendo bypass para superusuarios (`containers/views.py`).
- Terminal WebSocket estabilizada y plantillas normalizadas (`containers/consumers.py`, `templates/containers/*.html`, `templates/base.html`, `templates/professor/*.html`).
- Migración `0031_alter_userproject_time.py` para default timezone-aware y dependencias fijadas en `requirements.txt`.
- Documentación de continuidad registrada en `document/continuacion_codex_analisis_20251105-1105.md`.
