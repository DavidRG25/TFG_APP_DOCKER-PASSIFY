import django.core.paginator
from django.shortcuts import render
from paasify.models.ProjectModel import Game
from django.core.paginator import Paginator

def index(request):
    context = {
        'user_id': request.session.get('user_id', None),
        'username': request.session.get('username', None)
    }
    return render(request, "index.html", context)

def table(request, n):
    games_list = Game.objects.all().order_by("-date", "id")
    paginator = Paginator(games_list, 10)

    next_page = None
    previous_page = None
    games = []

    try:
        current_page = paginator.page(n)

        if current_page.has_next():
            next_page = current_page.next_page_number()
        if current_page.has_previous():
            previous_page = current_page.previous_page_number()

        games = current_page.object_list

    except django.core.paginator.EmptyPage:
        games = []
    except django.core.paginator.PageNotAnInteger:
        games = []

    data = {
        "games": games,
        "notifications": get_notifications(),
        "n_len": len(get_notifications()),
        "total": paginator.count,
        "current": n,
        "next": next_page,
        "previous": previous_page,
        "n": n,
        "user_id": request.session.get('user_id', None),
        "username": request.session.get('username', None),
        "section": "table"
    }

    return render(request, "table.html", data)

def get_notifications():
    notifications = []
    return notifications

def config(request):
    if request.session.get("user_id", None):
        return render(request, "custom_admin.html")
    else:
        return render(request, "Error.html", {
            "type": 403,
            "message": "Error de autenticación",
            "description": "Debes estar autenticado para realizar esta acción"
        })