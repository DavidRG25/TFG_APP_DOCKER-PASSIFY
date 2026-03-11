# Plan de Testing Manual: Mejoras Admin Panel

**Fecha:** 11/03/2026  
**Tester:** David  
**Referencia:** `implementacion_mejoras_admin_20260311.md`
**Resultado:** COMPLETADO

---

## 📋 Instrucciones Generales

1. Arranca el servidor con `bash run.sh`
2. Accede al admin en `http://localhost:8000/admin/`
3. Inicia sesión con la cuenta admin
4. Sigue cada test en orden, marcando cada checkbox cuando se complete exitosamente.

---

## TEST 1: Exportar Usuarios a CSV (Mejora 1.1)

**Ubicación:** Admin → Autenticación y Autorización → Usuarios

- [SI] 1.1 Ir a la lista de Usuarios y ver que se muestra la tabla con todos los usuarios.
- [SI] 1.2 Seleccionar 2-3 usuarios con el checkbox a la izquierda.
- [SI] 1.3 En el dropdown de acciones superior, buscar y seleccionar la opción **"Exportar usuarios seleccionados a CSV"**.
- [SI] 1.4 Pulsar el botón azul **"EJECUTAR"** y verificar que se descarga el archivo `usuarios_paasify.csv`.
- [SI] 1.5 Abrir el CSV en Excel (o bloc de notas) y verificar que las columnas (Username, Email, Nombre, Rol, etc.) están separadas correctamente por `;`.
- [SI] 1.6 Verificar que los roles se identifican bien (Admin, Profesor, Alumno).
- [SI] 1.7 Comprobar que no hay problemas con tildes o caracteres especiales (BOM UTF-8 funcionando).

---

## TEST 2: Columna Última Conexión en Usuarios (Mejora 1.3)

**Ubicación:** Admin → Autenticación y Autorización → Usuarios

- [SI] 2.1 En la tabla de Usuarios, verificar que existe la nueva columna **"Última conexión"**.
- [SI] 2.2 Buscar tu usuario actual (admin) y comprobar que el texto pone algo como **"Hace unos minutos"** o "Hoy".
- [SI] 2.3 Buscar un usuario de prueba que no se haya logueado nunca y asegurar que pone **"Nunca"**.
- [SI] 2.4 Hacer clic en el título de la cabecera "Última conexión" y comprobar que la tabla se reordena correctamente por este campo.

---

## TEST 3: Filtro por Tipo de Imagen en Servicios (Mejora 3.1)

**Ubicación:** Admin → Containers → Servicios

- [SI] 3.1 Navegar a la sección de Servicios.
- [SI] 3.2 Mirar en los menús desplegables superiores y verificar que existe el filtro **"Tipo de imagen"**.
- [SI] 3.3 Hacer clic en **"🌐 Web / Frontend"** y verificar que en la tabla solo se muestran servicios cuya imagen sea de este tipo.
- [SI] 3.4 Hacer clic en **"⚙️ Personalizado"** y verificar que filtra mostrando solo servicios instanciados vía Dockerfile o Docker Compose subido por el alumno.
- [SI] 3.5 Seleccionar **"---------"** en el desplegable para limpiar este filtro.

---

## TEST 4: Acciones masivas de Servicios (Mejora 3.2 y adicionales)

**Ubicación:** Admin → Containers → Servicios  
**Prerrequisito:** Tener al menos 1 servicio con contenedor Docker activo (status=running o stopped).

- [SI] 4.1 Marcar el checkbox de 1 servicio que tenga el contenedor activo.
- [SI] 4.2 Clic en el desplegable de acciones, seleccionar **"Reiniciar servicios seleccionados"** y darle a **"EJECUTAR"**.
- [SI] 4.3 Comprobar que arriba sale un mensaje verde que dice **"✅ 1 reiniciado(s)"** y que su estado pasa a "running".
- [SI] 4.4 Seleccionar 1 servicio que esté "running", elegir **"Detener servicios seleccionados"** y verificar que cambia a **"stopped"**.
- [SI] 4.5 Seleccionar el mismo servicio (ahora 'stopped'), elegir **"Iniciar servicios seleccionados"** y comprobar que vuelve a **"running"**.
- [SI] 4.6 Marcar un par de servicios y elegir **"Exportar a CSV Excel"**. Comprobar que el archivo `servicios.csv` se descarga correctamente, separado por `;` y sin problemas de formatos.
- [SI] 4.7 Seleccionar un servicio sin contenedor (removed) e intentar cualquiera de las acciones de docker, verificando que avise de **"⚪ ignorados / sin contenedor"**.

---

## TEST 5: Exportar Alumnos de Asignaturas a CSV (Mejora 4.2)

**Ubicación:** Admin → Paasify → Asignaturas

- [SI] 5.1 En la vista de lista de Asignaturas, seleccionar 1 o 2 materias con el checkbox.
- [SI] 5.2 Ejecutar la acción **"Exportar alumnos de asignaturas seleccionadas a CSV"** dándole a **"EJECUTAR"**.
- [SI] 5.3 Verificar que se descarga el fichero `alumnos_asignaturas.csv`.
- [SI] 5.4 Abrir el CSV con Excel y confirmar que los datos se leen correctamente.
- [SI] 5.5 Comprobar que en la columna "Servicios Activos" muestra una relación (ej: "1/3") o "0", indicando cuántos servicios tiene encendidos frente a totales ese alumno en esa asignatura.

---

## TEST 6: Columna Última Conexión en Perfiles de Alumnos (Mejora 5.3)

**Ubicación:** Admin → Paasify → Perfiles de alumnos

- [SI] 6.1 Revisar que la tabla de perfiles ahora tiene la columna **"Última conexión"**.
- [SI] 6.2 Comprobar visualmente que el cálculo del tiempo concuerda (Hace X días, Hace unos minutos...).
- [SI] 6.3 Hacer clic sobre la cabecera de esta columna para verificar que se ordena de mayor a menor y viceversa sin errores.

---

## TEST 7: Filtro por Estado del Proyecto (Mejora 6.1)

**Ubicación:** Admin → Paasify → Proyectos asignados

- [SI] 7.1 Mirar en los menús desplegables superiores el nuevo filtro **"Estado del Proyecto"**.
- [SI] 7.2 Filtrar por **"✅ Todos activos"** y comprobar que los que devuelve tienen todos sus contenedores Docker corriendo.
- [SI] 7.3 Filtrar por **"⚪ Sin servicios"** y ver si devuelve correctamente aquellos que no tienen ni un solo servicio subido por el alumno.
- [SI] 7.4 Comprobar los flujos de "Detenido" y "Parcialmente activo" si da tiempo a montar esos escenarios (alguno activo y otro parado a propósito).
- [SI] 7.5 Limpiar el filtro seleccionando **"---------"**.

---

## TEST 8: Verificaciones Generales

- [SI] 8.1 Dar una vuelta general visualmente para garantizar que no hay errores 500 al navegar entre secciones del admin.
- [SI] 8.2 Comprobar que los filtros antiguos, como el filtro de **Rol** en Perfiles de Alumno, siguen apareciendo y funcionan sin reventar.
- [SI] 8.3 Comprobar que la acción antigua de **Refrescar Tokens API** tampoco se ha sobrescrito, sigue ahí disponible.
