# Feature: Logs Avanzados con Filtrado Temporal y Navegación Inteligente

**Fecha:** 15/02/2026
**Versión:** v6.4.0
**Estado:** ✅ Implementado y Verificado

## 📝 Descripción

Se ha evolucionado el sistema de logs para ofrecer capacidades de depuración profesional. La mejora se centra en la capacidad de filtrar por antigüedad (timestamps) utilizando el motor nativo de Docker y mejorar la navegabilidad en logs de gran volumen.

## 🚀 Funcionalidades Implementadas

### 1. Filtrado por Antigüedad (Timestamps)

- **Motor Nativo:** Se integró el parámetro `--since` de Docker en el backend, permitiendo que el daemon de Docker realice el filtrado antes de enviar los datos al servidor.
- **Presets Disponibles:**
  - Últimos 5 minutos
  - Últimos 15 minutos
  - Última hora
  - Últimas 4 horas / 24 horas
  - Últimos 7 días
- **Persistencia:** El filtro se mantiene al cambiar otros parámetros (búsqueda, nivel de log o cantidad de líneas) gracias a la integración con HTMX.

### 2. Navegación Rápida (Smart Scroll)

- **Botón Inicio:** Scroll suave e instantáneo al principio del documento.
- **Botón Final:** Nuevo botón para saltar directamente a la última línea escrita, facilitando el seguimiento de los eventos más recientes sin scroll manual.
- **Estética:** Botones con diseño premium y degradados coherentes con la identidad visual de PaaSify.

### 3. Streaming Gen 2 (Live Logs)

- **Sincronización:** El streaming mediante WebSockets ahora respeta los filtros de tiempo y cantidad de líneas (`tail`) al conectar.
- **Modo Diferido:** Si un usuario selecciona "Última hora" y activa el vivo, el sistema carga primero los logs históricos de esa hora y luego continúa con el flujo en tiempo real sin interrupciones.

### 4. Optimización de Rendimiento

- **Invalidación de Caché:** Se actualizó el sistema de caché atómica para contemplar las nuevas variantes de tiempo, asegurando que el botón "Refrescar" siempre traiga datos frescos incluso con filtros activos.
- **Eficiencia:** Al delegar el filtrado temporal a Docker, se reduce drásticamente el uso de memoria en el servidor Django al procesar logs de larga duración.

## 🛠️ Detalles Técnicos

- **Backend:** Actualización de `fetch_container_logs` en `utils.py` y `logs_page` en `views.py`.
- **WebSockets:** Modificación de `LogsStreamConsumer` en `consumers.py` para procesar `query_params` de antigüedad.
- **Frontend:** Integración de nuevos selectores y botones en `logs_page.html` con lógica de scroll en JS puro.

---

_Documentación generada por Antigravity AI para David RG - TFG PaaSify_
