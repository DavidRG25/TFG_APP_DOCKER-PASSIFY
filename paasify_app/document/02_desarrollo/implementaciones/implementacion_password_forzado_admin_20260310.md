# Seguridad: Cambio de contraseña forzado para Administradores

**Fecha:** 10/03/2026
**Estado:** ✅ Completado
**Referencia Plan:** `plan_reunion_03032026.md` → Seguridad y Sesiones → Cambio de contraseña forzado del Admin

---

## 📋 Objetivo

Garantizar que al hacer login por primera vez con un superusuario (admin) en la plataforma (por ejemplo, aquellos generados por comandos `createsuperuser` o herramientas de inicialización), el sistema intercepte la sesión de forma idéntica a como lo hace con alumnos y profesores, forzando obligatoriamente el cambio de contraseña por motivos de seguridad antes de permitirles navegar.

## 🚧 Contexto y Arquitectura Original

*   El sistema cuenta con un modelo `UserProfile` que contiene la bandera `must_change_password`.
*   Existe un `ForcePasswordChangeMiddleware` encargado de interceptar peticiones, comprobar dicha bandera en el perfil activo y encerrar al usuario en una página de cambio de contraseña forzoso (`/profile/`).
*   **Problema principal:** Los superusuarios generados nativamente por Django **no** poseen automáticamente un registro de `UserProfile`. Por lo tanto, el middleware histórico fallaba al intentar acceder a la propiedad, se producía un error silencioso ahogado en un `try/except` y el administrador quedaba con paso libre eterno a cualquier ruta.
*   **Problema secundario UI:** Se enviaban notificaciones Toast a través del sistema de `messages` de Django (`"⚠️ POR SEGURIDAD: Debes configurar..."`), que colisionaban estéticamente con el z-index de los modales y que resultaban redundantes, ya que la interfaz ya presenta de por sí un modal de ancho casi completo (`"Protege tu cuenta"`) con el mismo mensaje y el formulario de cambio. Además, al redirigirse al administrador al frontend `/profile/`, resultaba incoherente para un administrador puro.

## ✅ Soluciones Implementadas

Se ha reimplementado de manera integral la lógica central en el archivo `paasify/middleware/must_change_password.py`, y ajustado aspectos de visualización en el template base.

### 1. Inyección Perezosa de Perfiles de Administrador

*   El Middleware ha sido modificado para que reciba cualquier inicio de sesión activo y consulte `getattr(request.user, 'is_superuser', False)`.
*   Si es admin y no dispone del atributo en memoria (`hasattr(request.user, 'user_profile') == False`), importamos instantes antes la función utilitaria nativa del sistema de roles (`ensure_user_profile` desde `paasify.roles`) para enganchar imperativamente un nuevo registro de perfil vacío dependiente del modelo Administrador, activando por defecto en código el flag: `profile.must_change_password = True` y salvando a la BD. Así la trampa actúa igual para todos en el sistema.

### 2. Bifurcación Inteligente de Redirecciones (Front vs. Panel Admin)

*   Una vez bloqueado por el flag, se abrieron de urgencia las rutas de administración de Django permitidas en la whitelist (`admin:password_change`, `admin:logout` y especialmente `admin:password_change_done`).
*   El bucle condicional se ramificó. 
    *   Si es un usuario mortal (`alumnos`/`profes`), la asfixia redirige forzosamente hacia `profile_url` (cuyos templates lanzan el modal amarillo de frontend).
    *   Si detecta que se trata de `request.user.is_superuser`, **fuerza la redirección imperativa hacia `admin_change_pw_url`**, aterrizando directamente dentro de la interfaz limpia del panel de control de `Jazzmin` / `Admin`, manteniéndole su entorno natural pero reteniéndolo firmemente ahí.

### 3. Mecanismo de liberación

*   La validación de la eliminación de la bandera se produce por la intercepción de URLs.
*   Cuando en la URL se detecte la visita única a `admin_pw_done_url` (pantalla verde de "Contraseña modificada" posterior a form submit), se ejecuta en ese frame `request.user.user_profile.must_change_password = False`, limpiando la celda y dejándole liberado para moverse a `/admin/` permanentemente en su futuro.

### 4. Limpiezas Visuales (Z-Index Toasts)

*   Se procedió a eliminar la mensajería del toast `messages.warning` duplicativa que originaba el middleware ahorrando redundancia en la interfaz frontal del alumno/profesor.
*   Durante el proceso y a nivel de diseño UI visual colateral, se forzó el `z-index: 200000` de las notificaciones `SweetAlert2` del archivo maestro `base.html` y se le introdujo un degradado dorado cuando el evento emitido es tipo `Warning`, manteniendo mejor cohesión frente a cortinas oscuras y modales de advertencia en otros puntos futuros del programa.

## 📁 Archivos Modificados

| Ruta y Archivo | Modificación Resumida |
| :--- | :--- |
| `paasify_app/paasify/middleware/must_change_password.py` | (Refactor de Core) Creación perezosa SuperUser Profile, ruteo bifurcado Front/Admin, eliminación notificaciones duplicadas, y liberación de la flag tras evento `change_done` de Jazzmin. |
| `paasify_app/templates/base.html` | (Corrección de diseño heredada) Modificaciones inline del `z-index` a capas superiores, inserción JavaScript dinámico en `didOpen` Swal2 y pintados Warning degradado para futuros eventos globales. |
| `paasify_app/document/04_planes/plan_reunion_03032026.md`| Marcado de completitud de tarea original (`[x]`). |
