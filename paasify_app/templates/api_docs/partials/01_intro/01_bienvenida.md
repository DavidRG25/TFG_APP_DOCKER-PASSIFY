# 🏠 Bienvenida a PaaSify

PaaSify se ha diseñado para que los alumnos de Ingeniería Informática puedan experimentar con **contenedores y orquestación** de forma real. Todo lo que puedes hacer a través de la interfaz web está disponible mediante esta API REST.

---

### 🌐 Conectividad

Todas las peticiones deben realizarse a la siguiente URL base:

> **`{{ PAASIFY_API_URL }}/`**

| Característica   | Detalle                    |
| :--------------- | :------------------------- |
| **Formato**      | JSON (Application/json)    |
| **Codificación** | UTF-8                      |
| **Auth**         | Bearer Token               |
| **Soporte**      | Proyectos Academicos / TFG |

---

### 🚀 Ciclo de Vida del Estudiante en PaaSify

Para sacar el máximo provecho a la API, te recomendamos seguir este flujo de trabajo:

1.  **Exploración**: Consulta tus proyectos (`GET /projects/`) y asignaturas (`GET /subjects/`).
2.  **Despliegue**: Crea tu primer servicio usando una imagen del catálogo o DockerHub.
3.  **Gestión**: Monitoriza los logs y el estado de tu contenedor en tiempo real.
4.  **Evolución**: Integra tu repositorio de código mediante pipelines de CI/CD para que PaaSify se actualice solo en cada commit.

---

### ¿Por qué usar la API?

- **🔄 Automatización**: No pierdas tiempo con clics manuales; despliega con un comando.
- **⚡ Integración**: Conecta tu frontend con servicios backend desplegados dinámicamente.
- **🎓 Portfolio**: Demuestra que sabes trabajar con infraestructura como código (IaC).
