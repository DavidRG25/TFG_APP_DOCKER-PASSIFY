from django.shortcuts import redirect
from django.urls import reverse

class ForcePasswordChangeMiddleware:
    """
    Middleware para forzar a un usuario a cambiar su contraseña
    si el campo `must_change_password` de su UserProfile está activo.
    Afecta a todos los usuarios, incluyendo administradores en su primer login.
    
    - Usuarios normales (alumnos/profes): se redirigen a /profile/ donde el modal
      de "Protege tu cuenta" les pide la nueva contraseña.
    - Superusuarios (admin): se redirigen a /admin/password_change/ para usar
      el formulario nativo del panel de administración.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Creación perezosa del UserProfile para superusuarios (su 1er login)
            if getattr(request.user, 'is_superuser', False):
                if not hasattr(request.user, 'user_profile'):
                    from paasify.roles import ensure_user_profile
                    profile = ensure_user_profile(request.user)
                    profile.must_change_password = True
                    profile.save()

            if hasattr(request.user, 'user_profile') and request.user.user_profile.must_change_password:
                path = request.path_info
                
                # Ignorar peticiones API y estáticos para no romper clientes
                if path.startswith('/api/') or path.startswith('/static/'):
                    return self.get_response(request)
                    
                try:
                    profile_url = reverse('profile')
                    change_password_url = reverse('change_password')
                    logout_url = reverse('logout')
                    login_url = reverse('paasify:login')
                    
                    admin_change_pw_url = reverse('admin:password_change')
                    admin_logout_url = reverse('admin:logout')
                    admin_pw_done_url = reverse('admin:password_change_done')
                    
                    # Rutas donde el usuario sí puede estar aunque deba cambiar la contraseña
                    allowed_paths = [
                        profile_url, change_password_url, logout_url, login_url,
                        admin_change_pw_url, admin_logout_url, admin_pw_done_url
                    ]
                    
                    # Si acabamos de aterrizar en admin:password_change_done, el admin
                    # acaba de cambiarla exitosamente, ¡limpiamos el flag!
                    if path == admin_pw_done_url:
                        request.user.user_profile.must_change_password = False
                        request.user.user_profile.save()
                        return self.get_response(request)
                        
                    if path not in allowed_paths:
                        # Si es superusuario, SIEMPRE al formulario del panel admin
                        if request.user.is_superuser:
                            return redirect(admin_change_pw_url)
                        # El resto de usuarios al perfil (donde el modal ya muestra el aviso)
                        return redirect(profile_url)
                except Exception:
                    pass

        response = self.get_response(request)
        return response
