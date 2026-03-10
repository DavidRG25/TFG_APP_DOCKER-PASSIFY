class DisableSessionUpdateMiddleware:
    """
    Middleware avanzado para la gestión de la inactividad de la sesión.
    
    Identifica las peticiones web HTTP y marca la sesión de Django como 'modificada'
    para renovar artificialmente la cookie basándose en SESSION_COOKIE_AGE solo 
    cuando la petición proviene de interacciones reales del usuario, NO de 
    peticiones HTMX generadas en segundo plano.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info
        
        # Rutas de endpoints automáticos/HTMX que operan en background periódico
        # (por ejemplo en el panel "Mis servicios" o logs)
        background_paths = [
            "/paasify/containers/table-fragment/",
            "/paasify/containers/check-port/",
            "/paasify/containers/status/",
            "/paasify/containers/logs/stream/"
        ]
        
        is_background = any(path.startswith(p) for p in background_paths)
        
        response = self.get_response(request)
        
        # Si NO es una petición de fondo y el usuario tiene asociada una estructura
        # de sesión activa, le decimos a Django que "fuerce" el reseteo del timeout
        # marcándola como si hubiese sido modificada.
        if not is_background and hasattr(request, 'session'):
            if request.user.is_authenticated:
                request.session.modified = True
                
        # Reparación para colapsos visuales de HTMX al caducar la sesión:
        # Si la sesión expira, Django devuelve un 302 (Redirect) hacia el login.
        # Si la petición original la hizo HTMX, el navegador sigue el 302 ciegamente y 
        # HTMX incrusta el HTML resultante (login) en medio de la web.
        # Al poner estado 204 (No content) y el cabezal HX-Redirect, HTMX toma el
        # control y fuerza una redirección total de la pestaña.
        if response.status_code in [301, 302] and hasattr(response, 'url') and '/login' in response.url.lower():
            if request.headers.get('HX-Request') == 'true' or request.META.get('HTTP_HX_REQUEST') == 'true':
                response['HX-Redirect'] = response.url
                response.status_code = 204
            
        return response
