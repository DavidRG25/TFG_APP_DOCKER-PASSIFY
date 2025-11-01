from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.conf import settings

from paasify.views.NavigationViews import get_notifications


def login(request):
    """
    Login unificado:
    - Autentica con django.contrib.auth (request.user pasa a estar autenticado).
    - Mantiene algunas claves en session por compatibilidad con plantillas antiguas.
    - Si es AJAX (htmx/fetch), devuelve JSON con redirect; si no, redirige.
    """
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)

        if user is None:
            msg = "Usuario o contraseña incorrectos."
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"message": msg}, status=403)
            ctx = {
                "error": msg,
                "section": "login",
                "notifications": get_notifications(),
                "n_len": len(get_notifications()),
            }
            return render(request, "registration/login.html", ctx)

        # Autenticar sesión Django
        auth_login(request, user)

        # Compatibilidad con plantillas que leen estas claves
        request.session["user_id"] = user.id
        request.session["username"] = user.username
        request.session["email"] = user.email
        request.session["is_staff"] = user.is_staff
        request.session["is_superuser"] = user.is_superuser

        # Respuesta según tipo de petición
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"message": "success", "redirect": "/post-login/"}, status=200)
        return redirect(settings.LOGIN_REDIRECT_URL)

    # GET: si ya está autenticado, envía a su pantalla por rol
    if request.user.is_authenticated:
        return redirect("/post-login/")

    ctx = {
        "section": "login",
        "notifications": get_notifications(),
        "n_len": len(get_notifications()),
    }
    return render(request, "registration/login.html", ctx)


def logout(request):
    """Cierra sesión y vuelve al login configurado."""
    auth_logout(request)
    # Limpieza extra de la sesión (opcional, ya lo hace auth_logout)
    request.session.flush()
    return redirect(settings.LOGIN_URL)  # p.ej. /paasify/login/