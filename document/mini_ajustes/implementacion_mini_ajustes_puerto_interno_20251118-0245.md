Implementacion - Mini ajustes puerto interno (20251118-0245)

Problema
- Los servicios custom (Dockerfile/compose) siempre mapeaban a 80/tcp, bloqueando apps que escuchan en otros puertos (Flask 5000, Django 8000, Node 3000).

Cambios realizados
- Backend: `containers/services.py` usa `internal_port = service.internal_port or 80` y lo persiste si venia vacio; los puertos se mapean como `{f\"{internal_port}/tcp\": external}`.
- Serializer: `containers/serializers.py` admite `internal_port` opcional, valida rango 1-65535 y por defecto fija 80.
- Frontend: `templates/containers/student_panel.html` agrega campo opcional "Puerto interno del contenedor" (solo en modo custom) con ayuda y ejemplos; se habilita/inhabilita junto a los bloques custom.
- Tabla de servicios: `templates/containers/_service_rows.html` muestra interno y externo (interno por defecto 80).

Compatibilidad
- Servicios existentes sin internal_port siguen usando 80 por defecto; no se tocan.

Pruebas sugeridas
- Crear servicio Flask con puerto interno 5000 y externo 49123: `docker run` debe mapear 49123:5000 y la app responde en 49123.
- Crear sin puerto interno: usa 80 por defecto, igual que antes.
- Valida que internal_port fuera de rango rechaza la creacion con error en el campo.
