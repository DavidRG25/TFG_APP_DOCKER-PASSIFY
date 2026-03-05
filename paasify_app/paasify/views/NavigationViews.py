import django.core.paginator
from django.shortcuts import render
from paasify.models.ProjectModel import UserProject
from django.core.paginator import Paginator

def index(request):
    context = {
        'user_id': request.session.get('user_id', None),
        'username': request.session.get('username', None)
    }
    return render(request, "index.html", context)

def table(request, n):
    projects_list = UserProject.objects.all().order_by("-date", "id")
    paginator = Paginator(projects_list, 10)

    next_page = None
    previous_page = None
    projects = []

    try:
        current_page = paginator.page(n)

        if current_page.has_next():
            next_page = current_page.next_page_number()
        if current_page.has_previous():
            previous_page = current_page.previous_page_number()

        projects = current_page.object_list

    except django.core.paginator.EmptyPage:
        projects = []
    except django.core.paginator.PageNotAnInteger:
        projects = []

    data = {
        "projects": projects,
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

