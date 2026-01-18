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
from rest_framework.exceptions import ValidationError

from docker.errors import DockerException, NotFound

from paasify.models.ProjectModel import UserProject
from paasify.models.SubjectModel import Subject
from paasify.roles import (
    user_is_admin as roles_user_is_admin,
    user_is_student as roles_user_is_student,
    user_is_teacher as roles_user_is_teacher,
)

from .docker_client import get_docker_client
from .models import AllowedImage, Service, ServiceContainer
from .serializers import AllowedImageSerializer, ServiceSerializer
from .services import (
    remove_container, 
    run_container, 
    stop_container,
    start_service_container_record,
    stop_service_container_record,
    fetch_container_logs,
)


# ----------------------------- helpers -----------------------------

def _sync_service(service: Service):
    """
    Sincroniza el estado del servicio con Docker.
    
    Mejorado para manejar estados transitorios correctamente:
    - No marca error si el servicio está en "stopping", "pending", "deleting"
    - Solo marca error si el contenedor está definitivamente muerto (exited, dead)
    """
    if not service.container_id:
        return

    docker_client = get_docker_client()
    if docker_client is None:
        return

    try:
        container = docker_client.containers.get(service.container_id)
        container.reload()
        docker_status = (container.status or "").lower()
        
        # Estados transitorios: no hacer nada, dejar que el proceso termine
        if service.status in {"stopping", "pending", "deleting"}:
            return
        
        # Si el servicio está stopped/error y el contenedor NO está running, sincronizar a stopped
        # Esto evita marcar como error al reiniciar PaaSify con contenedores detenidos
        # Docker puede reportar: exited, stopped, created, paused, dead
        if service.status in {"stopped", "error"} and docker_status in {"exited", "stopped"}:
            if service.status == "error":
                # Recuperar de error si solo está detenido
                service.status = "stopped"
                service.save(update_fields=["status"])
            return  # Todo OK
        
        # Si el servicio cree que está running pero Docker dice que no
        if service.status == "running" and docker_status not in {"running"}:
            # Solo marcar error si está definitivamente muerto
            if docker_status in {"exited", "dead"}:
                try:
                    log_tail = container.logs(tail=200).decode(errors="replace")
                except Exception:
                    log_tail = "(logs no disponibles)"
                service.status = "error"
                service.logs = (service.logs or "") + f"\n[Docker] Contenedor en estado '{docker_status}'. Logs:\n{log_tail}".strip()
                service.save(update_fields=["status", "logs"])
            # Si está en otro estado (created, restarting), dar tiempo
            elif docker_status in {"created", "restarting"}:
                pass  # Esperar, puede estar arrancando
            else:
                # Estado desconocido, asumir stopped
                service.status = "stopped"
                service.save(update_fields=["status"])
        
        # Si el servicio cree que está stopped pero Docker dice running
        elif service.status == "stopped" and docker_status == "running":
            service.status = "running"
            service.save(update_fields=["status"])
            
    except NotFound:
        # Solo marcar como removed si no está en proceso de eliminación
        if service.status != "deleting":
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
    CODE_MAX = 1024 * 1024  # 1 MB max para mostrar código
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]

    def _is_htmx(self, request) -> bool:
        return request.headers.get("HX-Request") == "true"

    def _render_table_fragment(self, request) -> str:
        services = self.get_queryset()
        host = request.get_host().split(":")[0]
        return render_to_string(
            "containers/_service_rows.html",
            {"services": services, "host": host},
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
        data = request.data.copy()
        serializer = self.get_serializer(data=data, context={"request": request})
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as exc:
            if self._is_htmx(request):
                return self._validation_error_response(exc)
            raise

        mode = (request.data.get("mode") or "default").lower()
        if mode not in ("default", "custom"):
            mode = "default"

        custom_port = request.data.get("custom_port")
        if custom_port:
            try:
                custom_port = int(custom_port)
            except ValueError:
                return DRF_Response({"error": "Puerto invalido."}, status=400)

        project_id = request.data.get("project")
        project = None
        if project_id:
            project = get_object_or_404(UserProject, pk=project_id, user_profile__user=request.user)

        service = serializer.save(owner=request.user, status="creating", project=project)

        self._attach_uploaded_files(service, request, mode)

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

    def _validation_error_response(self, exc: ValidationError):
        """Devuelve un fragmento HTML con errores de validación para HTMX."""
        
        # Construir mensaje de error simple
        if isinstance(exc.detail, dict):
            errors = []
            for field, messages in exc.detail.items():
                text = ", ".join(messages) if isinstance(messages, (list, tuple)) else str(messages)
                errors.append(f"{field}: {text}")
            error_message = "\\n".join(errors)
        else:
            error_message = str(exc.detail)
        
        # Usar HX-Trigger para disparar evento que muestre alert
        response = DRF_Response("", status=400)
        response["HX-Trigger"] = json.dumps({
            "showValidationError": error_message
        })
        return response

    def _attach_uploaded_files(self, service: Service, request, mode: str):
        if mode == "default":
            return
        updated_fields = []
        for field in ("dockerfile", "compose", "code"):
            uploaded = request.FILES.get(field)
            if uploaded:
                filename = uploaded.name or f"{field}_{service.pk}"
                getattr(service, field).save(filename, uploaded, save=False)
                updated_fields.append(field)
        if updated_fields:
            service.save(update_fields=updated_fields)

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
        service.status = "deleting"
        service.save(update_fields=["status", "updated_at"])
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
        """
        Obtiene logs del servicio o de un contenedor específico.
        
        MODO SIMPLE: Muestra logs de service.container_id (comportamiento anterior)
        MODO COMPOSE: Si se pasa ?container=<id>, muestra logs de ese contenedor
        """
        service = self.get_object()
        container_id_param = request.query_params.get("container")
        
        # Determinar de dónde obtener los logs
        if container_id_param:
            # Modo compose: logs de contenedor específico
            try:
                container_record = ServiceContainer.objects.get(pk=container_id_param, service=service)
                log_content = fetch_container_logs(container_record)
                title = f"Logs de {service.name} - {container_record.name}"
            except ServiceContainer.DoesNotExist:
                log_content = "(contenedor no encontrado)"
                title = f"Logs de {service.name}"
        else:
            # Modo simple: logs del servicio (comportamiento anterior)
            log_content = service.logs or "(sin logs)"
            if service.container_id:
                docker_client = get_docker_client()
                if docker_client:
                    try:
                        container = docker_client.containers.get(service.container_id)
                        log_content = container.logs(tail=200).decode(errors="replace")
                    except Exception as e:
                        log_content = f"(error leyendo logs: {e})"
            title = f"Logs de {service.name}"
        
        if self._is_htmx(request):
            html = f"""
                <div class="modal-header">
                    <h5 class="modal-title">{title}</h5>
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

    def _serve_code(self, service, filename, language):
        """
        Lee y muestra el contenido de un archivo del workspace del servicio.
        Busca en media/services/<id>/<filename>
        """
        from pathlib import Path
        from django.conf import settings
        
        # Construir la ruta esperada
        workspace = Path(settings.MEDIA_ROOT) / "services" / str(service.pk)
        file_path = workspace / filename
        
        if not file_path.exists():
            return HttpResponse(f"(archivo {filename} no disponible)", status=404)
        
        if file_path.stat().st_size > self.CODE_MAX:
            return HttpResponse("(archivo demasiado grande)", status=413)
        
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                code = f.read()
        except Exception as e:
            return HttpResponse(f"(error leyendo archivo: {e})", status=500)
        
        html = f'<code class="language-{language}">{escape(code)}</code>'
        return HttpResponse(html)

    @action(detail=True, methods=["get"])
    def dockerfile(self, request, pk=None):
        service = self.get_object()
        return self._serve_code(service, "Dockerfile", "dockerfile")

    @action(detail=True, methods=["get"])
    def compose(self, request, pk=None):
        service = self.get_object()
        return self._serve_code(service, "docker-compose.yml", "yaml")

    # ---- Endpoints para ServiceContainer (docker-compose multi-contenedor) ----
    
    def _get_service_container(self, service: Service, container_pk: str) -> ServiceContainer:
        """Helper para obtener un ServiceContainer validando permisos"""
        try:
            return ServiceContainer.objects.get(pk=container_pk, service=service)
        except ServiceContainer.DoesNotExist:
            raise Http404("Contenedor no encontrado")
    
    @action(detail=True, methods=["post"], url_path="containers/(?P<container_pk>\\d+)/start")
    def start_container(self, request, pk=None, container_pk=None):
        """Inicia un contenedor específico de un servicio compose"""
        service = self.get_object()
        container = self._get_service_container(service, container_pk)
        
        try:
            start_service_container_record(container)
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
                message=f"Contenedor {container.name} iniciado.",
                level="text-bg-success",
            )
        return DRF_Response({"status": "started", "message": f"Contenedor {container.name} iniciado."})
    
    @action(detail=True, methods=["post"], url_path="containers/(?P<container_pk>\\d+)/stop")
    def stop_container_action(self, request, pk=None, container_pk=None):
        """Detiene un contenedor específico de un servicio compose"""
        service = self.get_object()
        container = self._get_service_container(service, container_pk)
        
        try:
            stop_service_container_record(container)
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
                message=f"Contenedor {container.name} detenido.",
                level="text-bg-warning",
            )
        return DRF_Response({"status": "stopped", "message": f"Contenedor {container.name} detenido."})



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
    user_projects = UserProject.objects.filter(user_profile__user=request.user)
    host = request.get_host().split(":")[0]

    running_count = services.filter(status="running").count()
    stopped_count = services.filter(status="stopped").count()
    error_count = services.filter(status="error").count()
    total_services = services.count()
    subjects_count = available_subjects.count() if hasattr(available_subjects, "count") else 0

    return render(
        request,
        "containers/student_panel.html",
        {
            "services": services,
            "images": images,
            "user_projects": user_projects,
            "current_subject": None,
            "available_subjects": available_subjects,
            "host": host,
            "title": "PaaSify - Mis servicios",
            "stats": {
                "total": total_services,
                "running": running_count,
                "stopped": stopped_count,
                "error": error_count,
                "subjects": subjects_count,
                "projects": user_projects.count(),
            },
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
    
    # Calcular estadísticas locales para esta asignatura
    running_count = services.filter(status="running").count()
    stopped_count = services.filter(status="stopped").count()
    error_count = services.filter(status="error").count()
    total_services = services.count()
    
    # Necesario para el selector de asignaturas en el filtro
    available_subjects = Subject.objects.filter(students=request.user).distinct()
    user_projects = UserProject.objects.filter(user_profile__user=request.user, subject=subject)

    images = AllowedImage.objects.all()
    host = request.get_host().split(":")[0]
    return render(
        request,
        "containers/student_panel.html",
        {
            "services": services, 
            "images": images, 
            "user_projects": user_projects,
            "current_subject": subject, 
            "host": host,
            "available_subjects": available_subjects,
            "stats": {
                "total": total_services,
                "running": running_count,
                "stopped": stopped_count,
                "error": error_count,
                "subjects": 1, # Solo 1 asignatura seleccionada
                "projects": user_projects.count(),
            },
        },
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

    host = request.get_host().split(":")[0]
    html = render_to_string("containers/_service_rows.html", {"services": qs, "host": host})
    return HttpResponse(html)


@login_required
def terminal_view(request, pk):
    """
    Muestra la terminal web para el servicio si el usuario es el propietario
    y el contenedor esta en ejecucion.
    """
    user = request.user
    if user_is_admin(user) or user_is_teacher(user):
        service = get_object_or_404(Service, pk=pk)
    else:
        service = get_object_or_404(Service, pk=pk, owner=user)

    if service.status != "running" or not service.container_id:
        return HttpResponse("El servicio no esta en ejecucion.", status=400)
    docker_client = get_docker_client()
    if docker_client is None:
        return HttpResponse("Docker no esta disponible actualmente.", status=400)
    try:
        container = docker_client.containers.get(service.container_id)
        container.reload()
        if (container.status or "").lower() != "running":
            return HttpResponse("El contenedor no esta en ejecucion.", status=400)
    except NotFound:
        return HttpResponse("El contenedor no existe.", status=404)
    except DockerException as exc:
        return HttpResponse(f"No se pudo acceder al contenedor: {exc}", status=400)

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
            # SEGURIDAD CRÍTICA: Volúmenes deshabilitados completamente
            # volumes = _parse_optional_json(request.POST.get("volumes", ""), "Volumenes")
        except ValueError as exc:
            return HttpResponse(str(exc), status=400)

        service.env_vars = env_vars or None
        # SEGURIDAD: No permitir modificación de volúmenes
        # service.volumes = volumes or None
        service.save(update_fields=["env_vars", "updated_at"])

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


@login_required
def new_service_page(request):
    """
    Página dedicada para crear nuevo servicio.
    Proporciona mejor UX que el modal con más espacio y ayuda contextual.
    """
    # Obtener datos necesarios para el formulario
    images = AllowedImage.objects.all().order_by('name')
    subjects = Subject.objects.filter(students=request.user)
    user_projects = UserProject.objects.filter(
        user_profile__user=request.user
    ).select_related('subject')
    
    # Obtener host para preview
    host = request.get_host().split(':')[0]
    
    context = {
        'images': images,
        'available_subjects': subjects,
        'user_projects': user_projects,
        'host': host,
    }
    
    return render(request, 'containers/new_service.html', context)


@login_required
def manage_api_token(request):
    """
    Gestionar token API del usuario con caducidad de 30 días.
    Permite generar, regenerar y visualizar el Bearer Token para acceso a la API.
    """
    from paasify.models.TokenModel import ExpiringToken
    from django.contrib import messages
    
    if request.method == "POST":
        # Regenerar token (eliminar el anterior y crear uno nuevo)
        ExpiringToken.objects.filter(user=request.user).delete()
        token = ExpiringToken.objects.create(user=request.user)
        messages.success(request, 'Token regenerado exitosamente. Válido por 30 días.')
    else:
        # Obtener o crear token
        token, created = ExpiringToken.objects.get_or_create(user=request.user)
        if created:
            messages.success(request, 'Token creado exitosamente. Válido por 30 días.')
        elif token.is_expired():
            messages.warning(request, 'Tu token ha expirado. Por favor, regenera un nuevo token.')
    
    context = {
        'token': token.key,
        'created': token.created,
        'expires_at': token.expires_at,
        'days_remaining': token.days_until_expiration(),
        'is_expired': token.is_expired(),
    }
    
    return render(request, 'containers/api_token.html', context)
