# Plan de Tareas - Reunión 03/03/2026

**Fecha**: 04-03-2026
**Estado**: Pendiente
**Origen**: Feedback de revisión final con el profesor.

---

## 📋 Lista de Tareas y Ajustes

### UI / Presentación

- [Si] **Texto y emoticonos separados**: Revisar todos los paneles para asegurar que los emoticonos y los textos no están unidos sin espacios, asegurando una estética limpia.
- [Si] **Mejoras Modal Asignatura (Nueva/Editar)**: Implementar previsualización de logo, botón para limpiar logo, reinicio del formulario al cerrar y validación estricta del nombre del archivo (< 90 caracteres).
- [Si] **Renombrar panel**: Cambiar el nombre del panel superior/lateral de "Proyectos" a "Mis Servicios".
- [Si] **Panel de personalización más pequeño**: Ajustar el tamaño del panel de diseño/personalización para que no ocupe demasiado espacio en pantalla.
- [Si] **Panel "No estás matriculado" visual**: Mejorar el diseño del panel vacío que se muestra cuando un alumno no tiene asignaturas, haciéndolo más amigable/visual y validando correctamente el estado de su sesión.
- [Si] **Visualización de proyectos vacíos**: Permitir que los profesores/alumnos puedan ver y entrar en proyectos que todavía no tienen servicios asociados.
- [Si] **Cerrar botón cerrar sesión**: Arreglar/Ajustar el comportamiento o estilo del botón de cerrar sesión.

### Funcionalidades de Carga (Excel)

- [Si] **Carga masiva por Excel**: Implementar/afinar la importación de datos.
- [Si] **Creación de alumnos por Excel**: Cargar una lista de alumnos a partir de un archivo Excel.
- [Si] **Generación de proyectos desde Excel**: A partir de la carga de alumnos, auto-generar sus proyectos/espacios de trabajo automáticamente.
- [Si] **Selección múltiple de alumnos**: Permitir que al vincular alumnos existentes a un proyecto/asignatura se puedan seleccionar múltiples a la vez en lugar de uno por uno.

### APIs y Documentación

- [Si] **Colección Postman exportable**: A partir de nuestra documentación OAS (Swagger/drf-spectacular), generar un JSON de Postman o un mecanismo que permita descargar un archivo directo para importarlo en Postman.
  - **Esquema de mejoras adicionales aportadas al testing de Postman**:
    - _Autenticación Dinámica_: Neutralización de `cookieAuth` individual para priorizar autenticación en cascada `Inherit auth from parent` y no depender de pre-scripts.
    - _URLs Resolutivas_: Eliminado el path absoluto roto de exportación DRF (`/api/`) e instanciado un `baseUrl` iterativo a base de Host Request Django.
    - _Semántica Limpia_: Translación automática de `operationIds` internos (`api_containers_create`) por etiquetas de lectura humana (`Create container`).
    - _Inyección de Ejemplos_: Los métodos POST y dependientes de Compose ahora cuentan con Bodies auto-completados por defecto con plantillas Json.
    - _Documentación Estructurada_: Implementación de descripciones formales Markdown tanto en subcarpetas de interfaz como en métodos específicos.
    - _Exportación OpenAPI Nivelada_: Generación dinámica paralela a drf-spectacular del mismo JSON pero adaptado 100% a la especificación estándar Postman/OpenAPI sin depender de librerías extraídas.
    - _Guía de API Docs Incorporada_: Creación de un documento volcado/guía (sección interactiva dentro del portal) con equivalente funcionalidad semántica para acompañar la experiencia técnica del usuario con ejemplos visuales y explicaciones precisas.
- [Si] **Menú Profesor - API Docs**: El enlace a `API-DOCS` debe estar visible también en el panel del profesor, no solo en el del admin o alumno.

### Seguridad y Sesiones

- [Si] **Timeout de sesión**: Ajustar la configuración de la sesión en Django para que caduque automáticamente por inactividad.
- [Si] **Cambio de contraseña forzado del Admin**: Al hacer login por primera vez con el superusuario (admin), el sistema debe forzar obligatoriamente el cambio de contraseña por seguridad.

### Bugs / Fixes detectados

- [Si] **Bug ZIP Docker Compose**: Resolver problema de validación frontend donde el formulario exige falsamente subir un archivo ZIP al desplegar una configuración `docker-compose.yml`.
- [Si] **Admin de profesores**: Resolver el bug en el panel de administrador donde los "Perfiles de profesores" no están cargando correctamente los usuarios asociados.
- [Si] **Despliegue README hardcodeado**: Revisar `deploy/README.md` (o la conf real) porque actualmente figura un `server_name` quemado ("a cañón") con una URL específica en lugar de una variable.

### Feedback Tutor (20/03/2026) 🎓

- [Si] **Optimizar Git Sparse-Checkout**: Revisar por qué se clona todo el repo en lugar de solo la carpeta `deploy` y corregir el comando en el README.
- [Si] **Limpiar Warnings Docker**: Eliminar `version: "3.8"` de los archivos compose ya que es obsoleto y provoca advertencias.
- [Si] **Documentación de Certificados**: Añadir guía paso a paso de cómo generar o sustituir los certificados SSL y el `server_name` de Nginx.
- [Si] **Requisito apache2-utils**: Notificar o documentar que `htpasswd` requiere la instalación de `apache2-utils`.
- [Si] **Fix UI: Spinner infinito en errores**: Corregir el bug donde el spinner de "Creando servicio..." no desaparece si falla el despliegue de un Docker Compose.

### CI / CD

- [ ] **Montar el modelo GitHub Action**: Establecer y configurar los flujos de GitHub Actions para el empaquetado y subida del contenedor directamente desde el refactor realizado.

---

### Mejoras Extras (Implementadas)

- [Si] **Rediseño de Checkboxes y Selección de Filas**: Checkboxes estilizados, con márgenes correctos (evitando pisar íconos), y con selección avanzada mediante clic en toda la fila (alumnos y proyectos).
- [Si] **Gestión Múltiple en Tabla**: Añadida funcionalidad no planificada para seleccionar y desmatricular/eliminar múltiples alumnos y proyectos a la vez, con contadores visuales y botones de acción dinámicos.
- [Si] **UI de Checkbox de Contraseña**: Transformado el checkbox estándar de "Obligar a cambiar contraseña" en los modales de alumno a un gran botón interactivo vinculado lógicamente al color principal de la Asignatura.
- [Si] **Seguimiento de Actividad de Alumnos**: Añadida una nueva columna "Última Actividad" en la tabla de proyectos del panel de profesor que calcula la fecha/hora en la que los servicios de un proyecto fueron editados o iniciados por última vez. Incluye un tooltip de información estilizado para aclarar su funcionamiento.
- [Si] **Ajustes Flexbox en Modal de Asignatura**: Solucionados los problemas de clases CSS de Bootstrap que hacían que determinados iconos (sombrero principal, imágenes de logo y paletas de color) se acoplaran al texto adyacente dentro del formulario "Nueva Asignatura".
- [Si] **Espaciado en Página de Perfil**: Refinamiento por todo el panel de Control de Cuenta, Seguridad y Token API separando exhaustivamente los iconos que se apilaban sobre los textos de los botones tras cargar las hojas de estilos personalizadas.

---

## 🛠 Plan de Acción

1. **Fase 1: Fixes Rápidos y Textos** (UI, Bugs directos, renombres).
2. **Fase 2: Autenticación y Seguridad** (Sesiones inactivas, Cambio forzado de clave Admin).
3. **Fase 3: Importaciones Excel y Gestión Múltiple** (Lógica de pandas/openpyxl, lógica de BD masiva).
4. **Fase 4: Documentación y CI/CD** (Postman, README deploy, GH Actions).

---

## 📧 ANEXO: Correo del Tutor (20-03-2026)

**Asunto**: Feedback revisión local y despliegue.

> Buenas tardes David,
> 
> Por fin he podido lanzarlo en local con calma. Algunos comentarios:
> 
> **1. Despliegue Git Sparse**:
> Al arrancar utilizas lo siguiente, pero creo que no consigue su objetivo de no clonar todo el proyecto (se acaba clonando todo completo)
> ```bash
> mkdir PaaSify && cd PaaSify
> git clone --no-checkout --sparse https://github.com/DavidRG25/TFG_APP_DOCKER-PASSIFY.git .
> git sparse-checkout set deploy
> git checkout main
> ```
> 
> **2. Compose Version Warning**:
> Ya no es necesario usar el `version: "3.8"`, salta un warning.
> 
> **3. Certificados y Configuración Nginx**:
> Los certificados siguen a fuego en la configuración, debería indicarse cómo generar uno nuevo/sustituirlo. Los certificados incluidos son los de producción, al igual que el `server_name` de la config de nginx.
> 
> **4. Herramientas del sistema**:
> `htpasswd -c .htpasswd admin` -> La herramienta no está instalada por defecto en los sistemas: `sudo apt install apache2-utils`
> 
> **5. Bug UI (Spinner Bloqueado)**:
> He probado a subir un docker compose que parece que no es válido: me dices correctamente el error, sin embargo, como **se queda el spinner dando vueltas**, me toca recargar la página.
> 
> He probado otro Docker Compose y parece que todo iba bien.
> 
> **6. Postman**:
> Respecto a lo de Postman, no he conseguido encontrarlo, quizás no estaba subido aún.
> 
> Cuando tengas los cambios restantes, los puedo probar directamente en el de producción.
> 
> Muchas gracias por tu trabajo, David, está quedando muy redondo.
> 
> Un saludo.

### 🌟 Mejoras Adicionales y Evolución (Extra)

Se han completado un conjunto de mejoras transversales documentadas en el plan adicional:
[COMPLETADO_plan_mejoras_adicionales_20251128.md](file:///c:/Users/david/OneDrive/Escritorio/TFG/TGF_APP_DOCKER-PASSIFY/paasify_app/document/04_planes/completado/COMPLETADO_plan_mejoras_adicionales_20251128.md)

**Resumen de lo realizado (Esquema):**

1. **Admin Panel**: Filtros avanzados por tipo de imagen y estado real de Docker.
2. **Bulk Actions**: Reinicio masivo de servicios, exportación a CSV (BOM Excel) y refresco de tokens API.
3. **Persistencia**: Sistema de volúmenes automáticos y persistencia garantizada en reinicios.
4. **Seguridad**: Cambio obligado de clave, tokens API con caducidad de 30 días y auditoría.
5. **UI/UX**: Toasts premium (fondo blanco/dorado), micro-animaciones y espaciado corregido en todo el panel.
6. **Docker Engine**: Soporte completo para Compose multi-contenedor con mapeo de puertos dinámico.
