# Plan de Implementación - Docker Compose Multi-Contenedor

## Estado Actual
✅ **Completado:**
1. Modelo `ServiceContainer` creado y migrado
2. Propiedad `has_compose` añadida al modelo `Service`
3. Serializers actualizados con `ServiceContainerSerializer` y `has_compose`
4. Endpoints `dockerfile` y `compose` corregidos para leer desde `media/services/<id>/`

## Pendiente de Implementar

### 1. services.py - Funciones Auxiliares

Necesito añadir estas funciones nuevas:

```python
def ensure_service_workspace(service: Service) -> Path:
    """Crea y retorna media/services/<id>/"""
    
def prepare_service_workspace(service: Service) -> Path:
    """
    - Asegura que dockerfile/compose/code estén en services/<id>/
    - Descomprime el código a services/<id>/src/
    """

def _extract_container_port_info(container):
    """Extrae puertos de un contenedor Docker"""
    
def _previous_port_assignments(service: Service):
    """Mapa de puertos previos para reutilizar en compose"""
    
def _load_compose_data(compose_path: Path) -> dict:
    """Carga y valida docker-compose.yml"""
    
def _ensure_compose_ports(data: dict, previous_map: dict) -> list[int]:
    """Asigna puertos a servicios compose y retorna lista de reservados"""
```

### 2. services.py - Modificar `_run_container_internal`

**Lógica actual (INCORRECTA):**
- No distingue bien entre simple y compose
- No crea `ServiceContainer` records
- Build context incorrecto

**Lógica nueva (CORRECTA):**

```python
def _run_container_internal(service, *, force_restart=False, custom_port=None, command=None):
    docker_client = get_docker_client()
    workspace = prepare_service_workspace(service)  # Asegura media/services/<id>/
    
    # DECISIÓN: ¿Es compose o simple?
    if service.has_compose:
        # === MODO COMPOSE ===
        compose_path = workspace / "docker-compose.yml"
        
        # 1. Cargar y procesar puertos
        data = _load_compose_data(compose_path)
        previous_ports = _previous_port_assignments(service)
        reserved_ports = _ensure_compose_ports(data, previous_ports)
        
        # 2. Ejecutar docker compose desde workspace
        project = f"svc{service.id}"
        cmd = _compose_cmd() + ["-p", project, "-f", str(compose_path), "up", "--build", "-d"]
        subprocess.run(cmd, cwd=workspace, check=True)  # ← CWD CORRECTO
        
        # 3. Detectar contenedores creados
        containers = docker_client.containers.list(
            all=True, 
            filters={"label": f"com.docker.compose.project={project}"}
        )
        
        # 4. Crear/actualizar ServiceContainer por cada uno
        for ctr in containers:
            svc_name = ctr.labels.get("com.docker.compose.service") or ctr.name
            # IMPORTANTE: NO crear si name == "principal"
            if svc_name == "principal":
                continue
                
            internal_ports, assigned_ports = _extract_container_port_info(ctr)
            ServiceContainer.objects.update_or_create(
                service=service,
                name=svc_name,
                defaults={
                    "container_id": ctr.id,
                    "status": ctr.status,
                    "internal_ports": internal_ports,
                    "assigned_ports": assigned_ports,
                }
            )
        
        # 5. Actualizar Service
        service.container_id = containers[0].id  # Contenedor principal
        service.status = "running"
        service.save()
        
    else:
        # === MODO SIMPLE ===
        # NO crear ServiceContainer
        # Lógica actual de build + run simple
        ...
```

### 3. services.py - Nuevas funciones para ServiceContainer

```python
def start_service_container_record(container_record: ServiceContainer):
    """Inicia un contenedor específico de compose"""
    docker_client.containers.get(container_record.container_id).start()
    container_record.status = "running"
    container_record.save()

def stop_service_container_record(container_record: ServiceContainer):
    """Detiene un contenedor específico de compose"""
    docker_client.containers.get(container_record.container_id).stop()
    container_record.status = "stopped"
    container_record.save()

def fetch_container_logs(container_record: ServiceContainer) -> str:
    """Obtiene logs de un contenedor específico"""
    return docker_client.containers.get(container_record.container_id).logs(tail=200)
```

### 4. views.py - Añadir endpoints para ServiceContainer

```python
@action(detail=True, methods=["post"], url_path="containers/(?P<container_pk>\\d+)/start")
def start_container(self, request, pk=None, container_pk=None):
    service = self.get_object()
    container = get_object_or_404(ServiceContainer, pk=container_pk, service=service)
    start_service_container_record(container)
    return self._htmx_response(...)

@action(detail=True, methods=["post"], url_path="containers/(?P<container_pk>\\d+)/stop")
def stop_container_action(self, request, pk=None, container_pk=None):
    ...
```

### 5. templates/_service_rows.html - UI Condicional

```django
{% if s.has_compose %}
  <!-- Mostrar tarjetas de contenedores -->
  {% for c in s.containers.all %}
    {% if c.name != "principal" %}
      <div class="container-card">
        <strong>{{ c.name }}</strong>
        <span class="badge">{{ c.status }}</span>
        <!-- Botones: Iniciar/Detener/Logs/Terminal por contenedor -->
      </div>
    {% endif %}
  {% endfor %}
{% else %}
  <!-- Interfaz simple: solo botones del servicio -->
  <button>Iniciar</button>
  <button>Detener</button>
  ...
{% endif %}
```

### 6. consumers.py - Terminal multicontenedor

```python
class TerminalConsumer(WebsocketConsumer):
    def connect(self):
        service_id = self.scope["url_route"]["kwargs"]["service_id"]
        container_pk = parse_qs(self.scope["query_string"]).get("container")
        
        if container_pk:
            container_record = ServiceContainer.objects.get(pk=container_pk[0])
            target_container_id = container_record.container_id
        else:
            target_container_id = service.container_id
        
        # Conectar a target_container_id
        ...
```

## Orden de Implementación

1. ✅ Models + Migrations
2. ✅ Serializers
3. ✅ Views (dockerfile/compose endpoints)
4. ⏳ **SIGUIENTE:** services.py (funciones auxiliares)
5. ⏳ services.py (_run_container_internal)
6. ⏳ services.py (start/stop/logs container)
7. ⏳ views.py (endpoints container)
8. ⏳ templates (UI condicional)
9. ⏳ consumers.py (terminal)
10. ⏳ Pruebas

## Notas Importantes

- **Build Context**: SIEMPRE `cwd=workspace` en subprocess.run()
- **No "principal"**: Filtrar contenedores con name == "principal"
- **Workspace**: Todo en `media/services/<id>/`
- **has_compose**: Única fuente de verdad para decidir modo
