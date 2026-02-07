
# 🏆 Plan Maestro de Testing: API Docs & Navegación Premium (v5.0)

**Fecha**: 07/02/2026  
**Objetivo**: Validar la experiencia de usuario completa en la documentación de la API, incluyendo navegación multipágina, sub-secciones dinámicas, prefetch/spinner y despliegue personalizado.

---

## 🏗️ FASE 1: UI/UX Y NAVEGACIÓN (EXPERIENCIA PREMIUM)

### **Test 01: Navegación de Extremos (Fix "Anterior")**
1. Ir a la sección **1. Introducción**.
2. **Verificar**: 
   - [ ] El botón **"← Anterior"** aparece deshabilitado.
   - [ ] No existen enlaces a "Inicio" o variables `{{ ... }}`.
3. Ir a la sección **7. Códigos de Error**.
4. **Verificar**: 
   - [ ] El botón **"Siguiente →"** aparece deshabilitado.

### **Test 02: Sidebar Dinámico (Sub-secciones H3)**
1. Navegar a **"Crear Servicio"**.
2. **Verificar**: 
   - [ ] Debajo del enlace activo en el sidebar, aparece un sub-menú (desplegable visual) con:
     - Imagen de Catálogo
     - DockerHub Personalizado
     - Código Personalizado (ZIP)
3. Navegar a **"Consultas (GETs)"**.
4. **Verificar**: 
   - [ ] Aparecen sub-enlaces para "Listar Servicios", "Listar Asignaturas" y "Listar Proyectos".
5. **Test 02.b: Botón Expandir Todo**:
   - [ ] Pulsar el botón con el icono de flechas junto a "Guía de Inicio".
   - [ ] Verificar que se muestran los sub-apartados de TODAS las secciones a la vez.
   - [ ] Pulsar de nuevo y verificar que se vuelven a agrupar (quedando solo la activa).
6. Al hacer clic en un sub-enlace -> scroll suave al punto exacto.

### **Test 03: Feedback de Carga (Spinner & Lock)**
1. Hacer clic en cualquier sección y verificar el spinner central.
2. Comprobar que el contenido se vuelve translúcido durante la carga.

### **Test 04: Prefetch y Teclado**
1. Verificar en Network el prefetch de la siguiente página.
2. Probar navegación con flechas `←` y `→`.

---

## � FASE 2: SEGURIDAD Y TOKEN

### **Test 05: Aislamiento de Alumno**
1. Intentar acceder a `/api/containers/` sin token o con token ajeno.
2. **Verificar**: Respuesta **401 Unauthorized**.

---

## � FASE 3: CONTENIDO TÉCNICO Y DESPLIEGUES

### **Test 06: Despliegue Personalizado (Código ZIP)**
1. Ir a la sección **"Crear Servicio" > "Código Personalizado (ZIP)"**.
2. **Verificar**: 
   - [ ] Se documenta el uso de `-F` (multipart) para subir archivos.
   - [ ] Se explica que se requiere `code` (.zip/.rar) y un `Dockerfile` o `docker-compose.yml`.

### **Test 06.b: Escenarios Avanzados (Compose)**
1. Bajar hasta la sección **"Escenarios Avanzados"**.
2. **Verificar**:
   - [ ] Aparece el ejemplo de `curl` para un despliegue multi-contenedor (Web+DB).
   - [ ] Se mencionan las buenas prácticas (Healthchecks, usuario no-root).
   - [ ] El sidebar muestra "Escenarios Avanzados" como sub-apartado.

### **Test 07: Acordeones de Error Contextuales**
1. Navegar por todos los endpoints y verificar que el desplegable "Códigos de error de este endpoint" muestra información coherente con la acción.

---

## 📱 FASE 4: DISEÑO RESPONSIVE

### **Test 08: Sidebar Colapsable en Móvil**
1. Verificar el botón "Menú" y la apertura del drawer en pantallas pequeñas.

---

## 🔍 CRITERIOS DE ACEPTACIÓN
- [ ] La navegación se siente instantánea y con feedback visual claro.
- [ ] El sidebar ayuda a la navegación rápida mediante sub-secciones automáticas.
- [ ] Todas las modalidades de creación de servicio (incluida la personalizada) están documentadas.
- [ ] No hay errores de renderizado ni lógica de servidor visible.
