# Test 3 - Docker Compose: Bugs detectados y resueltos
**Fecha**: 2025-12-09 23:33  
**Resuelto**: 2025-12-09 23:49  
**Test**: Test 3 - Docker Compose (2 contenedores)  
**Estado**: ✅ RESUELTO

---

## ✅ BUGS RESUELTOS

### **Bug 1: Puertos externos usan puertos internos en lugar de rango 40000-50000** ✅
**Problema**: Los contenedores de compose usaban los puertos internos (5000, 6379) como externos

**Solución implementada**:
- Modificado `_ensure_compose_ports` en `containers/services.py`
- Ahora verifica si el puerto especificado está en el rango 40000-50000
- Si está fuera del rango, asigna uno aleatorio del rango correcto
- Mantiene compatibilidad con puertos previamente asignados

**Archivo modificado**: `containers/services.py` (líneas 275-296)

**Resultado**: ✅ Verificado funcionando correctamente

---

### **Bug 2: Texto "Detener servicio" en singular** ✅
**Problema**: Botón decía "Detener servicio" en lugar de "Detener servicios" (plural)

**Solución implementada**:
- Cambiado texto del botón a "Detener servicios"

**Archivo modificado**: `templates/containers/_service_rows.html` (línea 74)

**Resultado**: ✅ Verificado funcionando correctamente

---

## 📋 BUGS SEPARADOS PARA FUTURO

Los siguientes bugs se han documentado en archivos separados para implementación futura:

### **Bug 3: Botón "Acceder" en servicios no-HTTP**
**Archivo**: `bug_acceder_redis.md`  
**Prioridad**: MEDIA  
**Descripción**: Redis y otras bases de datos no deberían tener botón "Acceder" activo

### **Bug 4: Auto-refresh no funciona**
**Archivo**: `bug_autorefresh.md`  
**Prioridad**: MEDIA  
**Descripción**: La tabla no se actualiza automáticamente cada 5 segundos

---


**Fixes implementados**:
1. ✅ Puertos externos en rango 40000-50000
2. ✅ Texto "Detener servicios" en plural

**Bugs pendientes (documentados)**:
3. ⏳ Deshabilitar "Acceder" para servicios no-HTTP → `bug_acceder_redis.md`
4. ⏳ Auto-refresh → `bug_autorefresh.md`

---

## 🔧 ARCHIVOS MODIFICADOS

1. `containers/services.py` - Función `_ensure_compose_ports` (líneas 275-296)
2. `templates/containers/_service_rows.html` - Texto del botón (línea 74)

---

## 🧪 TESTING REALIZADO

✅ **Test 1**: Puertos externos en rango 40000-50000  
- Creado servicio compose con web (5000) + redis (6379)
- Verificado: Puertos asignados en rango 42430, 43971 (correcto)

✅ **Test 2**: Texto "Detener servicios"  
- Verificado: Botón muestra "Detener servicios" en plural

---

**Última actualización**: 2025-12-09 23:49  
**Estado**: ✅ RESUELTO - Bugs críticos implementados, bugs menores documentados para futuro
