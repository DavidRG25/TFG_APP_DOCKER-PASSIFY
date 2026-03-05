# 📖 Documentación de PaaSify

<p align="center">
  <img src="assets/logo.png" alt="PaaSify Logo" width="280"/>
</p>

<p align="center">
  <em>Plataforma como Servicio (PaaS) educativa para despliegue de contenedores Docker</em>
</p>

---

## Guías Disponibles

| Documento                                           | Audiencia                    | Descripción                                                                                                                     |
| --------------------------------------------------- | ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| [**🚀 Despliegue y Administración**](DEPLOYMENT.md) | Sysadmins / DevOps           | Cómo desplegar PaaSify en producción, configurar TLS, monitorizar con cAdvisor, hacer backups y resolver problemas              |
| [**🛠 Desarrollo**](DEVELOPMENT.md)                 | Desarrolladores              | Stack tecnológico, arquitectura interna (con diagramas), modelo de datos, estructura del código, API REST, CI/CD y convenciones |
| [**📘 Guía de Usuario**](USER_GUIDE.md)             | Alumnos / Profesores / Admin | Qué es PaaSify, cómo desplegar servicios, roles, terminal web, API programática y preguntas frecuentes                          |

---

## Resumen de la Arquitectura

```mermaid
graph TB
    subgraph "Repositorio"
        ROOT["📁 Raíz (Monorepo)"]
        ROOT --> GH[".github/ — CI/CD"]
        ROOT --> DEPLOY["deploy/ — Producción"]
        ROOT --> DOCS["docs/ — Documentación"]
        ROOT --> APP["paasify_app/ — Aplicación"]
    end

    subgraph "paasify_app/"
        APP --> DJANGO["Django Backend<br/>(paasify + containers)"]
        APP --> DOCKER_STUFF["Dockerfile +<br/>docker-compose.yml"]
        APP --> SCRIPTS["Scripts de utilidad"]
    end

    subgraph "Producción"
        DEPLOY --> COMPOSE["docker-compose.yml"]
        COMPOSE --> NGINX["Nginx (TLS)"]
        COMPOSE --> CORE["PaaSify (Daphne)"]
        COMPOSE --> PG["PostgreSQL"]
        COMPOSE --> CADV["cAdvisor"]
    end
```

---

## Enlaces Rápidos

- **Código fuente:** [`paasify_app/`](../paasify_app/)
- **CI/CD:** [`.github/workflows/`](../.github/workflows/)
- **Configuración de producción:** [`deploy/`](../deploy/)
- **API interactiva:** `/api-docs/` (disponible en la instancia desplegada)
