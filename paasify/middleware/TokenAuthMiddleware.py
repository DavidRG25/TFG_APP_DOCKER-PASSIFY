"""
Middleware para autenticacion mediante Bearer Token JWT.
Valida tokens generados desde el perfil del usuario y asigna request.user.
"""
from django.http import JsonResponse

from paasify.models.StudentModel import UserProfile


class TokenAuthMiddleware:
    """
    Intercepta peticiones API con Authorization: Bearer TOKEN.
    - Si el token es valido, autentica al usuario y desactiva CSRF para la request.
    - Si el token es invalido/expirado, devuelve 401 JSON.
    - Si no hay header Bearer, deja fluir la request sin modificar request.user.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if request.path.startswith("/api/") and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "", 1).strip()
            try:
                user = UserProfile.get_user_from_token(token)
            except Exception:
                user = None

            if not user:
                return JsonResponse(
                    {
                        "detail": "Token invalido o expirado.",
                        "code": "token_not_valid",
                    },
                    status=401,
                )

            request.user = user
            request._dont_enforce_csrf_checks = True
        return self.get_response(request)
