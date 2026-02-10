# Plan de Implementación: Detección Automática de Puertos en Docker Compose

**Fecha:** 2026-02-02  
**Autor:** Sistema PaaSify  
**Estado:** Propuesta  
**Prioridad:** Alta

---

## 📋 **Resumen Ejecutivo**

Implementar un sistema de análisis automático de archivos `docker-compose.yml` que:

1. Detecte todos los servicios/contenedores definidos
2. Extraiga puertos internos y externos de cada servicio
3. Muestre una lista visual de contenedores con sus puertos
4. Valide la estructura del archivo y muestre errores claros
5. Oculte los campos manuales de puerto cuando se usa Docker Compose

---

## 🎯 **Objetivos**

### **Objetivo Principal**

Mejorar la experiencia de usuario al crear servicios con Docker Compose, eliminando la necesidad de configurar puertos manualmente y proporcionando feedback visual inmediato sobre la configuración.

### **Objetivos Específicos**

1. ✅ Parsear automáticamente archivos `docker-compose.yml`
2. ✅ Extraer información de puertos de cada servicio
3. ✅ Mostrar lista visual de contenedores detectados
4. ✅ Validar sintaxis y estructura del archivo
5. ✅ Detectar conflictos de puertos
6. ✅ Mostrar errores de forma clara y accionable

---

## 🔍 **Análisis del Problema Actual**

### **Situación Actual**

- Usuario sube `docker-compose.yml`
- Debe configurar manualmente "Puerto personalizado" y "Puerto interno"
- No hay feedback sobre qué contenedores se desplegarán
- No se valida si los puertos están correctamente configurados
- Errores de sintaxis solo se descubren al intentar desplegar

### **Problemas Identificados**

1. **Falta de visibilidad**: No se sabe qué contenedores se crearán
2. **Configuración redundante**: Puertos ya están en el compose
3. **Errores tardíos**: Problemas se descubren al desplegar
4. **Conflictos de puertos**: No se detectan antes de crear el servicio

---

## 💡 **Solución Propuesta**

### **Flujo de Usuario Mejorado**

```
1. Usuario selecciona "Configuración personalizada"
2. Usuario sube docker-compose.yml
3. Sistema analiza el archivo automáticamente
4. Sistema muestra:
   ├─ ✅ Lista de contenedores detectados
   ├─ ✅ Puertos de cada contenedor (interno:externo)
   ├─ ✅ Volúmenes detectados
   ├─ ⚠️  Advertencias (puertos no declarados, conflictos)
   └─ ❌ Errores de sintaxis o estructura
5. Usuario revisa y confirma
6. Usuario crea el servicio
```

### **Ejemplo Visual**

#### **Caso 1: Docker Compose Válido**

```yaml
services:
  nginx-sin-volumen:
    image: nginx:latest
    ports:
      - "8080:80"
  redis:
    image: redis:7
    ports:
      - "6379:6379"
```

**UI Mostrada:**

```
📦 Contenedores detectados (2):

┌─────────────────────────────────────────────┐
│ 🐳 nginx-sin-volumen                        │
│ Imagen: nginx:latest                        │
│ Puerto: 8080 → 80                           │
│ Estado: ✅ Configuración válida             │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ 🐳 redis                                    │
│ Imagen: redis:7                             │
│ Puerto: 6379 → 6379                         │
│ Estado: ✅ Configuración válida             │
└─────────────────────────────────────────────┘
```

#### **Caso 2: Puerto No Declarado**

```yaml
services:
  nginx:
    image: nginx:latest
    # Sin puertos declarados
```

**UI Mostrada:**

```
📦 Contenedores detectados (1):

┌─────────────────────────────────────────────┐
│ 🐳 nginx                                    │
│ Imagen: nginx:latest                        │
│ Puerto: ⚠️ No declarado en compose          │
│ Estado: ⚠️ Sin exposición de puertos        │
└─────────────────────────────────────────────┘

⚠️ Advertencia: Este contenedor no tiene puertos
   expuestos. No será accesible desde el host.
```

#### **Caso 3: Error de Sintaxis**

```yaml
services:
  nginx
    image: nginx:latest  # Falta ':'
    ports:
      - "8080:80"
```

**UI Mostrada:**

```
❌ Error al analizar docker-compose.yml

Línea 2: Error de sintaxis YAML
  nginx
      ^
  Falta ':' después del nombre del servicio

Corrección sugerida:
  nginx:
    image: nginx:latest
```

---

## 🏗️ **Arquitectura de la Solución**

### **Componentes**

```
┌─────────────────────────────────────────────────────┐
│                    FRONTEND                         │
├─────────────────────────────────────────────────────┤
│ 1. File Upload Component                           │
│    - Detecta cuando se sube docker-compose.yml     │
│    - Envía archivo al backend para análisis        │
│                                                     │
│ 2. Container List Component (NUEVO)                │
│    - Muestra lista de contenedores detectados      │
│    - Muestra puertos, imágenes, volúmenes          │
│    - Muestra advertencias y errores                │
│                                                     │
│ 3. Port Fields (OCULTOS cuando hay compose)        │
│    - Puerto personalizado                          │
│    - Puerto interno                                │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│                    BACKEND                          │
├─────────────────────────────────────────────────────┤
│ 1. Docker Compose Parser (NUEVO)                   │
│    - Parsea YAML con PyYAML                        │
│    - Extrae servicios, puertos, volúmenes          │
│    - Valida estructura                             │
│                                                     │
│ 2. Port Validator (NUEVO)                          │
│    - Verifica puertos disponibles                  │
│    - Detecta conflictos                            │
│    - Sugiere alternativas                          │
│                                                     │
│ 3. API Endpoint: /analyze-compose/ (NUEVO)         │
│    - Recibe archivo docker-compose.yml             │
│    - Retorna JSON con análisis completo            │
└─────────────────────────────────────────────────────┘
```

---

## 📝 **Especificación Técnica**

### **1. Backend: API Endpoint**

**Endpoint:** `POST /paasify/containers/analyze-compose/`

**Request:**

```http
POST /paasify/containers/analyze-compose/
Content-Type: multipart/form-data

compose_file: <archivo docker-compose.yml>
```

**Response (Éxito):**

```json
{
  "success": true,
  "containers": [
    {
      "name": "nginx-sin-volumen",
      "image": "nginx:latest",
      "ports": [
        {
          "host": "8080",
          "container": "80",
          "protocol": "tcp"
        }
      ],
      "volumes": [],
      "environment": {},
      "warnings": []
    },
    {
      "name": "redis",
      "image": "redis:7",
      "ports": [
        {
          "host": "6379",
          "container": "6379",
          "protocol": "tcp"
        }
      ],
      "volumes": [],
      "environment": {},
      "warnings": []
    }
  ],
  "volumes": ["datos_nginx"],
  "networks": [],
  "warnings": [],
  "errors": []
}
```

**Response (Error de Sintaxis):**

```json
{
  "success": false,
  "error": "Error de sintaxis YAML en línea 2",
  "line": 2,
  "column": 10,
  "message": "Falta ':' después del nombre del servicio",
  "suggestion": "nginx:\n  image: nginx:latest"
}
```

**Response (Puerto No Declarado):**

```json
{
  "success": true,
  "containers": [
    {
      "name": "nginx",
      "image": "nginx:latest",
      "ports": [],
      "volumes": [],
      "environment": {},
      "warnings": [
        "No se declararon puertos. El contenedor no será accesible desde el host."
      ]
    }
  ],
  "warnings": ["El servicio 'nginx' no tiene puertos expuestos"]
}
```

### **2. Backend: Parser Implementation**

**Archivo:** `containers/compose_parser.py` (NUEVO)

```python
import yaml
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class PortMapping:
    host: str
    container: str
    protocol: str = "tcp"

@dataclass
class ContainerInfo:
    name: str
    image: str
    ports: List[PortMapping]
    volumes: List[str]
    environment: Dict[str, str]
    warnings: List[str]

class DockerComposeParser:
    """
    Parser para archivos docker-compose.yml
    Extrae información de servicios, puertos, volúmenes, etc.
    """

    def __init__(self, compose_content: str):
        self.content = compose_content
        self.parsed_data = None
        self.errors = []
        self.warnings = []

    def parse(self) -> Dict:
        """
        Parsea el contenido del docker-compose.yml
        Retorna diccionario con información estructurada
        """
        try:
            self.parsed_data = yaml.safe_load(self.content)
        except yaml.YAMLError as e:
            return {
                'success': False,
                'error': 'Error de sintaxis YAML',
                'line': e.problem_mark.line if hasattr(e, 'problem_mark') else None,
                'column': e.problem_mark.column if hasattr(e, 'problem_mark') else None,
                'message': str(e.problem),
                'suggestion': self._generate_suggestion(e)
            }

        # Validar estructura básica
        if not self._validate_structure():
            return {
                'success': False,
                'error': 'Estructura inválida',
                'message': 'El archivo no tiene la estructura esperada de docker-compose',
                'errors': self.errors
            }

        # Extraer información de contenedores
        containers = self._extract_containers()
        volumes = self._extract_volumes()
        networks = self._extract_networks()

        return {
            'success': True,
            'containers': [self._container_to_dict(c) for c in containers],
            'volumes': volumes,
            'networks': networks,
            'warnings': self.warnings,
            'errors': self.errors
        }

    def _validate_structure(self) -> bool:
        """Valida que el compose tenga la estructura mínima"""
        if not isinstance(self.parsed_data, dict):
            self.errors.append("El archivo debe ser un diccionario YAML válido")
            return False

        if 'services' not in self.parsed_data:
            self.errors.append("Falta la sección 'services'")
            return False

        if not isinstance(self.parsed_data['services'], dict):
            self.errors.append("La sección 'services' debe ser un diccionario")
            return False

        if len(self.parsed_data['services']) == 0:
            self.errors.append("No se definieron servicios")
            return False

        # Validar límite de contenedores (máximo 5)
        if len(self.parsed_data['services']) > 5:
            self.errors.append(f"Máximo 5 servicios permitidos, encontrados {len(self.parsed_data['services'])}")
            return False

        return True

    def _extract_containers(self) -> List[ContainerInfo]:
        """Extrae información de cada servicio/contenedor"""
        containers = []

        for service_name, service_config in self.parsed_data['services'].items():
            container = ContainerInfo(
                name=service_name,
                image=service_config.get('image', 'No especificada'),
                ports=self._extract_ports(service_config),
                volumes=self._extract_service_volumes(service_config),
                environment=self._extract_environment(service_config),
                warnings=[]
            )

            # Advertencias
            if not container.ports:
                container.warnings.append(
                    "No se declararon puertos. El contenedor no será accesible desde el host."
                )

            if not container.image or container.image == 'No especificada':
                container.warnings.append(
                    "No se especificó imagen. Se requiere 'image' o 'build'."
                )

            containers.append(container)

        return containers

    def _extract_ports(self, service_config: Dict) -> List[PortMapping]:
        """Extrae mapeo de puertos de un servicio"""
        ports = []

        if 'ports' not in service_config:
            return ports

        for port_mapping in service_config['ports']:
            # Formato: "8080:80" o "8080:80/tcp"
            if isinstance(port_mapping, str):
                parts = port_mapping.split(':')
                if len(parts) == 2:
                    host_port = parts[0]
                    container_part = parts[1]

                    # Separar puerto y protocolo
                    if '/' in container_part:
                        container_port, protocol = container_part.split('/')
                    else:
                        container_port = container_part
                        protocol = 'tcp'

                    ports.append(PortMapping(
                        host=host_port,
                        container=container_port,
                        protocol=protocol
                    ))
            # Formato largo: {target: 80, published: 8080}
            elif isinstance(port_mapping, dict):
                ports.append(PortMapping(
                    host=str(port_mapping.get('published', '')),
                    container=str(port_mapping.get('target', '')),
                    protocol=port_mapping.get('protocol', 'tcp')
                ))

        return ports

    def _extract_service_volumes(self, service_config: Dict) -> List[str]:
        """Extrae volúmenes de un servicio"""
        if 'volumes' not in service_config:
            return []

        volumes = []
        for vol in service_config['volumes']:
            if isinstance(vol, str):
                volumes.append(vol)
            elif isinstance(vol, dict):
                volumes.append(f"{vol.get('source', '')}:{vol.get('target', '')}")

        return volumes

    def _extract_environment(self, service_config: Dict) -> Dict[str, str]:
        """Extrae variables de entorno"""
        if 'environment' not in service_config:
            return {}

        env = service_config['environment']

        # Formato lista: ["KEY=value"]
        if isinstance(env, list):
            return {item.split('=')[0]: item.split('=')[1] for item in env if '=' in item}

        # Formato dict: {KEY: value}
        if isinstance(env, dict):
            return {k: str(v) for k, v in env.items()}

        return {}

    def _extract_volumes(self) -> List[str]:
        """Extrae volúmenes nombrados definidos a nivel global"""
        if 'volumes' not in self.parsed_data:
            return []

        return list(self.parsed_data['volumes'].keys())

    def _extract_networks(self) -> List[str]:
        """Extrae redes definidas"""
        if 'networks' not in self.parsed_data:
            return []

        return list(self.parsed_data['networks'].keys())

    def _container_to_dict(self, container: ContainerInfo) -> Dict:
        """Convierte ContainerInfo a diccionario para JSON"""
        return {
            'name': container.name,
            'image': container.image,
            'ports': [
                {
                    'host': p.host,
                    'container': p.container,
                    'protocol': p.protocol
                }
                for p in container.ports
            ],
            'volumes': container.volumes,
            'environment': container.environment,
            'warnings': container.warnings
        }

    def _generate_suggestion(self, error) -> Optional[str]:
        """Genera sugerencia de corrección basada en el error"""
        # Implementar lógica de sugerencias
        return None
```

### **3. Backend: View Implementation**

**Archivo:** `containers/views.py`

```python
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .compose_parser import DockerComposeParser

@login_required
@require_POST
def analyze_compose(request):
    """
    Analiza un archivo docker-compose.yml y retorna información estructurada
    """
    if 'compose_file' not in request.FILES:
        return JsonResponse({
            'success': False,
            'error': 'No se proporcionó archivo docker-compose.yml'
        }, status=400)

    compose_file = request.FILES['compose_file']

    # Validar tamaño (máximo 1MB)
    if compose_file.size > 1024 * 1024:
        return JsonResponse({
            'success': False,
            'error': 'El archivo es demasiado grande (máximo 1MB)'
        }, status=400)

    # Leer contenido
    try:
        content = compose_file.read().decode('utf-8')
    except UnicodeDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'El archivo no es un archivo de texto válido'
        }, status=400)

    # Parsear
    parser = DockerComposeParser(content)
    result = parser.parse()

    # Si hay errores, retornar con status 400
    if not result.get('success'):
        return JsonResponse(result, status=400)

    # Validar puertos disponibles
    from .models import Service
    used_ports = set(Service.objects.filter(
        assigned_port__isnull=False
    ).values_list('assigned_port', flat=True))

    # Verificar conflictos de puertos
    for container in result['containers']:
        for port in container['ports']:
            host_port = int(port['host'])
            if host_port in used_ports:
                container['warnings'].append(
                    f"Puerto {host_port} ya está en uso por otro servicio"
                )

    return JsonResponse(result)
```

### **4. Frontend: UI Component**

**Archivo:** `templates/containers/new_service.html`

Añadir después del campo de subida de `docker-compose.yml`:

```html
<!-- Análisis de Docker Compose (se muestra después de subir archivo) -->
<div id="compose-analysis" style="display: none;" class="mt-3">
  <!-- Contenedores detectados -->
  <div id="compose-containers" class="mb-3">
    <h6 class="fw-bold">📦 Contenedores detectados:</h6>
    <div id="container-list"></div>
  </div>

  <!-- Volúmenes detectados -->
  <div id="compose-volumes" style="display: none;" class="mb-3">
    <h6 class="fw-bold">💾 Volúmenes:</h6>
    <div id="volume-list"></div>
  </div>

  <!-- Advertencias -->
  <div id="compose-warnings" style="display: none;" class="alert alert-warning">
    <i class="fas fa-exclamation-triangle me-2"></i>
    <strong>Advertencias:</strong>
    <ul id="warning-list" class="mb-0 mt-2"></ul>
  </div>

  <!-- Errores -->
  <div id="compose-errors" style="display: none;" class="alert alert-danger">
    <i class="fas fa-times-circle me-2"></i>
    <strong>Errores:</strong>
    <div id="error-details" class="mt-2"></div>
  </div>
</div>
```

### **5. Frontend: JavaScript**

**Archivo:** `templates/containers/_partials/panels/_scripts.html`

```javascript
// Analizar docker-compose.yml cuando se suba
document.addEventListener("DOMContentLoaded", function () {
  const composeInput = document.querySelector('input[name="compose"]');

  if (composeInput) {
    composeInput.addEventListener("change", async function (e) {
      const file = e.target.files[0];
      if (!file) return;

      // Mostrar loading
      showComposeLoading();

      // Enviar al backend para análisis
      const formData = new FormData();
      formData.append("compose_file", file);

      try {
        const response = await fetch("/paasify/containers/analyze-compose/", {
          method: "POST",
          body: formData,
          headers: {
            "X-CSRFToken": getCsrfToken(),
          },
        });

        const result = await response.json();

        if (result.success) {
          displayComposeAnalysis(result);
          hidePortFields(); // Ocultar campos de puerto manual
        } else {
          displayComposeError(result);
        }
      } catch (error) {
        displayComposeError({
          error: "Error al analizar el archivo",
          message: error.message,
        });
      } finally {
        hideComposeLoading();
      }
    });
  }
});

function displayComposeAnalysis(result) {
  const analysisDiv = document.getElementById("compose-analysis");
  const containerList = document.getElementById("container-list");

  // Limpiar
  containerList.innerHTML = "";

  // Mostrar contenedores
  result.containers.forEach((container) => {
    const card = createContainerCard(container);
    containerList.appendChild(card);
  });

  // Mostrar volúmenes si existen
  if (result.volumes && result.volumes.length > 0) {
    displayVolumes(result.volumes);
  }

  // Mostrar advertencias si existen
  if (result.warnings && result.warnings.length > 0) {
    displayWarnings(result.warnings);
  }

  // Mostrar análisis
  analysisDiv.style.display = "block";
}

function createContainerCard(container) {
  const card = document.createElement("div");
  card.className = "card mb-2";

  let portsHtml = "";
  if (container.ports && container.ports.length > 0) {
    portsHtml = container.ports
      .map(
        (p) =>
          `<span class="badge bg-primary">${p.host} → ${p.container}</span>`,
      )
      .join(" ");
  } else {
    portsHtml = '<span class="badge bg-warning">⚠️ No declarado</span>';
  }

  let warningsHtml = "";
  if (container.warnings && container.warnings.length > 0) {
    warningsHtml = `
      <div class="alert alert-warning alert-sm mt-2 mb-0">
        ${container.warnings.map((w) => `<small>⚠️ ${w}</small>`).join("<br>")}
      </div>
    `;
  }

  card.innerHTML = `
    <div class="card-body">
      <h6 class="card-title">🐳 ${container.name}</h6>
      <p class="card-text mb-1">
        <strong>Imagen:</strong> ${container.image}<br>
        <strong>Puertos:</strong> ${portsHtml}
      </p>
      ${warningsHtml}
    </div>
  `;

  return card;
}

function displayComposeError(error) {
  const analysisDiv = document.getElementById("compose-analysis");
  const errorsDiv = document.getElementById("compose-errors");
  const errorDetails = document.getElementById("error-details");

  errorDetails.innerHTML = `
    <strong>${error.error}</strong><br>
    ${error.message || ""}
    ${error.line ? `<br><small>Línea ${error.line}, columna ${error.column}</small>` : ""}
    ${error.suggestion ? `<pre class="mt-2 bg-light p-2"><code>${error.suggestion}</code></pre>` : ""}
  `;

  errorsDiv.style.display = "block";
  analysisDiv.style.display = "block";
}

function hidePortFields() {
  // Ocultar campos de puerto personalizado e interno
  const portField = document
    .querySelector('[name="custom_port"]')
    ?.closest(".mb-3");
  const internalPortField = document
    .querySelector('[name="internal_port"]')
    ?.closest(".mb-3");

  if (portField) portField.style.display = "none";
  if (internalPortField) internalPortField.style.display = "none";
}

function showComposeLoading() {
  // Implementar spinner de carga
}

function hideComposeLoading() {
  // Ocultar spinner
}

function getCsrfToken() {
  return document.querySelector("[name=csrfmiddlewaretoken]").value;
}
```

---

## 📅 **Plan de Implementación por Fases**

### **Fase 1: Backend Parser (2-3 días)**

- [ ] Crear `compose_parser.py`
- [ ] Implementar parsing básico de YAML
- [ ] Implementar extracción de servicios y puertos
- [ ] Implementar validación de estructura
- [ ] Añadir tests unitarios

### **Fase 2: Backend API (1 día)**

- [ ] Crear endpoint `/analyze-compose/`
- [ ] Integrar parser
- [ ] Validar puertos disponibles
- [ ] Añadir tests de integración

### **Fase 3: Frontend UI (2 días)**

- [ ] Crear componente de lista de contenedores
- [ ] Implementar diseño de tarjetas
- [ ] Añadir visualización de advertencias/errores
- [ ] Ocultar campos de puerto manual

### **Fase 4: Frontend JavaScript (1-2 días)**

- [ ] Implementar upload handler
- [ ] Implementar llamada a API
- [ ] Implementar renderizado de resultados
- [ ] Añadir manejo de errores

### **Fase 5: Testing y Refinamiento (2 días)**

- [ ] Testing manual con diferentes compose files
- [ ] Corregir bugs
- [ ] Mejorar mensajes de error
- [ ] Documentar casos edge

### **Fase 6: Documentación (1 día)**

- [ ] Actualizar documentación de usuario
- [ ] Crear guía de troubleshooting
- [ ] Documentar API

**Tiempo Total Estimado:** 9-11 días

---

## 🧪 **Casos de Prueba**

### **Test 1: Compose Válido con Múltiples Servicios**

```yaml
services:
  web:
    image: nginx:latest
    ports:
      - "8080:80"
  db:
    image: postgres:14
    ports:
      - "5432:5432"
```

**Resultado Esperado:** ✅ 2 contenedores detectados, puertos correctos

### **Test 2: Servicio Sin Puertos**

```yaml
services:
  worker:
    image: python:3.9
    command: python worker.py
```

**Resultado Esperado:** ⚠️ Advertencia "No se declararon puertos"

### **Test 3: Error de Sintaxis**

```yaml
services
  web:
    image: nginx
```

**Resultado Esperado:** ❌ Error "Falta ':' en línea 1"

### **Test 4: Puerto en Conflicto**

```yaml
services:
  web:
    image: nginx
    ports:
      - "42802:80" # Puerto ya usado
```

**Resultado Esperado:** ⚠️ Advertencia "Puerto 42802 ya en uso"

### **Test 5: Más de 5 Servicios**

```yaml
services:
  s1: ...
  s2: ...
  s3: ...
  s4: ...
  s5: ...
  s6: ... # Excede límite
```

**Resultado Esperado:** ❌ Error "Máximo 5 servicios permitidos"

---

## 📊 **Métricas de Éxito**

1. **Reducción de errores de despliegue:** -80%
2. **Tiempo de configuración:** -60%
3. **Satisfacción de usuario:** +40%
4. **Tasa de éxito en primer intento:** +50%

---

## 🔒 **Consideraciones de Seguridad**

1. ✅ Validar tamaño de archivo (máx 1MB)
2. ✅ Sanitizar contenido YAML
3. ✅ Limitar número de servicios (máx 5)
4. ✅ Validar puertos en rango permitido (40000-50000)
5. ✅ No ejecutar código del compose, solo parsear

---

## 📚 **Referencias**

- [Docker Compose File Reference](https://docs.docker.com/compose/compose-file/)
- [PyYAML Documentation](https://pyyaml.org/wiki/PyYAMLDocumentation)
- [Docker Compose Validation](https://github.com/docker/compose/blob/master/compose/config/config_schema_v3.9.json)

---

## ✅ **Checklist de Implementación**

- [ ] Backend parser implementado
- [ ] API endpoint creado
- [ ] Frontend UI diseñado
- [ ] JavaScript integrado
- [ ] Tests unitarios pasando
- [ ] Tests de integración pasando
- [ ] Documentación actualizada
- [ ] Code review completado
- [ ] Testing manual completado
- [ ] Deploy a staging
- [ ] Testing en staging
- [ ] Deploy a producción

---

**Fin del documento**
