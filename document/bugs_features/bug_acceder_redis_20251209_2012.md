# Bug: Botón "Acceder" en servicios no-HTTP (Redis)
**Fecha**: 2025-12-09 23:49  
**Prioridad**: MEDIA  
**Estado**: PENDIENTE

---

## 🐛 DESCRIPCIÓN DEL BUG

**Problema**: El botón "Acceder" intenta abrir servicios no-HTTP (como Redis) con HTTP, causando errores de seguridad.

**Log observado en Redis**:
```
Possible SECURITY ATTACK detected. It looks like somebody is sending POST or Host: commands to Redis.
Connection from 172.21.0.1:40458 aborted.
```

**Causa**: Redis (y otras bases de datos) no son servicios HTTP, pero tienen botón "Acceder" que intenta abrir `http://localhost:PORT`

---

## 🔍 ANÁLISIS

**Servicios afectados**:
- Redis (puerto 6379)
- PostgreSQL (puerto 5432)
- MySQL (puerto 3306)
- MongoDB (puerto 27017)
- Memcached (puerto 11211)
- Cualquier base de datos o servicio no-HTTP

**Comportamiento actual**:
- Todos los contenedores con puertos tienen botón "Acceder"
- El botón abre `http://localhost:PORT` sin verificar si es HTTP

**Comportamiento esperado**:
- Solo servicios HTTP/HTTPS deberían tener botón "Acceder"
- Servicios no-HTTP deberían tener el botón deshabilitado o no mostrarlo

---

## 💡 SOLUCIÓN PROPUESTA

### **Opción 1: Lista de puertos HTTP conocidos (SIMPLE)**

```python
# containers/models.py
HTTP_PORTS = {80, 443, 3000, 5000, 8000, 8080, 8443, 9000}

class ServiceContainer(models.Model):
    # ...
    
    def is_http_service(self):
        """Detecta si el servicio es HTTP basado en puertos"""
        for port_info in self.assigned_ports or []:
            internal = port_info.get('internal')
            if internal in HTTP_PORTS:
                return True
        return False
```

**Template**:
```html
{% if c.is_http_service %}
  <button>Acceder</button>
{% else %}
  <button disabled title="Servicio no-HTTP">Acceder</button>
{% endif %}
```

---

### **Opción 2: Configuración manual en AllowedImage**

```python
class AllowedImage(models.Model):
    name = models.CharField(...)
    image = models.CharField(...)
    is_http_service = models.BooleanField(
        default=True,
        help_text="¿Es un servicio HTTP accesible por navegador?"
    )
```

**Ventaja**: Más flexible, el admin decide  
**Desventaja**: Requiere configuración manual

---

### **Opción 3: Detección por nombre de imagen**

```python
NON_HTTP_IMAGES = ['redis', 'postgres', 'mysql', 'mongo', 'memcached', 'rabbitmq']

def is_http_service(self):
    """Detecta si es HTTP por nombre de imagen"""
    image_name = self.service.image_name.lower()
    for non_http in NON_HTTP_IMAGES:
        if non_http in image_name:
            return False
    return True
```

---

## 📋 IMPLEMENTACIÓN RECOMENDADA

**Combinar Opción 1 + Opción 3**:

```python
# containers/models.py
HTTP_PORTS = {80, 443, 3000, 5000, 8000, 8080, 8443, 9000}
NON_HTTP_KEYWORDS = ['redis', 'postgres', 'mysql', 'mongo', 'memcached', 'rabbitmq', 'elasticsearch']

class ServiceContainer(models.Model):
    # ...
    
    def is_http_service(self):
        """Detecta si el servicio es HTTP"""
        # 1. Verificar por nombre de imagen
        if hasattr(self.service, 'image_name'):
            image_name = self.service.image_name.lower()
            for keyword in NON_HTTP_KEYWORDS:
                if keyword in image_name:
                    return False
        
        # 2. Verificar por puerto interno
        for port_info in self.assigned_ports or []:
            internal = port_info.get('internal')
            if internal in HTTP_PORTS:
                return True
        
        # Por defecto, asumir que es HTTP
        return True
```

**Template** (`_service_rows.html`):
```html
{% if c.is_http_service %}
  <a href="http://{{ host }}:{{ port.external }}" 
     target="_blank" 
     class="btn btn-sm btn-primary">
    Acceder
  </a>
{% else %}
  <button class="btn btn-sm btn-secondary" 
          disabled 
          title="Servicio no-HTTP ({{ c.name }})">
    Acceder
  </button>
{% endif %}
```

---

## 🎯 IMPACTO

**Severidad**: MEDIA  
**Funcionalidad afectada**: Botón "Acceder" en servicios compose  
**Usuarios afectados**: Usuarios con servicios de bases de datos

**Beneficios del fix**:
- ✅ No más intentos de conexión HTTP a servicios no-HTTP
- ✅ Mejor UX (botón deshabilitado con tooltip explicativo)
- ✅ Evita logs de "SECURITY ATTACK" en Redis

---

## 🧪 TESTING

1. Crear servicio compose con Redis
2. **Verificar**: Botón "Acceder" está deshabilitado para Redis
3. Crear servicio compose con web (Flask/nginx)
4. **Verificar**: Botón "Acceder" funciona para web
5. Verificar que no hay logs de "SECURITY ATTACK"

---

**Archivos a modificar**:
- `containers/models.py` - Añadir método `is_http_service()`
- `templates/containers/_service_rows.html` - Condicional en botón "Acceder"

---

**Última actualización**: 2025-12-09 23:49  
**Estado**: Documentado, pendiente de implementación
