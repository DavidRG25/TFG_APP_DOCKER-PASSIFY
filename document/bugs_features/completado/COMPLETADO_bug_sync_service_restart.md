# Bug: Estado "error" al reiniciar PaaSify con contenedor detenido
**Fecha**: 2025-12-09 23:05  
**Resuelto**: 2025-12-09 23:12  
**Prioridad**: ALTA  
**Estado**: ✅ RESUELTO

---

## 🐛 DESCRIPCIÓN DEL BUG

**Problema**: Al reiniciar PaaSify, los servicios con contenedores detenidos se marcan como "error".

**Escenario**:
1. Usuario detiene un contenedor (estado: "stopped")
2. Usuario cierra PaaSify
3. Usuario reinicia PaaSify
4. **Resultado**: Servicio aparece con estado "error" ❌

**Comportamiento esperado**:
- Servicio debería seguir en estado "stopped" ✅

---

## 🔍 CAUSA

La función `_sync_service` no manejaba correctamente el caso:
- `service.status = "stopped"` (o "error")
- `docker_status = "exited"`

Este es un estado **VÁLIDO** pero se marcaba como error.

---

## ✅ SOLUCIÓN IMPLEMENTADA

**Archivo modificado**: `containers/views.py` - Función `_sync_service`

**Cambio realizado**:
Añadida lógica para sincronizar servicios stopped/error con contenedores detenidos:

```python
# Líneas 73-80
if service.status in {"stopped", "error"} and docker_status in {"exited", "stopped"}:
    if service.status == "error":
        # Recuperar de error si solo está detenido
        service.status = "stopped"
        service.save(update_fields=["status"])
    return  # Todo OK
```

**Beneficios**:
- ✅ No marca error al reiniciar con contenedores detenidos
- ✅ Recupera automáticamente servicios en "error" si el contenedor solo está detenido
- ✅ Sincronización correcta de estados

---

## 🧪 TESTING REALIZADO

✅ **Test 1**: Contenedor detenido + reinicio PaaSify → Estado "stopped" (correcto)  
✅ **Test 2**: Servicio en "error" con contenedor detenido → Recupera a "stopped"  
✅ **Test 3**: Contenedor running → Estado "running" (sin cambios)

---

**Última actualización**: 2025-12-09 23:12  
**Estado**: ✅ RESUELTO Y VERIFICADO
