# 🚀 Implementación: DNS Dinámico con Traefik y Subdominios

**Fecha:** 22/03/2026
**Versión:** v10.15.0 (Propuesta)
**Plan de referencia:** [plan_dns_dinamico_subdominios.md](../../04_planes/plan_dns_dinamico_subdominios.md)

---

## 1. Introducción
Se ha implementado un sistema de enrutamiento dinámico basado en subdominios para que cada servicio desplegado por los alumnos en PaaSify sea accesible mediante una URL limpia (ej: `mi-proyecto-123.localhost`) en lugar de depender únicamente de la dirección IP y un puerto aleatorio.

## 2. Cambios Realizados

### 2.1. Modelos y Base de Datos (`containers/models.py`)
- Se ha añadido el campo `subdomain` (CharField) a los modelos `Service` y `ServiceContainer`.
- Se han generado las migraciones correspondientes: `0024_service_subdomain_servicecontainer_subdomain.py`.

### 2.2. Lógica de Negocio (`containers/utils.py` y `services.py`)
- **Extracción de Dominio**: Nueva utilidad `get_paasify_domain()` en `containers/utils.py` que extrae el host de la variable `PAASIFY_BASE_URL`.
- **Inyección de Etiquetas (Labels)**: 
    - En el arranque de servicios simples (`_run_simple_service`), se añaden etiquetas de Traefik al contenedor.
    - En servicios compuestos (`_run_compose_service`), se inyectan dinámicamente etiquetas y la red externa en el archivo `docker-compose.yml` antes de ejecutar `up`.
- **Gestión de Redes**: Se ha configurado el sistema para que todos los contenedores con acceso web se conecten automáticamente a la red `traefik-net`.

### 2.3. Infraestructura de Despliegue (`deploy/docker-compose.yml`)
- Se ha añadido el servicio **Traefik v3.0** como punto de entrada (Reverse Proxy).
- Traefik escucha en el puerto 80 (y opcionalmente 443).
- El servicio **Nginx** (PaaSify Proxy) se ha movido detrás de Traefik, perdiendo la exposición directa de puertos y ganando etiquetas de enrutamiento para el dominio principal.
- Se ha definido la red `traefik-net` como externa.

### 2.4. Interfaz de Usuario y UX
- **Context Processor**: Actualizado `global_settings` en `paasify/context_processors.py` para exponer `PAASIFY_DOMAIN` en todas las plantillas.
- **Plantillas**: 
    - `_service_rows.html`: Muestra el enlace del subdominio en la lista de servicios.
    - `_container_card.html`: Muestra el enlace individual para cada contenedor de un stack que sea marcado como web.

## 3. Configuración Requerida

### 3.1. Variable de Entorno
En el archivo `.env`:
- `PAASIFY_BASE_URL`: El sistema usará este valor para determinar el dominio base (ej: `localhost` o `paas.tfg.etsii.urjc.es`).

### 3.2. Preparación de Red
Es obligatorio crear la red manualmente antes de iniciar el sistema:
```bash
docker network create traefik-net
```

## 4. Impacto en Contenedores Existentes
Los contenedores desplegados antes de esta implementación seguirán funcionando mediante IP:Puerto, pero **no** tendrán subdominio ni conexión a `traefik-net`.
- **Solución**: El usuario simplemente debe hacer clic en "Reiniciar" o "Desplegar" nuevamente en PaaSify para que el sistema inyecte las nuevas configuraciones.

## 5. Conclusión
Esta mejora aporta un nivel de profesionalidad y facilidad de uso significativos a la plataforma, permitiendo a los alumnos acceder a sus aplicaciones de forma nemotécnica y facilitando el despliegue de múltiples servicios web en un mismo servidor sin conflictos de puertos en la URL final.
