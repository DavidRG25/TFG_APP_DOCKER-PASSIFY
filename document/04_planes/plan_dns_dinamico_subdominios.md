# 🌐 Plan: DNS Dinámico con Subdominios Automáticos

> [!IMPORTANT]
> **Estado: OPCIONAL / SECUNDARIO**
> Esta funcionalidad es una mejora opcional que no forma parte del núcleo de PaaSify.
> El sistema funciona perfectamente sin ella (acceso por puerto directo).
> Se plantea como una mejora de UX que aporta un acabado profesional al proyecto.

---

## 📋 Índice

1. [Objetivo](#1-objetivo)
2. [Situación Actual vs. Propuesta](#2-situación-actual-vs-propuesta)
3. [Arquitectura](#3-arquitectura)
4. [Requisitos Previos](#4-requisitos-previos)
5. [Fases de Implementación](#5-fases-de-implementación)
6. [Detalles Técnicos por Fase](#6-detalles-técnicos-por-fase)
7. [Gestión de Servicios Compose](#7-gestión-de-servicios-compose)
8. [Impacto en la API](#8-impacto-en-la-api)
9. [Estimación de Tiempos](#9-estimación-de-tiempos)
10. [Riesgos y Consideraciones](#10-riesgos-y-consideraciones)

---

## 1. Objetivo

Permitir que cada servicio desplegado en PaaSify tenga una **URL automática** del tipo:

```
https://nombre-servicio-id.paasify.com
```

Sin configuración manual por parte del alumno. El subdominio se genera automáticamente al crear el servicio y es de solo lectura.

### Ejemplo

| Antes (actual)                       | Después (propuesta)               |
| ------------------------------------ | --------------------------------- |
| `http://servidor:45327`              | `https://miniapp-273.paasify.com` |
| Puerto aleatorio difícil de recordar | URL limpia y compartible          |

---

## 2. Situación Actual vs. Propuesta

### Acceso actual

- Cada servicio recibe un **puerto aleatorio** (ej: 45327, 48660).
- El alumno accede por `http://IP_SERVIDOR:PUERTO`.
- Funcional pero poco profesional para compartir.

### Acceso propuesto

- Cada servicio web recibe un **subdominio automático**.
- El alumno accede por `https://nombre-id.paasify.com`.
- El acceso por puerto sigue funcionando como **fallback**.
- Las bases de datos y servicios internos **no** reciben subdominio.

---

## 3. Arquitectura

```
┌──────────────────────────────────────────────────────────────┐
│                    Internet / Navegador                       │
│                                                              │
│   miniapp-273.paasify.com    api-273.paasify.com             │
│            │                        │                        │
└────────────┼────────────────────────┼────────────────────────┘
             │                        │
             ▼                        ▼
┌──────────────────────────────────────────────────────────────┐
│                 Wildcard DNS: *.paasify.com                   │
│              Apunta a la IP del servidor PaaSify              │
└──────────────────────────────────────────────────────────────┘
             │                        │
             ▼                        ▼
┌──────────────────────────────────────────────────────────────┐
│                    TRAEFIK (Reverse Proxy)                    │
│                                                              │
│  - Escucha en puertos 80 y 443                               │
│  - Lee labels Docker de cada contenedor                      │
│  - Enruta automáticamente por Host header                    │
│  - HTTPS automático con Let's Encrypt                        │
│                                                              │
│  Reglas detectadas automáticamente:                          │
│    miniapp-273.paasify.com → contenedor miniapp:8000         │
│    api-273.paasify.com     → contenedor api:5000             │
└──────────────────────────────────────────────────────────────┘
             │                        │
             ▼                        ▼
┌─────────────────────┐  ┌─────────────────────┐
│   Contenedor Web    │  │   Contenedor API    │
│   (puerto 8000)     │  │   (puerto 5000)     │
└─────────────────────┘  └─────────────────────┘
```

### Componentes clave

| Componente                     | Rol                                         | Coste                            |
| ------------------------------ | ------------------------------------------- | -------------------------------- |
| Dominio (`paasify.com`)        | Dominio base                                | ~10-12€/año                      |
| Wildcard DNS (`*.paasify.com`) | Un registro que cubre TODOS los subdominios | Gratis (incluido con el dominio) |
| Traefik                        | Reverse proxy que enruta por subdominio     | Gratis (open source)             |
| Let's Encrypt                  | Certificados HTTPS automáticos              | Gratis                           |

---

## 4. Requisitos Previos

### 4.1 Dominio

- Comprar un dominio (ej: `paasify.com`, `paasify.es`, o similar).
- Proveedor recomendado: **Cloudflare** (DNS gratuito + gestión sencilla).

### 4.2 Registro DNS Wildcard

- Crear **un único** registro DNS:
  ```
  Tipo: A
  Nombre: *
  Valor: IP_DEL_SERVIDOR
  TTL: Auto
  ```
- Con este registro, **cualquier** `xxx.paasify.com` apuntará al servidor.
- Los subdominios NO se compran. Son ilimitados y gratuitos.

### 4.3 Servidor

- Puerto 80 y 443 libres para Traefik.
- Docker instalado (ya lo tienes).

---

## 5. Fases de Implementación

### Fase 1: Infraestructura base

- [ ] Comprar dominio
- [ ] Configurar wildcard DNS
- [ ] Desplegar Traefik como contenedor
- [ ] Crear red Docker compartida (`traefik-net`)

### Fase 2: Modelo y generación de subdominios

- [ ] Añadir campo `subdomain` al modelo `Service`
- [ ] Crear función `_ensure_subdomain()` en `services.py`
- [ ] Migración de base de datos

### Fase 3: Integración con contenedores

- [ ] Inyectar labels Traefik en servicios simples (`_run_simple_service`)
- [ ] Inyectar labels Traefik en servicios compose (`_run_compose_service`)
- [ ] Conectar contenedores a la red `traefik-net`

### Fase 4: UI y API

- [ ] Mostrar URL en la vista de detalle del servicio
- [ ] Mostrar URL en la tabla de servicios
- [ ] Añadir `subdomain` y `url` al serializer de la API
- [ ] Mostrar URL en respuestas POST/GET

### Fase 5: HTTPS

- [ ] Configurar Let's Encrypt en Traefik
- [ ] Verificar certificados automáticos

---

## 6. Detalles Técnicos por Fase

### Fase 1: Traefik

Archivo `docker-compose.traefik.yml` (se levanta una sola vez en el servidor):

```yaml
version: "3.8"

services:
  traefik:
    image: traefik:v3.0
    restart: always
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.email=tu@email.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
      - "--certificatesresolvers.letsencrypt.acme.tlschallenge=true"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - traefik-certs:/letsencrypt
    networks:
      - traefik-net

networks:
  traefik-net:
    name: traefik-net
    driver: bridge

volumes:
  traefik-certs:
```

Red Docker compartida:

```bash
docker network create traefik-net
```

### Fase 2: Modelo

```python
# containers/models.py - Añadir al modelo Service
subdomain = models.CharField(
    max_length=100,
    unique=True,
    blank=True,
    null=True,
    editable=False,
    help_text="Subdominio generado automáticamente para acceso web."
)
```

```python
# containers/services.py - Nueva función
from django.utils.text import slugify

def _ensure_subdomain(service: Service) -> None:
    """Genera un subdominio único si el servicio aún no tiene uno."""
    if service.subdomain:
        return

    base = slugify(service.name) or "svc"
    # Formato: nombre-id (ej: miniapp-273)
    service.subdomain = f"{base}-{service.id}"
    service.save(update_fields=["subdomain"])
```

### Fase 3: Labels Docker

#### Servicios simples

```python
# En _run_simple_service(), antes de docker_client.containers.run()

_ensure_subdomain(service)

traefik_labels = {}
if service.subdomain:
    router_name = service.subdomain.replace("-", "_")
    traefik_labels = {
        "traefik.enable": "true",
        f"traefik.http.routers.{router_name}.rule": f"Host(`{service.subdomain}.paasify.com`)",
        f"traefik.http.routers.{router_name}.entrypoints": "websecure",
        f"traefik.http.routers.{router_name}.tls.certresolver": "letsencrypt",
        f"traefik.http.services.{router_name}.loadbalancer.server.port": str(internal_port),
    }

container = docker_client.containers.run(
    image=image_to_run,
    # ... parámetros existentes ...
    labels=traefik_labels,
    networks=["traefik-net"],  # Añadir a la red de Traefik
)
```

#### Servicios compose

```python
# En _run_compose_service(), después de procesar puertos y antes de guardar el YAML

# Inyectar red Traefik al compose
if "networks" not in data:
    data["networks"] = {}
data["networks"]["traefik-net"] = {"external": True}

# Inyectar labels solo en contenedores web
for svc_name, svc_config in data["services"].items():
    c_config = (container_configs or {}).get(svc_name, {})
    if not c_config.get("is_web", False):
        continue

    subdomain = f"{slugify(svc_name)}-{service.id}"
    router_name = subdomain.replace("-", "_")

    # Añadir labels
    labels = svc_config.get("labels", [])
    if isinstance(labels, dict):
        labels = [f"{k}={v}" for k, v in labels.items()]
    labels.extend([
        "traefik.enable=true",
        f"traefik.http.routers.{router_name}.rule=Host(`{subdomain}.paasify.com`)",
        f"traefik.http.routers.{router_name}.entrypoints=websecure",
        f"traefik.http.routers.{router_name}.tls.certresolver=letsencrypt",
        f"traefik.http.services.{router_name}.loadbalancer.server.port={puerto}",
    ])
    svc_config["labels"] = labels

    # Añadir red Traefik al servicio (manteniendo default para comunicación interna)
    networks = svc_config.get("networks", [])
    if isinstance(networks, list):
        if "traefik-net" not in networks:
            networks.append("traefik-net")
    svc_config["networks"] = networks
```

### Fase 4: API y UI

#### Serializer

```python
# containers/serializers.py
class ServiceSerializer(serializers.ModelSerializer):
    subdomain = serializers.CharField(read_only=True)
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        if obj.subdomain:
            return f"https://{obj.subdomain}.paasify.com"
        return None

    class Meta:
        model = Service
        fields = [..., "subdomain", "url"]
```

#### Template (vista de detalle o tabla)

```html
{% if service.subdomain %}
<a
  href="https://{{ service.subdomain }}.paasify.com"
  target="_blank"
  class="text-decoration-none"
>
  <i class="fas fa-globe me-1"></i>
  {{ service.subdomain }}.paasify.com
</a>
{% endif %}
```

---

## 7. Gestión de Servicios Compose

| Contenedor              | `is_web` | ¿Subdominio? | URL generada          |
| ----------------------- | -------- | ------------ | --------------------- |
| `web` (nginx, frontend) | ✅       | Sí           | `web-273.paasify.com` |
| `api` (backend, flask)  | ✅       | Sí           | `api-273.paasify.com` |
| `db` (mysql, postgres)  | ❌       | No           | Solo acceso interno   |
| `redis` (caché)         | ❌       | No           | Solo acceso interno   |

**Regla**: Solo los `ServiceContainer` marcados como `is_web=True` reciben labels de Traefik y subdominio.

---

## 8. Impacto en la API

### Resumen de cambios

| Endpoint                             | Entrada                             | Salida                                  |
| ------------------------------------ | ----------------------------------- | --------------------------------------- |
| `POST /api/containers/`              | Sin cambios                         | Añade `subdomain` y `url` en respuesta  |
| `PATCH /api/containers/{id}/`        | `subdomain` es read-only, se ignora | Devuelve `subdomain` y `url`            |
| `GET /api/containers/{id}/`          | N/A                                 | Añade `subdomain` y `url`               |
| `POST /api/containers/{id}/start/`   | Sin cambios                         | Sin cambios                             |
| `POST /api/containers/{id}/stop/`    | Sin cambios                         | Sin cambios                             |
| `POST /api/containers/{id}/restart/` | Sin cambios                         | Sin cambios                             |
| `DELETE /api/containers/{id}/`       | Sin cambios                         | Traefik deja de enrutar automáticamente |

### Ejemplo de respuesta API con subdominio

```bash
CURL -X GET "http://localhost:8000/api/containers/273/" \
  -H "Authorization: Bearer <TOKEN>"
```

```json
{
  "id": 273,
  "name": "miniapp-paasify-testing",
  "status": "running",
  "assigned_port": 45327,
  "internal_port": 8000,
  "subdomain": "miniapp-paasify-testing-273",
  "url": "https://miniapp-paasify-testing-273.paasify.com",
  "image": "davidrg25/miniapp-paasify-tes"
}
```

---

## 9. Estimación de Tiempos

| Fase       | Tarea                            | Tiempo estimado |
| ---------- | -------------------------------- | --------------- |
| **Fase 1** | Comprar dominio + configurar DNS | 30 min          |
| **Fase 1** | Desplegar Traefik + red Docker   | 1 hora          |
| **Fase 2** | Campo `subdomain` + migración    | 15 min          |
| **Fase 2** | Función `_ensure_subdomain()`    | 20 min          |
| **Fase 3** | Labels en servicios simples      | 30 min          |
| **Fase 3** | Labels en servicios compose      | 45 min          |
| **Fase 3** | Red compartida Traefik           | 30 min          |
| **Fase 4** | Serializer + API                 | 20 min          |
| **Fase 4** | Templates UI                     | 30 min          |
| **Fase 5** | HTTPS Let's Encrypt              | 30 min          |
|            | **Pruebas y ajustes**            | 1 hora          |
|            | **TOTAL**                        | **≈ 6 horas**   |

---

## 10. Riesgos y Consideraciones

### ⚠️ Desarrollo local

- En local (Windows) no se puede usar un dominio real.
- **Solución para desarrollo**: usar `nip.io` (ej: `miniapp.127.0.0.1.nip.io`) o editar `C:\Windows\System32\drivers\etc\hosts`.
- **Alternativa**: desarrollar y probar esta feature directamente en un servidor con IP pública.

### ⚠️ Coexistencia con puertos

- El sistema de puertos actual **sigue funcionando** como siempre.
- Traefik es una capa adicional, no reemplaza nada.
- Si Traefik cae, los servicios siguen accesibles por puerto directo.

### ⚠️ Colisiones de subdominio

- El formato `nombre-id` garantiza unicidad por diseño.
- El campo `subdomain` es `unique=True` en la base de datos como doble seguridad.

### ⚠️ Servicios no web

- Bases de datos, Redis, workers, etc. **no** reciben subdominio.
- Solo se enrutan los contenedores marcados como `is_web=True`.

### ⚠️ Rendimiento

- Traefik es muy ligero (~30MB RAM).
- No añade latencia perceptible al enrutamiento.
- Let's Encrypt tiene rate limits (50 certificados/semana por dominio), suficiente para un entorno educativo.

---

> **Nota final**: Este plan es una mejora de calidad de vida (Quality of Life) para los alumnos.
> PaaSify funciona perfectamente sin él. Se recomienda implementar solo cuando el núcleo del
> sistema esté estable y todas las funcionalidades principales estén completas y testeadas.
