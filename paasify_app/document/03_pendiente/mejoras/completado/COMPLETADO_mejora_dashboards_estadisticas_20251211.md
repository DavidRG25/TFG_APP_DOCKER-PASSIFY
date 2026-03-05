# Mejora de Diseño: Dashboards con Estadísticas y Contexto de Usuario

**Fecha:** 11/12/2025 14:53  
**Tipo:** Mejora de UX/UI  
**Prioridad:** Media  
**Estado:** COMPLETADO

## Descripción

Mejorar los dashboards de estudiante y profesor añadiendo información contextual y estadísticas visuales para una mejor experiencia de usuario.

## Contexto

El plan de mejoras UI/UX (`plan_mejoras_ui_tokens_20251124-2252`) está completado en su funcionalidad core (~80%), pero faltan refinamientos visuales en los dashboards que fueron parte de la Fase 3 del plan original.

## Mejoras Pendientes

### 1. Dashboard de Estudiante (`student_panel.html`)

**Elementos a añadir:**

- [ ] Header con información del alumno (nombre completo, email)
- [ ] Sección "Mis asignaturas" con cards visuales
  - Mostrar asignaturas matriculadas
  - Indicador visual de año/categoría
  - Enlace rápido a cada asignatura
- [ ] Mejora visual de la tabla de servicios
  - Iconos de estado más prominentes
  - Colores diferenciados por tipo de servicio

**Ubicación sugerida:**

- Header: Justo debajo de la barra de navegación
- Sección asignaturas: Entre el header y las estadísticas actuales

### 2. Dashboard de Profesor (`professor/dashboard.html`)

**Elementos a añadir:**

- [ ] Sección de estadísticas con cards
  - Total de asignaturas impartidas
  - Total de alumnos (sumando todas las asignaturas)
  - Servicios activos de alumnos
  - Proyectos creados
- [ ] Cards con métricas visuales
  - Gráficos simples (barras o donuts)
  - Colores diferenciados por métrica
- [ ] Mejora de tabla de proyectos
  - Filtros por asignatura
  - Paginación si hay muchos proyectos
  - Ordenación por columnas

### 3. Navegación (Opcional - Mejora adicional)

**Mejora sugerida:**

- [ ] Convertir enlaces de usuario en menú desplegable
  - Actualmente: Enlaces directos en barra lateral
  - Propuesta: Dropdown en esquina superior derecha
  - Contenido: Avatar + nombre, "Mi perfil", "Mis asignaturas", "Cerrar sesión"

## Beneficios Esperados

1. **Contexto inmediato**: Usuario sabe quién es y qué asignaturas tiene al entrar
2. **Navegación más rápida**: Acceso directo a asignaturas desde dashboard
3. **Información relevante**: Profesor ve métricas clave de un vistazo
4. **Mejor UX**: Interfaz más informativa y profesional

## Archivos a Modificar

```
templates/containers/student_panel.html
templates/professor/dashboard.html
templates/base.html (opcional, para menú desplegable)
staticfiles/assets/css/dashboard.css (estilos adicionales)
```

## Referencias

- Plan original: `document/plan/completado/plan_mejoras_ui_tokens_20251124-2252_COMPLETADO.md`
- Fase 3 del plan (líneas 124-169)

## Notas

Esta mejora es **cosmética** y no afecta la funcionalidad existente. El sistema funciona correctamente sin estos cambios, pero mejoraría significativamente la experiencia de usuario.

---

_Creado automáticamente al completar el plan de mejoras UI/UX_
