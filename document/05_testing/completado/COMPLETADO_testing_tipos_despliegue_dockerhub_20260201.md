# Plan de Testing - Tipos de Despliegue y Verificación DockerHub

**Fecha Inicio**: 02/02/2026  
**Fecha Finalización**: 03/02/2026  
**Tipo**: Testing de UI - Refactorización Tipos de Despliegue  
**Estado**: ✅ COMPLETADO

---

## 📋 **ALCANCE DE ESTE DOCUMENTO**

Este documento cubre el testing de las mejoras implementadas en el sistema de creación de servicios:

- ✅ Refactorización de tipos de despliegue (3 modos independientes)
- ✅ Nuevo tipo: "Imagen desde DockerHub"
- ✅ Verificación de imágenes con detección automática de puertos
- ✅ Lógica de exclusión entre tipos de despliegue
- ✅ Mejoras de UI/UX en formulario de nuevo servicio

**Implementación**: Ver `implementacion_mejoras_ui_configuracion_personalizada_20260201.md`

---

## 🧪 TESTING TIPOS DE DESPLIEGUE

### **Test 1.1: Modo "Imagen por Defecto"**

**Objetivo**: Verificar que el modo "Imagen por defecto" muestra solo los campos relevantes

**Pasos**:

1. Acceder a `/paasify/containers/new/`
2. Seleccionar radio button "Imagen por defecto"
3. Observar qué campos se muestran/ocultan

**Verificar**:

- [SI] Selector de imagen del catálogo VISIBLE
- [SI] Campo DockerHub OCULTO
- [SI] Campos Custom (Dockerfile/Compose/Código) OCULTOS
- [SI] Campo puerto personalizado VISIBLE

**Resultado Esperado**: ✅ Solo se muestran campos relevantes para modo default

---

### **Test 1.2: Modo "Imagen desde DockerHub"**

**Objetivo**: Verificar que el modo DockerHub muestra solo los campos relevantes

**Pasos**:

1. Acceder a `/paasify/containers/new/`
2. Seleccionar radio button "Imagen desde DockerHub"
3. Observar qué campos se muestran/ocultan

**Verificar**:

- [SI] Campo DockerHub VISIBLE con botones "Verificar" y "Limpiar"
- [SI] Selector de catálogo OCULTO
- [SI] Campos Custom (Dockerfile/Compose/Código) OCULTOS
- [SI] Warning sobre imágenes privadas VISIBLE
- [SI] Campo puerto personalizado VISIBLE

**Resultado Esperado**: ✅ Solo se muestran campos relevantes para modo DockerHub

---

### **Test 1.3: Modo "Configuración Personalizada"**

**Objetivo**: Verificar que el modo Custom muestra solo los campos relevantes

**Pasos**:

1. Acceder a `/paasify/containers/new/`
2. Seleccionar radio button "Configuración personalizada"
3. Observar qué campos se muestran/ocultan

**Verificar**:

- [SI] Campos Dockerfile, Compose y Código VISIBLES
- [SI] Selector de catálogo OCULTO
- [SI] Campo DockerHub OCULTO
- [SI] Campo puerto personalizado VISIBLE

**Resultado Esperado**: ✅ Solo se muestran campos relevantes para modo custom

---

### **Test 1.4: Cambio Entre Modos**

**Objetivo**: Verificar que cambiar entre modos actualiza la UI correctamente

**Pasos**:

1. Seleccionar "Imagen desde DockerHub"
2. Escribir `nginx:latest` en el campo
3. Cambiar a "Imagen por defecto"
4. Volver a "Imagen desde DockerHub"

**Verificar**:

- [SI] Al cambiar de modo, los campos se ocultan/muestran correctamente
- [SI] No queda información residual al volver
- [SI] Transiciones visuales suaves

**Resultado Esperado**: ✅ Cambios entre modos funcionan correctamente

---

## 🧪 TESTING VERIFICACIÓN DOCKERHUB

### **Test 2.1: Verificar Imagen Oficial Existente**

**Objetivo**: Verificar que la verificación funciona con imágenes oficiales

**Pasos**:

1. Seleccionar "Imagen desde DockerHub"
2. Escribir: `nginx:latest`
3. Click en botón "Verificar"
4. Esperar respuesta

**Verificar**:

- [SI] Mensaje de éxito: "✅ Imagen encontrada en DockerHub"
- [SI] Muestra nombre: `nginx:latest`
- [SI] Muestra última actualización
- [SI] Muestra tamaño en MB
- [SI] **Muestra puerto detectado: 80**
- [SI] Botón "Usar este puerto" VISIBLE

**Resultado Esperado**: ✅ Verificación exitosa con información completa

---

### **Test 2.2: Verificar Imagen de Usuario**

**Objetivo**: Verificar que funciona con imágenes de usuarios (no oficiales)

**Pasos**:

1. Seleccionar "Imagen desde DockerHub"
2. Escribir: `postgres:15`
3. Click en "Verificar"
4. Esperar respuesta

**Verificar**:

- [SI] Mensaje de éxito
- [SI] Muestra información de la imagen
- [SI] **Puerto detectado: 5432**
- [SI] Botón "Usar este puerto" funciona

**Resultado Esperado**: ✅ Verificación exitosa para imagen de usuario

---

### **Test 2.3: Imagen No Existente**

**Objetivo**: Verificar manejo de errores cuando la imagen no existe

**Pasos**:

1. Seleccionar "Imagen desde DockerHub"
2. Escribir: `imagen-que-no-existe-12345:latest`
3. Click en "Verificar"
4. Esperar respuesta

**Verificar**:

- [SI] Mensaje de error: "❌ Imagen no encontrada en DockerHub"
- [SI] Mensaje claro indicando verificar nombre y tag
- [SI] No se muestra información de puerto
- [SI] Botón vuelve a estado normal

**Resultado Esperado**: ✅ Error manejado correctamente

---

### **Test 2.4: Campo Vacío**

**Objetivo**: Verificar validación de campo vacío

**Pasos**:

1. Seleccionar "Imagen desde DockerHub"
2. Dejar campo vacío
3. Click en "Verificar"

**Verificar**:

- [SI] Mensaje de advertencia: "Por favor, ingresa un nombre de imagen"
- [SI] No se hace petición al servidor
- [SI] Feedback amarillo (warning)

**Resultado Esperado**: ✅ Validación de campo vacío funciona

---

### **Test 2.5: Detección de Puertos - Imágenes Comunes**

**Objetivo**: Verificar detección automática de puertos para imágenes conocidas

**Imágenes a probar**:

| Imagen           | Puerto Esperado |
| ---------------- | --------------- |
| `nginx:latest`   | 80              |
| `postgres:15`    | 5432            |
| `mysql:8`        | 3306            |
| `redis:alpine`   | 6379            |
| `mongodb:latest` | 27017           |

**Pasos**:

1. Para cada imagen, verificar en DockerHub
2. Comprobar que el puerto detectado es correcto

**Verificar**:

- [SI] nginx → 80
- [SI] postgres → 5432
- [SI] mysql → 3306
- [SI] redis → 6379
- [SI] mongodb → 27017

**Resultado Esperado**: ✅ Todos los puertos detectados correctamente

---

### **Test 2.6: Botón "Usar este puerto"**

**Objetivo**: Verificar que el botón auto-completa el puerto correctamente

**Pasos**:

1. Verificar imagen `nginx:latest` (puerto 80)
2. Click en botón "Usar este puerto"
3. Verificar campo "Puerto interno del contenedor"

**Verificar**:

- [SI] Campo "Puerto interno" se rellena con `80`
- [SI] Valor visible en el input
- [SI] Campo queda editable por si el usuario quiere cambiarlo

**Resultado Esperado**: ✅ Auto-completado de puerto funciona

---

### **Test 2.7: Botón "Limpiar"**

**Objetivo**: Verificar que el botón limpia el campo correctamente

**Pasos**:

1. Escribir `nginx:latest` en campo DockerHub
2. Click en "Verificar" (aparece feedback)
3. Click en "Limpiar"

**Verificar**:

- [SI] Campo de texto se vacía
- [SI] Feedback de verificación desaparece
- [SI] Campo queda limpio para nueva entrada

**Resultado Esperado**: ✅ Botón limpiar funciona correctamente

---

### **Test 2.8: Creación Completa de Servicio con DockerHub**

**Objetivo**: Verificar el flujo completo de creación de un servicio usando una imagen de DockerHub

**Pasos**:

1. Seleccionar modo "Imagen desde DockerHub"
2. Escribir `nginx:latest` en el campo
3. Click en "Verificar" (debe mostrar éxito y puerto 80)
4. Click en "Usar este puerto" (rellena puerto interno con 80)
5. Ingresar un puerto personalizado válido (ej: 49123)
6. Click en "Verificar disponibilidad" del puerto
7. Rellenar:
   - **Nombre**: `test-dockerhub-nginx`
   - **Asignatura**: Seleccionar una disponible
   - **Proyecto**: Seleccionar uno disponible
8. Click en "Crear Servicio"

**Verificar**:

- [SI] No aparece error de validación "Debe seleccionar una imagen del catálogo"
- [SI] El servicio se crea correctamente
- [SI] Se muestra mensaje de éxito
- [SI] Redirección al panel de servicios
- [SI] El servicio aparece en la lista con estado "running" o "creating"
- [SI] El contenedor Docker se crea con la imagen `nginx:latest`
- [SI] El puerto asignado es el 49123 (o el que hayas elegido)

**Datos de Prueba**:

```
Modo: DockerHub
Imagen: nginx:latest
Puerto interno: 80
Puerto personalizado: 49123
Nombre: test-dockerhub-nginx
```

**Resultado Esperado**: ✅ Servicio creado exitosamente desde imagen de DockerHub

---

## 🧪 TESTING EXCLUSIÓN DE CAMPOS (MODO CUSTOM)

### **Test 3.1: Exclusión Dockerfile vs Compose**

**Objetivo**: Verificar que Dockerfile y Compose son mutuamente exclusivos

**Pasos**:

1. Seleccionar "Configuración personalizada"
2. Subir un Dockerfile
3. Verificar que campo Compose desaparece
4. Limpiar Dockerfile (botón X)
5. Verificar que Compose reaparece

**Verificar**:

- [SI] Al subir Dockerfile → Compose se OCULTA
- [SI] Al limpiar Dockerfile → Compose REAPARECE
- [SI] Código fuente siempre visible (opcional)

**Resultado Esperado**: ✅ Exclusión Dockerfile/Compose funciona

---

### **Test 3.2: Exclusión Compose vs Dockerfile**

**Objetivo**: Verificar exclusión en sentido inverso

**Pasos**:

1. Seleccionar "Configuración personalizada"
2. Subir un docker-compose.yml
3. Verificar que campo Dockerfile desaparece
4. Limpiar Compose (botón X)
5. Verificar que Dockerfile reaparece

**Verificar**:

- [SI] Al subir Compose → Dockerfile se OCULTA
- [SI] Al limpiar Compose → Dockerfile REAPARECE
- [SI] Código fuente siempre visible (opcional)

**Resultado Esperado**: ✅ Exclusión Compose/Dockerfile funciona

---

## 🧪 TESTING UI/UX

### **Test 4.1: Diseño y Estilos**

**Objetivo**: Verificar que el diseño es consistente y profesional

**Aspectos a verificar**:

- [SI] Grid de 3 columnas para tipos de despliegue (col-md-4)
- [SI] Cards con bordes visibles en campos de archivo
- [SI] Botones con colores apropiados (azul Verificar, rojo Limpiar)
- [SI] Iconos visibles y bien espaciados
- [SI] Warnings con borde amarillo destacado
- [SI] Inputs con tamaño `form-control-lg`
- [SI] Fuente monospace en campo DockerHub

**Resultado Esperado**: ✅ Diseño limpio y profesional

---

### **Test 4.2: Responsive Design**

**Objetivo**: Verificar que la interfaz es responsive

**Pasos**:

1. Acceder a `/paasify/containers/new/`
2. Redimensionar ventana del navegador
3. Probar en diferentes tamaños

**Verificar**:

- [SI] Desktop (>1200px): Grid de 3 columnas
- [SI] Tablet (768-1200px): Grid adaptado
- [SI] Mobile (<768px): Columnas apiladas
- [SI] Todos los elementos visibles y accesibles

**Resultado Esperado**: ✅ Interfaz responsive funciona correctamente

---

### **Test 4.3: Errores de Red**

**Objetivo**: Verificar manejo de errores de conexión

**Pasos**:

1. Desconectar internet (o usar DevTools para simular offline)
2. Intentar verificar imagen
3. Observar mensaje de error

**Verificar**:

- [SI] Mensaje de error claro
- [SI] No se rompe la aplicación
- [SI] Botón vuelve a estado normal
- [SI] Usuario puede reintentar

**Resultado Esperado**: ✅ Errores de red manejados correctamente

---

## 📊 RESUMEN DE TESTING

### **Total de Tests**: 15

**Por Categoría**:

- Tipos de Despliegue: 4 tests
- Verificación DockerHub: 7 tests
- Exclusión de Campos: 2 tests
- UI/UX: 2 tests

**Estado**:

- Tests ejecutados: 0/15
- Tests pasados: 0/15
- Tests fallidos: 0/15

---

## 🎯 CRITERIOS DE ACEPTACIÓN

### **Funcionalidad**:

- [SI] Los 3 tipos de despliegue funcionan correctamente
- [SI] Verificación de DockerHub funciona
- [SI] Detección de puertos funciona
- [SI] Exclusión de campos funciona
- [SI] Botones "Verificar" y "Limpiar" funcionan

### **UI/UX**:

- [SI] Diseño limpio y profesional
- [SI] Responsive en diferentes tamaños
- [SI] Transiciones suaves
- [SI] Mensajes de error claros

### **Seguridad**:

- [SI] Solo imágenes públicas (warning visible)
- [SI] Validación de entrada
- [SI] Manejo de errores robusto

---

## 🔧 CONFIGURACIÓN DE TESTING

### **Entorno**:

- URL: `http://localhost:8000/paasify/containers/new/`
- Usuario de prueba: (especificar)
- Navegador: (especificar)

### **Datos de Prueba**:

**Imágenes válidas**:

- `nginx:latest`
- `postgres:15`
- `mysql:8`
- `redis:alpine`
- `mongodb:latest`

**Imágenes inválidas**:

- `imagen-inexistente:latest`

---

## 📝 ARCHIVOS MODIFICADOS

### **Backend**:

- `containers/views.py` - Nueva vista `verify_dockerhub_image`
- `containers/urls.py` - Nueva ruta `/verify-dockerhub/`

### **Frontend**:

- `templates/containers/new_service.html` - Refactorización tipos de despliegue
- `templates/containers/_partials/panels/_scripts.html` - Funciones JS actualizadas

---

## 🔗 REFERENCIAS

**Documentos relacionados**:

- Implementación: `implementacion_mejoras_ui_configuracion_personalizada_20260201.md`
- Mejora futura: `mejora_dockerhub_api_auth_global.md`
- Mejora futura: `mejora_dockerhub_imagenes_privadas.md`

**Código fuente**:

- Vista verificación: `containers/views.py` (función `verify_dockerhub_image`)
- JavaScript: `templates/containers/_partials/panels/_scripts.html`
- Template: `templates/containers/new_service.html`

---

## 📊 RESUMEN DE RESULTADOS

### **Estadísticas de Testing**:

- **Total de tests ejecutados**: 15
- **Tests pasados**: 15 ✅
- **Tests fallados**: 0 ❌
- **Tasa de éxito**: 100%

### **Bugs Encontrados y Solucionados**:

#### **Bug #1: Validación de Imagen DockerHub**

- **Descripción**: El sistema permitía crear servicios con imágenes de DockerHub que no existían, causando errores en tiempo de ejecución.
- **Solución**: Implementada validación obligatoria en el backend (`containers/serializers.py`) que verifica la existencia de la imagen en DockerHub antes de crear el servicio.
- **Estado**: ✅ SOLUCIONADO

#### **Bug #2: Conflicto de Nombres de Campos**

- **Descripción**: El campo de imagen del catálogo y el campo de DockerHub tenían el mismo nombre `image`, causando conflictos en el envío del formulario.
- **Solución**: Actualizada la lógica JavaScript para deshabilitar el campo no activo según el modo seleccionado, asegurando que solo se envíe un valor.
- **Estado**: ✅ SOLUCIONADO

### **Mejoras Implementadas Durante el Testing**:

1. **Nota Informativa de Puerto Interno**: Añadida nota que indica que el puerto por defecto es 80 si no se especifica ninguno.
2. **Mejora Visual de Radio Buttons**: Implementado diseño moderno con cards resaltadas en lugar de radio buttons tradicionales.
3. **Validación Automática de Imágenes**: Sistema ahora valida automáticamente que las imágenes de DockerHub existen antes de crear el servicio.

---

## 📝 ARCHIVOS MODIFICADOS

### **Backend**:

- `containers/serializers.py` - Validación de imágenes DockerHub
- `containers/views.py` - Vista `verify_dockerhub_image` y soporte para modo DockerHub
- `containers/urls.py` - Nueva ruta `/verify-dockerhub/`

### **Frontend**:

- `templates/containers/new_service.html` - Refactorización tipos de despliegue y mejoras visuales
- `templates/containers/_partials/panels/_scripts.html` - Funciones JS actualizadas para modo DockerHub

---

## 🔗 REFERENCIAS

**Documentos relacionados**:

- Implementación: `implementacion_mejoras_ui_configuracion_personalizada_20260201.md`
- Mejora futura: `mejora_dockerhub_api_auth_global.md`
- Mejora futura: `mejora_dockerhub_imagenes_privadas.md`

**Código fuente**:

- Vista verificación: `containers/views.py` (función `verify_dockerhub_image`)
- Serializer: `containers/serializers.py` (validación modo DockerHub)
- JavaScript: `templates/containers/_partials/panels/_scripts.html`
- Template: `templates/containers/new_service.html`

---

**Fecha de Inicio**: 2026-02-02  
**Fecha de Finalización**: 2026-02-03  
**Estado**: ✅ COMPLETADO  
**Resultado**: Todos los tests pasados exitosamente. Sistema listo para producción.
