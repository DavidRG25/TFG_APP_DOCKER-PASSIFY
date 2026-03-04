# Bug: Obligatoriedad de adjuntar ZIP al subir docker-compose

**Fecha**: 2026-03-03 (Reunión con el profesor)
**Prioridad**: MEDIA  
**Estado**: PENDIENTE

---

## 🐛 DESCRIPCIÓN DEL BUG

**Problema**: Al intentar desplegar un servicio en modo "Configuración personalizada" usando únicamente un archivo `docker-compose.yml`, el formulario del frontend bloquea el envío y exige subir también un archivo ZIP en el campo de "Código fuente", a pesar de que para un compose básico no es necesario a nivel arquitectónico.

**Causa**: Existe una validación residual estricta en el HTML (un atributo `required="true"` que inyecta el Javascript activado mediante `#block-code input[name="code"]`) que asume que la subida de un archivo ZIP es obligatoria tanto para un `Dockerfile` suelto como para modificar un stack `docker-compose.yml`.

---

## 🔍 ANÁLISIS

**Impacto**:

- Genera confusión en el usuario (como se reportó en la reunión del 03-03-2026).
- Obliga a crear un archivo .zip vacío o redundante simplemente para sortear la validación del formulario del frontend y lograr desplegar un `docker-compose`.

**Comportamiento actual**:

- El script de frontend (`_scripts.html` en la función `applyMode`) activa `code.required = true` globalmente en modo `custom`.
- El navegador impide enviar el formulario si no hay un zip.

**Comportamiento esperado**:

- Si se selecciona la pestaña de "Docker Compose", el ZIP debe ser opcional (`required = false`).
- Solo si se selecciona "Dockerfile Único", el ZIP debe ser obligatorio (`required = true`).

---

## 💡 SOLUCIÓN PROPUESTA

Modificar la lógica en `templates/containers/_partials/panels/_scripts.html` dentro de la función `applyMode()`:

```javascript
// ...
if (mode === "custom") {
  if (customSubtypeBlock) customSubtypeBlock.style.display = "block";
  if (codeBlock) codeBlock.style.display = "block";

  // Deshabilitar selectores de imagen no usados en modo custom
  if (imgSel) {
    imgSel.disabled = true;
    imgSel.required = false;
  }
  if (dockerhubInput) {
    dockerhubInput.disabled = true;
    dockerhubInput.required = false;
  }

  if (submode === "dockerfile") {
    if (dockerfileBlock) dockerfileBlock.style.display = "block";
    if (dockerfile) dockerfile.disabled = false;
    if (compose) compose.disabled = true;
    if (code) {
      code.required = true;
    } // <--- Hacer obligatorio
  } else {
    // submode === "compose"
    if (composeBlock) composeBlock.style.display = "block";
    if (compose) compose.disabled = false;
    if (dockerfile) dockerfile.disabled = true;
    if (code) {
      code.required = false;
    } // <--- Hacer opcional
  }
}
// ...
```

Cambiar también los textos/labels en `new_service.html`, `_modals.html` y `student_panel.html` indicando:

> **Obligatorio** si usas Dockerfile. **Opcional** si usas docker-compose.

---

## 🎯 IMPACTO

**Severidad**: MEDIA (Bloqueante para el flujo esperado de Compose, fácilmente bypasseable con zip falso)  
**Funcionalidad afectada**: Interfaz de creación de servicios  
**Usuarios afectados**: Todos los usuarios que intentan desplegar un `docker-compose.yml`

---

## 🧪 TESTING (Una vez resuelto)

1. Abrir modal o página de "Nuevo Servicio".
2. Seleccionar "Configuración personalizada" y luego "Docker Compose".
3. Subir un archivo `.yml` estándar.
4. Presionar "Crear servicio" sin aportar ningún archivo ZIP.
5. **Verificar**: El formulario se envía correctamente sin que el navegador mande avisos.

---

**Última actualización**: 2026-03-03 (Anotado)  
**Estado**: Documentado, pendiente de implementación en el próximo fix global.
