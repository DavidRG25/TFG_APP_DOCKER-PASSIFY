# Bug Report / Feature Request - Rama: dev2
> Resumen: No se puede cambiar puerto interno sin eliminar el contenedor

## 🐛 Problema detectado durante testing

**Fase de testing:** Test 3.x - Service Admin  
**Fecha:** 2025-11-29  
**Reportado por:** Usuario (testing manual)  
**Tipo:** UX Issue / Missing Feature

---

## 📋 Descripcion del problema

Si un usuario **se equivoca al configurar el puerto interno** de un servicio, no puede corregirlo sin **eliminar completamente el contenedor** y crear uno nuevo.

### Escenario:

1. Usuario crea servicio con puerto interno **8080**
2. Inicia el servicio
3. Se da cuenta que deberia ser **3000** (ej: app Node.js)
4. **No hay forma de cambiar el puerto interno**
5. Debe:
   - Eliminar el servicio completo
   - Perder configuracion, volumenes, logs
   - Crear servicio nuevo desde cero

### Comportamiento esperado:

Deberia existir una opcion para **cambiar el puerto interno** que:
1. Detenga el contenedor
2. Actualice la configuracion de puertos
3. Reinicie el contenedor con el nuevo puerto

---

## 🔍 Analisis tecnico

### Estado actual:

En el panel del alumno, el campo "Puerto interno" es **readonly** una vez que el servicio esta creado.

**Codigo relevante** (probablemente en `paasify/templates/paasify/services.html`):

```html
<!-- Puerto interno (readonly despues de crear) -->
<input type="number" value="{{ service.internal_port }}" readonly>
```

### Limitacion tecnica:

Docker **no permite cambiar el mapeo de puertos** de un contenedor en ejecucion. Para cambiar puertos se debe:

1. Detener el contenedor
2. Eliminar el contenedor
3. Crear nuevo contenedor con nuevos puertos
4. **Mantener el volumen** (para no perder datos)

---

## 💡 Solucion propuesta

### Opcion A: Boton "Cambiar puerto interno" (RECOMENDADA)

Agregar funcionalidad para cambiar puerto interno **sin perder datos**:

**UI:**
```
[Puerto interno: 8080] [Cambiar puerto ⚙️]
```

**Flujo:**
1. Usuario hace click en "Cambiar puerto"
2. Modal/formulario para ingresar nuevo puerto
3. Sistema:
   - Detiene contenedor
   - Elimina contenedor (pero **mantiene volumen**)
   - Actualiza `service.internal_port`
   - Recrea contenedor con nuevo puerto
   - Inicia contenedor

**Ventajas:**
- ✅ No se pierden datos (volumen se mantiene)
- ✅ UX mejorada
- ✅ No requiere eliminar servicio completo

**Implementacion sugerida:**

```python
# En containers/services.py
def change_internal_port(service: Service, new_port: int):
    """
    Cambia el puerto interno de un servicio sin perder datos.
    """
    docker_client = get_docker_client()
    if docker_client is None:
        raise RuntimeError("Docker no esta disponible")
    
    # Validar puerto
    if not (1 <= new_port <= 65535):
        raise ValueError("Puerto invalido")
    
    # Guardar volumen actual (para no perderlo)
    old_volume = service.volume_name
    
    # Detener y eliminar contenedor (pero NO el volumen)
    if service.container_id:
        try:
            container = docker_client.containers.get(service.container_id)
            container.remove(force=True)
        except NotFound:
            pass
    
    # Actualizar puerto interno
    service.internal_port = new_port
    service.container_id = None
    service.save()
    
    # Reiniciar contenedor con nuevo puerto
    run_container(service, force_restart=True)
```

**Vista (en `paasify/views.py`):**

```python
@login_required
def change_service_port(request, service_id):
    service = get_object_or_404(Service, pk=service_id, owner=request.user)
    
    if request.method == 'POST':
        new_port = int(request.POST.get('new_port'))
        try:
            change_internal_port(service, new_port)
            messages.success(request, f"Puerto interno cambiado a {new_port}")
        except Exception as e:
            messages.error(request, f"Error: {e}")
    
    return redirect('services')
```

### Opcion B: Permitir editar siempre (MAS SIMPLE)

Hacer que el campo "Puerto interno" sea **siempre editable**, y al guardar:
- Si el contenedor esta corriendo → Reiniciar automaticamente
- Si esta detenido → Solo actualizar configuracion

**Ventajas:**
- ✅ Mas simple de implementar
- ✅ UX intuitiva

**Desventajas:**
- ⚠️ Puede confundir (cambiar puerto reinicia el servicio)
- ⚠️ Requiere mensaje de advertencia claro

### Opcion C: Editar solo si esta detenido

Permitir cambiar puerto **solo cuando el servicio esta detenido**:

```html
{% if service.status == 'stopped' %}
    <input type="number" name="internal_port" value="{{ service.internal_port }}">
{% else %}
    <input type="number" value="{{ service.internal_port }}" readonly>
    <small>Detén el servicio para cambiar el puerto</small>
{% endif %}
```

**Ventajas:**
- ✅ Evita confusion
- ✅ Usuario tiene control

**Desventajas:**
- ⚠️ Requiere detener manualmente primero

---

## 🎯 Recomendacion

**Implementar Opcion A (Boton "Cambiar puerto"):**

1. Agregar boton "Cambiar puerto interno" en el panel del servicio
2. Modal para ingresar nuevo puerto
3. Funcion `change_internal_port()` que:
   - Detiene contenedor
   - Elimina contenedor (mantiene volumen)
   - Actualiza puerto
   - Reinicia servicio

**Prioridad:** Media (mejora de UX, no critico)

---

## 📝 Pasos para reproducir

1. Login como alumno
2. Crear servicio (ej: nginx)
3. Configurar puerto interno: 8080
4. Iniciar servicio
5. Darse cuenta que deberia ser 80
6. Intentar cambiar puerto interno
7. **Resultado:** Campo readonly, no se puede cambiar

---

## 📊 Impacto

### Usuarios afectados:
- ✅ Alumnos que se equivocan al configurar puertos
- ✅ Alumnos que prueban diferentes configuraciones

### Severidad:
- **Media:** Workaround existe (eliminar y recrear), pero es molesto y se pierden logs

### Workaround actual:
1. Eliminar servicio completo
2. Crear nuevo servicio
3. Configurar puerto correcto
4. **Problema:** Se pierden logs, historial, configuracion

---

## 🔧 Archivos afectados

- `containers/services.py` (nueva funcion `change_internal_port`)
- `paasify/views.py` (nueva vista `change_service_port`)
- `paasify/templates/paasify/services.html` (boton UI)
- `paasify/urls.py` (nueva ruta)

---

## 📌 Notas adicionales

### Consideraciones:

1. **Validacion de puerto:**
   - Rango valido: 1-65535
   - Evitar puertos del sistema (1-1024) si no es root

2. **Mensaje al usuario:**
   ```
   ⚠️ Cambiar el puerto interno reiniciara el contenedor.
   Los datos en volumenes se mantendran.
   ¿Continuar?
   ```

3. **Logs:**
   - Registrar cambio de puerto en logs del servicio
   - Ej: "Puerto interno cambiado de 8080 a 3000"

---

**Estado:** 🟡 Feature Request / UX Improvement  
**Asignado a:** Por definir  
**Relacionado con:** Plan de Testing Admin - Fase 3
