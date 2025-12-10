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
- [SI] Columna "Nombre completo" visible
- [SI] Columna "Rol" con badges de colores:
  - 🔑 Admin (rojo)
  - 👨‍🏫 Profesor (verde)
  - 👨‍🎓 Alumno (azul)
- [SI] Columna "Asignaturas" con contador
- [SI] Columna "Servicios Activos" con código de color
- [SI] Filtro "Rol" en sidebar

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
- [SI] Formulario muestra campo "Rol"
- [SI] Opción de generar contraseña automática
- [SI] Mensaje de éxito muestra contraseña generada
- [SI] Usuario creado tiene grupo "Student"
- [SI] UserProfile creado automáticamente

**Resultado esperado:** ✅ Usuario creado con todos los datos correctos

---

#### Test 1.3: Filtrar por Rol
**URL:** `/admin/auth/user/`

**Pasos:**
1. Usar filtro "Rol" en sidebar
2. Seleccionar "Profesor"
3. Verificar resultados

**Verificar:**
- [SI] Solo muestra usuarios con rol Profesor
- [SI] Contador de resultados correcto

**Resultado esperado:** ✅ Filtro funciona correctamente

---

### FASE 2: AllowedImage Admin ✅ (Completada previamente)

#### Test 2.1: Lista de Imágenes
**URL:** `/admin/containers/allowedimage/`

**Pasos:**
1. Acceder a la lista de imágenes permitidas
2. Verificar columnas

**Verificar:**
- [SI] Columna "Icono" con emojis:
  - 🌐 Web
  - 🗄️ Database
  - 🚀 API
  - 📦 Misc
- [SI] Columna "Tipo de imagen"
- [SI] Columna "Fecha de creación"
- [SI] Filtros por tipo y fecha
- [SI] Al menos 11 imágenes de ejemplo

**Resultado esperado:** ✅ Todas las columnas y filtros funcionan

---

#### Test 2.2: Editar Imagen
**URL:** `/admin/containers/allowedimage/<id>/change/`

**Pasos:**
1. Editar imagen `nginx:latest`
2. Verificar campo "Tags disponibles en DockerHub"

**Verificar:**
- [SI] Campo "Tags disponibles" muestra tags
- [SI] Tags ordenados (latest primero)
- [SI] Campo "Tipo de imagen" con radio buttons
- [SI] Help text con descripciones de funcionalidades

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
- [SI] Formulario muestra selector de tipo con descripciones
- [SI] Mensaje de éxito muestra funcionalidad futura
- [SI] Imagen guardada con tipo correcto

**Resultado esperado:** ✅ Imagen creada con tipo correcto

---

### FASE 3: Service Admin ✨ (Nueva)

#### Test 3.1: Lista de Servicios
**URL:** `/admin/containers/service/`

**Pasos:**
1. Acceder a la lista de servicios
2. Verificar columnas

**Verificar:**
- [SI] Columna "Tipo" con icono según imagen
- [SI] Columna "Volúmenes" con contador
- [SI] Si hay servicios, verificar iconos correctos

**Resultado esperado:** ✅ Columnas nuevas visibles y correctas

---

#### Test 3.2: Editar Servicio con Imagen Web
**URL:** `/admin/containers/service/<id>/change/`

**Pasos:**
1. Editar un servicio que use nginx o httpd
2. Scroll hasta "Opciones de Imagen"

**Verificar:**
- [SI] Caja naranja con icono 🌐
- [SI] Texto: "Funcionalidad futura: Editor HTML/CSS/JS"
- [SI] Sección "Configuración de Red" con puerto
- [SI] URL clickeable funciona

**Resultado esperado:** ✅ Opciones de imagen correctas

---

#### Test 3.3: Editar Servicio con Imagen Database
**URL:** `/admin/containers/service/<id>/change/`

**Pasos:**
1. Editar un servicio que use mysql o postgres
2. Verificar "Opciones de Imagen"

**Verificar:**
- [SI] Caja azul con icono 🗄️
- [SI] Texto sobre configuración de credenciales

**Resultado esperado:** ✅ Opciones de imagen correctas

---

#### Test 3.4: Información de Puerto
**URL:** `/admin/containers/service/<id>/change/`

**Pasos:**
1. Editar servicio con puerto asignado
2. Ver sección "Configuración de Red"

**Verificar:**
- [SI] Caja verde con información de puerto
- [SI] Puerto asignado visible
- [SI] Puerto interno visible
- [SI] URL de acceso clickeable

**Resultado esperado:** ✅ Información de puerto completa

---

#### Test 3.5: Detalles de Volúmenes
**URL:** `/admin/containers/service/<id>/change/`

**Pasos:**
1. Editar servicio con volúmenes configurados
2. Expandir "Configuración Avanzada"

**Verificar:**
- [SI] Lista de volúmenes con formato `host → container`
- [SI] Código con fondo de color

**Resultado esperado:** ✅ Volúmenes listados correctamente

---

### FASE 4: Subject Admin ✨ (Nueva)

#### Test 4.1: Lista de Asignaturas
**URL:** `/admin/paasify/subject/`

**Pasos:**
1. Acceder a la lista de asignaturas
2. Verificar columnas

**Verificar:**
- [SI] Columna "Alumnos" con icono 👥
- [SI] Columna "Servicios" con icono 🐳
- [SI] Contadores correctos

**Resultado esperado:** ✅ Columnas nuevas visibles

---

#### Test 4.2: Crear Asignatura
**URL:** `/admin/paasify/subject/add/`

**Pasos:**
1. Click en "Agregar asignatura"
2. Ver selector de profesor

**Verificar:**
- [SI] Selector muestra solo profesores
- [SI] Formato: `username - Nombre Completo`
- [SI] Help text visible y claro
- [SI] Selector de alumnos ordenado alfabéticamente

**Resultado esperado:** ✅ Selectores mejorados

---

### FASE 5: Perfiles de Alumnos y Profesores ✨ (Nueva)

#### Test 5.1: Lista de Perfiles de Alumnos
**URL:** `/admin/paasify/userprofile/`

**Pasos:**
1. Acceder a la lista de perfiles de alumnos
2. Verificar columnas

**Verificar:**
- [SI] Columna "Nombre"
- [SI] Columna "Usuario (auth)"
- [SI] Columna "Rol" con badge azul "👨‍🎓 Alumno"
- [SI] Columna "Email"
- [SI] Columna "Asignaturas" con icono 📚
- [SI] Columna "Token API (JWT)"
- [SI] Columna "Fecha creacion token"
- [SI] Contador correcto de perfiles

**Resultado esperado:** ✅ Solo muestra usuarios Student

---

#### Test 5.2: Crear Perfil de Alumno
**URL:** `/admin/paasify/userprofile/add/`

**Pasos:**
1. Clic en "Agregar perfil de alumno"
2. Verificar fieldsets visibles

**Verificar:**
- [SI] Fieldset "Datos de Usuario" visible:
  - Nombre de usuario
  - Direccion de email
  - Nombre
  - Apellido
- [SI] Fieldset "Contraseña" visible:
  - Checkbox "Generar contraseña automaticamente"
  - Contraseña
  - Confirmacion de contraseña
- [SI] Fieldset "Informacion del Perfil" NO visible (se autocompleta)
- [SI] Fieldset "Token API" NO visible (se genera automaticamente)

**Resultado esperado:** ✅ Solo muestra campos necesarios para crear

---

#### Test 5.3: Crear Alumno con Contraseña Manual
**URL:** `/admin/paasify/userprofile/add/`

**Pasos:**
1. Rellenar datos de usuario
2. NO marcar "Generar contraseña automaticamente"
3. Introducir contraseña manualmente
4. Guardar

**Verificar:**
- [SI] Perfil creado correctamente
- [SI] Usuario creado con rol "Student"
- [SI] Campo "nombre" autocompletado desde first_name + last_name
- [SI] Campo "year" autocompletado desde email

**Resultado esperado:** ✅ Alumno creado con contraseña manual

---

#### Test 5.4: Crear Alumno con Contraseña Automatica
**URL:** `/admin/paasify/userprofile/add/`

**Pasos:**
1. Rellenar datos de usuario
2. Marcar "Generar contraseña automaticamente"
3. Dejar campos de contraseña vacios
4. Guardar

**Verificar:**
- [SI] Perfil creado correctamente
- [SI] Usuario creado con contraseña aleatoria de 12 caracteres
- [SI] Usuario tiene rol "Student"

**Resultado esperado:** ✅ Alumno creado con contraseña automatica

---

#### Test 5.5: Editar Perfil de Alumno
**URL:** `/admin/paasify/userprofile/<id>/change/`

**Pasos:**
1. Editar un perfil existente
2. Verificar fieldsets visibles

**Verificar:**
- [SI] Fieldset "Datos de Usuario" visible y editable
- [SI] Campo "Nombre de usuario" deshabilitado (no editable)
- [SI] Fieldset "Contraseña" visible (opcional)
- [SI] Checkbox "Generar contraseña automaticamente" NO visible
- [SI] Fieldset "Informacion del Perfil" visible con:
  - Nombre completo (readonly, caja azul con 👤)
  - Email / Curso (readonly, caja morada con �)
- [SI] Fieldset "Token API" visible (colapsado)

**Resultado esperado:** ✅ Todos los fieldsets visibles al editar

---

#### Test 5.6: Actualizar Nombre de Alumno
**URL:** `/admin/paasify/userprofile/<id>/change/`

**Pasos:**
1. Editar perfil de alumno
2. Cambiar "Nombre" de "alumno2" a "alumno4"
3. Guardar

**Verificar:**
- [SI] Campo "Nombre completo" se actualiza a "alumno4 <apellido>"
- [SI] Cambio reflejado en la lista de perfiles

**Resultado esperado:** ✅ Nombre se actualiza automaticamente

---

#### Test 5.7: Lista de Perfiles de Profesores
**URL:** `/admin/paasify/teacherprofile/`

**Pasos:**
1. Acceder a "Perfiles de profesores"
2. Verificar columnas

**Verificar:**
- [SI] Columna "Nombre"
- [SI] Columna "Usuario (auth)"
- [SI] Columna "Rol" con badge verde "👨‍🏫 Profesor"
- [SI] Columna "Email"
- [SI] Columna "Asignaturas" con icono 📚 (asignaturas que imparte)
- [SI] Columna "Token API (JWT)"
- [SI] Columna "Fecha creacion token"
- [SI] Solo muestra usuarios Teacher

**Resultado esperado:** ✅ Solo muestra usuarios Teacher

---

#### Test 5.8: Crear Perfil de Profesor
**URL:** `/admin/paasify/teacherprofile/add/`

**Pasos:**
1. Clic en "Agregar perfil de profesor"
2. Rellenar datos de usuario
3. Marcar "Generar contraseña automaticamente"
4. Guardar

**Verificar:**
- [SI] Perfil creado correctamente
- [SI] Usuario creado con rol "Teacher" (no "Student")
- [SI] Campo "nombre" autocompletado
- [SI] Campo "year" autocompletado
- [SI] Aparece en lista de "Perfiles de profesores"
- [SI] NO aparece en lista de "Perfiles de alumnos"

**Resultado esperado:** ✅ Profesor creado con rol correcto

---

#### Test 5.9: Editar Perfil de Profesor
**URL:** `/admin/paasify/teacherprofile/<id>/change/`

**Pasos:**
1. Editar un perfil de profesor
2. Verificar fieldsets

**Verificar:**
- [SI] Fieldset "Informacion del Perfil" muestra:
  - Nombre completo (readonly, caja verde con 👨‍🏫)
  - Email / Curso (readonly, caja naranja con 📧)
- [SI] Sin inline de "Proyectos asignados"

**Resultado esperado:** ✅ Diseño diferente para profesores

---

#### Test 5.10: Filtrar por Fecha de Token
**URL:** `/admin/paasify/userprofile/` y `/admin/paasify/teacherprofile/`

**Pasos:**
1. Usar filtro "Por Fecha creacion token"
2. Seleccionar "Hoy"

**Verificar:**
- [SI] Filtra correctamente en ambas pantallas
- [SI] Solo muestra perfiles con token de hoy

**Resultado esperado:** ✅ Filtro funciona en ambas pantallas

---

### FASE 6: UserProject Admin ✨ (Nueva)

#### Test 6.1: Lista de Proyectos
**URL:** `/admin/paasify/userproject/`

**Pasos:**
1. Acceder a la lista de proyectos
2. Verificar columnas

**Verificar:**
- [SI] Columna "Alumno" con nombre completo
- [SI] Columna "Servicios" con icono 🐳
- [SI] Columna "Estado" con colores:
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
- [SI] Estado refleja servicios correctamente
- [SI] Contador de servicios correcto
- [SI] Colores apropiados

**Resultado esperado:** ✅ Estados correctos

---

#### Test 6.3: Búsqueda
**URL:** `/admin/paasify/userproject/`

**Pasos:**
1. Buscar por nombre de alumno
2. Buscar por nombre de asignatura

**Verificar:**
- [SI] Búsqueda por alumno funciona
- [SI] Búsqueda por asignatura funciona

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
- [SI] Panel del alumno funciona igual
- [SI] No hay cambios visuales
- [SI] Todas las funciones disponibles

**Resultado esperado:** ✅ Panel del alumno intacto

---

## 📊 Resumen de Testing

### Checklist General

**Fases Implementadas:**
- [SI] Fase 1: User Admin
- [SI] Fase 2: AllowedImage Admin
- [SI] Fase 3: Service Admin
- [SI] Fase 4: Subject Admin
- [SI] Fase 5: UserProfile Admin
- [SI] Fase 6: UserProject Admin

**Tests de Regresión:**
- [SI] Funcionalidad existente intacta
- [SI] Panel del alumno no modificado

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
