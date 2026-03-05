from django.shortcuts import redirect
from django.urls import reverse

class ForcePasswordChangeMiddleware:
    """
    Middleware para forzar a un usuario a cambiar su contraseña
    si el campo `must_change_password` de su UserProfile está activo.
    No se aplica si la petición va hacia logout o a la página de 
    cambiar contraseña. No afecta a superusuarios o al admin global.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Ignorar para vistas especiales o admin puro
            path = request.path_info
            if path.startswith('/admin/') or path.startswith('/api/'):
                return self.get_response(request)

            try:
                profile_url = reverse('profile')
                change_password_url = reverse('change_password')
                logout_url = reverse('logout')
                
                # Vistas permitidas para no crear un bucle de redirecciones
                allowed_paths = [
                    profile_url,
                    change_password_url, 
                    logout_url,
                    reverse('paasify:login')
                ]
                
                if path not in allowed_paths:
                    # Comprobar si tiene el flag must_change_password
                    if hasattr(request.user, 'user_profile'):
                        if request.user.user_profile.must_change_password:
                            from django.contrib import messages
                            
                            # Añadir solo un mensaje en la sesion si aún no hay uno del mismo tipo
                            has_warning = False
                            storage = messages.get_messages(request)
                            for m in storage:
                                if "Debes configurar una contraseña personal" in str(m):
                                    has_warning = True
                                    break
                            # Restore messages back
                            storage.used = False
                                
                            if not has_warning:
                                messages.warning(request, "Debes configurar una contraseña personal antes de continuar.")
                            return redirect(profile_url)
            except Exception:
                pass

        response = self.get_response(request)
        return response
