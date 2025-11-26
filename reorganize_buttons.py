import re

# Leer el archivo original
encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
content = None

for enc in encodings:
    try:
        with open('templates/containers/_service_rows.html', 'r', encoding=enc) as f:
            content = f.read()
        print(f"Read with encoding: {enc}")
        break
    except UnicodeDecodeError:
        continue

if content is None:
    print("ERROR: Could not read file")
    exit(1)

# Reorganizar botones en modo simple
# Buscar la sección de modo simple y reemplazarla
simple_mode_pattern = r'({% else %}\s*{# ========== MODO SIMPLE.*?)({% endif %}\s*</td>)'

new_simple_mode = r'''{% else %}
      {# ========== MODO SIMPLE: Contenedor único ========== #}
      <div class="d-flex flex-wrap gap-1">
        {# 1. BOTONES ESTÁTICOS (siempre visibles) #}
        <button
          class="btn btn-sm btn-success"
          {% if s.status == "running" %}disabled{% endif %}
          hx-post="{% url 'service-start' s.id %}"
          hx-target="#service-{{ s.id }}"
          hx-swap="none"
          title="Iniciar">
          Iniciar
        </button>

        <button
          class="btn btn-sm btn-warning"
          {% if s.status != "running" %}disabled{% endif %}
          hx-post="{% url 'service-stop' s.id %}"
          hx-target="#service-{{ s.id }}"
          hx-swap="none"
          title="Detener">
          Detener
        </button>

        <button
          class="btn btn-sm btn-danger"
          hx-post="{% url 'service-remove' s.id %}"
          hx-target="#service-{{ s.id }}"
          hx-swap="none"
          hx-confirm="Eliminar definitivamente?"
          title="Eliminar">
          Eliminar
        </button>

        <button
          class="btn btn-sm btn-secondary"
          hx-get="{% url 'service-logs' s.id %}"
          hx-target="#genericModalContent"
          hx-swap="innerHTML"
          data-bs-toggle="modal"
          data-bs-target="#genericModal"
          title="Ver logs">
          Logs
        </button>

        {# 2. BOTONES DE ARCHIVOS (si existen) #}
        {% if s.dockerfile %}
        <button
          class="btn btn-sm btn-info"
          hx-get="{% url 'service-dockerfile' s.id %}"
          hx-target="#code-body"
          hx-swap="innerHTML"
          data-bs-toggle="modal"
          data-bs-target="#codeModal"
          title="Ver Dockerfile">
          Dockerfile
        </button>
        {% endif %}

        {% if s.compose %}
        <button
          class="btn btn-sm btn-info"
          hx-get="{% url 'service-compose' s.id %}"
          hx-target="#code-body"
          hx-swap="innerHTML"
          data-bs-toggle="modal"
          data-bs-target="#codeModal"
          title="Ver docker-compose">
          Compose
        </button>
        {% endif %}

        {# 3. BOTONES CONDICIONALES (dependen del estado) #}
        {% if s.container_id and s.status == 'running' %}
          {% if host and s.assigned_port %}
          <a
            href="http://{{ host }}:{{ s.assigned_port }}"
            class="btn btn-sm btn-outline-primary"
            target="_blank"
            rel="noopener"
            title="Abrir en navegador">
            Acceder
          </a>
          {% endif %}
          <a
            href="{% url 'containers:terminal_view' s.id %}"
            class="btn btn-sm btn-dark"
            title="Abrir terminal interactiva">
            Terminal
          </a>
        {% else %}
          <button
            class="btn btn-sm btn-dark"
            disabled
            title="Terminal disponible solo cuando el servicio esta en ejecucion">
            Terminal
          </button>
        {% endif %}
      </div>
    {% endif %}
  </td>'''

# Aplicar el reemplazo
content = re.sub(simple_mode_pattern, new_simple_mode, content, flags=re.DOTALL)

# Guardar con UTF-8
with open('templates/containers/_service_rows.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Template reorganized successfully!")
