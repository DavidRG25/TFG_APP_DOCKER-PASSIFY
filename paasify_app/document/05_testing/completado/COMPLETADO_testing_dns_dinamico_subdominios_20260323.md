# 🧪 Plan de Test: DNS Dinámico y Subdominios (Traefik)

**Fecha:** 22/03/2026
**Objetivo:** Verificar el correcto enrutamiento de servicios mediante subdominios dinámicos.

---

## 1. Pruebas en Entorno Local (localhost)

- [SI] **Test 1.1: Despliegue de Servicio Simple (Dockerfile/Catálogo)**
  - **Pasos:** Desplegar un servicio de Nginx desde el catálogo.
  - **Resultado esperado:** Comprobar que aparece una URL del tipo `nginx-id.localhost` y que al hacer clic carga la página de bienvenida.

- [SI] **Test 1.2: Despliegue de Stack Compose (Multicontenedor)**
  - **Pasos:** Desplegar un `docker-compose.yml` con un servicio marcado como web (ej: `wordpress`).
  - **Resultado esperado:** Verificar que en el contenedor correspondiente aparece la URL `nombre-contenedor-id.localhost` y carga correctamente.

- [SI] **Test 1.3: Compatibilidad con Fallback (Puerto Directo)**
  - **Pasos:** Desplegar cualquier servicio web e identificar su puerto (ej: 45000).
  - **Resultado esperado:** Acceder mediante `http://localhost:45000` y verificar que sigue respondiendo.

---

## 2. Pruebas de Sistema e Infraestructura

- [SI] **Test 2.1: Aislamiento por Subdominio**
  - **Pasos:** Desplegar dos servicios diferentes (PHP y Python). Acceder a `svc1-id.localhost` y `svc2-id.localhost`.
  - **Resultado esperado:** Cada subdominio dirige al contenedor correcto sin cruce de contenidos.

- [SI] **Test 2.2: Persistencia del Subdominio (Reiniciar)**
  - **Pasos:** Reiniciar un servicio ya desplegado.
  - **Resultado esperado:** El subdominio debe mantenerse idéntico (basado en el ID de base de datos).

- [SI] **Test 2.3: Servicios No-Web (Bases de datos)**
  - **Pasos:** Desplegar una base de datos PostgreSQL en un stack.
  - **Resultado esperado:** La base de datos NO debe tener enlace de subdominio en la interfaz.

---

## 3. Verificación Técnica (Checklist)

- [SI] La red `traefik-net` ha sido creada: `docker network ls | grep traefik-net`
- [SI] El contenedor `paasify_traefik` está en estado `running`.
- [SI] Los nuevos contenedores tienen las labels de Traefik: `docker inspect <id> | grep traefik`
- [SI] La variable `PAASIFY_DOMAIN` en el context processor devuelve el host correcto.
