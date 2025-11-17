# Analisis — Endpoints y UI (Fase D) - 20251116-2347

## Problemas pendientes
1. El modal "Logs" solo muestra la respuesta de Docker, y ahora necesitamos asegurar que siempre incluya service.logs (build logs). Verificar tambien el endpoint de Dockerfile (mostrar contenido guardado en MEDIA_ROOT).
2. La terminal debe impedirse cuando el contenedor no existe/esta en error para evitar _PipeSocket.
3. El boton "Dockerfile" puede seguir fallando si el archivo se procesó desde ZIP (hay que confirmar rutas del FileField). 

## Áreas a revisar
- containers/views.py::logs, _serve_code, 	erminal_view
- Templates _service_rows.html (boton Dockerfile/Terminal)
- URLs / endpoints relacionados

## Plan de accion Fase D
1. **Endpoint logs**: ya usa service.logs (Fase C), pero se debe verificar que el fragmento ant XSS (escape) se aplica.
2. **Endpoint Dockerfile/Docker-compose**: asegurar que _serve_code maneje FileField sin archivo y mostrar mensaje amistoso si no hay contenido.
3. **Terminal**: deshabilitar definitivamente el boton cuando no existe container_id y mejorar el mensaje en 	erminal_view si el contenedor desaparecio.
4. **UI**: mostrar estados y tooltips para aclarar que la terminal solo funciona con contenedores en RUNNING.

Este analisis guiara la Fase D.
