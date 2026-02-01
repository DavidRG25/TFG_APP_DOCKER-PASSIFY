# 🧪 TESTING - Tipos de Despliegue y DockerHub

**Fecha:** 01/02/2026  
**Estado:** PENDIENTE  
**Prioridad:** ALTA

---

## 📋 OBJETIVO

Validar la implementación de las mejoras en el sistema de creación de servicios:

1. ✅ Nuevo tipo de despliegue: "Imagen desde DockerHub"
2. ✅ Verificación de imágenes de DockerHub con detección de puertos
3. ✅ Mejoras en campos de configuración personalizada
4. ✅ Lógica de exclusión entre tipos de despliegue

---

## 🎯 CASOS DE PRUEBA

### **CASO 1: Tipo de Despliegue - Imagen por Defecto**

**Objetivo:** Verificar que el modo "Imagen por defecto" funciona correctamente

**Pasos:**

1. Acceder a `/paasify/containers/new/`
2. Seleccionar "Imagen por defecto"
3. Verificar que se muestra el selector de imágenes del catálogo
4. Verificar que NO se muestran campos de DockerHub ni Custom

**Resultado Esperado:**

- ✅ Selector de imagen visible
- ✅ Campos DockerHub ocultos
- ✅ Campos Custom (Dockerfile/Compose/Código) ocultos
- ✅ Puertos personalizados visibles

**Estado:** [ ] PASS | [ ] FAIL | [ ] PENDIENTE

**Notas:**

```
Fecha de prueba: __/__/____
Resultado:


Errores encontrados:


```

---

### **CASO 2: Tipo de Despliegue - Imagen desde DockerHub**

**Objetivo:** Verificar que el modo "Imagen desde DockerHub" funciona correctamente

**Pasos:**

1. Acceder a `/paasify/containers/new/`
2. Seleccionar "Imagen desde DockerHub"
3. Verificar que se muestra el campo de imagen DockerHub
4. Verificar que NO se muestran selector de catálogo ni campos Custom

**Resultado Esperado:**

- ✅ Campo DockerHub visible con botones "Verificar" y "Limpiar"
- ✅ Selector de catálogo oculto
- ✅ Campos Custom (Dockerfile/Compose/Código) ocultos
- ✅ Warning sobre imágenes privadas visible
- ✅ Puertos personalizados visibles

**Estado:** [ ] PASS | [ ] FAIL | [ ] PENDIENTE

**Notas:**

```
Fecha de prueba: __/__/____
Resultado:


Errores encontrados:


```

---

### **CASO 3: Tipo de Despliegue - Configuración Personalizada**

**Objetivo:** Verificar que el modo "Configuración personalizada" funciona correctamente

**Pasos:**

1. Acceder a `/paasify/containers/new/`
2. Seleccionar "Configuración personalizada"
3. Verificar que se muestran campos Dockerfile, Compose y Código
4. Verificar que NO se muestran selector de catálogo ni campo DockerHub

**Resultado Esperado:**

- ✅ Campos Dockerfile, Compose y Código visibles
- ✅ Selector de catálogo oculto
- ✅ Campo DockerHub oculto
- ✅ Puertos personalizados visibles

**Estado:** [ ] PASS | [ ] FAIL | [ ] PENDIENTE

**Notas:**

```
Fecha de prueba: __/__/____
Resultado:


Errores encontrados:


```

---

### **CASO 4: Verificar Imagen de DockerHub - Imagen Oficial Existente**

**Objetivo:** Verificar que la verificación funciona con imágenes oficiales

**Pasos:**

1. Seleccionar "Imagen desde DockerHub"
2. Escribir: `nginx:latest`
3. Click en "Verificar"
4. Esperar respuesta

**Resultado Esperado:**

- ✅ Mensaje de éxito: "✅ Imagen encontrada en DockerHub"
- ✅ Muestra nombre: `nginx:latest`
- ✅ Muestra última actualización
- ✅ Muestra tamaño en MB
- ✅ **Muestra puerto detectado: 80**
- ✅ Botón "Usar este puerto" visible

**Estado:** [ ] PASS | [ ] FAIL | [ ] PENDIENTE

**Notas:**

```
Fecha de prueba: __/__/____
Resultado:


Errores encontrados:


```

---

### **CASO 5: Verificar Imagen de DockerHub - Imagen de Usuario**

**Objetivo:** Verificar que funciona con imágenes de usuarios

**Pasos:**

1. Seleccionar "Imagen desde DockerHub"
2. Escribir: `library/postgres:15` o `postgres:15`
3. Click en "Verificar"
4. Esperar respuesta

**Resultado Esperado:**

- ✅ Mensaje de éxito
- ✅ Muestra información de la imagen
- ✅ **Puerto detectado: 5432**
- ✅ Botón "Usar este puerto" funciona

**Estado:** [ ] PASS | [ ] FAIL | [ ] PENDIENTE

**Notas:**

```
Fecha de prueba: __/__/____
Resultado:


Errores encontrados:


```

---

### **CASO 6: Verificar Imagen de DockerHub - Imagen No Existente**

**Objetivo:** Verificar manejo de errores cuando la imagen no existe

**Pasos:**

1. Seleccionar "Imagen desde DockerHub"
2. Escribir: `imagen-que-no-existe-12345:latest`
3. Click en "Verificar"
4. Esperar respuesta

**Resultado Esperado:**

- ✅ Mensaje de error: "❌ Imagen no encontrada en DockerHub"
- ✅ Mensaje claro indicando verificar nombre y tag
- ✅ No se muestra información de puerto

**Estado:** [ ] PASS | [ ] FAIL | [ ] PENDIENTE

**Notas:**

```
Fecha de prueba: __/__/____
Resultado:


Errores encontrados:


```

---

### **CASO 7: Botón "Usar este puerto"**

**Objetivo:** Verificar que el botón auto-completa el puerto correctamente

**Pasos:**

1. Verificar imagen `nginx:latest` (puerto 80)
2. Click en botón "Usar este puerto"
3. Verificar campo "Puerto interno del contenedor"

**Resultado Esperado:**

- ✅ Campo "Puerto interno" se rellena con `80`
- ✅ Valor visible en el input

**Estado:** [ ] PASS | [ ] FAIL | [ ] PENDIENTE

**Notas:**

```
Fecha de prueba: __/__/____
Resultado:


Errores encontrados:


```

---

### **CASO 8: Botón "Limpiar" en DockerHub**

**Objetivo:** Verificar que el botón limpia el campo correctamente

**Pasos:**

1. Escribir `nginx:latest` en campo DockerHub
2. Click en "Verificar" (aparece feedback)
3. Click en "Limpiar"

**Resultado Esperado:**

- ✅ Campo de texto se vacía
- ✅ Feedback de verificación desaparece
- ✅ Campo queda limpio para nueva entrada

**Estado:** [ ] PASS | [ ] FAIL | [ ] PENDIENTE

**Notas:**

```
Fecha de prueba: __/__/____
Resultado:


Errores encontrados:


```

---

### **CASO 9: Exclusión Dockerfile vs Compose (Modo Custom)**

**Objetivo:** Verificar que Dockerfile y Compose son mutuamente exclusivos

**Pasos:**

1. Seleccionar "Configuración personalizada"
2. Subir un Dockerfile
3. Verificar que campo Compose desaparece
4. Limpiar Dockerfile
5. Verificar que Compose reaparece

**Resultado Esperado:**

- ✅ Al subir Dockerfile → Compose se oculta
- ✅ Al limpiar Dockerfile → Compose reaparece
- ✅ Código fuente siempre visible (opcional)

**Estado:** [ ] PASS | [ ] FAIL | [ ] PENDIENTE

**Notas:**

```
Fecha de prueba: __/__/____
Resultado:


Errores encontrados:


```

---

### **CASO 10: Exclusión Compose vs Dockerfile (Modo Custom)**

**Objetivo:** Verificar exclusión en sentido inverso

**Pasos:**

1. Seleccionar "Configuración personalizada"
2. Subir un docker-compose.yml
3. Verificar que campo Dockerfile desaparece
4. Limpiar Compose
5. Verificar que Dockerfile reaparece

**Resultado Esperado:**

- ✅ Al subir Compose → Dockerfile se oculta
- ✅ Al limpiar Compose → Dockerfile reaparece
- ✅ Código fuente siempre visible (opcional)

**Estado:** [ ] PASS | [ ] FAIL | [ ] PENDIENTE

**Notas:**

```
Fecha de prueba: __/__/____
Resultado:


Errores encontrados:


```

---

### **CASO 11: Detección de Puertos - Imágenes Comunes**

**Objetivo:** Verificar detección automática de puertos para imágenes conocidas

**Imágenes a probar:**

| Imagen           | Puerto Esperado |
| ---------------- | --------------- |
| `nginx:latest`   | 80              |
| `postgres:15`    | 5432            |
| `mysql:8`        | 3306            |
| `redis:alpine`   | 6379            |
| `mongodb:latest` | 27017           |

**Pasos:**

1. Para cada imagen, verificar en DockerHub
2. Comprobar que el puerto detectado es correcto

**Resultado Esperado:**

- ✅ Todos los puertos detectados correctamente
- ✅ Botón "Usar este puerto" funciona para todos

**Estado:** [ ] PASS | [ ] FAIL | [ ] PENDIENTE

**Notas:**

```
Fecha de prueba: __/__/____
Resultado:


Errores encontrados:


```

---

### **CASO 12: Campo Vacío en Verificación**

**Objetivo:** Verificar manejo de campo vacío

**Pasos:**

1. Seleccionar "Imagen desde DockerHub"
2. Dejar campo vacío
3. Click en "Verificar"

**Resultado Esperado:**

- ✅ Mensaje de advertencia: "Por favor, ingresa un nombre de imagen"
- ✅ No se hace petición al servidor
- ✅ Feedback amarillo (warning)

**Estado:** [ ] PASS | [ ] FAIL | [ ] PENDIENTE

**Notas:**

```
Fecha de prueba: __/__/____
Resultado:


Errores encontrados:


```

---

### **CASO 13: Cambio Entre Tipos de Despliegue**

**Objetivo:** Verificar que cambiar entre tipos limpia campos correctamente

**Pasos:**

1. Seleccionar "Imagen desde DockerHub"
2. Escribir `nginx:latest`
3. Cambiar a "Imagen por defecto"
4. Volver a "Imagen desde DockerHub"
5. Verificar que el campo está limpio

**Resultado Esperado:**

- ✅ Al cambiar de modo, campos se limpian
- ✅ No queda información residual
- ✅ Feedback desaparece

**Estado:** [ ] PASS | [ ] FAIL | [ ] PENDIENTE

**Notas:**

```
Fecha de prueba: __/__/____
Resultado:


Errores encontrados:


```

---

### **CASO 14: Estilos y Diseño**

**Objetivo:** Verificar que el diseño es consistente y atractivo

**Aspectos a verificar:**

- [ ] Cards con bordes visibles en campos de archivo
- [ ] Botones con colores apropiados (azul para Verificar, rojo para Limpiar)
- [ ] Iconos visibles y bien espaciados
- [ ] Warnings con borde amarillo destacado
- [ ] Inputs con tamaño `form-control-lg`
- [ ] Fuente monospace en campo DockerHub
- [ ] Grid de 3 columnas para tipos de despliegue (col-md-4)

**Resultado Esperado:**

- ✅ Diseño limpio y profesional
- ✅ Colores consistentes con el resto de la app
- ✅ Espaciado adecuado
- ✅ Responsive en diferentes tamaños de pantalla

**Estado:** [ ] PASS | [ ] FAIL | [ ] PENDIENTE

**Notas:**

```
Fecha de prueba: __/__/____
Resultado:


Errores encontrados:


```

---

### **CASO 15: Timeout y Errores de Red**

**Objetivo:** Verificar manejo de errores de conexión

**Pasos:**

1. Desconectar internet (o simular timeout)
2. Intentar verificar imagen
3. Observar mensaje de error

**Resultado Esperado:**

- ✅ Mensaje de error claro
- ✅ No se rompe la aplicación
- ✅ Botón vuelve a estado normal

**Estado:** [ ] PASS | [ ] FAIL | [ ] PENDIENTE

**Notas:**

```
Fecha de prueba: __/__/____
Resultado:


Errores encontrados:


```

---

## 📊 RESUMEN DE RESULTADOS

### **Estadísticas:**

- Total de casos: 15
- Casos PASS: \_\_
- Casos FAIL: \_\_
- Casos PENDIENTE: \_\_
- Porcentaje de éxito: \_\_%

### **Errores Críticos Encontrados:**

```
1.

2.

3.

```

### **Errores Menores Encontrados:**

```
1.

2.

3.

```

### **Mejoras Sugeridas:**

```
1.

2.

3.

```

---

## 📝 ARCHIVOS MODIFICADOS

### **Backend:**

- `containers/views.py` - Nueva vista `verify_dockerhub_image`
- `containers/urls.py` - Nueva ruta `/verify-dockerhub/`

### **Frontend:**

- `templates/containers/new_service.html` - Nuevo tipo de despliegue DockerHub
- `templates/containers/_partials/panels/_scripts.html` - Funciones JS actualizadas

---

## 🔧 CONFIGURACIÓN DE TESTING

### **Entorno:**

- URL: `http://localhost:8000/paasify/containers/new/`
- Usuario de prueba: (especificar)
- Navegador: (especificar)

### **Datos de Prueba:**

**Imágenes válidas:**

- `nginx:latest`
- `postgres:15`
- `mysql:8`
- `redis:alpine`
- `mongodb:latest`

**Imágenes inválidas:**

- `imagen-inexistente:latest`
- `usuario/repo-privado:v1.0` (si es privada)

---

## ✅ CRITERIOS DE ACEPTACIÓN

Para considerar el testing COMPLETADO, se deben cumplir:

- [ ] Todos los casos de prueba ejecutados
- [ ] Al menos 90% de casos PASS
- [ ] Errores críticos documentados y reportados
- [ ] Screenshots de casos importantes capturados
- [ ] Documento actualizado con resultados

---

**Tester:** ******\_\_\_******  
**Fecha de inicio:** **/**/\_**\_  
**Fecha de finalización:** **/**/\_\_**  
**Estado final:** [ ] APROBADO | [ ] RECHAZADO | [ ] PENDIENTE

---

## 📸 SCREENSHOTS

(Adjuntar screenshots de casos importantes)

1. **Tipo de Despliegue - 3 opciones:**
   - [ ] Capturado

2. **Verificación exitosa con puerto detectado:**
   - [ ] Capturado

3. **Error de imagen no encontrada:**
   - [ ] Capturado

4. **Exclusión Dockerfile/Compose:**
   - [ ] Capturado
