# test comment

# containers/views.py
import json
from django.db import models
from django.conf import settings

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.exceptions import FieldError
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.html import escape

from rest_framework import viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import PermissionDenied, NotFound as DRFNotFound
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
from .compose_parser import DockerComposeParser
from .services import (
    remove_container, 
    run_container, 
    stop_container,
    start_service_container_record,
    stop_service_container_record,
    fetch_container_logs,
    sync_service_status
)

@login_required
@require_POST
def analyze_compose(request):
    """
    Analiza un archivo docker-compose.yml y retorna información estructurada.
    """
    if 'compose_file' not in request.FILES:
        return JsonResponse({'success': False, 'error': 'No se proporcionó archivo'}, status=400)

    compose_file = request.FILES['compose_file']
    try:
        content = compose_file.read().decode('utf-8')
    except Exception:
        return JsonResponse({'success': False, 'error': 'Archivo no válido'}, status=400)

    parser = DockerComposeParser(content)
    result = parser.parse()
    return JsonResponse(result)


# ----------------------------- helpers -----------------------------

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

    def get_serializer_class(self):
        if self.action == "list":
            from .serializers import ServiceSimpleSerializer
            return ServiceSimpleSerializer
        return ServiceSerializer

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise DRFNotFound("No se encontró ningún servicio con esa consulta o no tienes permisos.")

    def _is_htmx(self, request) -> bool:
        # Algunos navegadores o proxys pueden variar la capitalización, comprobamos de forma más robusta
        hx = request.headers.get("HX-Request", "").lower()
        return hx == "true"

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
        # Si no es HTMX (raro pero posible), devolvemos el fragmento de la tabla
        if not self._is_htmx(request):
            html = self._render_table_fragment(request)
        response = DRF_Response(html, status=status)
        
        # Siempre incluimos el refresh de la tabla para asegurar que el pooling se active/actualice
        trigger = dict(extra_triggers or {})
        trigger["service:table-refresh"] = {}
        
        if message:
            trigger["service:toast"] = {"message": message, "variant": level}
            
        # Siempre enviar como JSON para que HTMX lo procese consistentemente
        response["HX-Trigger"] = json.dumps(trigger)
            
        return response

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        user = request.user
        if user.is_superuser or user_is_admin(user) or user_is_teacher(user):
            return
        if not user_is_student(user):
            raise PermissionDenied("Solo los alumnos pueden gestionar contenedores.")

    def get_queryset(self):
        user = self.request.user
        if user_is_admin(user) or user_is_teacher(user):
            qs = Service.objects.all()
        else:
            qs = Service.objects.filter(owner=user)
        
        # Filtros adicionales por API (GET params)
        project_id = self.request.query_params.get('project')
        if project_id:
            if not project_id.isdigit():
                raise ValidationError({"project": "El ID del proyecto debe ser un numero entero."})
            qs = qs.filter(project_id=project_id)
            
        subject_id = self.request.query_params.get('subject')
        if subject_id:
            if not subject_id.isdigit():
                raise ValidationError({"subject": "El ID de la asignatura debe ser un numero entero."})
            qs = qs.filter(subject_id=subject_id)
            
        status = self.request.query_params.get('status')
        if status:
            qs = qs.filter(status=status)

        for s in qs:
            sync_service_status(s)
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
        if mode not in ("default", "custom", "dockerhub"):
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

        # Capturar configuraciones personalizadas de contenedores (para compose)
        container_configs = request.data.get("container_configs")
        if isinstance(container_configs, str):
            try:
                container_configs = json.loads(container_configs)
            except:
                container_configs = None

        service = serializer.save(owner=request.user, status="creating", project=project)

        try:
            run_container(service, custom_port=custom_port, container_configs=container_configs)
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

    def perform_update(self, serializer):
        service = self.get_object()
        if service.mode == 'default':
            raise PermissionDenied("Los servicios del catálogo oficial no se pueden editar.")
        
        # Guardar cambios
        updated_service = serializer.save()
        
        # Procesar archivos si vienen por multipart
        self._attach_uploaded_files(updated_service, self.request, updated_service.mode)
        
        # Reiniciar contenedor
        try:
            remove_container(updated_service)
            run_container(updated_service)
        except Exception as exc:
            # En API reportamos el error pero permitimos que el objeto se guarde
            updated_service.status = "error"
            updated_service.logs = f"Error al actualizar: {exc}"
            updated_service.save()
            raise ValidationError(f"Error al reiniciar contenedor: {exc}")

    def _validation_error_response(self, exc: ValidationError):
        """Devuelve un fragmento HTML con errores de validación para HTMX."""
        
        # Construir mensaje de error simple y legible
        if isinstance(exc.detail, dict):
            errors = []
            for field, messages in exc.detail.items():
                # Extraer el mensaje limpio
                if isinstance(messages, (list, tuple)):
                    msg_text = ", ".join(str(m) for m in messages)
                elif isinstance(messages, str):
                    msg_text = messages
                else:
                    msg_text = str(messages)
                
                # Formatear el campo de forma legible
                field_name = field.replace("_", " ").title()
                errors.append(f"<strong>{field_name}:</strong> {msg_text}")
            error_message = "<br>".join(errors)
        else:
            error_message = str(exc.detail)
        
        # Usar HX-Trigger para disparar evento que muestre el error
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
                message=f"Servicio '{service.name}' iniciado correctamente.",
                level="text-bg-success"
            )
        return DRF_Response({"status": "queued", "message": "Servicio encolado para iniciar."})

    @action(detail=True, methods=["post"])
    def stop(self, request, pk=None):
        service = self.get_object()
        
        try:
            from .services import stop_container_async
            stop_container_async(service)
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
                message=f"Servicio '{service.name}' deteniendo...",
                level="text-bg-warning"
            )
        return DRF_Response({"status": "stopping", "message": "Servicio deteniendo."})

    @action(detail=True, methods=["post"], url_path="remove")
    def remove(self, request, pk=None):
        service = self.get_object()
        
        try:
            from .services import remove_container_async
            remove_container_async(service)
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
                message="El servicio está siendo eliminado...",
                level="text-bg-success",
            )
        return DRF_Response({"status": "deleting", "message": "Servicio eliminando."})

    @action(detail=True, methods=["get"])
    def logs(self, request, pk=None):
        """
        Obtiene logs del servicio o de un contenedor específico.
        
        MODO SIMPLE: Muestra logs de service.container_id (comportamiento anterior)
        MODO COMPOSE: Si se pasa ?container=<id>, muestra logs de ese contenedor
        """
        service = self.get_object()
        container_id_param = request.query_params.get("container")
        tail_param = request.query_params.get("tail", "200")
        since_param = request.query_params.get("since")
        
        # Validar tail
        try:
            tail_val = int(tail_param) if tail_param != 'all' else 'all'
        except:
            tail_val = 200

        # Determinar de dónde obtener los logs usando la utilidad unificada
        container_name = None
        if container_id_param:
            try:
                container_record = ServiceContainer.objects.get(pk=container_id_param, service=service)
                container_name = container_record.name
            except ServiceContainer.DoesNotExist:
                pass
        
        # Obtener logs (la utilidad ya maneja tail, since y la conversión horaria)
        logs_lines, _ = fetch_container_logs(
            service, 
            tail=tail_val, 
            since=since_param, 
            container_name=container_name
        )
        log_content = "\n".join(logs_lines) if logs_lines else "(sin logs en este periodo)"
        title = f"Logs de {service.name}" + (f" - {container_name}" if container_name else "")
        
        if self._is_htmx(request):
            # Determinamos si hace falta polling (si está operando o si está corriendo para ver logs frescos)
            is_transient = service.status in ["pending", "starting", "building", "pulling", "deleting", "creating", "stopping"]
            polling_attr = ""
            if is_transient or service.status == "running":
                # Si pasamos container_id, mantenerlo en el polling
                poll_url = request.path
                if container_id_param:
                    poll_url += f"?container={container_id_param}"
                polling_attr = f'hx-get="{poll_url}" hx-trigger="load delay:2s" hx-target="#genericModalContent" hx-swap="innerHTML"'

            html = f"""
                <div class="modal-header">
                    <h5 class="modal-title">{title}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cerrar"></button>
                </div>
                <div class="modal-body" {polling_attr}>
                    <pre class="bg-dark text-light p-3 rounded shadow-sm" style="max-height: 400px; overflow-y: auto;">
                        <code class="language-plaintext">{escape(log_content)}</code>
                    </pre>
                    {f'<div class="text-center mt-2"><div class="spinner-border spinner-border-sm text-primary" role="status"></div><small class="ms-2 text-muted">Actualizando logs...</small></div>' if polling_attr else ""}
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


class SubjectViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Lista las asignaturas en las que el alumno está matriculado.
    """
    serializer_class = None  # Se define dinámicamente o importando
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_serializer_class(self):
        from .api_serializers import SubjectSerializer
        return SubjectSerializer

    def get_queryset(self):
        user = self.request.user
        if user_is_admin(user) or user.is_superuser:
            return Subject.objects.all()
        # Si es profesor, sus asignaturas
        if user_is_teacher(user):
            return Subject.objects.filter(teacher_user=user)
        # Si es alumno, donde está matriculado
        return Subject.objects.filter(students=user).distinct()


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Lista los proyectos asignados al alumno.
    """
    serializer_class = None
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_serializer_class(self):
        from .api_serializers import ProjectSerializer
        return ProjectSerializer

    def get_queryset(self):
        user = self.request.user
        if user_is_admin(user) or user.is_superuser:
            qs = UserProject.objects.all()
        # Si es profesor, proyectos de sus asignaturas
        elif user_is_teacher(user):
            qs = UserProject.objects.filter(subject__teacher_user=user)
        # Si es alumno, sus proyectos personales
        else:
            qs = UserProject.objects.filter(user_profile__user=user)
            
        # Filtro opcional por asignatura
        subject_id = self.request.query_params.get('subject')
        if subject_id:
            qs = qs.filter(subject_id=subject_id)
            
        return qs



@login_required
def verify_dockerhub_image(request):
    """
    Verifica si una imagen existe en DockerHub y extrae información útil.
    Soluciona el problema de CORS al hacer la petición desde el backend.
    """
    import requests
    from django.http import JsonResponse
    
    image_name = request.GET.get('image', '').strip()
    
    if not image_name:
        return JsonResponse({
            'success': False,
            'error': 'No se especificó ninguna imagen'
        }, status=400)
    
    try:
        # Parsear nombre de imagen (usuario/imagen:tag o imagen:tag)
        parts = image_name.split(':')
        repo = parts[0]
        tag = parts[1] if len(parts) > 1 else 'latest'
        
        # Construir URL de la API de DockerHub
        if '/' in repo:
            # Imagen de usuario: usuario/imagen
            url = f'https://hub.docker.com/v2/repositories/{repo}/tags/{tag}'
        else:
            # Imagen oficial: library/imagen
            url = f'https://hub.docker.com/v2/repositories/library/{repo}/tags/{tag}'
        
        # Hacer petición a DockerHub
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extraer puerto expuesto si existe
            exposed_port = None
            try:
                # Los puertos están en images[0].architecture (normalmente)
                if 'images' in data and len(data['images']) > 0:
                    # Buscar en la metadata de la imagen
                    for img_data in data['images']:
                        # DockerHub no siempre expone esta info en la API pública
                        # Intentamos extraerla si está disponible
                        pass
                
                # Puertos comunes por nombre de imagen (fallback)
                common_ports = {
                    'nginx': 80,
                    'apache': 80,
                    'httpd': 80,
                    'postgres': 5432,
                    'postgresql': 5432,
                    'mysql': 3306,
                    'mariadb': 3306,
                    'redis': 6379,
                    'mongodb': 27017,
                    'mongo': 27017,
                    'elasticsearch': 9200,
                }
                
                # Intentar detectar por nombre
                repo_name = repo.split('/')[-1].lower()
                for key, port in common_ports.items():
                    if key in repo_name:
                        exposed_port = port
                        break
                        
            except Exception:
                pass
            
            return JsonResponse({
                'success': True,
                'image': image_name,
                'last_updated': data.get('last_updated'),
                'full_size': data.get('full_size'),
                'exposed_port': exposed_port,
                'repo': repo,
                'tag': tag,
            })
            
        elif response.status_code == 404:
            return JsonResponse({
                'success': False,
                'error': 'Imagen no encontrada en DockerHub. Verifica el nombre y el tag.'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'Error al consultar DockerHub (código {response.status_code})'
            })
            
    except requests.exceptions.Timeout:
        return JsonResponse({
            'success': False,
            'error': 'Timeout al consultar DockerHub. Intenta de nuevo.'
        })
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            'success': False,
            'error': f'Error de conexión: {str(e)}'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error inesperado: {str(e)}'
        })


@login_required
def check_port_availability(request):
    """
    Verifica si un puerto está disponible y sugiere alternativas si está ocupado.
    """
    import random
    from .models import Service
    
    port = request.GET.get('port', '').strip()
    
    if not port:
        return JsonResponse({
            'success': False,
            'error': 'Por favor, ingresa un puerto'
        })
    
    try:
        port = int(port)
        
        # Validar rango
        if port < 40000 or port > 50000:
            return JsonResponse({
                'success': False,
                'error': 'El puerto debe estar entre 40000 y 50000'
            })
        
        # 1. Puertos en Service (Contenedores simples y lista de puertos de compose)
        services_with_ports = Service.objects.filter(models.Q(assigned_port__isnull=False) | models.Q(assigned_ports__isnull=False))
        
        # 2. Puertos en ServiceContainer (Docker Compose - Ejecutándose)
        from .models import ServiceContainer, PortReservation
        compose_running_ports = []
        for sc in ServiceContainer.objects.filter(assigned_ports__isnull=False):
            if isinstance(sc.assigned_ports, list):
                for p_info in sc.assigned_ports:
                    ext_port = p_info.get('external')
                    if ext_port:
                        compose_running_ports.append((f"{sc.service.name} ({sc.name})", int(ext_port)))
        
        # 3. Puertos en PortReservation (Reservas activas en Docker)
        reserved_ports = list(PortReservation.objects.all().values_list('port', flat=True))
        
        # Consolidar todos los puertos en uso
        used_ports_map = {} # port -> owner_name
        for s in services_with_ports:
            if s.assigned_port:
                used_ports_map[int(s.assigned_port)] = s.name
            if s.assigned_ports: # Lista de puertos del compose
                for p in s.assigned_ports:
                    used_ports_map[int(p)] = f"{s.name} (Compose)"
        
        for owner, p in compose_running_ports:
            used_ports_map[int(p)] = owner
        for p in reserved_ports:
            if p not in used_ports_map:
                used_ports_map[int(p)] = "Reserva activa"
        
        port_in_use = port in used_ports_map
        
        if not port_in_use:
            return JsonResponse({
                'success': True,
                'available': True,
                'port': port,
                'message': f'✅ Puerto {port} disponible'
            })
        else:
            # Puerto ocupado, generar 3 sugerencias aleatorias
            # Usamos los puertos que ya calculamos en used_ports_map
            all_used_ports = set(used_ports_map.keys())
            
            available_ports = [p for p in range(40000, 50001) if p not in all_used_ports]
            
            if len(available_ports) == 0:
                return JsonResponse({
                    'success': False,
                    'available': False,
                    'error': 'No hay puertos disponibles en el rango 40000-50000'
                })
            
            # Seleccionar 3 puertos aleatorios disponibles
            suggestions = random.sample(available_ports, min(3, len(available_ports)))
            suggestions.sort()
            
            return JsonResponse({
                'success': True,
                'available': False,
                'port': port,
                'message': f'⚠️ Puerto {port} ya está en uso',
                'suggestions': suggestions
            })
            
    except ValueError:
        return JsonResponse({
            'success': False,
            'error': 'Puerto inválido'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al verificar puerto: {str(e)}'
        })


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
    
    # Sincronizar estado de servicios con Docker
    for service in services:
        sync_service_status(service)
    
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
    user = request.user
    if not (user.is_superuser or user_is_admin(user) or user_is_teacher(user) or user_is_student(user)):
        return HttpResponse("No tienes permiso para consultar servicios.", status=403)

    if user.is_superuser or user_is_admin(user) or user_is_teacher(user):
        qs = Service.objects.all()
        is_supervisor = True
    else:
        qs = Service.objects.filter(owner=user)
        is_supervisor = False
        
    qs = qs.exclude(status="removed")
    subject_id = request.GET.get("subject")
    project_id = request.GET.get("project")

    if subject_id:
        qs = qs.filter(subject_id=subject_id)
    if project_id:
        qs = qs.filter(project_id=project_id)

    # Sincronizar estados con Docker antes de renderizar
    for s in qs:
        sync_service_status(s)

    host = request.get_host().split(":")[0]
    
    # Evaluar si algún servicio está en estado transitorio para forzar polling en el cliente
    transient_states = ["pending", "starting", "stopping", "building", "pulling", "deleting", "creating"]
    has_transient = qs.filter(status__in=transient_states).exists()
    
    if not has_transient:
        # Tambien considerar transitorios los contenedores individuales de Compose
        # (ej: si estan en 'created', 'restarting', 'removing')
        has_transient = ServiceContainer.objects.filter(
            service__in=qs,
            status__in=["created", "restarting", "removing"]
        ).exists()

    html = render_to_string("containers/_service_rows.html", {
        "services": qs, 
        "host": host, 
        "is_supervisor": is_supervisor,
        "has_transient": has_transient,
        "subject_id": subject_id,
        "project_id": project_id
    }, request=request)
    return HttpResponse(html)


@login_required
def terminal_v2_view(request, pk):
    """
    Terminal web mejorada con PyXtermJS.
    
    Características:
    - Soporte para múltiples shells
    - Mejor manejo de errores
    - Soporte para servicios Compose (múltiples contenedores)
    - Timeout configurable
    """
    user = request.user
    
    # 1. Intentar obtener el servicio sin filtrar por dueño primero
    try:
        service = Service.objects.get(pk=pk)
    except Service.DoesNotExist:
        raise Http404("El servicio solicitado no existe.")

    # 2. Validar Permisos
    has_permission = False
    if user_is_admin(user):
        has_permission = True
    elif user_is_teacher(user):
        # El profesor solo puede entrar si es de su asignatura
        if service.subject and service.subject.teacher_user == user:
            has_permission = True
    elif service.owner == user:
        has_permission = True

    if not has_permission:
        # En lugar de 404, devolvemos una página de error estilizada
        return render(request, "containers/errors/no_permission.html", {
            "service_name": service.name,
            "error_title": "Acceso Denegado",
            "error_message": "No tienes los permisos necesarios para acceder a esta terminal interactiva."
        }, status=403)
    
    # Obtener parámetro de contenedor (para servicios Compose)
    container_id = request.GET.get('container')
    container_name = service.name
    
    # Verificar estado del servicio
    if container_id:
        # Modo Compose: verificar contenedor específico
        try:
            container_record = ServiceContainer.objects.get(pk=container_id, service=service)
            if container_record.status != "running":
                return HttpResponse(
                    f"El contenedor '{container_record.name}' no está en ejecución.",
                    status=400
                )
            container_name = container_record.name
        except ServiceContainer.DoesNotExist:
            return HttpResponse("Contenedor no encontrado.", status=404)
    else:
        # Modo simple: verificar servicio principal
        if service.status != "running" or not service.container_id:
            return HttpResponse("El servicio no está en ejecución.", status=400)
    
    # Verificar Docker disponible
    docker_client = get_docker_client()
    if docker_client is None:
        return HttpResponse("Docker no está disponible actualmente.", status=503)
    
    # Construir WebSocket path
    ws_path = f"/ws/terminal-v2/{service.id}/"
    if container_id:
        ws_path += f"?container={container_id}"
    
    # Capturar URL de retorno
    return_url = request.GET.get('return_url')
    if not return_url:
        referer = request.META.get('HTTP_REFERER', '')
        if 'subjects/' in referer:
            return_url = referer
        else:
            from django.urls import reverse
            return_url = reverse('containers:student_panel')
    
    return render(request, "containers/terminal_v2.html", {
        "service": service,
        "container_name": container_name,
        "ws_path": ws_path,
        "return_url": return_url,
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

    projects_qs = (
        UserProject.objects.filter(subject__teacher_user=request.user)
        if not request.user.is_superuser
        else UserProject.objects.all()
    )
    projects = projects_qs.select_related("subject", "user_profile")

    # Estadísticas para el profesor
    total_students = subjects.values('students').distinct().count()
    total_services = Service.objects.filter(subject__in=subjects).exclude(status="removed").count()
    active_services = Service.objects.filter(subject__in=subjects, status="running").count()

    context = {
        "subjects": subjects,
        "projects": projects,
        "stats": {
            "subjects": subjects.count(),
            "projects": projects.count(),
            "students": total_students,
            "total_services": total_services,
            "active_services": active_services,
        }
    }

    return render(request, "professor/dashboard.html", context)


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
    host = request.get_host().split(":")[0]

    return render(
        request,
        "professor/subject_detail.html",
        {
            "subject": subject,
            "students": students,
            "services": services,
            "projects": projects,
            "host": host,
        },
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
    host = request.get_host().split(":")[0]

    return render(
        request,
        "professor/project_detail.html",
        {"project": project, "related_services": related_services, "host": host},
    )


# Editar servicio (env/archivos) y reiniciar
@login_required
def edit_service(request, pk):
    service = get_object_or_404(Service, pk=pk, owner=request.user)

    # Restricción: No se pueden editar servicios del catálogo (default)
    if service.mode == 'default':
        return render(request, 'containers/edit_service_forbidden.html', {
            'service': service,
            'title': 'No Permitido - Editar Servicio'
        })

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
            container_configs = _parse_optional_json(request.POST.get("container_configs", ""), "Configuración de contenedores")
        except ValueError as exc:
            return HttpResponse(str(exc), status=400)

        # Actualizar campos
        service.env_vars = env_vars if env_vars is not None else None
        service.container_configs = container_configs if container_configs is not None else None
        
        # Tipo y visibilidad (solo modo dockerhub o custom/dockerfile)
        if service.mode == 'dockerhub' or (service.mode == 'custom' and service.dockerfile):
            service.container_type = request.POST.get("container_type", service.container_type)
            service.is_web = request.POST.get("is_web") == "on"
            
            i_port = request.POST.get("internal_port")
            if i_port:
                try:
                    service.internal_port = int(i_port)
                except ValueError:
                    pass
        
        # Puerto externo (assigned_port)
        c_port = request.POST.get("custom_port")
        if c_port:
            try:
                service.assigned_port = int(c_port)
            except ValueError:
                pass
        else:
            # Si se deja vacío, se vuelve a automático (None)
            service.assigned_port = None

        # Actualizar archivos si se proporcionan (reemplazo total)
        if request.FILES.get("dockerfile"):
            service.dockerfile = request.FILES["dockerfile"]
        if request.FILES.get("compose"):
            service.compose = request.FILES["compose"]
        if request.FILES.get("code"):
            service.code = request.FILES["code"]

        service.save()

        try:
            # Purga y reconstrucción total
            remove_container(service, keep_files=True)
            # Usar configs del POST o caer al modelo
            configs_to_use = container_configs if container_configs else service.container_configs
            run_container(service, container_configs=configs_to_use)
        except Exception as exc:
            return HttpResponse(f"Error al reiniciar: {exc}", status=500)

        return_url = request.POST.get('return_url')
        if not return_url:
            return_url = reverse('containers:student_panel')
        return redirect(return_url)

    # Capturar URL de retorno inicial
    return_url = request.GET.get('return_url')
    if not return_url:
        referer = request.META.get('HTTP_REFERER', '')
        if 'subjects/' in referer or 'projects/' in referer:
            return_url = referer
        else:
            return_url = reverse('containers:student_panel')

    # Para Compose, necesitamos los contenedores actuales para la tabla si existen
    containers_info = []
    if service.has_compose:
        for c in service.containers.all():
            if c.name != "principal":
                containers_info.append({
                    'name': c.name,
                    'image': c.image_name,
                    'internal_ports': c.internal_ports,
                    'assigned_ports': c.assigned_ports,
                    'is_web': c.is_web,
                    'container_type': c.container_type
                })

    return render(request, "containers/edit_service.html", {
        "service": service,
        "return_url": return_url,
        "containers_info": containers_info,
        "env_vars_json": json.dumps(service.env_vars or {}, indent=2)
    })


@login_required
def view_service_file(request, pk):
    """
    Retorna el contenido de un archivo (Dockerfile o Compose) en formato JSON para el modal de vista.
    """
    service = get_object_or_404(Service, pk=pk)
    
    # Seguridad: solo dueño o admin
    if service.owner != request.user and not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'No autorizado'}, status=403)
    
    file_type = request.GET.get('type')
    file_obj = None
    
    if file_type == 'dockerfile':
        file_obj = service.dockerfile
    elif file_type == 'compose':
        file_obj = service.compose
    
    if not file_obj:
        return JsonResponse({'success': False, 'error': 'Archivo no asignado o inexistente'})
    
    try:
        if not file_obj or not file_obj.name:
            return JsonResponse({'success': False, 'error': 'El archivo no tiene una ruta válida en la base de datos.'})

        # Importar settings localmente para mayor seguridad en la función
        from django.conf import settings
        from pathlib import Path
        
        # Construir ruta absoluta
        media_root = Path(settings.MEDIA_ROOT)
        file_path = media_root / file_obj.name
        
        if not file_path.exists():
            return JsonResponse({
                'success': False, 
                'error': f"Archivo físico no encontrado en: {file_obj.name}"
            })

        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
            return JsonResponse({'success': True, 'content': content})
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': f"Excepción al leer archivo: {str(e)}"})


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
    images = AllowedImage.objects.all().order_by('image_type', 'name')
    
    # Agrupar imágenes por tipo para el selector categorizado
    images_by_type = {}
    for img in images:
        type_label = dict(AllowedImage.IMAGE_TYPES).get(img.image_type, "Otros")
        if type_label not in images_by_type:
            images_by_type[type_label] = []
        images_by_type[type_label].append(img)
    
    subjects = Subject.objects.filter(students=request.user)
    user_projects = UserProject.objects.filter(
        user_profile__user=request.user
    ).select_related('subject')
    
    # Obtener host para preview
    host = request.get_host().split(':')[0]
    
    # Capturar URL de retorno para redirigir correctamente después de crear servicio
    # Prioridad: 1) Query param 'return_url', 2) HTTP_REFERER, 3) student_panel por defecto
    return_url = request.GET.get('return_url')
    selected_subject_id = None
    
    if not return_url:
        referer = request.META.get('HTTP_REFERER', '')
        if 'subjects/' in referer:
            # Si viene de una asignatura, extraer la URL y el ID
            return_url = referer
            # Extraer ID de asignatura de la URL (ej: /subjects/1/)
            import re
            match = re.search(r'/subjects/(\d+)/', referer)
            if match:
                selected_subject_id = int(match.group(1))
        else:
            # Por defecto, panel principal
            from django.urls import reverse
            return_url = reverse('containers:student_panel')
    
    context = {
        'images': images,
        'images_by_type': images_by_type,
        'available_subjects': subjects,
        'user_projects': user_projects,
        'host': host,
        'return_url': return_url,  # Pasar URL de retorno al template
        'selected_subject_id': selected_subject_id,  # ID de asignatura pre-seleccionada
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

@login_required
def api_documentation_view(request, section_slug="introduccion"):
    """
    Pagina dedicada de documentacion de la API REST para los alumnos.
    Ahora soporta navegacion por secciones independientes.
    """
    from paasify.models.TokenModel import ExpiringToken
    import os
    from django.conf import settings
    from django.shortcuts import redirect
    from django.http import Http404

    # Definicion del orden fijo de secciones
    SECTIONS = [
        {"slug": "introduccion",    "title": "Introducción",          "file": "01_introduction.md"},
        {"slug": "autenticacion",   "title": "Autenticación",          "file": "02_authentication.md"},
        {"slug": "gets",            "title": "Consultas (GETs)",      "file": "03_gets.md"},
        {"slug": "crear",           "title": "Crear Servicio",        "file": "04_create.md"},
        {"slug": "modificar",       "title": "Modificar Servicio",    "file": "05_modify.md"},
        {"slug": "acciones",        "title": "Acciones del Servicio", "file": "06_actions.md"},
        {"slug": "logs",            "title": "Logs del Servicio",     "file": "07_logs.md"},
        {"slug": "ci-cd",           "title": "Integración CI/CD",     "file": "08_cicd.md"},
        {"slug": "errores",         "title": "Códigos de Error",      "file": "09_errors.md"},
    ]

    # Buscar la seccion actual
    current_index = -1
    for i, s in enumerate(SECTIONS):
        if s["slug"] == section_slug:
            current_index = i
            break
    
    if current_index == -1:
        raise Http404("Sección de documentación no encontrada")

    # Leer el archivo Markdown de la seccion actual y extraer H3 de todas
    partials_dir = os.path.join(settings.BASE_DIR, "templates", "api_docs", "partials")
    
    # Enriquecer SECTIONS con sus sub-encabezados (H3)
    for section in SECTIONS:
        section["subsections"] = []
        path = os.path.join(partials_dir, section["file"])
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines:
                    if line.startswith("### "):
                        title = line.replace("### ", "").strip()
                        # Generar slug para el link
                        import unicodedata
                        import re
                        slug = unicodedata.normalize('NFD', title).encode('ascii', 'ignore').decode('utf-8')
                        slug = re.sub(r'[^a-z0-9]+', '-', slug.lower()).strip('-')
                        section["subsections"].append({"title": title, "slug": slug})

    current_section = SECTIONS[current_index]
    
    # Navegacion (Siguiente / Anterior)
    prev_section = SECTIONS[current_index - 1] if current_index > 0 else None
    next_section = SECTIONS[current_index + 1] if current_index < len(SECTIONS) - 1 else None

    # Obtener el token del usuario e imágenes del catálogo
    from paasify.models.TokenModel import ExpiringToken
    from containers.models import AllowedImage
    
    token, _ = ExpiringToken.objects.get_or_create(user=request.user)
    images = AllowedImage.objects.all().order_by('name')
    
    file_path = os.path.join(partials_dir, current_section["file"])
    
    md_content = ""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            md_content = f.read()
    else:
        md_content = f"# {current_section['title']}\n\nContenido en preparación..."

    context = {
        'token': token.key,
        'user_token': token.key,
        'markdown_content': md_content,
        'sections': SECTIONS,
        'current_slug': section_slug,
        'current_index': current_index + 1,
        'total_sections': len(SECTIONS),
        'prev_section': prev_section,
        'next_section': next_section,
        'images': images,
        'title': f"{current_section['title']} - API Docs",
    }
    
    return render(request, 'containers/api_documentation.html', context)


@login_required
def api_command_generator_view(request):
    """
    Generador interactivo de comandos API.
    Permite al alumno configurar un servicio visualmente y obtener el comando curl.
    """
    from paasify.models.TokenModel import ExpiringToken
    
    token, _ = ExpiringToken.objects.get_or_create(user=request.user)
    images = AllowedImage.objects.all().order_by('name')
    subjects = Subject.objects.filter(students=request.user)
    user_projects = UserProject.objects.filter(
        user_profile__user=request.user
    ).select_related('subject')
    
    # URL de retorno
    return_url = request.GET.get('return_url')
    if not return_url:
        referer = request.META.get('HTTP_REFERER', '')
        if 'subjects/' in referer:
            return_url = referer
        else:
            from django.urls import reverse
            return_url = reverse('containers:student_panel')
        
    context = {
        'token': token.key,
        'images': images,
        'available_subjects': subjects,
        'user_projects': user_projects,
        'return_url': return_url,
    }
    
    return render(request, 'containers/api_command_generator.html', context)


# ============================================================================
# LOGS PAGE - Página dedicada para visualización de logs
# ============================================================================

@login_required
def logs_page(request, pk):
    """
    Página dedicada para visualización de logs con funcionalidades avanzadas.
    
    Características:
    - Filtros por nivel (ERROR, WARN, INFO, DEBUG)
    - Búsqueda de texto
    - Selector de cantidad de líneas
    - Selector de contenedor (para Compose)
    - Colorización con Rich
    - Caché de logs
    - Soporte para servicios Compose
    """
    user = request.user
    if user_is_admin(user) or user_is_teacher(user):
        service = get_object_or_404(Service, pk=pk)
    else:
        service = get_object_or_404(Service, pk=pk, owner=user)
    
    # Parámetros de filtro
    search_text = request.GET.get('search', '').strip()
    log_level = request.GET.get('level', 'ALL')
    tail = request.GET.get('tail', '1000')
    since = request.GET.get('since', '')
    use_rich = request.GET.get('rich', 'true').lower() == 'true'
    selected_container = request.GET.get('container', 'all')
    force_refresh = request.GET.get('refresh', 'false').lower() == 'true'
    
    # Inicializar contenedores (necesario para el context de retorno)
    containers = []
    if service.has_compose:
        containers = list(service.containers.all())

    # Obtener utilidades
    from .utils import (
        fetch_container_logs,
        group_logs_by_container,
        colorize_logs_rich,
        colorize_logs_simple,
        filter_logs,
        filter_by_level,
        invalidate_logs_cache
    )
    
    # Si se pide refrescar, invalidar caché antes de obtener logs
    if force_refresh:
        invalidate_logs_cache(service)

    # Convertir tail a int (o None para 'all')
    try:
        tail_int = int(tail) if tail != 'all' else 'all'
    except ValueError:
        tail_int = 1000

    since_val = since if since else None

    if service.has_compose and selected_container != 'all':
        try:
            container_id = int(selected_container)
            specific_container = service.containers.get(id=container_id)
            logs_lines, from_cache = fetch_container_logs(service, tail=tail_int, since=since_val, container_name=specific_container.name, force_refresh=force_refresh)
        except (ValueError, ServiceContainer.DoesNotExist):
            logs_lines, from_cache = fetch_container_logs(service, tail=tail_int, since=since_val, force_refresh=force_refresh)
    else:
        logs_lines, from_cache = fetch_container_logs(service, tail=tail_int, since=since_val, force_refresh=force_refresh)
    
    # Aplicar filtros sobre las líneas "raw" (con prefijo [name] si aplica)
    if search_text:
        logs_lines = filter_logs(logs_lines, search_text)
    
    if log_level != 'ALL':
        logs_lines = filter_by_level(logs_lines, log_level)
    
    # Guardar conteo real antes de añadir cabeceras
    total_logs_count = len(logs_lines)
    
    # Agrupar por contenedor y añadir cabeceras '==='
    if service.has_compose or selected_container != 'all':
        logs_lines = group_logs_by_container(logs_lines)
    
    # Colorizar logs final
    try:
        if use_rich:
            logs_html = colorize_logs_rich(logs_lines)
        else:
            logs_html = colorize_logs_simple(logs_lines)
    except Exception as e:
        logger.error(f"Error colorizando logs: {e}")
        logs_html = colorize_logs_simple(logs_lines)
    
    # Capturar URL de retorno
    return_url = request.GET.get('return_url')
    if not return_url:
        referer = request.META.get('HTTP_REFERER', '')
        if 'subjects/' in referer:
            return_url = referer
        else:
            from django.urls import reverse
            return_url = reverse('containers:student_panel')
    
    # Si es request HTMX, solo devolver el fragmento de logs
    if request.headers.get('HX-Request'):
        return render(request, "containers/_partials/logs/_logs_content.html", {
            "logs_html": logs_html,
            "total_logs_count": total_logs_count,
            "total_lines": len(logs_lines),
            "from_cache": from_cache,
            "search_text": search_text,
            "log_level": log_level,
            "since": since,
        })
    
    # Request normal: página completa
    return render(request, "containers/logs_page.html", {
        "service": service,
        "logs_html": logs_html,
        "search_text": search_text,
        "log_level": log_level,
        "tail": tail,
        "since": since,
        "use_rich": use_rich,
        "total_lines": len(logs_lines),
        "from_cache": from_cache,
        "return_url": return_url,
        "containers": containers,
        "selected_container": selected_container,
    })
