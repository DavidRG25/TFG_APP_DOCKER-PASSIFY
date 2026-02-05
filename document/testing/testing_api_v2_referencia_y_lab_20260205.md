# Plan de Testing - Referencia API y Guía de Despliegue

**Fecha**: 05/02/2026  
**Versión**: 2.1 (Adaptada a Guía Técnica)  
**Estado**: PENDIENTE DE EJECUCIÓN

---

## 📖 PARTE 1: VERIFICACIÓN DE API DOCS (MANUAL DE REFERENCIA)

### **Test 1.1: Privacidad y Neutralidad**

1. Entrar en **API Docs** desde el menú superior.
2. Ir a la sección **"Autenticación"**.
3. **Verificar**:
   - [ ] El ejemplo de cURL muestra literalmente: `Authorization: Bearer <TU_API_TOKEN>`.
4. Ir a la sección **"Gestión de Servicios"**.
5. **Verificar**:
   - [ ] Se documentan los comandos para: Iniciar, Detener, Reiniciar y Ver Logs.

### **Test 1.2: Integridad Técnica**

1. **Verificar**:
   - [ ] La URL Base mostrada coincide con el dominio real o configurado.
   - [ ] El Sidebar permite saltar rápidamente entre métodos (GET, POST).

---

## 🧪 PARTE 2: TESTING DE LA GUÍA DE DESPLIEGUE (COMANDOS API)

### **Test 2.1: Navegación por Modos (Experiencia de Usuario)**

**Objetivo**: Validar que el sistema de pestañas y cards funciona correctamente.
**Pasos**:

1. Entrar en **Guía de Despliegue por Terminal** (Menú lateral).
2. Hacer clic en la card de **"Imagen desde DockerHub"**.
3. **Verificar**:
   - [ ] El contenido cambia y muestra las reglas de Imágenes Externas.
   - [ ] El ejemplo de cURL a la derecha cambia al de DockerHub.
4. Hacer clic en **"Configuración personalizada"**.
5. **Verificar**:
   - [ ] Aparecen las sub-pestañas: **1. Caso Dockerfile** y **2. Caso Compose**.
   - [ ] Al alternar entre ambas, el ejemplo de código de la derecha se actualiza.

### **Test 2.2: Verificación de Ayuda Educativa**

**Objetivo**: Confirmar que las aclaraciones técnicas son visibles y correctas.
**Pasos**:

1. En la pestaña **Catálogo**:
   - [ ] Verificar que aparece el listado de "Imágenes disponibles" (nginx, postgres, etc.).
2. En la pestaña **DockerHub**:
   - [ ] Verificar la presencia del aviso azul: "¿Es necesario environment?".
   - [ ] Confirmar que el cURL de ejemplo incluye un objeto `environment` de muestra.
3. En la pestaña **Personalizado**:
   - [ ] Verificar el bloque informativo sobre el contenido del archivo ZIP.

### **Test 2.3: Funcionalidad de Copiado**

1. En cualquier pestaña, hacer clic en el botón **"Copiar"** del bloque de código.
2. **Verificar**:
   - [ ] Aparece un mensaje flotante (Toast/SweetAlert) confirmando el copiado.
   - [ ] Al pegar en un editor, el contenido coincide exactamente con la plantilla.

---

## 📊 CRITERIOS DE ACEPTACIÓN FINAL

1. **Consistencia Visual**: Los colores y estilos coinciden con la pantalla de "Nuevo Servicio".
2. **Claridad Educativa**: El alumno entiende qué enviar en el ZIP y para qué sirve el `environment` gracias a las notas.
3. **Robustez de Navegación**: Cambiar de pestaña no provoca que la pantalla se quede en blanco o desordenada.
