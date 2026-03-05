# Assets Visuales - PaaSify

Este directorio contiene todos los assets visuales de la aplicación.

---

## Fondos para Login (3 opciones)

### 1. login_background_containers.png ⭐ (Recomendado)
- **Descripción:** Cubos 3D isométricos como elemento principal, ballena Docker muy sutil en el fondo
- **Uso:** Fondo decorativo para página de login
- **Estilo:** Minimalista, enfocado en contenedores
- **Tamaño:** ~441 KB

### 2. login_background_pattern.png
- **Descripción:** Patrón geométrico de cubos 3D en tonos azules
- **Uso:** Alternativa de fondo para login
- **Estilo:** Más abstracto y geométrico
- **Tamaño:** ~472 KB

### 3. login_background_docker.png
- **Descripción:** Ballenas Docker sutiles con contenedores
- **Uso:** Opción con más presencia de Docker (si se desea)
- **Estilo:** Más relacionado directamente con Docker
- **Tamaño:** ~475 KB

---

## Logos e Iconos

### 4. paasify_logo_icon.png
- **Descripción:** Icono de cubo 3D isométrico en azul
- **Uso:** Logo/icono principal de la aplicación
- **Tamaño:** 512x512px (~385 KB)
- **Formatos sugeridos:** Convertir a SVG para mejor escalabilidad

### 5. docker_whale_icon.png
- **Descripción:** Icono minimalista de ballena Docker en azul
- **Uso:** Elemento decorativo secundario, icono de Docker
- **Nota:** Usar con moderación, no como elemento principal
- **Tamaño:** ~248 KB

---

## Ilustraciones

### 6. hero_illustration_containers.png
- **Descripción:** Stack de contenedores con flechas de despliegue
- **Uso:** Hero section, landing page, o header de dashboard
- **Estilo:** Flat design, profesional
- **Tamaño:** ~587 KB

### 7. empty_state_illustration.png
- **Descripción:** Ilustración amigable para estado vacío (sin servicios)
- **Uso:** Cuando el alumno no tiene servicios desplegados
- **Mensaje:** "No hay servicios desplegados aún" (agregar texto en HTML)
- **Tamaño:** ~447 KB

---

## Iconos de UI

### 8. service_card_icons.png
- **Descripción:** Set de iconos de tecnologías (Node.js, Python, Nginx, Docker)
- **Uso:** Referencia para tarjetas de servicios
- **Nota:** En producción, usar logos oficiales de cada tecnología
- **Tamaño:** ~314 KB

### 9. service_status_icons.png
- **Descripción:** Iconos de estado (running, stopped, building)
- **Uso:** Indicadores de estado de servicios
- **Colores:** Verde (running), Rojo (stopped), Amarillo (building)
- **Tamaño:** ~364 KB

---

## Logo Existente

### 10. logo.png (Original del proyecto)
- **Descripción:** Logo actual de PaaSify
- **Tamaño:** ~47 KB

---

## Uso en Templates Django

```django
{% load static %}

<!-- Fondo de login -->
<div style="background-image: url('{% static 'assets/img/login_background_containers.png' %}');">
    <!-- Contenido -->
</div>

<!-- Logo en topbar -->
<img src="{% static 'assets/img/logo.png' %}" alt="PaaSify Logo">

<!-- Estado vacío -->
<img src="{% static 'assets/img/empty_state_illustration.png' %}" alt="Sin servicios">
```

---

## Próximos Assets a Crear

**Sprint 2:**
- [ ] Logo completo (icono + texto "PaaSify") en SVG
- [ ] Favicon en múltiples tamaños (16x16, 32x32, 180x180, 512x512)
- [ ] Iconos de navegación para sidebar en SVG
- [ ] Convertir `paasify_logo_icon.png` a SVG vectorial

**Sprint 3:**
- [ ] Gráficos de ejemplo para dashboard de profesor
- [ ] Ilustraciones para wizard de creación
- [ ] Iconos animados de estado
- [ ] Imágenes de fondo para cards de asignaturas

---

**Última actualización:** 2025-12-13  
**Total de assets:** 10 archivos  
**Tamaño total:** ~3.7 MB
