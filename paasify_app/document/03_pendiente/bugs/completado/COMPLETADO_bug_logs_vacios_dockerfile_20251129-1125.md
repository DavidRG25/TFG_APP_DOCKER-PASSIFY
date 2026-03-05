# Bug Report - Rama: dev2

> Resumen: Logs vacios en servicios con error de Dockerfile

## 🐛 Bug detectado durante testing

**Fase de testing:** Test 3.1 - Service Admin  
**Fecha:** 2025-11-29  
**Reportado por:** Usuario (testing manual)

---

## 📋 Descripcion del problema

Al crear un servicio con un **Dockerfile personalizado** que falla durante el build, el modal de "Logs" aparece **vacio**, aunque el servicio se marca como ERROR.

### Comportamiento observado:

1. Usuario sube Dockerfile personalizado
2. Dockerfile tiene un error (sintaxis, comando invalido, etc.)
3. Servicio se marca como **ERROR** (estado correcto ✅)
4. Usuario hace click en boton "Logs"
5. Modal se abre pero esta **vacio** ❌
6. No hay informacion sobre por que fallo

### Comportamiento esperado:

El modal de logs deberia mostrar:

- Output del comando `docker build`
- Mensaje de error especifico
- Linea del Dockerfile que causo el error

---

## 🔍 Causa raiz

### Problema 1: Ejecucion asincrona

El servicio se ejecuta en **background** usando `ThreadPoolExecutor` (linea 493 de `services.py`):

```python
EXECUTOR.submit(_run_container_worker, service.pk, force_restart, custom_port, command)
```

**Flujo:**

1. Usuario crea servicio → Estado: `pending`
2. Tarea se encola en background
3. Usuario ve servicio en lista (estado aun `pending`)
4. Usuario abre logs → **Vacio** (tarea aun ejecutandose)
5. Tarea falla → Estado cambia a `error` + logs se guardan
6. Usuario refresca → Ve estado `error` pero logs ya no se actualizan en el modal

### Problema 2: Sobrescritura de logs

En `containers/services.py`, lineas 364-369:

```python
except subprocess.CalledProcessError as e:
    build_out = (e.stdout or "") + "\n" + (e.stderr or "")
    service.status = "error"
    service.logs = build_out.strip() or str(e)  # <-- Logs del build
    service.save(update_fields=["status", "logs"])
    raise RuntimeError(f"Error al construir la imagen:\n{service.logs}")
```

Pero luego, en el bloque `except` general (lineas 451-456):

```python
except (APIError, DockerException, RuntimeError, ValueError) as exc:
    _release_port(port)
    service.status = "error"
    service.logs = str(exc)  # <-- SOBRESCRIBE los logs del build ❌
    service.save()
    raise
```

**Resultado:** Los logs detallados del build se pierden y se reemplazan con un mensaje generico.

---

## 💡 Soluciones propuestas

### Opcion A: No sobrescribir logs si ya existen (RAPIDA)

Modificar linea 454 para **agregar** en lugar de sobrescribir:

```python
except (APIError, DockerException, RuntimeError, ValueError) as exc:
    _release_port(port)
    service.status = "error"
    # No sobrescribir si ya hay logs del build
    if not service.logs or service.logs == "Ejecucion encolada.":
        service.logs = str(exc)
    else:
        _append_log(service, f"\nError adicional: {exc}")
    service.save()
    raise
```

**Ventajas:**

- ✅ Fix rapido (1 linea)
- ✅ Mantiene logs del build
- ✅ No rompe funcionalidad existente

**Desventajas:**

- ⚠️ No resuelve el problema de timing (logs vacios al abrir modal)

### Opcion B: Polling automatico en el frontend (COMPLETA)

Agregar JavaScript en el modal de logs para refrescar automaticamente:

```javascript
// En el modal de logs
function refreshLogs(serviceId) {
  fetch(`/api/services/${serviceId}/logs/`)
    .then((r) => r.json())
    .then((data) => {
      document.getElementById("logs-content").textContent = data.logs;
      // Si el estado es 'pending', seguir refrescando
      if (data.status === "pending") {
        setTimeout(() => refreshLogs(serviceId), 2000);
      }
    });
}
```

**Ventajas:**

- ✅ Resuelve el problema de timing
- ✅ UX mejorada (logs en tiempo real)
- ✅ Usuario ve progreso del build

**Desventajas:**

- ⚠️ Requiere endpoint API nuevo
- ⚠️ Mas codigo JavaScript

### Opcion C: Ejecutar sincronicamente para Dockerfile (HIBRIDA)

Modificar `run_container` para ejecutar **sincronicamente** cuando hay Dockerfile:

```python
def run_container(service, force_restart=False, custom_port=None, command=None, enqueue=True):
    # Si hay Dockerfile, ejecutar sincronicamente para capturar logs inmediatamente
    if service.dockerfile and enqueue:
        enqueue = False  # Forzar ejecucion sincronica

    if not enqueue:
        _run_container_internal(service, force_restart, custom_port, command)
        return

    # ... resto del codigo ...
```

**Ventajas:**

- ✅ Logs disponibles inmediatamente
- ✅ No requiere cambios en frontend
- ✅ Fix simple

**Desventajas:**

- ⚠️ Bloquea el request (puede ser lento)
- ⚠️ Timeout si el build tarda mucho

---

## 🎯 Recomendacion

**Implementar Opcion A + Opcion B:**

1. **Corto plazo (Opcion A):** Fix rapido para no perder logs del build
2. **Medio plazo (Opcion B):** Agregar polling en el frontend para UX mejorada

**Prioridad:** Media-Alta (afecta debugging de usuarios)

---

## 📝 Pasos para reproducir

1. Login como alumno
2. Crear nuevo servicio
3. Modo: "Personalizado (Dockerfile)"
4. Subir Dockerfile con error (ej: `FROM nginx:latest\nRUN comando_invalido`)
5. Iniciar servicio
6. Hacer click en "Logs"
7. **Resultado:** Modal vacio o mensaje generico

---

## 📊 Impacto

### Usuarios afectados:

- ✅ Alumnos que usan Dockerfile personalizado
- ✅ Profesores que debugean servicios de alumnos

### Severidad:

- **Media:** El servicio falla correctamente (estado ERROR), pero sin informacion util para debugging

### Workaround actual:

- Ver logs desde Docker Desktop
- Ver logs desde terminal: `docker logs <container_id>`
- Revisar archivos en `archivos_dockerfile/`

---

## 🔧 Archivos afectados

- `containers/services.py` (lineas 364-369, 451-456)
- `paasify/templates/paasify/services.html` (modal de logs)
- Potencialmente: nueva vista API para polling de logs

---

**Estado:** COMPLETADO  
**Asignado a:** Por definir  
**Relacionado con:** Plan de Testing Admin - Fase 3
