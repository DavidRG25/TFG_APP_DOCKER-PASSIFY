# containers/views.py
import json

from django.contrib.auth.decorators import login_required
from django.core.exceptions import FieldError
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.html import escape

from rest_framework import viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response as DRF_Response

from docker.errors import DockerException, NotFound

from paasify.models.ProjectModel import UserProject
from paasify.models.SubjectModel import Subject
from paasify.roles import (
    user_is_admin as roles_user_is_admin,
    user_is_student as roles_user_is_student,
    user_is_teacher as roles_user_is_teacher,
)

from .docker_client import get_docker_client
from .models import AllowedImage, Service
from .serializers import AllowedImageSerializer, ServiceSerializer
from .services import SSH_USERNAME, remove_container, run_container, stop_container


# ----------------------------- helpers -----------------------------

def _sync_service(service: Service):
    """Si el container_id ya no existe en Docker, marcamos el servicio como 'removed'."""
    if not service.container_id:
        return

    docker_client = get_docker_client()
    if docker_client is None:
        return

    try:
        docker_client.containers.get(service.container_id)
    except NotFound:
        service.status = "removed"
        service.save()
    except DockerException:
        # Si no podemos verificar el contenedor, conservamos el estado actual.
        return


def user_is_student(user) -> bool:
    if not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_superuser", False):
        return True
    return roles_user_is_student(user)


def user_is_teacher(user) -> bool:
    if not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_superuser", False):
        return True
    return roles_user_is_teacher(user)


def user_is_admin(user) -> bool:
    if not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_superuser", False):
        return True
    return roles_user_is_admin(user)


# ------------------------------ API --------------------------------

class ServiceViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]

    def _is_htmx(self, request) -> bool:
        return request.headers.get("HX-Request") == "true"

    def _render_table_fragment(self, request) -> str:
        services = self.get_queryset()
        return render_to_string(
            "containers/_service_rows.html",
            {"services": services},
            request=request,
        )

    def _htmx_response(
        self,
        request,
        *,
        status=200,
        message=None,
        level="text-bg-success",
        extra_triggers=None,
    ):
        html = ""
        if not self._is_htmx(request):
            html = self._render_table_fragment(request)
        response = DRF_Response(html, status=status)
        trigger = dict(extra_triggers or {})
        trigger.setdefault("service:table-refresh", {})
        if message:
            trigger["service:toast"] = {"message": message, "variant": level}
        if trigger:
            response["HX-Trigger"] = json.dumps(trigger)
        return response

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        user = request.user
        if user.is_superuser or user_is_admin(user):
            return
        if not user_is_student(user):
            raise PermissionDenied("Solo los alumnos pueden gestionar contenedores.")

    def get_queryset(self):
        user = self.request.user
        if user_is_admin(user) or user_is_teacher(user):
            qs = Service.objects.all()
        else:
            qs = Service.objects.filter(owner=user)
        
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

        mode = (request.data.get("mode") or "default").lower()
        if mode not in ("default", "custom"):
            mode = "default"

        has_df = bool(request.FILES.get("dockerfile"))
        has_comp = bool(request.FILES.get("compose"))
        has_code = bool(request.FILES.get("code"))

        if mode == "default":
            if has_df or has_comp or has_code:
                return DRF_Response(
                    {"error": "En modo 'Imagen por defecto' no se permiten Dockerfile/Compose/Codigo."},
                    status=400,
                )
        else:
            if has_df and has_comp:
                return DRF_Response(
                    {"error": "Sube Dockerfile O docker-compose, pero no ambos."},
                    status=400,
                )
            if not (has_df or has_comp):
                return DRF_Response(
                    {"error": "En modo 'Configuracion personalizada' debes subir Dockerfile o docker-compose."},
                    status=400,
                )

        custom_port = request.data.get("custom_port")
        if custom_port:
            try:
                custom_port = int(custom_port)
            except ValueError:
                return DRF_Response({"error": "Puerto invalido."}, status=400)

        service = serializer.save(owner=request.user, status="creating")

        if has_df:
            service.dockerfile = request.FILES["dockerfile"]
        if has_comp:
            service.compose = request.FILES["compose"]
        if has_code:
            service.code = request.FILES["code"]
        service.save()

        try:
            run_container(service, custom_port=custom_port)
        except Exception as exc:
            service.status = "error"
            service.logs = str(exc)
            service.save(update_fields=["status", "logs"])
            if self._is_htmx(request):
                return self._htmx_response(
                    request,
                    status=500,
                    message=str(exc),
                    level="text-bg-danger",
                )
            return DRF_Response({"error": str(exc)}, status=500)

        if self._is_htmx(request):
            return self._htmx_response(
                request,
                status=201,
                message="Servicio encolado para iniciar.",
                level="text-bg-success",
                extra_triggers={"service:modal-close": {"modalId": "newServiceModal"}},
            )

        headers = self.get_success_headers(serializer.data)
        return DRF_Response(
            ServiceSerializer(service, context={"request": request}).data,
            status=201,
            headers=headers
        )

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        service = self.get_object()
        try:
            run_container(service)
        except Exception as exc:
            if self._is_htmx(request):
                return self._htmx_response(
                    request,
                    status=500,
                    message=str(exc),
                    level="text-bg-danger",
                )
            return DRF_Response({"status": "error", "message": str(exc)}, status=500)

        if self._is_htmx(request):
            return self._htmx_response(
                request,
                message="Servicio encolado para iniciar.",
                level="text-bg-success",
            )
        return DRF_Response({"status": "queued", "message": "Servicio encolado para iniciar."})

    @action(detail=True, methods=["post"])
    def stop(self, request, pk=None):
        service = self.get_object()
        try:
            stop_container(service)
        except Exception as exc:
            if self._is_htmx(request):
                return self._htmx_response(
                    request,
                    status=500,
                    message=str(exc),
                    level="text-bg-danger",
                )
            return DRF_Response({"status": "error", "message": str(exc)}, status=500)

        if self._is_htmx(request):
            return self._htmx_response(
                request,
                message="Servicio detenido.",
                level="text-bg-warning",
            )
        return DRF_Response({"status": "stopped", "message": "Servicio detenido."})

    @action(detail=True, methods=["post"], url_path="remove")
    def remove(self, request, pk=None):
        service = self.get_object()
        try:
            remove_container(service)
        except Exception as exc:
            if self._is_htmx(request):
                return self._htmx_response(
                    request,
                    status=500,
                    message=str(exc),
                    level="text-bg-danger",
                )
            return DRF_Response({"status": "error", "message": str(exc)}, status=500)

        if self._is_htmx(request):
            return self._htmx_response(
                request,
                message="Servicio eliminado.",
                level="text-bg-danger",
            )
        return DRF_Response({"status": "removed", "message": "Servicio eliminado."})

    @action(detail=True, methods=["get"])
    def logs(self, request, pk=None):
        service = self.get_object()
        log_content = "(sin logs)"
        if service.container_id:
            docker_client = get_docker_client()
            if docker_client:
                try:
                    container = docker_client.containers.get(service.container_id)
                    log_content = container.logs(tail=200).decode(errors="replace")
                except Exception as e:
                    log_content = f"(error leyendo logs: {e})"
        
        if self._is_htmx(request):
            html = f"""
                <div class="modal-header">
                    <h5 class="modal-title">Logs de {service.name}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cerrar"></button>
                </div>
                <div class="modal-body">
                    <pre><code class="language-plaintext">{escape(log_content)}</code></pre>
                </div>
            """
            return HttpResponse(html)
        
        return HttpResponse(log_content, content_type="text/plain")

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

    @action(detail=True, methods=["get"], url_path="ssh-uri")
    def ssh_uri(self, request, pk=None):
        service = self.get_object()
        if service.status != "running" or not service.ssh_port:
            return DRF_Response(
                {"error": "El servicio no está en ejecución o no tiene puerto SSH asignado."},
                status=400,
            )

        host = request.get_host().split(":")[0]
        uri = f"ssh {SSH_USERNAME}@{host} -p {service.ssh_port}"
        password = service.ssh_password or "No disponible"

        if self._is_htmx(request):
            safe_uri = escape(uri)
            safe_password = escape(password)
            safe_user = escape(SSH_USERNAME)
            # Si es HTMX, devolvemos un fragmento de HTML para el modal
            html = f"""
                <div class="modal-header">
                    <h5 class="modal-title">Conexión SSH</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cerrar"></button>
                </div>
                <div class="modal-body">
                    <p>Copia y pega el siguiente comando en tu terminal:</p>
                    <div class="input-group">
                        <input type="text" id="sshCommand" class="form-control" value="{safe_uri}" readonly>
                        <button class="btn btn-outline-secondary" onclick="copyToClipboard('#sshCommand')">Copiar</button>
                    </div>
                    <p class="mt-3 mb-1">Contraseña:</p>
                    <div class="input-group">
                        <input type="text" id="sshPassword" class="form-control" value="{safe_password}" readonly>
                        <button class="btn btn-outline-secondary" onclick="copyToClipboard('#sshPassword')">Copiar</button>
                    </div>
                    <small class="text-muted d-block mt-2">Usuario: {safe_user}</small>
                </div>
            """
            return HttpResponse(html)

        return DRF_Response({"ssh_uri": uri, "password": password, "user": SSH_USERNAME})


class AllowedImageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AllowedImage.objects.all()
    serializer_class = AllowedImageSerializer
    permission_classes = [IsAuthenticated]


# ------------------------------ HTML -------------------------------

@login_required
def student_panel(request):
    """Listado genérico de servicios del alumno (todas sus asignaturas)."""
    if request.user.is_superuser:
        available_subjects = Subject.objects.all()
    elif user_is_teacher(request.user):
        return redirect("professor_dashboard")
    elif not user_is_student(request.user):
        return HttpResponse("No tienes permiso para acceder al panel de contenedores.", status=403)
    else:
        available_subjects = Subject.objects.filter(students=request.user).distinct()

    services = Service.objects.filter(owner=request.user).exclude(status="removed")
    images = AllowedImage.objects.all()
    return render(
        request,
        "containers/student_panel.html",
        {
            "services": services,
            "images": images,
            "current_subject": None,
            "available_subjects": available_subjects,
            "title": "PaaSify - Mis servicios",
        },
    )



@login_required
def student_subjects(request):
    """
    - Teacher/Profesor: asignaturas donde es profesor (Subject.teacher_user = user)
    - Student: asignaturas donde estÃƒÂ¡ matriculado (Subject.students contiene user)
    """
    if request.user.is_superuser:
        subjects = Subject.objects.all()
    elif user_is_teacher(request.user):
        return redirect("professor_dashboard")
    else:
        subjects = Subject.objects.filter(students=request.user).distinct()
    return render(request, "containers/subjects.html", {"subjects": subjects, "title": "PaaSify - Asignaturas"})


@login_required
def student_services_in_subject(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)

    # Si es profesor y entra aqui, lo mandamos a su dashboard salvo que sea superusuario
    if user_is_teacher(request.user) and not request.user.is_superuser:
        return redirect("professor_dashboard")

    # Solo alumnos matriculados pueden entrar (salvo administradores)
    if not (user_is_admin(request.user) or subject.students.filter(pk=request.user.pk).exists()):
        return HttpResponse("No estas matriculado en esta asignatura.", status=403)

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
    if not (request.user.is_superuser or user_is_student(request.user)):
        return HttpResponse("No tienes permiso para consultar servicios.", status=403)

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
    y el contenedor está en ejecución.
    """
    user = request.user
    if user_is_admin(user) or user_is_teacher(user):
        service = get_object_or_404(Service, pk=pk)
    else:
        service = get_object_or_404(Service, pk=pk, owner=user)

    if service.status != "running" or not service.container_id:
        return HttpResponse("El servicio no está en ejecución.", status=400)
    
    # El endpoint del WebSocket se construye dinámicamente
    ws_path = f"/ws/terminal/{service.id}/"
    return render(request, "containers/terminal.html", {
        "service": service,
        "ws_path": ws_path,
    })


@login_required
def post_login(request):
    """
    RedirecciÃƒÂ³n post-login segÃƒÂºn rol:
    - superusuario -> /admin/
    - 'teacher'/'profesor' -> dashboard de profesor
    - resto (alumno) -> 'Mis asignaturas'
    """
    u = request.user
    if u.is_superuser:
        return redirect("/admin/")
    if user_is_teacher(u):
        return redirect("professor_dashboard")
    # La vista estÃƒÂ¡ dentro del app 'containers' (namespaced)
    return redirect("containers:student_subjects")


@login_required
def professor_dashboard(request):
    """
    Dashboard de profesor: solo para usuarios del grupo Teacher/Profesor.
    Muestra sus asignaturas y proyectos asociados.
    """
    if not (user_is_teacher(request.user) or request.user.is_superuser):
        return HttpResponse("No tienes permiso para acceder a esta pÃƒÂ¡gina.", status=403)

    subjects = Subject.objects.filter(teacher_user=request.user)
    if request.user.is_superuser:
        subjects = Subject.objects.all()

    projects = (
        UserProject.objects.filter(subject__teacher_user=request.user)
        if not request.user.is_superuser
        else UserProject.objects.all()
    ).select_related("subject", "user_profile")

    return render(
        request,
        "professor/dashboard.html",
        {"subjects": subjects, "projects": projects},
    )


@login_required
def professor_subject_detail(request, subject_id):
    if not (user_is_teacher(request.user) or user_is_admin(request.user)):
        return HttpResponse("No tienes permiso para acceder a esta pagina.", status=403)

    base_qs = Subject.objects.all() if request.user.is_superuser else Subject.objects.filter(teacher_user=request.user)
    subject = get_object_or_404(base_qs.select_related("teacher_user"), pk=subject_id)

    students = subject.students.all().order_by("username")
    services = (
        Service.objects.filter(subject=subject)
        .select_related("owner")
        .exclude(status="removed")
        .order_by("owner__username", "name")
    )
    projects = subject.projects.select_related("user_profile")

    return render(
        request,
        "professor/subject_detail.html",
        {"subject": subject, "students": students, "services": services, "projects": projects},
    )


@login_required
def professor_project_detail(request, project_id):
    if not (user_is_teacher(request.user) or user_is_admin(request.user)):
        return HttpResponse("No tienes permiso para acceder a esta pagina.", status=403)

    base_qs = UserProject.objects.select_related("subject", "user_profile")
    if not request.user.is_superuser:
        base_qs = base_qs.filter(subject__teacher_user=request.user)

    project = get_object_or_404(base_qs, pk=project_id)

    student_user = getattr(project.user_profile, "user", None)
    related_services = Service.objects.none()
    if student_user is not None:
        related_services = (
            Service.objects.filter(owner=student_user)
            .exclude(status="removed")
            .select_related("owner", "subject")
        )

    return render(
        request,
        "professor/project_detail.html",
        {"project": project, "related_services": related_services},
    )


# Editar servicio (env/volumenes) y reiniciar
@login_required
def edit_service(request, pk):
    service = get_object_or_404(Service, pk=pk, owner=request.user)

    if request.method == "POST":
        def _parse_optional_json(raw_value: str, field_label: str):
            if not raw_value:
                return {}
            try:
                data = json.loads(raw_value)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{field_label}: JSON invalido ({exc.msg}).") from exc
            if not isinstance(data, dict):
                raise ValueError(f"{field_label}: debe ser un objeto JSON.")
            return data

        try:
            env_vars = _parse_optional_json(request.POST.get("env_vars", ""), "Variables de entorno")
            volumes = _parse_optional_json(request.POST.get("volumes", ""), "Volumenes")
        except ValueError as exc:
            return HttpResponse(str(exc), status=400)

        service.env_vars = env_vars or None
        service.volumes = volumes or None
        service.save(update_fields=["env_vars", "volumes", "updated_at"])

        try:
            remove_container(service)
            run_container(service)
        except Exception as exc:
            return HttpResponse(f"Error al reiniciar: {exc}", status=500)

        return redirect("containers:student_panel")

    return render(request, "containers/edit_service.html", {"service": service})


@login_required
def subjects_list(request):
    if user_is_teacher(request.user):
        subjects = Subject.objects.filter(teacher_user=request.user)
    else:
        subjects = Subject.objects.filter(students=request.user)
    return render(request, "containers/subjects.html", {"subjects": subjects})
