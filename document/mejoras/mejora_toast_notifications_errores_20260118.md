# Feature: Toast Notifications para Errores de Validación

**Fecha:** 18/01/2026  
**Prioridad:** BAJA  
**Tipo:** Mejora UX  
**Estado:** PROPUESTA  
**Esfuerzo estimado:** 15-20 minutos

---

## 🎯 OBJETIVO

Reemplazar los modales de error (SweetAlert2) por **Toast Notifications** modernas que aparecen en la esquina superior derecha, mejorando la experiencia de usuario al no bloquear la pantalla.

---

## 📸 SITUACIÓN ACTUAL

### **Problema:**

Cuando hay un error de validación (ej: bind mounts no permitidos), se muestra un **modal oscuro** que:

- ❌ Bloquea toda la pantalla
- ❌ Requiere hacer click en "Aceptar" para cerrar
- ❌ Interrumpe el flujo del usuario
- ❌ Diseño pesado y anticuado

**Ejemplo actual:**

```javascript
Swal.fire({
  icon: "error",
  title: "Error de Validación",
  text: "compose: SEGURIDAD: Bind mounts no permitidos...",
  confirmButtonText: "Aceptar",
});
```

---

## ✨ SOLUCIÓN PROPUESTA

### **Toast Notification:**

- ✅ Aparece en esquina superior derecha
- ✅ No bloquea la pantalla
- ✅ Desaparece automáticamente (5 segundos)
- ✅ Se puede cerrar manualmente (X)
- ✅ Diseño moderno y limpio
- ✅ Permite múltiples notificaciones apiladas

---

## 🎨 DISEÑO PROPUESTO

### **Toast de Error:**

```
┌─────────────────────────────────────────┐
│ ❌ Error de Validación              [X] │
├─────────────────────────────────────────┤
│ SEGURIDAD: Bind mounts no permitidos    │
│ Volumen rechazado: /data:/app/data      │
│                                          │
│ ▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │ (barra de progreso)
└─────────────────────────────────────────┘
```

### **Características:**

- **Color:** Rojo suave (#f44336) con fondo blanco
- **Posición:** Top-right
- **Duración:** 5 segundos
- **Animación:** Slide-in desde la derecha
- **Icono:** ❌ (error), ✅ (éxito), ⚠️ (warning), ℹ️ (info)
- **Barra de progreso:** Indica tiempo restante

---

## 🔧 IMPLEMENTACIÓN

### **Opción 1: Usar Toastify.js (Recomendada)**

**Ventajas:**

- ✅ Librería ligera (3KB)
- ✅ Sin dependencias
- ✅ Muy personalizable
- ✅ Soporte para múltiples toasts

**Instalación:**

```html
<!-- En base.html o new_service.html -->
<link
  rel="stylesheet"
  href="https://cdn.jsdelivr.net/npm/toastify-js/src/toastify.min.css"
/>
<script src="https://cdn.jsdelivr.net/npm/toastify-js"></script>
```

**Uso:**

```javascript
function showToast(message, type = "error") {
  const colors = {
    error: "#f44336",
    success: "#4caf50",
    warning: "#ff9800",
    info: "#2196f3",
  };

  Toastify({
    text: message,
    duration: 5000,
    gravity: "top",
    position: "right",
    backgroundColor: colors[type],
    stopOnFocus: true,
    close: true,
    onClick: function () {}, // Callback
  }).showToast();
}

// Uso:
showToast("SEGURIDAD: Bind mounts no permitidos", "error");
```

### **Opción 2: Bootstrap Toast (Ya incluido)**

**Ventajas:**

- ✅ Ya está en el proyecto (Bootstrap 5)
- ✅ Sin dependencias adicionales
- ✅ Consistente con el diseño actual

**Implementación:**

```html
<!-- Contenedor de toasts (añadir a base.html) -->
<div
  class="toast-container position-fixed top-0 end-0 p-3"
  style="z-index: 9999"
>
  <div
    id="toast-template"
    class="toast"
    role="alert"
    aria-live="assertive"
    aria-atomic="true"
  >
    <div class="toast-header">
      <i class="fas fa-exclamation-circle text-danger me-2"></i>
      <strong class="me-auto">Error de Validación</strong>
      <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
    </div>
    <div class="toast-body"></div>
  </div>
</div>
```

```javascript
function showToast(message, type = "error") {
  const icons = {
    error: "fa-exclamation-circle text-danger",
    success: "fa-check-circle text-success",
    warning: "fa-exclamation-triangle text-warning",
    info: "fa-info-circle text-info",
  };

  const titles = {
    error: "Error de Validación",
    success: "Éxito",
    warning: "Advertencia",
    info: "Información",
  };

  const toastEl = document.getElementById("toast-template").cloneNode(true);
  toastEl.querySelector(".fas").className = `fas ${icons[type]} me-2`;
  toastEl.querySelector("strong").textContent = titles[type];
  toastEl.querySelector(".toast-body").textContent = message;

  document.querySelector(".toast-container").appendChild(toastEl);

  const toast = new bootstrap.Toast(toastEl, {
    autohide: true,
    delay: 5000,
  });

  toast.show();

  // Eliminar del DOM después de cerrar
  toastEl.addEventListener("hidden.bs.toast", () => {
    toastEl.remove();
  });
}
```

---

## 📝 ARCHIVOS A MODIFICAR

### **1. templates/base.html**

Añadir contenedor de toasts:

```html
<!-- Antes de </body> -->
<div
  class="toast-container position-fixed top-0 end-0 p-3"
  style="z-index: 9999"
></div>
```

### **2. static/assets/js/toast.js (nuevo)**

Crear archivo con función `showToast()`:

```javascript
/**
 * Muestra una notificación toast
 * @param {string} message - Mensaje a mostrar
 * @param {string} type - Tipo: error, success, warning, info
 * @param {number} duration - Duración en ms (default: 5000)
 */
function showToast(message, type = "error", duration = 5000) {
  // Implementación aquí
}
```

### **3. templates/containers/new_service.html**

Reemplazar `Swal.fire()` por `showToast()`:

**Antes:**

```javascript
Swal.fire({
  icon: "error",
  title: "Error de Validación",
  text: errorMessage,
  confirmButtonText: "Aceptar",
});
```

**Después:**

```javascript
showToast(errorMessage, "error");
```

---

## 🧪 TESTING

### **Casos de prueba:**

1. **Error de validación (bind mount)**
   - Crear servicio con bind mount
   - Verificar toast rojo aparece top-right
   - Verificar desaparece en 5 segundos
   - Verificar se puede cerrar con X

2. **Múltiples errores**
   - Generar 3 errores seguidos
   - Verificar toasts se apilan correctamente
   - Verificar no se solapan

3. **Éxito**
   - Crear servicio correctamente
   - Verificar toast verde de éxito

4. **Responsive**
   - Probar en móvil
   - Verificar toast se adapta al ancho

---

## 📊 BENEFICIOS

### **UX:**

- ✅ Menos intrusivo
- ✅ No interrumpe el flujo
- ✅ Más moderno y profesional
- ✅ Mejor para múltiples errores

### **Técnico:**

- ✅ Código más limpio
- ✅ Reutilizable en toda la app
- ✅ Fácil de mantener
- ✅ Consistente con diseño moderno

---

## 🎯 PRIORIDAD Y ESFUERZO

**Prioridad:** BAJA (mejora cosmética)  
**Esfuerzo:** 15-20 minutos  
**Impacto:** MEDIO (mejora UX significativa)

**Recomendación:** Implementar después de completar testing de seguridad crítica.

---

## 📚 REFERENCIAS

- [Toastify.js](https://apvarun.github.io/toastify-js/)
- [Bootstrap 5 Toasts](https://getbootstrap.com/docs/5.3/components/toasts/)
- [Material Design Snackbars](https://material.io/components/snackbars)

---

## 🔄 ALTERNATIVAS CONSIDERADAS

1. **Alert inline** - Descartada (menos visible)
2. **Mejorar modal actual** - Descartada (sigue siendo intrusivo)
3. **Notificaciones push** - Descartada (overkill para esta app)

---

**Creado por:** Testing de Seguridad Crítica  
**Fecha:** 2026-01-18  
**Próximo paso:** Implementar después de completar testing
