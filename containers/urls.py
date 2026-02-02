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
    path("terminal/<int:pk>/", views.terminal_view, name="terminal_view"),
    path("edit/<int:pk>/", views.edit_service, name="edit_service"),
    
    # Nueva página dedicada para crear servicio
    path("new/", views.new_service_page, name="new_service"),
    
    # Verificar imágenes de DockerHub
    path("verify-dockerhub/", views.verify_dockerhub_image, name="verify_dockerhub"),
    
    # Verificar disponibilidad de puertos
    path("check-port/", views.check_port_availability, name="check_port"),
    
    # Gestión de tokens API
    path("api-token/", views.manage_api_token, name="api_token"),
]
