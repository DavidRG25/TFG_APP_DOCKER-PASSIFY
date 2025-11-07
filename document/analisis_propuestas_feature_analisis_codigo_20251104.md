# Propuestas - feature-analisis-codigo - 2025-11-04
_Sugerencias de ajuste para alinear la documentación con la nueva política operativa._

## 📂 Cambios sugeridos
1. **Archivo**: `document/overview.md` y `document/vision_general.md`  
   **Bloque/Línea**: Documento completo  
   **Descripción técnica**: Fusionar ambos archivos en un único `vision-general-<fecha>.md`, manteniendo el contenido en español y añadiendo historial y referencias cruzadas.  
   **Justificación**: Evita duplicidades y asegura que futuras actualizaciones se concentren en una sola fuente de la visión general.

2. **Archivo**: `document/backend_components.md` y `document/componentes_backend.md`  
   **Bloque/Línea**: Documento completo  
   **Descripción técnica**: Consolidar los componentes backend en un solo archivo, incorporando tablas con rutas y responsables, y corrigiendo la codificación UTF-8.  
   **Justificación**: Reduce ambigüedad y soluciona problemas de encoding que actualmente muestran caracteres corruptos.

3. **Archivo**: `document/pruebas_operaciones.md` y `document/testing_and_operations.md`  
   **Bloque/Línea**: Secciones de “Automatización existente” y “Operaciones con Docker”  
   **Descripción técnica**: Reescribir el documento en el formato estándar (secciones con emojis, historial y dependencias) y documentar métricas de pruebas junto con enlaces a informes recientes.  
   **Justificación**: Alinea las guías operativas con el estilo requerido, evitando contradicciones entre versiones inglés/español.

4. **Archivo**: `document/implementacion-codigo-20251101-2243.md` y `document/implementacion-codigo-20251103-2315.md`  
   **Bloque/Línea**: Sección final de observaciones / próximos pasos  
   **Descripción técnica**: Añadir referencias explícitas a los documentos de análisis y propuestas que originaron cada implementación, incluyendo identificadores de commits cuando estén disponibles.  
   **Justificación**: Mejora la trazabilidad entre análisis, aprobación e implementación, facilitando auditorías futuras.

5. **Archivo**: Documentación histórica con artefactos de codificación (`analisis-*`, `implementacion-*`)  
   **Bloque/Línea**: Encabezados y texto que contienen caracteres `�`  
   **Descripción técnica**: Normalizar los archivos a UTF-8 limpio y revisar manualmente los encabezados para recuperar los acentos y símbolos perdidos.  
   **Justificación**: Garantiza legibilidad para agentes y herramientas de procesamiento automático.

## 🧾 Historial
- [2025-11-04] [David]: Propuestas generadas tras el análisis integrado de la rama feature/analisis-codigo.
