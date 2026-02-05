# Plan de Testing - URL Centralizada (PAASIFY_BASE_URL)

**Fecha**: 05/02/2026  
**Objetivo**: Validar que la plataforma responde correctamente a cambios en la URL base, ya sea por detección automática o por configuración manual (Override).

---

## 🏗️ PARTE 1: ESCENARIO DE DETECCIÓN AUTOMÁTICA

**Configuración**: Asegurarse de que el entorno NO tiene la variable `PAASIFY_BASE_URL` seteada.

### **Test 1.1: Consistencia en Localhost**

1. Arrancar el servidor normalmente: `bash run.sh`.
2. Acceder a `http://127.0.0.1:8000/paasify/containers/api-docs/`.
3. **Verificar**:
   - [ ] La sección "URL Base de la API" muestra `http://127.0.0.1:8000/api`.
   - [ ] Los ejemplos de `curl` usan `http://127.0.0.1:8000`.

### **Test 1.2: Cambio Dinámico de Host**

1. Acceder ahora usando localhost: `http://localhost:8000/paasify/containers/api-docs/`.
2. **Verificar**:
   - [ ] La documentación se adapta automáticamente y muestra `http://localhost:8000/api`.

---

## 🚀 PARTE 2: ESCENARIO DE OVERRIDE (DESPLIEGUE REAL)

**Configuración**: Simular un despliegue en un dominio específico.

### **Test 2.1: Validación de Dominio Fijo**

1. Detener el servidor.
2. Arrancarlo con la variable de entorno seteada (en PowerShell):
   ```powershell
   $env:PAASIFY_BASE_URL="https://paasify-urjc.es"; bash run.sh
   ```
3. Acceder a la plataforma (aunque sea desde localhost para la prueba).
4. Ir a **API Docs**.
5. **Verificar**:
   - [ ] La URL Base de la API muestra **obligatoriamente** `https://paasify-urjc.es/api` (aunque estés navegando desde 127.0.0.1).
   - [ ] Todos los comandos `curl` de la página usan el nuevo dominio urjc.es.

### **Test 2.2: Propagación a la Guía de Despliegue (Templates)**

1. Ir a la **Guía de Despliegue por Terminal**.
2. Navegar por las diferentes pestañas (Catálogo, DockerHub, Personalizado).
3. **Verificar**:
   - [ ] Todos los ejemplos de `curl` en todas las pestañas empiezan por `curl -X POST https://paasify-urjc.es/api/containers/...`.
   - [ ] No hay rastro de `localhost` ni `127.0.0.1` en ninguna de las plantillas mostradas.

### **Test 2.3: Ejemplo GitHub Actions**

1. Ir a la página de **API Token** o a la sección CI/CD de la Doc.
2. Revisar el snippet de YAML para GitHub.
3. **Verificar**:
   - [ ] La línea del `curl` apunta a `https://paasify-urjc.es/api/containers/`.

---

## 🔍 CRITERIOS DE ACEPTACIÓN

- **Prioridad**: Si existe `PAASIFY_BASE_URL`, esta SIEMPRE manda sobre lo que detecte el navegador.
- **Limpieza**: No deben aparecer barras duplicadas al final de la URL (ej: `...com//api`).
- **Persistencia**: El cambio debe ser efectivo en:
  - Encabezados de tablas informativas.
  - Bloques de código (Prism.js).
  - Lógica interna de JavaScript del laboratorio.
