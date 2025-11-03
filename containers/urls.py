# containers/urls.py
from django.urls import path
from . import views
from .views import ServiceViewSet

app_name = "containers"

urlpatterns = [
    # Panel del alumno (listado general de servicios)
    path("", views.student_panel, name="student_panel"),

    # Asignaturas del alumno / profesor
    path("subjects/", views.student_subjects, name="student_subjects"),
    path("subjects/<int:subject_id>/", views.student_services_in_subject, name="student_services_in_subject"),

    # Fragmento HTMX de la tabla
    path("table-fragment/", views.service_table, name="service_table"),

    # Terminal web
    path("terminal/<int:pk>/", views.terminal_view, name="terminal_view"),

    # Editar servicio (env/volúmenes) y reiniciar
    path("edit/<int:pk>/", views.edit_service, name="edit_service"),

    # ===========================
    # Helpers de acciones Service
    # ===========================
    # Estos endpoints delegan en las acciones del ViewSet para poder usar {% url 'containers:...' %}
    path("service/<int:pk>/start/",   ServiceViewSet.as_view({"post": "start"}),      name="service-start"),
    path("service/<int:pk>/stop/",    ServiceViewSet.as_view({"post": "stop"}),       name="service-stop"),
    path("service/<int:pk>/remove/",  ServiceViewSet.as_view({"post": "remove"}),     name="service-remove"),
    path("service/<int:pk>/logs/",    ServiceViewSet.as_view({"get":  "logs"}),       name="service-logs"),
    path("service/<int:pk>/dockerfile/", ServiceViewSet.as_view({"get": "dockerfile"}), name="service-dockerfile"),
    path("service/<int:pk>/compose/", ServiceViewSet.as_view({"get":  "compose"}),    name="service-compose"),
]

