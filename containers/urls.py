# containers/urls.py
from django.urls import path
from . import views

app_name = "containers"

urlpatterns = [
    path("", views.student_panel, name="student_panel"),

    # SOLO rutas propias de containers (sin duplicar post-login/professor)
    path("subjects/", views.student_subjects, name="student_subjects"),
    path("subjects/<int:subject_id>/", views.student_services_in_subject, name="student_services_in_subject"),

    path("table-fragment/", views.service_table, name="service_table"),
    path("terminal-v2/<int:pk>/", views.terminal_v2_view, name="terminal_v2"),  # Terminal mejorada
    path("logs/<int:pk>/", views.logs_page, name="logs_page"),  # Página de logs
    path("edit/<int:pk>/", views.edit_service, name="edit_service"),
    
    # Nueva página dedicada para crear servicio
    path("new/", views.new_service_page, name="new_service"),
    
    # Verificar imágenes de DockerHub
    path("verify-dockerhub/", views.verify_dockerhub_image, name="verify_dockerhub"),
    
    # Verificar disponibilidad de puertos
    path("check-port/", views.check_port_availability, name="check_port"),
    
    # Análisis de Docker Compose
    path("analyze-compose/", views.analyze_compose, name="analyze_compose"),
    
    # Gestión de tokens API
    path("api-token/", views.manage_api_token, name="api_token"),
    
    # Documentación dedicada de la API (Navegación por secciones)
    path("api-docs/", views.api_documentation_view, name="api_docs"),
    path("api-docs/<slug:section_slug>/", views.api_documentation_view, name="api_docs_section"),


    # Generador interactivo de comandos API
    path("api-generator/", views.api_command_generator_view, name="api_generator"),
]
