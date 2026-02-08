# Plan de Testing - Fase 4 y 5: Documentación API Premium y Validación

**Fecha**: 05/02/2026  
**Tipo**: Testing + UX  
**Estado**: PENDIENTE (Listo para ejecución)

---

## 🧪 TESTS DE LA FASE 4: DOCUMENTACIÓN API PREMIUM

### **Test 4.1: Acceso y Navegación**

**Objetivo**: Verificar que la nueva página de documentación carga y es fácilmente accesible.
**Pasos**:

1. Iniciar sesión como alumno.
2. Verificar que en el Navbar aparece el enlace **"API Docs"** con el icono de código (`< />`).
3. Hacer clic en el enlace.
4. **Verificar**:
   - [SI] Carga la URL `/paasify/containers/api-docs/`.
   - [SI] Se visualiza el Sidebar a la izquierda y el contenido a la derecha.
   - [SI] Al hacer scroll, el sidebar se mantiene fijo.
   - [SI] El enlace activo en el sidebar cambia automáticamente según la sección visible.

### **Test 4.2: Personalización de Ejemplos (Token y URL)**

**Objetivo**: Confirmar que la documentación inyecta los datos reales del usuario.
**Pasos**:

1. Acceder a `/paasify/containers/api-docs/`.
2. Ir a la sección **"Autenticación"**.
3. **Verificar**:
   - [SI] El ejemplo de Bearer Token no muestra tu token real.
4. Ir a la sección **"Listar Servicios"**.
5. **Verificar**:
   - [SI] La URL del comando curl detecta correctamente el dominio actual.

### **Test 4.3: Funcionalidad de Copiado (Markdown)**

**Objetivo**: Validar que los botones de copiar inyectados en el Markdown funcionan.
**Pasos**:

1. Ir a cualquier ejemplo de código generado desde el .md.
2. Hacer clic en el botón **"Copiar"**.
3. **Verificar**:
   - [SI] Aparece el Toast de SweetAlert2.
   - [SI] Al pegar, los placeholders `{{ ... }}` han sido reemplazados por valores reales.

### **Test 4.4: Diseño Responsive**

**Objetivo**: Verificar visualización móvil.
**Pasos**:

1. Reducir ancho del navegador.
2. **Verificar**:
   - [SI] El sidebar se oculta.
   - [SI] Las tablas de parámetros en Markdown son legibles o tienen scroll.

### **Test 4.5: Mantenibilidad (Markdown Dinámico)**

**Objetivo**: Confirmar carga desde archivo externo.
**Pasos**:

1. Editar `templates/api_docs/api_reference.md`.
2. Verificar reflejo en web sin reiniciar servidor.
   **Se ha modificado este tipo de ajuste y no existe ya api reference ya que se ha implementado la documentacion en diferentes archivos .md**

---

## 🧪 TESTS DE LA FASE 5: INTEGRACIÓN Y API

### **Test 5.1: Ejecución de comando real (POST)**

**Objetivo**: Probar que un comando copiado de la doc funciona en la terminal real.
**Pasos**:

1. Ir a la sección **"Crear Servicio"** > **"Ejemplo 1: Imagen del Catálogo"**.
2. Copiar el comando curl.
3. Abrir una terminal (PowerShell o Bash) y pegar el comando.
4. **Verificar**:
   - [SI] La respuesta es un JSON con status `201 Created`.
   - [SI] El servicio aparece inmediatamente en el panel web de PaaSify.

### **Test 5.2: Control vía API (Start/Stop)**

**Objetivo**: Validar que los comandos de control funcionan sobre servicios existentes.

1. Obtener el ID de un servicio desde la UI o ejecutando un GET a la API.
2. Ejecutar el comando POST de la sección **"Control de Servicios"** para detenerlo.
3. **Verificar**:
   - [SI] El servicio web cambia su estado a "stopped" casi al instante.

### **Test 5.3: Seguridad de Tokens Expulsados**

**Objetivo**: Confirmar que un token no válido no escala privilegios.
**Pasos**:

1. Intentar ejecutar cualquier comando curl modificando un solo carácter del token.
2. **Verificar**:
   - [SI] La respuesta es un error `401 Unauthorized`.
   - [SI] El cuerpo del JSON explica que el token es inválido o ha expirado.

---

## 📊 RESUMEN DE CRITERIOS DE ÉXITO

1. **Estética**: La página debe verse "Premium" (sombras suaves, fuentes monoespaciadas, degradados).
2. **Practicidad**: Un alumno debe poder desplegar un Nginx solo copiando y pegando sin editar ni una letra del curl.
3. **Consistencia**: Las rutas de la API deben coincidir con lo que los comandos curl intentan atacar.
