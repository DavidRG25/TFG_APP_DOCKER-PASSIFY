# 🎨 Plan: Rediseño de Paneles de Servicios (Alumno + Profesor)

> [!IMPORTANT]
> **Estado: COMPLETADO ✅**
> Todas las fases del rediseño (Vista Alumno y Vista Profesor) han sido implementadas
> exitosamente, incluyendo la lógica de agrupación, buscador mejorado y gestión de proyectos.

---

## 📋 Índice

1. [Objetivo](#1-objetivo)
2. [Problemas Actuales](#2-problemas-actuales)
3. [Diseño Propuesto: Vista Alumno](#3-diseño-propuesto-vista-alumno)
4. [Diseño Propuesto: Vista Profesor](#4-diseño-propuesto-vista-profesor)
5. [Diferencias por Rol](#5-diferencias-por-rol)
6. [Componentes Compartidos](#6-componentes-compartidos)
7. [Fases de Implementación](#7-fases-de-implementación)
8. [Detalles Técnicos](#8-detalles-técnicos)
9. [Estimación de Tiempos](#9-estimación-de-tiempos)

---

## 1. Objetivo

Transformar las vistas de servicios de **tablas planas** a **estructuras jerárquicas**
organizadas por roles:

- **Alumno**: Servicios agrupados por proyecto → visión operativa ("mis cosas")
- **Profesor**: Servicios agrupados por alumno → visión de supervisión ("qué hacen mis alumnos")

### Resultado esperado

| Antes                                       | Después                        |
| ------------------------------------------- | ------------------------------ |
| Tabla plana con 7+ columnas                 | Acordeones jerárquicos limpios |
| 7-8 botones de acción por fila              | 2-3 botones + menú `⋮`         |
| Información repetida (proyecto, asignatura) | Agrupada, sin redundancia      |
| Misma vista para todos los roles            | Vista adaptada por rol         |

---

## 2. Problemas Actuales

### 2.1 Vista Alumno ("Mis Servicios")

- Columnas "Asignatura" y "Proyecto" se repiten en cada fila.
- 7-8 botones de acción por fila, difíciles de distinguir.
- Botón de eliminar junto al de reiniciar → clics accidentales.
- Sin agrupación visual → el alumno no ve sus proyectos organizados.

### 2.2 Vista Profesor ("Detalle de Asignatura")

- Misma estructura de tabla plana que el alumno.
- No se ve qué alumnos tienen servicios activos de un vistazo.
- No hay indicadores de límite de recursos.
- No hay visión de supervisión (cuántos servicios tiene cada alumno).

---

## 3. Diseño Propuesto: Vista Alumno

### 3.1 Cabecera

```
🏠 Inicio / Mis Servicios

┌─────────────────────────────────────────────────────────────┐
│  📦 Mis Servicios                        [API/CLI] [+ Nuevo]│
│  Gestiona y despliega tus servicios                         │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Tarjetas de resumen (se mantienen)

```
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ SERVICIOS    │ │ ACTIVOS      │ │ DETENIDOS    │ │ ASIGNATURAS  │
│     6        │ │     4  🟢    │ │     2  ⚫    │ │     5        │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

### 3.3 Filtros (se mantienen)

```
🔍 Filtrar recursos
┌─────────────────────┐ ┌─────────────────────┐
│ Asignatura ▾        │ │ Proyecto ▾           │  [🔍 Buscar]
└─────────────────────┘ └─────────────────────┘
```

### 3.4 Estructura principal: Agrupación por Proyecto

```
┌─────────────────────────────────────────────────────────────┐
│ 📂 Asignatura 1                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ▼ proyecto1  (4 servicios · 1 ejecutando · 3 detenidos)     │
│ ┌───────────────────────────────────────────────────────────┐│
│ │ SERVICIO              IMAGEN        PUERTO    ESTADO  ACC ││
│ │─────────────────────────────────────────────────────────  ││
│ │ miniapp-testing       nginx:latest  49123     🟢 RUN  [▶][■][⋮] ││
│ │ prueba-imagen         nginx:latest  46993     ⚫ STOP [▶][⋮]     ││
│ │ p1-dockerfile         custom        41309     ⚫ STOP [▶][⋮]     ││
│ │ p1                    nginx:latest  48436     ⚫ STOP [▶][⋮]     ││
│ └───────────────────────────────────────────────────────────┘│
│                                                    [+ Crear]│
│                                                             │
│ ▶ proyecto 3  (1 servicio · 0 ejecutando)          [+ Crear]│
│                                                             │
│ ▶ Despliegue Multi  (1 servicio · 1 ejecutando)             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.5 Botones de Acción del Alumno

**Visibles directamente** (según estado del servicio):

| Estado      | Botones visibles                    |
| ----------- | ----------------------------------- |
| `running`   | `[■ Stop]` `[⋮]`                    |
| `stopped`   | `[▶ Start]` `[⋮]`                   |
| `error`     | `[▶ Start]` `[⋮]`                   |
| Transitorio | Sin botones (solo spinner en badge) |

**Dentro del menú `⋮`**:

```
┌─────────────────┐
│ 🔄 Reiniciar    │
│ 📜 Logs         │
│ ✏️ Editar       │
│ >_ Terminal     │
│ ─────────────── │
│ 🗑 Eliminar     │  ← Color rojo, separado visualmente
└─────────────────┘
```

**Reglas clave**:

- Solo mostrar el botón de acción que tiene sentido según el estado.
- Eliminar siempre dentro del menú `⋮`, nunca visible directamente.
- Acciones destructivas (Eliminar) separadas con un divisor y en rojo.

---

## 4. Diseño Propuesto: Vista Profesor

### 4.1 Cabecera con contexto académico

```
🏠 Inicio / Asignaturas / Sistemas Cloud y Contenedores

┌─────────────────────────────────────────────────────────────┐
│  📚 Sistemas Cloud y Contenedores        [API/CLI] [+ Nuevo]│
│  Prof. David Rodríguez · Curso 2025/2026                    │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Tarjetas de resumen (enfocadas a supervisión)

```
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ 👥 ALUMNOS   │ │ 📂 PROYECTOS │ │ 🐳 SERVICIOS │ │ 🟢 RUNNING   │ │ 🔴 STOPPED   │
│     18       │ │     9        │ │     32       │ │     21       │ │     11       │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

### 4.3 Filtros para profesor

```
🔍 Filtrar
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐
│ Alumno ▾     │ │ Proyecto ▾   │ │ Estado ▾     │ │ Ordenar por ▾        │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────────────┘

Opciones de "Ordenar por":
- Nombre del alumno (A-Z)
- Número de servicios (mayor a menor)
- Servicios activos
- Última actividad
```

### 4.4 Estructura principal: Agrupación por Alumno

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│ ▼ 👤 Diego Costa Fernández                                  │
│   Servicios: 7/5 ❗ (límite superado)                       │
│   🟢 4 activos · 🔴 3 detenidos · Última actividad: hace 1h│
│ ┌───────────────────────────────────────────────────────────┐│
│ │                                                           ││
│ │ 📂 Proyecto: API Final                                    ││
│ │ ┌───────────────────────────────────────────────────────┐ ││
│ │ │ SERVICIO        IMAGEN        PUERTO    ESTADO   ACC  │ ││
│ │ │ backend-api     node:18       49123     🟢 RUN  [■][⋮]│ ││
│ │ │ db-mysql        mysql:8       49124     🔴 STOP [▶][⋮]│ ││
│ │ └───────────────────────────────────────────────────────┘ ││
│ │                                                           ││
│ │ 📂 Proyecto: Web Fullstack                                ││
│ │ ┌───────────────────────────────────────────────────────┐ ││
│ │ │ nginx           nginx:alpine  49130     🟢 RUN  [■][⋮]│ ││
│ │ │ flask-app       python:3.11   49131     🟢 RUN  [■][⋮]│ ││
│ │ │ redis           redis:7       -         🟢 RUN  [■][⋮]│ ││
│ │ └───────────────────────────────────────────────────────┘ ││
│ └───────────────────────────────────────────────────────────┘│
│                                                             │
│ ▶ 👤 María López Fernández                                  │
│   Servicios: 3/5 ✅   🟢 2 · 🔴 1 · Última actividad: 3h  │
│                                                             │
│ ▶ 👤 Carlos Martínez Ruiz                                   │
│   Servicios: 0/5   ⚠️ Sin servicios                         │
│                                                             │
│ ▶ 👤 Ana Fernández García                                   │
│   Servicios: 5/5 ✅   🟢 3 · 🔴 2 · Última actividad: 20m │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.5 Indicadores de supervisión por alumno

En la cabecera de cada acordeón de alumno:

| Indicador              | Significado                    | Visual             |
| ---------------------- | ------------------------------ | ------------------ |
| `Servicios: 3/5 ✅`    | Dentro del límite              | Verde / check      |
| `Servicios: 7/5 ❗`    | Superó el límite               | Rojo / exclamación |
| `Servicios: 0/5 ⚠️`    | Sin servicios (inactividad)    | Amarillo / warning |
| `Última actividad: 3h` | Cuándo fue la última operación | Texto gris         |

Estos indicadores son **oro puro para el tribunal**: demuestran control académico real.

### 4.6 Acciones del Profesor

**Visibles directamente** (según estado):

| Estado    | Botones visibles  |
| --------- | ----------------- |
| `running` | `[■ Stop]` `[⋮]`  |
| `stopped` | `[▶ Start]` `[⋮]` |

**Dentro del menú `⋮` del profesor**:

```
┌─────────────────┐
│ 🔄 Reiniciar    │
│ 📜 Ver Logs     │
│ 🔍 Ver Detalle  │
│ ─────────────── │
│ 🗑 Eliminar     │  ← Solo si es necesario
└─────────────────┘
```

**A nivel de alumno** (no de servicio), un botón adicional:

```
┌─────────────────────┐
│ ⚙️ Gestionar límites │  ← Modal con: máx. servicios, máx. CPU, etc.
└─────────────────────┘
```

### 4.7 Límites por alumno (funcionalidad extra)

Modal "Gestionar límites":

```
┌──────────────────────────────────────────────┐
│ ⚙️ Límites para Diego Costa Fernández        │
│                                              │
│ Máx. servicios:  [  5  ] ▲▼                  │
│ Máx. servicios activos simultáneos: [ 3 ] ▲▼ │
│                                              │
│              [Cancelar]  [Guardar]           │
└──────────────────────────────────────────────┘
```

> **Nota**: Esta funcionalidad de límites es un extra que requiere añadir
> campos al modelo (ej: `max_services` en `UserProfile` o en la relación
> alumno-asignatura). Es opcional pero muy impactante en la defensa.

---

## 5. Diferencias por Rol

| Aspecto               | 🎓 Alumno                                             | 👨‍🏫 Profesor                                             |
| --------------------- | ----------------------------------------------------- | ------------------------------------------------------- |
| **Título**            | "Mis Servicios"                                       | Nombre de la asignatura                                 |
| **Agrupación**        | Por proyecto                                          | Por alumno → proyecto                                   |
| **Stats**             | Mis servicios/activos/detenidos                       | Alumnos/proyectos/servicios totales                     |
| **Filtros**           | Asignatura + Proyecto                                 | Alumno + Proyecto + Estado + Orden                      |
| **Acciones**          | Start, Stop + menú (editar, logs, terminal, eliminar) | Start, Stop + menú (reiniciar, logs, detalle, eliminar) |
| **Editar servicio**   | ✅ Sí (es suyo)                                       | ❌ No (no edita servicios de alumnos)                   |
| **Terminal**          | ✅ Sí                                                 | ❌ No                                                   |
| **Eliminar**          | ✅ Solo los suyos                                     | ✅ Puede eliminar cualquiera                            |
| **Indicadores extra** | No                                                    | Límites, última actividad, alertas                      |
| **Enfoque**           | Operativo ("hacer cosas")                             | Supervisión ("ver qué pasa")                            |

---

## 6. Componentes Compartidos

Ambas vistas comparten componentes base para evitar duplicación de código:

### 6.1 Partial: Badge de estado (`_status.html`)

- Ya existe y funciona para ambos roles.
- No requiere cambios.

### 6.2 Partial: Menú de acciones (`_actions_menu.html`) — NUEVO

```html
{# Botones visibles según estado #} {% if service.status == 'running' %}
<button class="btn btn-sm btn-warning" title="Detener">
  <i class="fas fa-stop"></i>
</button>
{% elif service.status == 'stopped' or service.status == 'error' %}
<button class="btn btn-sm btn-success" title="Iniciar">
  <i class="fas fa-play"></i>
</button>
{% endif %} {# Menú kebab #}
<div class="dropdown d-inline-block">
  <button class="btn btn-sm btn-outline-secondary" data-bs-toggle="dropdown">
    <i class="fas fa-ellipsis-v"></i>
  </button>
  <ul class="dropdown-menu dropdown-menu-end">
    <li>
      <a class="dropdown-item"><i class="fas fa-sync me-2"></i>Reiniciar</a>
    </li>
    <li>
      <a class="dropdown-item"><i class="fas fa-file-alt me-2"></i>Logs</a>
    </li>
    {% if user_is_owner %}
    <li>
      <a class="dropdown-item"><i class="fas fa-edit me-2"></i>Editar</a>
    </li>
    <li>
      <a class="dropdown-item"><i class="fas fa-terminal me-2"></i>Terminal</a>
    </li>
    {% endif %}
    <li><hr class="dropdown-divider" /></li>
    <li>
      <a class="dropdown-item text-danger"
        ><i class="fas fa-trash me-2"></i>Eliminar</a
      >
    </li>
  </ul>
</div>
```

### 6.3 Partial: Tabla de servicios (`_services_table.html`) — NUEVO

- Tabla reutilizable que muestra servicios de un proyecto.
- Recibe una lista de servicios como contexto.
- Usada tanto por la vista de alumno como por la de profesor.

### 6.4 Partial: Acordeón colapsable (`_accordion_item.html`) — NUEVO

- Componente genérico de acordeón Bootstrap.
- Usado para envolver proyectos (alumno) o alumnos (profesor).

---

## 7. Fases de Implementación

### Fase 1: Menú de acciones `⋮` (impacto inmediato, mínimo esfuerzo)

- [ ] Crear partial `_actions_menu.html`
- [ ] Reemplazar los 7-8 botones actuales por el nuevo menú
- [ ] Mostrar solo botón relevante según estado (Play O Stop, nunca ambos)
- [ ] Testear que todas las acciones HTMX siguen funcionando

### Fase 2: Vista Alumno — Agrupación por proyecto

- [ ] Modificar la vista `containers_list` para agrupar queryset por proyecto
- [ ] Crear partial `_project_accordion.html`
- [ ] Reutilizar `_services_table.html` dentro de cada acordeón
- [ ] Añadir botón "Crear servicio" dentro de cada proyecto
- [ ] Mantener el auto-refresh HTMX por tabla (no por acordeón completo)

### Fase 3: Vista Profesor — Agrupación por alumno

- [ ] Modificar la vista `professor_project_detail` para agrupar por alumno
- [ ] Crear partial `_student_accordion.html` con indicadores de supervisión
- [ ] Dentro de cada alumno, agrupar por proyecto
- [ ] Añadir indicadores: servicios x/límite, última actividad
- [ ] Filtros adicionales: alumno, estado, ordenación

### Fase 4: Indicadores de supervisión (extra)

- [ ] Añadir campo `max_services` al modelo (UserProfile o relación alumno-asignatura)
- [ ] Implementar lógica de comprobación de límites
- [ ] Modal "Gestionar límites" para el profesor
- [ ] Indicador visual ✅/❗/⚠️ en la cabecera de cada alumno
- [ ] Alerta o aviso al alumno cuando se acerque al límite

---

## 8. Detalles Técnicos

### 8.1 Agrupación en la vista (Django)

Para la vista del alumno:

```python
# views.py — containers_list
from itertools import groupby
from collections import OrderedDict

def containers_list(request):
    services = Service.objects.filter(
        owner=request.user
    ).select_related('project', 'project__subject').order_by(
        'project__subject__name', 'project__name', '-id'
    )

    # Agrupar por asignatura → proyecto
    grouped = OrderedDict()
    for service in services:
        subject = service.project.subject if service.project else None
        project = service.project

        subject_key = subject.name if subject else "Sin asignatura"
        if subject_key not in grouped:
            grouped[subject_key] = {"subject": subject, "projects": OrderedDict()}

        project_key = project.name if project else "Sin proyecto"
        if project_key not in grouped[subject_key]["projects"]:
            grouped[subject_key]["projects"][project_key] = {
                "project": project,
                "services": [],
                "running": 0,
                "stopped": 0,
            }

        group = grouped[subject_key]["projects"][project_key]
        group["services"].append(service)
        if service.status == "running":
            group["running"] += 1
        else:
            group["stopped"] += 1

    context = {"grouped_services": grouped}
    return render(request, "containers/my_services.html", context)
```

Para la vista del profesor:

```python
# views.py — professor_subject_detail
def professor_subject_services(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)

    # Obtener todos los servicios de la asignatura, agrupados por alumno
    services = Service.objects.filter(
        project__subject=subject
    ).select_related('owner', 'project').order_by('owner__username', 'project__name')

    grouped = OrderedDict()
    for service in services:
        user_key = service.owner.id
        if user_key not in grouped:
            profile = service.owner.profile  # Asumiendo que existe
            grouped[user_key] = {
                "user": service.owner,
                "full_name": service.owner.get_full_name() or service.owner.username,
                "projects": OrderedDict(),
                "total": 0,
                "running": 0,
                "stopped": 0,
                "max_services": getattr(profile, 'max_services', 5),
                "last_activity": None,
            }

        student = grouped[user_key]
        project_key = service.project.name if service.project else "Sin proyecto"
        if project_key not in student["projects"]:
            student["projects"][project_key] = []

        student["projects"][project_key].append(service)
        student["total"] += 1
        if service.status == "running":
            student["running"] += 1
        else:
            student["stopped"] += 1

        # Última actividad
        if student["last_activity"] is None or service.updated_at > student["last_activity"]:
            student["last_activity"] = service.updated_at

    context = {
        "subject": subject,
        "grouped_students": grouped,
        "total_students": len(grouped),
        "total_services": services.count(),
        "total_running": sum(s["running"] for s in grouped.values()),
    }
    return render(request, "professor/subject_services.html", context)
```

### 8.2 Template del acordeón (Bootstrap)

```html
{# _project_accordion.html #} {% for subject_name, subject_data in
grouped_services.items %}
<div class="card mb-3 border-0 shadow-sm">
  <div
    class="card-header bg-light d-flex justify-content-between align-items-center"
  >
    <h6 class="mb-0">
      <i class="fas fa-book me-2 text-primary"></i>{{ subject_name }}
    </h6>
  </div>
  <div class="card-body p-0">
    {% for project_name, project_data in subject_data.projects.items %}
    <div class="accordion" id="accordion-{{ forloop.counter }}">
      <div class="accordion-item border-0">
        <h2 class="accordion-header">
          <button
            class="accordion-button"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#collapse-{{ forloop.counter }}"
          >
            <i class="fas fa-folder me-2 text-warning"></i>
            <strong>{{ project_name }}</strong>
            <span class="ms-3 text-muted small">
              {{ project_data.services|length }} servicios ·
              <span class="text-success"
                >{{ project_data.running }} activos</span
              >
              ·
              <span class="text-secondary"
                >{{ project_data.stopped }} detenidos</span
              >
            </span>
          </button>
        </h2>
        <div
          id="collapse-{{ forloop.counter }}"
          class="accordion-collapse collapse show"
        >
          <div class="accordion-body p-0">
            {% include "_partials/services/_services_table.html" with
            services=project_data.services %}
          </div>
        </div>
      </div>
    </div>
    {% endfor %}
  </div>
</div>
{% endfor %}
```

### 8.3 HTMX: Auto-refresh compatible

El auto-refresh actual refresca toda la tabla. Con acordeones, hay que refrescar
solo el contenido de cada tabla dentro del acordeón, no el acordeón entero
(para no perder el estado abierto/cerrado):

```html
{# Cada tabla de servicios tiene su propio hx-trigger #}
<div
  hx-get="{% url 'service-table-fragment' %}?project={{ project.id }}"
  hx-trigger="every 3s"
  hx-swap="innerHTML"
>
  {% include "_partials/services/_services_table.html" %}
</div>
```

---

## 9. Estimación de Tiempos

### Fase 1: Menú `⋮` (Quick Win)

| Tarea                                     | Tiempo         |
| ----------------------------------------- | -------------- |
| Crear `_actions_menu.html`                | 30 min         |
| Integrar en templates existentes          | 30 min         |
| Lógica botón según estado (Play XOR Stop) | 20 min         |
| Testing manual                            | 20 min         |
| **Subtotal**                              | **~1.5 horas** |

### Fase 2: Vista Alumno

| Tarea                                      | Tiempo         |
| ------------------------------------------ | -------------- |
| Agrupar queryset por proyecto en la vista  | 45 min         |
| Crear template con acordeones              | 1 hora         |
| Reutilizar tabla de servicios como partial | 30 min         |
| Botón "Crear servicio" por proyecto        | 20 min         |
| Auto-refresh HTMX por sección              | 45 min         |
| Testing y ajustes CSS                      | 30 min         |
| **Subtotal**                               | **~3.5 horas** |

### Fase 3: Vista Profesor

| Tarea                                                | Tiempo         |
| ---------------------------------------------------- | -------------- |
| Agrupar queryset por alumno → proyecto               | 1 hora         |
| Template acordeón alumno + proyecto (anidado)        | 1.5 horas      |
| Indicadores en cabecera (x/límite, última actividad) | 45 min         |
| Filtros adicionales (alumno, estado, orden)          | 1 hora         |
| Stats de supervisión (tarjetas resumen)              | 30 min         |
| Testing y ajustes                                    | 45 min         |
| **Subtotal**                                         | **~5.5 horas** |

### Fase 4: Límites (Extra)

| Tarea                                  | Tiempo       |
| -------------------------------------- | ------------ |
| Campo `max_services` en modelo         | 20 min       |
| Migración                              | 5 min        |
| Modal "Gestionar límites"              | 45 min       |
| Lógica de validación al crear servicio | 30 min       |
| Indicadores visuales ✅/❗/⚠️          | 30 min       |
| **Subtotal**                           | **~2 horas** |

### Total general

| Fase                   | Tiempo          | Prioridad           |
| ---------------------- | --------------- | ------------------- |
| Fase 1: Menú `⋮`       | ~1.5h           | 🔴 Alta (quick win) |
| Fase 2: Vista Alumno   | ~3.5h           | 🟡 Media            |
| Fase 3: Vista Profesor | ~5.5h           | 🟡 Media            |
| Fase 4: Límites        | ~2h             | 🟢 Baja (extra)     |
| **TOTAL**              | **~12.5 horas** |                     |

---

> **Recomendación de implementación**:
>
> 1. Empezar por la **Fase 1** (menú `⋮`) → mejora inmediata, poco riesgo.
> 2. Continuar con la **Fase 2** (vista alumno) → la ve cualquier evaluador.
> 3. Si hay tiempo, **Fase 3** (vista profesor) → demuestra diseño por roles.
> 4. La **Fase 4** (límites) es el cherry on top para impresionar al tribunal.
>
> Cada fase es independiente y funcional por sí sola.
> No es necesario implementar todas para obtener valor.
