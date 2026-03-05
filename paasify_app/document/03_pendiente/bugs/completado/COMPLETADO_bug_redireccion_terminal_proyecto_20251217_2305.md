# Bug: Redirección Incorrecta al Volver de Terminal en Vista de Proyecto

**Fecha:** 17/12/2025 23:05  
**Tipo:** Bug de Navegación  
**Prioridad:** Media  
**Estado:** COMPLETADO  
**Versión afectada:** v5.0

---

## 📋 Descripción

Al abrir la terminal de un contenedor desde la vista de un proyecto específico (`/paasify/containers/subjects/{id}/`) y luego volver atrás, el usuario es redirigido incorrectamente a la vista general (`/paasify/containers/`) en lugar de volver a la vista del proyecto.

## 🔍 Reproducción

### Pasos:

1. Navegar a un proyecto específico:

   ```
   http://localhost:8000/paasify/containers/subjects/1/
   ```

2. Ver un servicio Docker Compose con múltiples contenedores (ej: `prueba-test4-docker-compose`)

3. Hacer clic en el botón **"Terminal"** de cualquier contenedor (ej: `web`, `redis`, `cache`, etc.)

4. Se abre la terminal web correctamente

5. Hacer clic en el botón **"Volver"** o usar la navegación del navegador

### Resultado Actual (Incorrecto):

```
Usuario es redirigido a: /paasify/containers/
```

### Resultado Esperado (Correcto):

```
Usuario debería volver a: /paasify/containers/subjects/1/
```

## 🐛 Causa Probable

La vista de terminal (`terminal_view`) probablemente no está guardando o pasando el contexto de origen (subject_id) para saber a dónde volver.

### Código Actual (Probable):

**Archivo:** `containers/views.py`

```python
@login_required
def terminal_view(request, pk):
    """Muestra la terminal web para el servicio"""
    service = get_object_or_404(Service, pk=pk, owner=request.user)

    # ... código de terminal ...

    return render(request, 'containers/terminal.html', {
        'service': service,
        # ← Falta: 'back_url' o 'subject_id'
    })
```

**Archivo:** `templates/containers/terminal.html`

```html
<!-- Botón volver probablemente tiene URL hardcodeada -->
<a href="{% url 'containers:student_panel' %}" class="btn btn-secondary">
  ← Volver
</a>
```

## ✅ Solución Propuesta

### Opción 1: Usar Referer Header (Más Simple)

**Archivo:** `containers/views.py`

```python
@login_required
def terminal_view(request, pk):
    """Muestra la terminal web para el servicio"""
    service = get_object_or_404(Service, pk=pk, owner=request.user)

    # Obtener URL de origen
    back_url = request.META.get('HTTP_REFERER', reverse('containers:student_panel'))

    # Si no hay referer, intentar detectar si viene de un subject
    if service.subject:
        # Preferir volver al subject si existe
        back_url = reverse('containers:student_services_in_subject',
                          kwargs={'subject_id': service.subject.id})

    return render(request, 'containers/terminal.html', {
        'service': service,
        'back_url': back_url,  # ← Añadir
    })
```

**Archivo:** `templates/containers/terminal.html`

```html
<!-- Usar URL dinámica -->
<a href="{{ back_url }}" class="btn btn-secondary"> ← Volver </a>
```

### Opción 2: Pasar subject_id como Query Parameter (Más Robusto)

**Archivo:** `templates/containers/_partials/services/_compose.html` (o donde esté el botón Terminal)\*\*

```html
<!-- Añadir subject_id al enlace de terminal -->
<a
  href="{% url 'containers:terminal' service.id %}{% if current_subject %}?subject={{ current_subject.id }}{% endif %}"
  class="btn btn-sm btn-outline-secondary"
>
  Terminal
</a>
```

**Archivo:** `containers/views.py`

```python
@login_required
def terminal_view(request, pk):
    """Muestra la terminal web para el servicio"""
    service = get_object_or_404(Service, pk=pk, owner=request.user)

    # Obtener subject_id del query parameter
    subject_id = request.GET.get('subject')

    # Determinar URL de retorno
    if subject_id:
        back_url = reverse('containers:student_services_in_subject',
                          kwargs={'subject_id': subject_id})
    else:
        back_url = reverse('containers:student_panel')

    return render(request, 'containers/terminal.html', {
        'service': service,
        'back_url': back_url,
    })
```

### Opción 3: Usar Session Storage (JavaScript)

**Archivo:** `templates/containers/terminal.html`

```html
<script>
  // Al cargar la terminal, guardar la URL anterior
  if (document.referrer) {
    sessionStorage.setItem("terminal_back_url", document.referrer);
  }

  // Botón volver
  document
    .getElementById("back-button")
    .addEventListener("click", function (e) {
      e.preventDefault();
      const backUrl =
        sessionStorage.getItem("terminal_back_url") ||
        '{% url "containers:student_panel" %}';
      window.location.href = backUrl;
    });
</script>

<button id="back-button" class="btn btn-secondary">← Volver</button>
```

## 🎯 Recomendación

**Opción 2** (Query Parameter) es la más robusta porque:

- ✅ No depende de headers que pueden ser bloqueados
- ✅ Funciona con navegación del navegador (botón atrás)
- ✅ Es explícita y fácil de debuggear
- ✅ Funciona con recarga de página

## 📝 Archivos a Modificar

1. **`containers/views.py`**:
   - Función `terminal_view()`
   - Añadir lógica de `back_url`

2. **`templates/containers/terminal.html`**:
   - Botón "Volver"
   - Usar `{{ back_url }}`

3. **`templates/containers/_partials/services/_compose.html`**:
   - Botón "Terminal"
   - Añadir `?subject={{ current_subject.id }}`

4. **`templates/containers/_partials/services/_simple.html`**:
   - Botón "Terminal"
   - Añadir `?subject={{ current_subject.id }}`

## 🧪 Testing

### Caso 1: Desde Vista General

```
1. Ir a /paasify/containers/
2. Click en Terminal de un servicio
3. Click en Volver
✅ Debe volver a /paasify/containers/
```

### Caso 2: Desde Vista de Proyecto

```
1. Ir a /paasify/containers/subjects/1/
2. Click en Terminal de un servicio
3. Click en Volver
✅ Debe volver a /paasify/containers/subjects/1/
```

### Caso 3: URL Directa

```
1. Acceder directamente a /paasify/containers/terminal/42/
2. Click en Volver
✅ Debe ir a vista general (fallback)
```

## 🔗 Contexto Adicional

Este bug afecta la experiencia de usuario (UX) porque:

- ❌ Pierde el contexto de navegación
- ❌ El usuario debe volver manualmente al proyecto
- ❌ Rompe el flujo de trabajo esperado

**Impacto:** Media prioridad (no rompe funcionalidad, pero molesta)

---

**Reportado por:** Usuario  
**Asignado a:** Pendiente  
**Etiquetas:** `bug`, `navegación`, `ux`, `terminal`, `docker-compose`
