# 🔮 MEJORA - Optimización API DockerHub y Autenticación Global

**Fecha de documentación:** 01/02/2026  
**Prioridad:** ALTA  
**Estado:** PENDIENTE  
**Tipo:** Infraestructura / Estabilidad

---

## 📋 DESCRIPCIÓN

Actualmente, el sistema de verificación de imágenes de DockerHub realiza peticiones anónimas. Esto limita la aplicación a **100 peticiones cada 6 horas** por IP (compartido entre todos los usuarios). Para escalar la aplicación y evitar bloqueos (Error 429), se propone implementar un sistema de autenticación global a nivel de servidor.

---

## 🎯 OBJETIVOS

1.  **Aumentar Límites:** Pasar de 100 a **200 peticiones cada 6 horas** mediante un token de acceso personal (PAT).
2.  **Identidad de Aplicación:** Realizar las consultas como "PaaSify App" en lugar de consultas anónimas.
3.  **Manejo de Errores:** Gestionar específicamente el error **429 (Too Many Requests)** con mensajes amigables y lógica de reintento.

---

## 🔧 PROPUESTA TÉCNICA

### **1. Configuración de Credenciales Globales**

Se debe crear una cuenta de DockerHub específica para el servidor PaaSify y generar un PAT.

```python
# settings.py
import os

DOCKERHUB_GLOBAL_TOKEN = os.getenv('DOCKERHUB_GLOBAL_TOKEN', 'tu_token_aqui')
```

### **2. Implementación en el Backend**

Modificar la lógica de consulta para incluir la cabecera de autorización y el tratamiento del error 429.

```python
# containers/views.py (Propuesta)

def verify_dockerhub_image(request):
    import requests
    from django.conf import settings

    # ... lógica de parseo ...

    headers = {}
    if settings.DOCKERHUB_GLOBAL_TOKEN:
        headers['Authorization'] = f'Bearer {settings.DOCKERHUB_GLOBAL_TOKEN}'

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            # ... éxito ...
            pass
        elif response.status_code == 429:
            return JsonResponse({
                'success': False,
                'error': 'Límite de consultas a DockerHub alcanzado. Inténtalo de nuevo en unas horas.'
            })
        # ... resto de errores ...
    except Exception as e:
        # ... manejo de excepciones ...
        pass
```

---

## 📊 COMPARATIVA

| Característica     | Anónimo (Actual)        | Autenticado (Propuesta)    |
| :----------------- | :---------------------- | :------------------------- |
| **Límite de Rate** | 100 petc. / 6h          | **200 petc. / 6h**         |
| **Identificación** | Por IP                  | **Por Cuenta**             |
| **Estabilidad**    | Volátil (IP compartida) | **Estable (Token propio)** |
| **Coste**          | Gratis                  | Gratis (Requiere cuenta)   |

---

## ✅ BENEFICIOS Y DESVENTAJAS

### **Beneficios:**

- ✅ **Doble de capacidad:** Mejora la experiencia de uso simultáneo por varios alumnos.
- ✅ **Límite Individual:** No dependemos de si otros servicios en la misma red están usando la API.
- ✅ **Feedback Claro:** El usuario entenderá por qué falla si se alcanza el límite.

### **Desventajas:**

- ❌ **Gestión de Cuenta:** Requiere mantener una cuenta de DockerHub activa para la app.
- ❌ **Seguridad de Token:** El token debe gestionarse de forma segura en las variables de entorno (`.env`).

---

## 🚀 PRÓXIMOS PASOS

1.  Crear cuenta oficial `@paasify-server` en DockerHub.
2.  Generar token con permisos de **Read-only**.
3.  Actualizar la vista de verificación en `containers/views.py`.
4.  Añadir lógica de **Caché** (Redis/Django Cache) para no repetir peticiones por la misma imagen en un periodo corto de tiempo.

---

**Estado actual:** DOCUMENTADO PARA FUTURA FASE  
**Prioridad:** MEDIA  
**Fecha:** 01/02/2026
