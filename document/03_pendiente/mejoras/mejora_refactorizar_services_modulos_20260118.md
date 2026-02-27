# Mejora: Refactorizar services.py en Módulos

**Fecha:** 18/01/2026  
**Prioridad:** MEDIA  
**Tipo:** Refactorización / Mantenibilidad  
**Estado:** PROPUESTA  
**Esfuerzo estimado:** 30-40 minutos

---

## 🎯 OBJETIVO

Refactorizar `containers/services.py` (1090 líneas) en módulos más pequeños y manejables para mejorar la legibilidad, mantenibilidad y testabilidad del código.

---

## 📊 SITUACIÓN ACTUAL

### **Problema:**

El archivo `containers/services.py` tiene **1090 líneas** con múltiples responsabilidades:

- ❌ Difícil de navegar y entender
- ❌ Cambios requieren revisar todo el archivo
- ❌ Testing complejo (muchas dependencias)
- ❌ Conflictos frecuentes en git
- ❌ Violación del principio de responsabilidad única

### **Funciones principales:**

1. Creación de servicios (`create_service`, `_validate_compose`)
2. Ejecución (`start_service`, `stop_service`, `restart_service`)
3. Eliminación (`delete_service`, limpieza)
4. Utilidades Docker Compose (`_compose_cmd`, `_get_compose_project_name`)
5. Utilidades Docker (`get_docker_client`, `_release_port`)
6. Logs (`_append_log`, `get_service_logs`)
7. Workspaces (`ensure_service_workspace`)

---

## ✨ SOLUCIÓN PROPUESTA

### **Nueva estructura:**

```
containers/
├── services.py                    # Solo imports y exports públicos
├── services/
│   ├── __init__.py               # Exports de la API pública
│   ├── creation.py               # Creación y validación de servicios
│   ├── execution.py              # Start, stop, restart
│   ├── deletion.py               # Delete y cleanup
│   ├── compose.py                # Utilidades Docker Compose
│   ├── docker_utils.py           # Cliente Docker, puertos
│   ├── logs.py                   # Gestión de logs
│   └── workspace.py              # Gestión de workspaces
```

---

## 📝 DISTRIBUCIÓN DE CÓDIGO

### **1. `services/creation.py` (~300 líneas)**

**Responsabilidad:** Crear y validar servicios

```python
# Funciones:
- create_service(service_data, user)
- _validate_compose(compose_content, service)
- _validate_volumes(volumes_config)
- _validate_dangerous_configs(compose_data)
- _check_port_available(port)
```

### **2. `services/execution.py` (~250 líneas)**

**Responsabilidad:** Ejecutar y controlar servicios

```python
# Funciones:
- start_service(service)
- stop_service(service)
- restart_service(service)
- _execute_compose_command(service, command)
- _update_container_status(service)
```

### **3. `services/deletion.py` (~150 líneas)**

**Responsabilidad:** Eliminar servicios y limpiar recursos

```python
# Funciones:
- delete_service(service)
- _cleanup_compose(service)
- _cleanup_simple(service)
- _prune_volumes()
- _remove_workspace(service)
```

### **4. `services/compose.py` (~100 líneas)**

**Responsabilidad:** Utilidades de Docker Compose

```python
# Funciones:
- _compose_cmd()
- _get_compose_project_name(service)
- _parse_compose_file(compose_path)
- _validate_compose_syntax(compose_content)
```

### **5. `services/docker_utils.py` (~150 líneas)**

**Responsabilidad:** Utilidades de Docker

```python
# Funciones:
- get_docker_client()
- _release_port(port)
- _allocate_port(preferred_port=None)
- _get_container_info(container_id)
- _inspect_container(container)
```

### **6. `services/logs.py` (~50 líneas)**

**Responsabilidad:** Gestión de logs

```python
# Funciones:
- _append_log(service, message)
- get_service_logs(service)
- _format_log_entry(message)
```

### **7. `services/workspace.py` (~50 líneas)**

**Responsabilidad:** Gestión de workspaces

```python
# Funciones:
- ensure_service_workspace(service)
- _create_workspace(service)
- _cleanup_workspace(service)
```

### **8. `services/__init__.py`**

**Responsabilidad:** Exportar API pública

```python
# Exports públicos:
from .creation import create_service
from .execution import start_service, stop_service, restart_service
from .deletion import delete_service
from .logs import get_service_logs
from .docker_utils import get_docker_client

__all__ = [
    'create_service',
    'start_service',
    'stop_service',
    'restart_service',
    'delete_service',
    'get_service_logs',
    'get_docker_client',
]
```

### **9. `containers/services.py` (nuevo)**

**Responsabilidad:** Mantener compatibilidad hacia atrás

```python
"""
Módulo de servicios de contenedores.
Este archivo mantiene compatibilidad con imports antiguos.
"""
from containers.services import *

# Imports antiguos siguen funcionando:
# from containers.services import create_service
```

---

## 🔧 PLAN DE IMPLEMENTACIÓN

### **Fase 1: Preparación (5 min)**

1. Crear carpeta `containers/services/`
2. Crear `__init__.py` vacío
3. Crear archivos vacíos para cada módulo

### **Fase 2: Extracción (20 min)**

1. Copiar funciones a sus módulos correspondientes
2. Mantener imports internos
3. Actualizar imports entre módulos

### **Fase 3: Integración (5 min)**

1. Actualizar `services/__init__.py` con exports
2. Actualizar `containers/services.py` para re-exportar
3. Verificar que no se rompa nada

### **Fase 4: Testing (5 min)**

1. Ejecutar tests existentes
2. Verificar que servicios se crean/eliminan correctamente
3. Probar desde UI

### **Fase 5: Limpieza (5 min)**

1. Eliminar código duplicado
2. Actualizar comentarios
3. Commit y push

---

## ✅ BENEFICIOS

### **Mantenibilidad:**

- ✅ Archivos pequeños (~50-300 líneas cada uno)
- ✅ Responsabilidades claras
- ✅ Fácil de navegar y entender
- ✅ Cambios localizados

### **Testing:**

- ✅ Módulos independientes más fáciles de testear
- ✅ Mocks más simples
- ✅ Tests más rápidos

### **Colaboración:**

- ✅ Menos conflictos en git
- ✅ Code reviews más fáciles
- ✅ Onboarding más rápido

### **Profesionalismo:**

- ✅ Estructura estándar de Django
- ✅ Mejor organización del código
- ✅ Más escalable

---

## 🧪 TESTING

### **Casos de prueba:**

1. **Crear servicio simple**
   - Verificar que funciona igual que antes
   - Verificar imports

2. **Crear servicio compose**
   - Verificar validaciones
   - Verificar creación de workspace

3. **Eliminar servicio**
   - Verificar limpieza de volúmenes
   - Verificar limpieza de workspace

4. **Logs**
   - Verificar que se siguen guardando correctamente

---

## ⚠️ RIESGOS Y MITIGACIÓN

### **Riesgo 1: Romper imports existentes**

**Mitigación:** Mantener `containers/services.py` como re-export

### **Riesgo 2: Imports circulares**

**Mitigación:** Diseñar dependencias unidireccionales

### **Riesgo 3: Olvidar actualizar algún import**

**Mitigación:** Ejecutar tests completos antes de commit

---

## 📊 IMPACTO

**Código afectado:**

- `containers/services.py` (refactorizado)
- Posibles imports en `containers/views.py`
- Posibles imports en `containers/admin.py`

**Usuarios afectados:** Ninguno (cambio interno)

**Compatibilidad:** 100% hacia atrás

---

## 🎯 PRIORIDAD Y ESFUERZO

**Prioridad:** MEDIA (mejora de código, no funcionalidad)  
**Esfuerzo:** 30-40 minutos  
**Impacto:** ALTO (mejora significativa de mantenibilidad)

**Recomendación:** Implementar después de completar testing de seguridad crítica.

---

## 📚 REFERENCIAS

- [Django Best Practices - Project Structure](https://docs.djangoproject.com/en/stable/intro/reusable-apps/)
- [Python Module Organization](https://docs.python.org/3/tutorial/modules.html)
- [Clean Code - Single Responsibility Principle](https://en.wikipedia.org/wiki/Single-responsibility_principle)

---

## 🔄 ALTERNATIVAS CONSIDERADAS

### **Alternativa 1: Dejar como está**

- ❌ Problema sigue creciendo
- ❌ Cada vez más difícil de mantener

### **Alternativa 2: Dividir solo en 2-3 archivos**

- ⚠️ Mejora parcial
- ⚠️ Archivos aún grandes (~300-400 líneas)

### **Alternativa 3: Refactorizar completamente (elegida)**

- ✅ Solución definitiva
- ✅ Escalable a futuro
- ✅ Mejor práctica

---

**Creado por:** Testing de Seguridad Crítica  
**Fecha:** 2026-01-18  
**Próximo paso:** Implementar después de completar testing
