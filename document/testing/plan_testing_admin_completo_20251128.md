# Plan de Testing: Mejoras Admin Panel PaaSify

**Fecha:** 2025-11-28  
**Versión:** 4.2.3-4.2.6  
**Rama:** dev2

---

## 🎯 Objetivo del Testing

Verificar que todas las mejoras implementadas en las Fases 1-6 del panel de administración funcionan correctamente y no rompen funcionalidad existente.

---

## ✅ Pre-requisitos

Antes de comenzar el testing, asegúrate de:

1. **Servidor corriendo:**
   ```bash
   bash scripts/run.sh
   ```

2. **Datos de ejemplo cargados:**
   ```bash
   python manage.py create_demo_users
   python manage.py populate_example_images
   ```

3. **Acceso al admin:**
   - URL: `http://127.0.0.1:8000/admin/`
   - Usuario: `admin` / `Admin!123`

---

## 📋 Plan de Testing por Fases

### FASE 1: User Admin ✅ (Completada previamente)

#### Test 1.1: Lista de Usuarios
**URL:** `/admin/auth/user/`

**Pasos:**
1. Acceder a la lista de usuarios
2. Verificar columnas visibles

**Verificar:**
- [ ] Columna "Nombre completo" visible
- [ ] Columna "Rol" con badges de colores:
  - 🔑 Admin (rojo)
  - 👨‍🏫 Profesor (verde)
  - 👨‍🎓 Alumno (azul)
- [ ] Columna "Asignaturas" con contador
- [ ] Columna "Servicios Activos" con código de color
- [ ] Filtro "Rol" en sidebar

**Resultado esperado:** ✅ Todas las columnas y filtros funcionan

---

#### Test 1.2: Crear Usuario
**URL:** `/admin/auth/user/add/`

**Pasos:**
1. Click en "Agregar usuario"
2. Completar formulario:
   - Username: `test_student`
   - Email: `test@example.com`
   - Nombre: `Test`
   - Apellidos: `Student`
   - Rol: `Alumno`
   - Marcar "Generar contraseña automáticamente"
3. Guardar

**Verificar:**
- [ ] Formulario muestra campo "Rol"
- [ ] Opción de generar contraseña automática
- [ ] Mensaje de éxito muestra contraseña generada
- [ ] Usuario creado tiene grupo "Student"
- [ ] UserProfile creado automáticamente

**Resultado esperado:** ✅ Usuario creado con todos los datos correctos

---

#### Test 1.3: Filtrar por Rol
**URL:** `/admin/auth/user/`

**Pasos:**
1. Usar filtro "Rol" en sidebar
2. Seleccionar "Profesor"
3. Verificar resultados

**Verificar:**
- [ ] Solo muestra usuarios con rol Profesor
- [ ] Contador de resultados correcto

**Resultado esperado:** ✅ Filtro funciona correctamente

---

### FASE 2: AllowedImage Admin ✅ (Completada previamente)

#### Test 2.1: Lista de Imágenes
**URL:** `/admin/containers/allowedimage/`

**Pasos:**
1. Acceder a la lista de imágenes permitidas
2. Verificar columnas

**Verificar:**
- [ ] Columna "Icono" con emojis:
  - 🌐 Web
  - 🗄️ Database
  - 🚀 API
  - 📦 Misc
- [ ] Columna "Tipo de imagen"
- [ ] Columna "Fecha de creación"
- [ ] Filtros por tipo y fecha
- [ ] Al menos 11 imágenes de ejemplo

**Resultado esperado:** ✅ Todas las columnas y filtros funcionan

---

#### Test 2.2: Editar Imagen
**URL:** `/admin/containers/allowedimage/<id>/change/`

**Pasos:**
1. Editar imagen `nginx:latest`
2. Verificar campo "Tags disponibles en DockerHub"

**Verificar:**
- [ ] Campo "Tags disponibles" muestra tags
- [ ] Tags ordenados (latest primero)
- [ ] Campo "Tipo de imagen" con radio buttons
- [ ] Help text con descripciones de funcionalidades

**Resultado esperado:** ✅ Tags de DockerHub se muestran correctamente

---

#### Test 2.3: Crear Nueva Imagen
**URL:** `/admin/containers/allowedimage/add/`

**Pasos:**
1. Click en "Agregar imagen permitida"
2. Completar:
   - Name: `redis`
   - Tag: `latest`
   - Description: `Base de datos en memoria`
   - Tipo: `Base de Datos`
3. Guardar

**Verificar:**
- [ ] Formulario muestra selector de tipo con descripciones
- [ ] Mensaje de éxito muestra funcionalidad futura
- [ ] Imagen guardada con tipo correcto

**Resultado esperado:** ✅ Imagen creada con tipo correcto

---

### FASE 3: Service Admin ✨ (Nueva)

#### Test 3.1: Lista de Servicios
**URL:** `/admin/containers/service/`

**Pasos:**
1. Acceder a la lista de servicios
2. Verificar columnas

**Verificar:**
- [ ] Columna "Tipo" con icono según imagen
- [ ] Columna "Volúmenes" con contador
- [ ] Si hay servicios, verificar iconos correctos

**Resultado esperado:** ✅ Columnas nuevas visibles y correctas

---

#### Test 3.2: Editar Servicio con Imagen Web
**URL:** `/admin/containers/service/<id>/change/`

**Pasos:**
1. Editar un servicio que use nginx o httpd
2. Scroll hasta "Opciones de Imagen"

**Verificar:**
- [ ] Caja naranja con icono 🌐
- [ ] Texto: "Funcionalidad futura: Editor HTML/CSS/JS"
- [ ] Sección "Configuración de Red" con puerto
- [ ] URL clickeable funciona

**Resultado esperado:** ✅ Opciones de imagen correctas

---

#### Test 3.3: Editar Servicio con Imagen Database
**URL:** `/admin/containers/service/<id>/change/`

**Pasos:**
1. Editar un servicio que use mysql o postgres
2. Verificar "Opciones de Imagen"

**Verificar:**
- [ ] Caja azul con icono 🗄️
- [ ] Texto sobre configuración de credenciales

**Resultado esperado:** ✅ Opciones de imagen correctas

---

#### Test 3.4: Información de Puerto
**URL:** `/admin/containers/service/<id>/change/`

**Pasos:**
1. Editar servicio con puerto asignado
2. Ver sección "Configuración de Red"

**Verificar:**
- [ ] Caja verde con información de puerto
- [ ] Puerto asignado visible
- [ ] Puerto interno visible
- [ ] URL de acceso clickeable

**Resultado esperado:** ✅ Información de puerto completa

---

#### Test 3.5: Detalles de Volúmenes
**URL:** `/admin/containers/service/<id>/change/`

**Pasos:**
1. Editar servicio con volúmenes configurados
2. Expandir "Configuración Avanzada"

**Verificar:**
- [ ] Lista de volúmenes con formato `host → container`
- [ ] Código con fondo de color

**Resultado esperado:** ✅ Volúmenes listados correctamente

---

### FASE 4: Subject Admin ✨ (Nueva)

#### Test 4.1: Lista de Asignaturas
**URL:** `/admin/paasify/subject/`

**Pasos:**
1. Acceder a la lista de asignaturas
2. Verificar columnas

**Verificar:**
- [ ] Columna "Alumnos" con icono 👥
- [ ] Columna "Servicios" con icono 🐳
- [ ] Contadores correctos

**Resultado esperado:** ✅ Columnas nuevas visibles

---

#### Test 4.2: Crear Asignatura
**URL:** `/admin/paasify/subject/add/`

**Pasos:**
1. Click en "Agregar asignatura"
2. Ver selector de profesor

**Verificar:**
- [ ] Selector muestra solo profesores
- [ ] Formato: `username - Nombre Completo`
- [ ] Help text visible y claro
- [ ] Selector de alumnos ordenado alfabéticamente

**Resultado esperado:** ✅ Selectores mejorados

---

### FASE 5: UserProfile Admin ✨ (Nueva)

#### Test 5.1: Lista de Perfiles
**URL:** `/admin/paasify/userprofile/`

**Pasos:**
1. Acceder a la lista de perfiles
2. Verificar columnas

**Verificar:**
- [ ] Columna "Rol" con badges:
  - 👨‍🏫 Profesor (verde)
  - 👨‍🎓 Alumno (azul)
- [ ] Columna "Asignaturas" con icono 📚
- [ ] Contador correcto

**Resultado esperado:** ✅ Columnas nuevas visibles

---

#### Test 5.2: Filtrar por Fecha
**URL:** `/admin/paasify/userprofile/`

**Pasos:**
1. Usar filtro "Token created at"
2. Seleccionar "Hoy"

**Verificar:**
- [ ] Filtra correctamente
- [ ] Solo muestra perfiles con token de hoy

**Resultado esperado:** ✅ Filtro funciona

---

### FASE 6: UserProject Admin ✨ (Nueva)

#### Test 6.1: Lista de Proyectos
**URL:** `/admin/paasify/userproject/`

**Pasos:**
1. Acceder a la lista de proyectos
2. Verificar columnas

**Verificar:**
- [ ] Columna "Alumno" con nombre completo
- [ ] Columna "Servicios" con icono 🐳
- [ ] Columna "Estado" con colores:
  - ✅ Todos activos (verde)
  - ⚠️ Parcialmente activo (naranja)
  - ❌ Detenido (rojo)
  - ⚪ Sin servicios (gris)

**Resultado esperado:** ✅ Columnas nuevas visibles

---

#### Test 6.2: Estados de Proyecto
**URL:** `/admin/paasify/userproject/`

**Pasos:**
1. Verificar proyectos con diferentes estados
2. Comparar con servicios reales

**Verificar:**
- [ ] Estado refleja servicios correctamente
- [ ] Contador de servicios correcto
- [ ] Colores apropiados

**Resultado esperado:** ✅ Estados correctos

---

#### Test 6.3: Búsqueda
**URL:** `/admin/paasify/userproject/`

**Pasos:**
1. Buscar por nombre de alumno
2. Buscar por nombre de asignatura

**Verificar:**
- [ ] Búsqueda por alumno funciona
- [ ] Búsqueda por asignatura funciona

**Resultado esperado:** ✅ Búsqueda funciona

---

## 🔍 Tests de Regresión

### Test R.1: Funcionalidad Existente
**Objetivo:** Verificar que nada se rompió

**Pasos:**
1. Crear un usuario manualmente
2. Crear una asignatura
3. Crear un servicio
4. Verificar que todo funciona como antes

**Verificar:**
- [ ] Creación de usuarios funciona
- [ ] Creación de asignaturas funciona
- [ ] Creación de servicios funciona
- [ ] No hay errores en consola

**Resultado esperado:** ✅ Todo funciona

---

### Test R.2: Panel del Alumno
**Objetivo:** Verificar que el panel del alumno no se tocó

**Pasos:**
1. Logout del admin
2. Login como `alumno` / `Alumno!2025`
3. Navegar por el panel

**Verificar:**
- [ ] Panel del alumno funciona igual
- [ ] No hay cambios visuales
- [ ] Todas las funciones disponibles

**Resultado esperado:** ✅ Panel del alumno intacto

---

## 📊 Resumen de Testing

### Checklist General

**Fases Implementadas:**
- [ ] Fase 1: User Admin
- [ ] Fase 2: AllowedImage Admin
- [ ] Fase 3: Service Admin
- [ ] Fase 4: Subject Admin
- [ ] Fase 5: UserProfile Admin
- [ ] Fase 6: UserProject Admin

**Tests de Regresión:**
- [ ] Funcionalidad existente intacta
- [ ] Panel del alumno no modificado

**Total de Tests:** 20+

---

## 🐛 Reporte de Bugs

Si encuentras algún bug durante el testing, documéntalo aquí:

### Bug Template:
```
**ID:** BUG-XXX
**Fase:** X
**URL:** /admin/...
**Descripción:** 
**Pasos para reproducir:**
1. 
2. 
3. 
**Resultado esperado:**
**Resultado actual:**
**Prioridad:** Alta/Media/Baja
```

---

## ✅ Aprobación Final

Una vez completados todos los tests:

- [ ] Todos los tests pasaron
- [ ] No hay bugs críticos
- [ ] Funcionalidad existente intacta
- [ ] Documentación completa

**Fecha de aprobación:** ___________  
**Aprobado por:** ___________

---

**Estado:** 📋 Listo para testing
