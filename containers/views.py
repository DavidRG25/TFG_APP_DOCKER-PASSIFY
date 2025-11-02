# containers/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.http import HttpResponse, Http404
from django.utils.html import escape
from django.core.exceptions import FieldError
import ast

from rest_framework import viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response as DRF_Response

from .models import Service, AllowedImage
from .serializers import ServiceSerializer, AllowedImageSerializer
from .services import run_container, stop_container, remove_container
from paasify.models.SportModel import Sport

import docker
from docker.errors import NotFound

client = docker.from_env()


# ----------------------------- helpers -----------------------------

def _sync_service(service: Service):
    """Si el container_id ya no existe en Docker, marcamos el servicio como 'removed'."""
    if not service.container_id:
        return
    try:
        client.containers.get(service.container_id)
    except NotFound:
        service.status = "removed"
        service.save()


def in_group(user, *group_names) -> bool:
    """True si el usuario pertenece (case-insensitive) a cualquiera de los grupos dados."""
    if not (user and user.is_authenticated):
        return False
    user_groups = set(n.lower() for n in user.groups.values_list("name", flat=True))
    targets = set(g.lower() for g in group_names)
    return bool(user_groups & targets)


# ------------------------------ API --------------------------------

class ServiceViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Service.objects.filter(owner=self.request.user)
        for s in qs:
            _sync_service(s)
        return qs.exclude(status="removed")

    def create(self, request, *args, **kwargs):
        """
        Reglas:
        - mode=default  -> solo 'image' (+ puerto opcional). NO dockerfile/compose/code.
        - mode=custom   -> obligatorio Dockerfile XOR Compose; 'image' se ignora si llega.
        """
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        # --- validación de modo ---
        mode = (request.data.get("mode") or "default").lower()
        if mode not in ("default", "custom"):
            mode = "default"

        has_df   = bool(request.FILES.get("dockerfile"))
        has_comp = bool(request.FILES.get("compose"))
        has_code = bool(request.FILES.get("code"))

        if mode == "default":
            if has_df or has_comp or has_code:
                return DRF_Response(
                    {"error": "En modo 'Imagen por defecto' no se permiten Dockerfile/Compose/Código."},
                    status=400
                )
        else:  # custom
            if has_df and has_comp:
                return DRF_Response(
                    {"error": "Sube Dockerfile O docker-compose, pero no ambos."},
                    status=400
                )
            if not (has_df or has_comp):
                return DRF_Response(
                    {"error": "En modo 'Configuración personalizada' debes subir Dockerfile o docker-compose."},
                    status=400
                )

        # Puerto custom (opcional)
        custom_port = request.data.get("custom_port")
        if custom_port:
            try:
                custom_port = int(custom_port)
            except ValueError:
                return DRF_Response({"error": "Puerto inválido."}, status=400)

        # Guardado base (el serializer ya valida subject/permissions)
        service = serializer.save(owner=request.user, status="creating")

        # Asociar archivos binarios
        if has_df:
            service.dockerfile = request.FILES["dockerfile"]
        if has_comp:
            service.compose = request.FILES["compose"]
        if has_code:
            service.code = request.FILES["code"]
        service.save()

        # Lanzar contenedor
        service._custom_port = custom_port  # usado por run_container
        try:
            run_container(service)
        except Exception as e:
            return DRF_Response({"error": str(e)}, status=500)

        row_html = render_to_string(
            "containers/_service_rows.html",
            {"services": [service]},
            request=request,
        )
        return DRF_Response(row_html, status=201)

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        run_container(self.get_object())
        return DRF_Response({"status": "started", "message": "Servicio iniciado."})

    @action(detail=True, methods=["post"])
    def stop(self, request, pk=None):
        stop_container(self.get_object())
        return DRF_Response({"status": "stopped", "message": "Servicio detenido."})

    @action(detail=True, methods=["post"], url_path="remove")
    def remove(self, request, pk=None):
        remove_container(self.get_object())
        return DRF_Response({"status": "removed", "message": "Servicio eliminado."})

    @action(detail=True, methods=["get"])
    def logs(self, request, pk=None):
        service = self.get_object()
        if service.container_id:
            try:
                container = client.containers.get(service.container_id)
                service.logs = container.logs(tail=100).decode(errors="replace")
                service.save()
            except Exception as e:
                service.logs = f"(error leyendo logs: {str(e)})"
                service.save()
        return HttpResponse(service.logs or "(sin logs)")

    # ---- ver Dockerfile/compose subidos ----
    CODE_MAX = 256 * 1024

    def _serve_code(self, filefield, language):
        if not filefield:
            raise Http404
        if filefield.size > self.CODE_MAX:
            return HttpResponse("(archivo demasiado grande)", status=413)
        with filefield.open("rb"):
            code = filefield.read().decode(errors="replace")
        html = f'<code class="language-{language}">{escape(code)}</code>'
        return HttpResponse(html)

    @action(detail=True, methods=["get"])
    def dockerfile(self, request, pk=None):
        return self._serve_code(self.get_object().dockerfile, "dockerfile")

    @action(detail=True, methods=["get"])
    def compose(self, request, pk=None):
        return self._serve_code(self.get_object().compose, "yaml")


class AllowedImageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AllowedImage.objects.all()
    serializer_class = AllowedImageSerializer
    permission_classes = [IsAuthenticated]


# ------------------------------ HTML -------------------------------

@login_required
def student_panel(request):
    """Listado genérico de servicios del alumno (todas sus asignaturas)."""
    services = Service.objects.filter(owner=request.user).exclude(status="removed")
    images = AllowedImage.objects.all()
    return render(
        request,
        "containers/student_panel.html",
        {"services": services, "images": images, "current_subject": None},
    )


@login_required
def student_subjects(request):
    """
    - Teacher/Profesor: asignaturas donde es profesor (Sport.teacher_user = user)
    - Student: asignaturas donde está matriculado (Sport.students contiene user)
    """
    if in_group(request.user, "teacher", "profesor"):
        subjects = Sport.objects.filter(teacher_user=request.user)
    else:
        subjects = Sport.objects.filter(students=request.user).distinct()
    return render(request, "containers/subjects.html", {"subjects": subjects})


@login_required
def student_services_in_subject(request, subject_id):
    subject = get_object_or_404(Sport, pk=subject_id)

    # Si es profesor y entra aquí, lo mandamos a su dashboard
    if in_group(request.user, "teacher", "profesor"):
        return redirect("professor_dashboard")

    # Solo alumnos matriculados pueden entrar
    if not subject.students.filter(pk=request.user.pk).exists():
        return HttpResponse("No estás matriculado en esta asignatura.", status=403)

    # Mostrar SOLO servicios del alumno para esa asignatura
    services = (
        Service.objects
        .filter(owner=request.user, subject=subject)
        .exclude(status="removed")
    )
    images = AllowedImage.objects.all()
    return render(
        request,
        "containers/student_panel.html",
        {"services": services, "images": images, "current_subject": subject},
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def service_table(request):
    qs = Service.objects.filter(owner=request.user).exclude(status="removed")
    subject_id = request.GET.get("subject")

    # Si el modelo tiene FK a subject, filtramos; si no, lo ignoramos (evita FieldError)
    try:
        if subject_id:
            qs = qs.filter(subject_id=subject_id)
    except FieldError:
        pass

    for s in qs:
        _sync_service(s)

    html = render_to_string("containers/_service_rows.html", {"services": qs})
    return HttpResponse(html)


@login_required
def terminal_view(request, pk):
    """
    Muestra la terminal web para el servicio si el usuario es el propietario
    y el contenedor está en ejecución (container_id presente).
    """
    service = get_object_or_404(Service, pk=pk, owner=request.user)
    if not service.container_id:
        return HttpResponse("El servicio no está en ejecución o no tiene container_id.", status=400)
    return render(request, "containers/terminal.html", {"service": service})


@login_required
def post_login(request):
    """
    Redirección post-login según rol:
    - superusuario -> /admin/
    - 'teacher'/'profesor' -> dashboard de profesor
    - resto (alumno) -> 'Mis asignaturas'
    """
    u = request.user
    if u.is_superuser:
        return redirect("/admin/")
    if in_group(u, "teacher", "profesor"):
        return redirect("professor_dashboard")
    # La vista está dentro del app 'containers' (namespaced)
    return redirect("containers:student_subjects")


@login_required
def professor_dashboard(request):
    """
    Dashboard de profesor: solo para usuarios del grupo Teacher/Profesor.
    Muestra sus asignaturas y proyectos asociados.
    """
    if not in_group(request.user, "teacher", "profesor"):
        return HttpResponse("No tienes permiso para acceder a esta página.", status=403)

    from paasify.models.ProjectModel import Game
    subjects = Sport.objects.filter(teacher_user=request.user)
    projects = Game.objects.filter(sport__teacher_user=request.user).select_related("sport", "student")

    return render(
        request,
        "professor/dashboard.html",
        {"subjects": subjects, "projects": projects},
    )


# Editar servicio (env/volúmenes) y reiniciar
@login_required
def edit_service(request, pk):
    service = get_object_or_404(Service, pk=pk, owner=request.user)

    if request.method == "POST":
        env_vars_raw = request.POST.get("env_vars") or "{}"
        volumes_raw = request.POST.get("volumes") or "{}"

        try:
            service.env_vars = ast.literal_eval(env_vars_raw)
            service.volumes = ast.literal_eval(volumes_raw)
            service.save()
        except Exception as e:
            return HttpResponse(f"Error al guardar: {e}", status=400)

        try:
            remove_container(service)
            run_container(service)
        except Exception as e:
            return HttpResponse(f"Error al reiniciar: {e}", status=500)

        return redirect("containers:student_panel")

    return render(request, "containers/edit_service.html", {"service": service})


@login_required
def subjects_list(request):
    """Alias: mis asignaturas (igual que student_subjects)."""
    if in_group(request.user, "teacher", "profesor"):
        subjects = Sport.objects.filter(teacher_user=request.user)
    else:
        subjects = Sport.objects.filter(students=request.user)
    return render(request, "containers/subjects.html", {"subjects": subjects})