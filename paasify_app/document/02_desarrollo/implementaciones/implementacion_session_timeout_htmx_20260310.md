# Configuración: Timeout de Sesión y Compatibilidad HTMX

**Fecha:** 10/03/2026  
**Estado:** ✅ Completado  
**Referencia Plan:** `plan_reunion_03032026.md` → Seguridad y Sesiones → Timeout de sesión

---

## 📋 Objetivo

Implementar un mecanismo de caducidad automática de la sesión de Django tras 30 minutos (1800 segundos) de inactividad por parte del usuario, incrementando la seguridad de la plataforma.

## 🚧 Problemas Técnicos Encontrados

Al habilitar la caducidad simple por cookies en Django, nos topamos con dos colisiones directas derivadas de la arquitectura frontend con **HTMX**:

1. **Renovación Infinita por Polling Background:** 
   El panel de "Mis Servicios" hace peticiones AJAX/HTMX en segundo plano cada 5 segundos a `/paasify/containers/table-fragment/` para comprobar estados de contenedores Docker. Django interpreta esto por defecto como "actividad real del usuario", extendiendo de forma infinita la sesión, inutilizando así la caducidad por inactividad.

2. **Colapso Visual de la UI ("Inception HTMX"):**
   Una vez que la sesión caducaba, si un script en segundo plano intentaba pedir datos por HTMX, Django le devolvía un código `302 Redirect` enviándolo a la pantalla de `/login/`. El navegador web, por protocolo asíncrono, sigue el `302` automáticamente, captura el HTML del login y se lo devuelve a HTMX. Como HTMX estaba esperando una tabla, terminaba incrustando un formulario de login gigantesco en mitad del panel de control destrozando la interfaz gráfica.

## ✅ Solución Implementada

Se adoptó un enfoque de control manual de vida de la sesión mediante un middleware personalizado (`paasify/middleware/session_timeout.py`). 

### Arquitectura de la Solución

1. **Desactivar el automatismo de Django (`app_passify/settings.py`):**
   ```python
   SESSION_COOKIE_AGE = 1800 # 30 min
   SESSION_SAVE_EVERY_REQUEST = False # <-- Anulamos el control ciego de Django
   SESSION_EXPIRE_AT_BROWSER_CLOSE = True
   ```
2. **Creación del `DisableSessionUpdateMiddleware`:**
   Este middleware asume la responsabilidad de decirle a Django manualmente cuándo debe reiniciar los 30 minutos de inactividad y controla el tráfico HTMX caducado:
   
   - **Evaluación Activa:** El middleware inspecciona cada petición entrante. Si coincide con una lista negra de operaciones de control en segundo plano (ej: `/paasify/containers/table-fragment/`), **NO** renueva la sesión. En caso contrario (un click normal del usuario), altera artificialmente la sesión (`request.session.modified = True`) diciéndole a Django que prolongue la vida del usuario.
   
   - **Intercepción de Redirects para HTMX:** Si la sesión caduca y Django escupe una orden `302` hacia el login, el middleware se interpone, evalúa si la petición viene de HTMX mediante sus cabeceras exclusivas (`HX-Request`), y si coincide, muta la respuesta:
     - Cambia el status a `204 No Content` (para que la Fetch API del navegador no absorba el redirect automáticamente).
     - Añade la cabecera `HX-Redirect` enviando a HTMX al `/login/`.
     - Esto hace que, en vez de inyectar el código, HTMX ejecute desde el frontal un *hard redirect* (`window.location.href`) pulcro y seguro expulsando al usuario completamente.

## 📁 Archivos Modificados / Creados

| Archivo | Cambio |
|---------|--------|
| `paasify/middleware/session_timeout.py` | (Nuevo) Middleware de protección de sesión activa y redirects lógicos. |
| `app_passify/settings.py` | Registro del middleware e incorporación de las variables de SESSION_*. |
| `document/04_planes/plan_reunion_03032026.md` | Marcada tarea "Timeout de sesión" como completada ✅ |
