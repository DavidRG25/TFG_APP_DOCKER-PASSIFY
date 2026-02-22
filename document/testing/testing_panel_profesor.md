# Plan de Testing: Panel de Profesor

**Fecha de Creación:** 21/02/2026

Este documento detalla las pruebas exhaustivas necesarias para validar la funcionalidad del Panel de Control Docente, garantizando que el diseño premium, los filtros de acceso y la gestión de la asignatura operan de manera correcta y segura.

## 1. Escenario: Dashboard de Resumen Global (`professor_dashboard`)

**Objetivo**: Validar la visualización correcta de métricas y la navegación general del panel del profesor.

- [ ] **Caso A: Interfaz y Métricas Generales**:
  - Iniciar sesión en rol Profesor/Teacher y navegar al Dashboard.
  - Observar las tarjetas de estadísticas globales superiores.
  - **Resultado Esperado**: Las 4 tarjetas deben mostrar un cómputo realista basado en los Subject y Projects del profesor (Asignaturas, Alumnos, Proyectos, Serv. Totales). Debe existir la tarjeta específica de "Serv. Totales" en color gris/secundario sin romper el grid CSS flex.
- [ ] **Caso B: Navegación de Asignaturas**:
  - En la sección "Mis Asignaturas", verificar que cada tarjeta de curso corresponde a las asignaturas donde el usuario es profesor.
  - Hacer clic en el botón `Gestionar Asignatura ->`.
  - **Resultado Esperado**: El enlace debe redirigir a la URL oficial de detalles de esa asignatura (`/professor/subjects/X/`).
- [ ] **Caso C: Visualización de Accesos Rápidos**:
  - Revisar la tabla inferior "Proyectos Desarrollados" en el Dashboard.
  - Comprobar que todos los proyectos listados correspondan a alumnos dentro de alguna asignatura o curso impartido por el profesor actual.
  - Hacer clic en el botón de acción de `Supervisar`.
  - **Resultado Esperado**: Redirección correcta a la vista individual de un proyecto.

## 2. Escenario: Gestión de Asignatura (`subject_detail`)

**Objetivo**: Confirmar que la vista de detalle de asignatura opera como pantalla de administración (creación de alumnos y proyectos) sin mezclar ruido de contenedores irrelevantes.

- [ ] **Caso A: Eliminación de la Vista a Granel**:
  - Entrar al detalle de una Asignatura (`/professor/subjects/X/`).
  - Inspeccionar todos los paneles de la pantalla.
  - **Resultado Esperado**: No debe aparecer la tabla técnica inferior con todos los contenedores en tiempo real. La interfaz debe restringirse puramente a mostrar alumnos y proyectos globales y el curso.
- [ ] **Caso B: Creación Rápida de Alumno (Modal)**:
  - En el panel "Alumnos Matriculados", pulsar el botón `+ Nuevo`.
  - Introducir credenciales falsas (Usuario, Nombre Completo, Email, Contraseña).
  - Enviar el formulario oculto `action="create_student"`.
  - **Resultado Esperado**: La página debe recargarse con un "Toast" o mensaje Django confirmando "Alumno creado exitosamente". El nuevo usuario debe aparecer listado en el recuadro con su avatar y nombre.
- [ ] **Caso C: Asignación Rápida de Proyecto (Modal)**:
  - En el panel "Proyectos de la Asignatura", pulsar el botón `+ Nuevo`.
  - Introducir un título descriptivo (ej. "Entrega Docker Compose").
  - En el desplegable (Select), certificar que el alumno creado en el "Caso B" aparece listado y seleccionarlo. Guardar.
  - **Resultado Esperado**: Un mensaje verde confirmará la asignación. El contador de la tarjeta "Proyectos" sumará 1 y aparecerá en la fila una vista previa del proyecto, mostrando a quién fue asignado.

## 3. Escenario: Supervisión de Proyecto (`project_detail`)

**Objetivo**: Garantizar que el docente puede observar estricta y únicamente los servicios correspondientes a ese proyecto y controlarlos con privilegios de supervisor (`is_supervisor=True`).

- [ ] **Caso A: Leak de Servicios (Aislamiento Total del Proyecto)**:
  - Crear un estudiante "Estudiante Z" y asignarle **dos** proyectos distintos ("Proyecto 1" y "Proyecto 2").
  - Usando la vista del Estudiante, crear servicios asociados uno al "Proyecto 1" y otros asociados al "Proyecto 2".
  - Entrar de nuevo como Profesor e ir a los detalles técnicos del "Proyecto 1".
  - **Resultado Esperado**: Única y exclusivamente deben listarse los servicios de entrega ligados a la ID de ese "Proyecto 1". Si se ven mezclados otros servicios o bases de datos del "Proyecto 2", la prueba fallará.
- [ ] **Caso B: Alineación Premium de las Columnas de la Tabla**:
  - Cargar la vista de detalles del proyecto y observar la tabla HTMX renderizada de los servicios.
  - **Resultado Esperado**: Debido al rol de profesor, la tabla debe añadir fluidamente la columna HTML de `Dueño` (con 7 columnas en el cabezal vs 7 celdas en las filas). La tabla no debe desconfigurarse mostrando imágenes donde deberían ir puertos o descripciones incorrectas.
- [ ] **Caso C: Master Switch "Pausar Todos"**:
  - Levantar (arrancar) 2 o más contenedores del proyecto.
  - Pulsar en la esquina superior derecha del panel de servicios de proyecto el botón rojo "Pausar Todos".
  - Confirmar el mensaje emergente de Javascript "Confirm: ¿Estás seguro...?".
  - **Resultado Esperado**: Django itera en backend el comando de paro `stop_container(svc)` recursivamente. Al refrescar, la tabla mostrará en color rojo `STOPPED` para todos los servicios del proyecto afectados, protegiendo contra fugas de memoria o bucles de CPU iniciados por el alumno.
- [ ] **Caso D: Uso de Botones Individuales de Intervención Docente**:
  - Hacer click en los iconos de las filas de contenedores (Botón Web en azul, Consola de Comandos o Logs).
  - **Resultado Esperado**: Todos deben permitir apertura sin restricción tipo `Access Denied 403` ya que el check `user_is_teacher(request.user)` y la protección heredada operan como permisos maestros sobre el dueño estandar del contenedor.

---

**Firmado:** PaaSify QA Team  
**Fecha de Revisión:** 2026-02-21
