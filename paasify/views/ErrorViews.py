from django.shortcuts import render

def handler404(request, exception):
    """Manejo personalizado de error 404 (Página no encontrada)"""
    return render(request, '404.html', status=404)

def handler500(request):
    """Manejo personalizado de error 500 (Error del servidor)"""
    return render(request, '500.html', status=500)

def handler403(request, exception=None):
    """Manejo personalizado de error 403 (Acceso denegado)"""
    return render(request, 'containers/errors/no_permission.html', {
        'error_title': 'Acceso Restringido',
        'error_message': 'No tienes permisos suficientes para realizar esta acción o acceder a este recurso.'
    }, status=403)
