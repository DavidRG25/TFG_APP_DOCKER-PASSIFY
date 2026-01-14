# Plan de Mejoras Futuras - Documentación API

**Fecha creación**: 14/01/2026  
**Prioridad**: BAJA  
**Estado**: PENDIENTE (Mejora futura)

---

## 🎯 OBJETIVO

Ampliar la página de documentación API (`/paasify/containers/api-token/`) para incluir todos los ejemplos y funcionalidades que actualmente solo están en la guía interna (`api_rest_curl_usage_20251211_1512.md`).

---

## 📋 FUNCIONALIDADES FALTANTES

### **1. Despliegue con Dockerfile Personalizado** 🔴 ALTA

**Estado actual:** Funciona en el backend, falta documentar en UI

**Añadir a la página:**

- Acordeón nuevo: "Despliegue con Dockerfile"
- Ejemplo de curl con `multipart/form-data`
- Explicación de campos: `dockerfile`, `code`, `internal_port`

**Ejemplo a incluir:**

```bash
curl --request POST \
  http://localhost:8000/api/containers/ \
  --header 'Authorization: Bearer TOKEN' \
  --form 'name=node-app' \
  --form 'mode=custom' \
  --form 'dockerfile=@./Dockerfile' \
  --form 'code=@./mi-app.zip' \
  --form 'internal_port=3000'
```

---

### **2. Despliegue con Docker Compose** 🔴 ALTA

**Estado actual:** Funciona en el backend, falta documentar en UI

**Añadir a la página:**

- Acordeón nuevo: "Despliegue con Docker Compose"
- Ejemplo de curl con compose file
- Explicación de límite de 5 contenedores

**Ejemplo a incluir:**

```bash
curl --request POST \
  http://localhost:8000/api/containers/ \
  --header 'Authorization: Bearer TOKEN' \
  --form 'name=mi-stack' \
  --form 'mode=custom' \
  --form 'compose=@./docker-compose.yml' \
  --form 'code=@./proyecto.zip'
```

---

### **3. Variables de Entorno** 🟡 MEDIA

**Estado actual:** Funciona en el backend, falta documentar en UI

**Añadir a la página:**

- Sección en acordeón "Crear Servicio"
- Ejemplo con `env_vars` en JSON

**Ejemplo a incluir:**

```bash
curl --request POST \
  http://localhost:8000/api/containers/ \
  --header 'Authorization: Bearer TOKEN' \
  --header 'Content-Type: application/json' \
  --data '{
    "name": "mysql-db",
    "image": "mysql:8.0",
    "mode": "default",
    "env_vars": {
      "MYSQL_ROOT_PASSWORD": "secret123",
      "MYSQL_DATABASE": "myapp"
    },
    "internal_port": 3306
  }'
```

---

### **4. Puertos Personalizados** 🟡 MEDIA

**Estado actual:** Funciona en el backend, falta documentar en UI

**Añadir a la página:**

- Ejemplo con `custom_port` e `internal_port`
- Explicación de rangos (40000-50000)

**Ejemplo a incluir:**

```bash
curl --request POST \
  http://localhost:8000/api/containers/ \
  --header 'Authorization: Bearer TOKEN' \
  --header 'Content-Type: application/json' \
  --data '{
    "name": "mi-app",
    "image": "nginx:latest",
    "mode": "default",
    "custom_port": 45100,
    "internal_port": 80
  }'
```

---

### **5. Consulta de Imágenes Disponibles** 🟢 BAJA

**Estado actual:** Endpoint existe, falta documentar en UI

**Añadir a la página:**

- Acordeón nuevo: "Consultar Imágenes Disponibles"
- Endpoint: `GET /api/images/`

**Ejemplo a incluir:**

```bash
curl --request GET \
  http://localhost:8000/api/images/ \
  --header 'Authorization: Bearer TOKEN'
```

---

### **6. Consulta de Proyectos y Asignaturas** 🟢 BAJA

**Estado actual:** Endpoints NO existen (bug documentado)

**Referencia:** `document/bugs_features/bug_falta_endpoint_listar_proyectos_20251211_1529.md`

**Pendiente:**

- Crear endpoint `GET /api/projects/`
- Crear endpoint `GET /api/subjects/`
- Documentar en la página

---

### **7. Códigos de Respuesta HTTP** 🟡 MEDIA

**Añadir a la página:**

- Tabla con códigos de respuesta comunes
- Explicación de cada código
- Ejemplos de errores

**Códigos a documentar:**

- 200 OK - Operación exitosa
- 201 Created - Servicio creado
- 400 Bad Request - Datos inválidos
- 401 Unauthorized - Token inválido
- 403 Forbidden - Sin permisos
- 404 Not Found - Servicio no encontrado
- 500 Internal Server Error - Error del servidor

---

### **8. Ejemplos de Integración CI/CD** 🟢 BAJA

**Estado actual:** Solo hay ejemplo de GitHub Actions

**Añadir:**

- Ejemplo de GitLab CI
- Ejemplo de Jenkins
- Ejemplo de CircleCI (opcional)

**Ejemplo GitLab CI:**

```yaml
deploy:
  stage: deploy
  script:
    - |
      curl --request POST \
        https://paasify.com/api/containers/ \
        --header "Authorization: Bearer $PAASIFY_TOKEN" \
        --header "Content-Type: application/json" \
        --data '{
          "name": "my-app",
          "image": "nginx:latest"
        }'
```

---

### **9. Scripts Completos** 🟢 BAJA

**Añadir a la página:**

- Script Bash completo para despliegue
- Script Python completo con requests
- Descargables o copiables

---

### **10. Ejemplos Avanzados** 🟢 BAJA

**Añadir:**

- Despliegue con volúmenes
- Despliegue con redes custom
- Despliegue con health checks
- Despliegue con restart policies

---

## 📊 RESUMEN DE MEJORAS

### **Por Prioridad:**

- 🔴 ALTA (2): Dockerfile, Docker Compose
- 🟡 MEDIA (3): Variables de entorno, Puertos, Códigos HTTP
- 🟢 BAJA (5): Imágenes, Proyectos, CI/CD, Scripts, Avanzados

### **Tiempo Estimado:**

- 🔴 ALTA: 3-4 horas
- 🟡 MEDIA: 2-3 horas
- 🟢 BAJA: 2-3 horas
- **Total:** 7-10 horas

---

## 🎯 IMPLEMENTACIÓN SUGERIDA

### **Fase 1: Esenciales (ALTA prioridad)**

1. Añadir acordeón "Despliegue con Dockerfile"
2. Añadir acordeón "Despliegue con Docker Compose"
3. Actualizar template `api_token.html`

### **Fase 2: Útiles (MEDIA prioridad)**

1. Ampliar ejemplos con variables de entorno
2. Ampliar ejemplos con puertos personalizados
3. Añadir tabla de códigos HTTP

### **Fase 3: Extras (BAJA prioridad)**

1. Añadir más ejemplos de CI/CD
2. Añadir scripts descargables
3. Añadir ejemplos avanzados

---

## 📝 NOTAS IMPORTANTES

### **Backend ya soporta todo:**

✅ Todos los endpoints ya funcionan  
✅ Dockerfile personalizado funciona  
✅ Docker Compose funciona  
✅ Variables de entorno funcionan  
✅ Puertos personalizados funcionan

### **Solo falta:**

❌ Documentar en la UI (`api_token.html`)  
❌ Añadir ejemplos visuales  
❌ Mejorar UX de la documentación

### **Guía interna sigue siendo útil:**

La guía `api_rest_curl_usage_20251211_1512.md` seguirá siendo la referencia técnica completa para desarrolladores. La página de tokens será la versión "user-friendly" para usuarios finales.

---

## 🔄 ESTADO ACTUAL

**Documentación en UI:** 30% completo  
**Documentación en guía interna:** 100% completo  
**Backend funcional:** 100% completo

**Conclusión:** El backend está 100% listo, solo falta mejorar la documentación visual en la UI.

---

## 📚 REFERENCIAS

**Archivos relacionados:**

- Guía completa: `document/internal_guides/api_rest_curl_usage_20251211_1512.md`
- Página actual: `templates/containers/api_token.html`
- Vista: `containers/views.py` (manage_api_token)

**Bugs relacionados:**

- `document/bugs_features/bug_falta_endpoint_listar_proyectos_20251211_1529.md`

---

**Estado**: PENDIENTE (Mejora futura)  
**Prioridad**: BAJA (funcionalidad ya existe, solo falta documentar)  
**Fecha creación**: 14/01/2026
