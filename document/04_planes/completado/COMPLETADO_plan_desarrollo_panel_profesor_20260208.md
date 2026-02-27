# Plan de Desarrollo y Rediseño: Panel de Profesor (Fase Final)

**Fecha de Creación:** 08/02/2026  
**Estado:** ✅ Completado  
**Prioridad:** ALTA

---

## 🎯 OBJETIVO

Transformar el actual Panel de Profesor en una herramienta de gestión completa, permitiendo la administración de alumnado y proyectos sin depender del panel de administración global, manteniendo la estética **Premium** de PaaSify.

---

## 🔐 ROLES Y PERMISOS (CONTEXTO PROFESOR)

Para garantizar la seguridad y el flujo de trabajo docente, se establecen las siguientes reglas:

- **Restricción de Creación Goblal**: El Administrador es el único que puede crear **Profesores** y **Asignaturas**.
- **Perfil de Uso**: El profesor opera principalmente vía **Web**. No visualiza botones de "Despliegue Web" ni "Generador de Comandos", ya que su rol es de gestión y supervisión, no de despliegue propio.
- **Acceso a Documentación**: El profesor mantiene acceso a las **API Docs** para consultas técnicas.
- **Seguridad de Borrado**: El profesor **no puede eliminar** contenedores de alumnos a través de la interfaz Web (para evitar pérdida accidental de trabajo). El borrado queda reservado a la API o al Administrador.

---

## 📋 FUNCIONALIDADES A IMPLEMENTAR

### 1. Gestión de Asignaturas (Subject Management)

- [ ] **Gestión de Alumnado**:
  - Asignación de alumnos existentes a la asignatura.
  - **Generación de Alumnos**: Herramienta para crear nuevas cuentas de estudiantes directamente desde el panel de la asignatura.
- [ ] **Selector de "Imagen Recomendada"**: Marcar imágenes del catálogo para que aparezcan destacadas al alumno.

### 2. Gestión de Proyectos (Project Management)

- [ ] **Creación de Proyectos**: Permitir al profesor definir nuevos proyectos asociados a sus asignaturas (gestión de nombres y estructura, sin fechas límite).
- [ ] **Control Maestro**: Botón de "Pausar todos" para detener todos los servicios de una asignatura de forma masiva.

### 3. Supervisión Técnica y Soporte

- [ ] **Intervención en Servicios de Alumno**:
  - Botones de control total: **Encender**, **Apagar** y **Reiniciar**.
  - Herramientas de soporte: Acceso a **Terminal interactiva**, **Logs de consola** y **Acceso Web** (URL) a los servicios desplegados por sus alumnos.
- [ ] **Monitorización**: Gráficos de consumo (CPU/RAM) acumulado por asignatura.

---

## 🎨 REDISEÑO PREMIUM (UI/UX)

- [x] **Dashboard Principal**:
  - Sustituir la lista simple de asignaturas por un **Grid de Cards Premium** con estadísticas de la clase.
  - Eliminar botones de despliegue innecesarios para el rol docente.
- [x] **Tablas de Seguimiento**:
  - Uso de avatares para alumnos.
  - Badges de estado modernos y acceso rápido a la terminal del alumno.
- [x] **Modales de Gestión**: Estilizados con el sistema de diseño premium (sombras, redondez, colores corporativos).

---

## 📊 FASES DE EJECUCIÓN

1. **Fase A (Estructura)**: ✅ Completada - URLs y vistas base funcionando.
2. **Fase B (Supervisión)**: ✅ Completada - Implementados controles de servicio (Start/Stop), Logs y Terminal desde el panel de profesor.
3. **Fase C (Diseño)**: ✅ Completada - Dashboard y detalles actualizados al estándar Premium.
4. **Fase D (Gestión Continua)**: ✅ Completada - Implementación de creación de alumnos y proyectos.

---

## 🚀 CRITERIOS DE ÉXITO Y VALIDACIÓN

1. El profesor puede dar de alta a sus alumnos y crear proyectos sin usar el `/admin/`.
2. El profesor tiene herramientas de soporte (terminal/logs) para ayudar a los alumnos.
3. Se respeta la restricción de borrado en web y la ocultación de herramientas de despliegue propio.
4. La estética es 100% consistente con el "Modo Premium" de PaaSify.

**IMPORTANTE**: Una vez finalizado el desarrollo de todas las funcionalidades de gestión de este plan, se deberá crear un **Documento de Testing específico para el Panel de Profesor** que verifique la seguridad de los roles y la correcta ejecución de todas las herramientas de administración y soporte.
