"""
Middleware para autenticacion mediante Bearer Token (DRF) con expiración.
Valida tokens DRF con caducidad de 30 días generados desde el perfil del usuario.
"""
from django.http import JsonResponse


class TokenAuthMiddleware:
    """
    Intercepta peticiones API con Authorization: Bearer TOKEN.
    - Valida tokens DRF con expiración (paasify.models.ExpiringToken)
    - Verifica que el token no haya expirado
    - Si el token es valido, autentica al usuario y desactiva CSRF para la request.
    - Si el token es invalido o expirado, devuelve 401 JSON.
    - Si no hay header Bearer, deja fluir la request sin modificar request.user.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if request.path.startswith("/api/") and auth_header.startswith("Bearer "):
            token_key = auth_header.replace("Bearer ", "", 1).strip()
            
            # Validar token API (ExpiringToken)
            from paasify.models.TokenModel import ExpiringToken
            
            try:
                token_obj = ExpiringToken.objects.select_related('user').get(key=token_key)
                if token_obj.is_expired():
                    return JsonResponse(
                        {
                            "detail": "Token expirado.",
                            "code": "token_not_valid",
                        },
                        status=401,
                    )
                user = token_obj.user
            except ExpiringToken.DoesNotExist:
                return JsonResponse(
                    {
                        "detail": "Token invalido o expirado.",
                        "code": "token_not_valid",
                    },
                    status=401,
                )

            # Autenticar usuario
            request.user = user
            request._dont_enforce_csrf_checks = True
        
        return self.get_response(request)
