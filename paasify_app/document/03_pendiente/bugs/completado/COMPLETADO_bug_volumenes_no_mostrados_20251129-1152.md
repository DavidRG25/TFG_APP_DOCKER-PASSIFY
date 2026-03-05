# Bug Report - Rama: dev2

> Resumen: Columna Volumenes muestra "-" aunque Docker Desktop muestra volumenes creados

## 🐛 Bug detectado durante testing

**Fase de testing:** Test 3.1 - Service Admin  
**Fecha:** 2025-11-29  
**Reportado por:** Usuario (testing manual)

---

## 📋 Descripcion del problema

La columna **"Volúmenes"** en el admin de servicios muestra **"-"** (guion), aunque **Docker Desktop muestra volúmenes creados** para esos servicios.

### Evidencia:

**Docker Desktop muestra:**

- ✅ `svc_1_prueba-nginx_data` (creado hace 2 horas)
- ✅ `svc_6_prueba-dockerfile_data` (creado hace 3 minutos)

**Admin de Django muestra:**

- ❌ Columna "VOLÚMENES": `-` (para ambos servicios)

### Comportamiento esperado:

- Servicio con volumen → "📁 1 volumen" (o cantidad correspondiente)
- Servicio sin volumen → "-"

---

## 🔍 Causa raiz

En `containers/admin.py`, metodo `get_volume_info` (lineas 294-305):

```python
def get_volume_info(self, obj):
    """Muestra información resumida de volúmenes"""
    if obj.volumes:  # <-- PROBLEMA: Verifica campo 'volumes'
        try:
            import json
            volumes = json.loads(obj.volumes) if isinstance(obj.volumes, str) else obj.volumes
            count = len(volumes) if isinstance(volumes, dict) else 0
            return f"📁 {count} volumen{'es' if count != 1 else ''}"
        except:
            return "📁 Configurado"
    return "-"
```

**Problema:** El metodo verifica el campo `obj.volumes` (volumenes **adicionales** configurados por el usuario), pero **no el volumen automatico** `obj.volume_name`.

### Campos del modelo Service:

```python
class Service(models.Model):
    volume_name = models.CharField(...)  # Volumen automatico: svc_{id}_{slug}_data
    volumes = models.JSONField(...)      # Volumenes adicionales del usuario (opcional)
```

**Flujo actual:**

1. Sistema crea volumen automatico → `volume_name = "svc_1_prueba-nginx_data"`
2. Campo `volumes` queda vacio (usuario no agrego volumenes adicionales)
3. `get_volume_info` verifica `obj.volumes` → vacio → devuelve "-"
4. **Resultado:** No se cuenta el volumen automatico

---

## 💡 Solucion propuesta

Modificar `get_volume_info` para contar **ambos tipos de volumenes**:

```python
def get_volume_info(self, obj):
    """Muestra información resumida de volúmenes"""
    count = 0

    # Contar volumen automatico
    if obj.volume_name:
        count += 1

    # Contar volumenes adicionales del usuario
    if obj.volumes:
        try:
            import json
            volumes = json.loads(obj.volumes) if isinstance(obj.volumes, str) else obj.volumes
            if isinstance(volumes, dict):
                count += len(volumes)
        except:
            pass

    if count == 0:
        return "-"

    return f"📁 {count} volumen{'es' if count != 1 else ''}"
```

**Mejora adicional:** Mostrar detalles en tooltip:

```python
from django.utils.html import format_html

def get_volume_info(self, obj):
    """Muestra información resumida de volúmenes"""
    count = 0
    volume_list = []

    # Volumen automatico
    if obj.volume_name:
        count += 1
        volume_list.append(f"{obj.volume_name} (automático)")

    # Volumenes adicionales
    if obj.volumes:
        try:
            import json
            volumes = json.loads(obj.volumes) if isinstance(obj.volumes, str) else obj.volumes
            if isinstance(volumes, dict):
                for host_path, container_path in volumes.items():
                    count += 1
                    volume_list.append(f"{host_path} → {container_path}")
        except:
            pass

    if count == 0:
        return "-"

    tooltip = "\\n".join(volume_list)
    return format_html(
        '<span title="{}">{} {}</span>',
        tooltip,
        "📁",
        f"{count} volumen{'es' if count != 1 else ''}"
    )
```

---

## 📊 Impacto

### Usuarios afectados:

- ✅ Profesores revisando servicios de alumnos
- ✅ Administradores monitoreando uso de disco

### Severidad:

- **Media:** Informacion incorrecta puede confundir
- **Funcionalidad:** Los volumenes existen y funcionan, solo no se muestran

### Confusion actual:

Usuario ve:

- Admin: "Volúmenes: -"
- Docker Desktop: Volumen existe

**Pregunta:** ¿El volumen se creo o no? ¿Hay un bug?

---

## 🔧 Archivos afectados

- `containers/admin.py` (metodo `get_volume_info`, lineas 294-305)

---

## 📌 Notas adicionales

### Verificacion en Docker Desktop:

Los volumenes mostrados en Docker Desktop confirman que:

1. ✅ Sistema crea volumenes correctamente
2. ✅ Volumenes tienen el formato esperado: `svc_{id}_{slug}_data`
3. ❌ Admin no los muestra porque solo verifica `obj.volumes` (campo adicional)

### Tipos de volumenes:

1. **Volumen automatico** (`volume_name`):
   - Creado automaticamente por el sistema
   - Formato: `svc_{id}_{slug}_data`
   - Montado en `/data` del contenedor
   - **Siempre existe** (a menos que se elimine el servicio)

2. **Volumenes adicionales** (`volumes`):
   - Configurados manualmente por el usuario
   - JSON: `{"/host/path": "/container/path"}`
   - **Opcional**

---

**Estado:** COMPLETADO  
**Prioridad:** Media  
**Relacionado con:** Test 3.1 - Service Admin
