# Implementacion de Middleware de Autenticacion API con Bearer Token (dev2)

## Archivos modificados
- `paasify/middleware/TokenAuthMiddleware.py` (nuevo): valida `Authorization: Bearer TOKEN` en rutas `/api/*` y responde 401 si el token es invalido o expirado.
- `paasify/middleware/__init__.py`: expone `TokenAuthMiddleware`.
- `app_passify/settings.py`: agrega el middleware en la pila.
- `paasify/views/ProfileView.py` y `templates/profile.html`: gestion de tokens desde el perfil.
- `paasify/models/StudentModel.py`: campos `api_token`, `token_created_at` y helpers de generacion/refresh.
- `paasify/admin.py`: visualizacion parcial del token y accion de refresco en admin.
- `security/tests.py`: pruebas del middleware con tokens emitidos desde el perfil.
- `README.md`: instrucciones de uso de Bearer Token via perfil.

## Comportamiento
- Para peticiones `/api/*` con header `Authorization: Bearer TOKEN`:
  - Si el token es valido, se asigna `request.user` y se desactiva CSRF para esa request.
  - Si el token es invalido/expirado, se responde `401` JSON con `code=token_not_valid`.
  - Sin header Bearer, la request fluye sin cambios (autenticacion por sesion sigue funcionando).
- Los tokens se generan/refrescan desde el perfil y se guardan en `UserProfile.api_token` con fecha `token_created_at`.

## Pruebas sugeridas
- `python manage.py test security.tests.TokenAuthMiddlewareTests`.
- Generar token desde **Mi Perfil** y consumir un endpoint con `curl -H "Authorization: Bearer TOKEN" ...`.

## Notas
- Tokens firmados con `SECRET_KEY` y caducidad definida en `generate_token` (365 dias por defecto).
- Refrescar un token lo invalida; usar el boton en el perfil.
- Middleware ubicado despues de `AuthenticationMiddleware` en `MIDDLEWARE`.

Fecha: 2025-11-24 23:54
