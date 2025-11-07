# Plan de trabajo — Servicios SSH y volúmenes (2025-11-05)

## 1. Contexto inicial
1. Proyecto: TGF_APP_DOCKER-PASSIFY (rama `develop`).
2. Objetivo previo: modernizar "Asignatura → Mis servicios" eliminando conexión local, habilitando SSH automático, gestionando volúmenes y mejorando UX/seguridad.
3. Estado actual tras últimos cambios: sidecar SSH experimental, nuevo modal HTMX, migraciones `0008` y `0033`; persisten referencias legacy (`Sport`, `enable_ssh`) y problemas de integración Docker/WSL.

## 2. Alcance inmediato (fases)
1. Fase 1 – Limpieza de dependencias legacy
   - Sustituir `Sport` por `Subject` en vistas y consultas.
   - Retirar lógica basada en `enable_ssh`; alinear con `ssh_port` y `volume_name`.
   - Verificar que creación/listado de servicios funcionan sin excepciones.
2. Fase 2 – Integración Docker + SSH
   - Normalizar `get_docker_client()` sin `sudo` y mantener `client.ping()` multiplataforma.
   - Definir estrategia SSH funcional (sidecar o alternativa) garantizando entrega de credenciales y networking con el contenedor principal.
   - Asegurar limpieza de contenedores, puertos y volúmenes (`svc_{service_id}`) en `remove_container`.
3. Fase 3 – Cobertura y utilidades
   - Restaurar tests de `containers/tests.py` con skips condicionales.
   - Corregir comandos de management (`create_test_user`, `add_allowed_image`) y extender ejemplos si procede.
   - Ejecutar pruebas locales/documentar limitaciones por permisos Docker.
4. Fase 4 – Documentación y trazabilidad
   - Actualizar archivos `cambio_` y `testing_` en UTF-8 con el comportamiento final.
   - Marcar documentos legacy (`Sport`, `Player`) como históricos o actualizarlos.
   - Registrar resultados en nuevos `analisis_/cambio_/implementacion_` según corresponda.

## 3. Entregables por fase
1. Fase 1: diffs de vistas/servicios sin errores + revisión manual básica.
2. Fase 2: implementación SSH consolidada, pruebas mínimas y documentación de uso.
3. Fase 3: suite de tests restaurada, comandos funcionales, notas de bloqueo si Docker no está disponible.
4. Fase 4: documentación actualizada y recomendaciones finales.

## 4. Riesgos y mitigación
1. Acceso restringido al daemon Docker → documentar permisos, proponer uso de socket TCP o mocks.
2. Compatibilidad Windows/WSL → evitar comandos dependientes de `sudo`, validar rutas y volúmenes.
3. Coherencia de migraciones → revisar dependencias (`0008`, `0033`) y preparar notas de migración.

## 5. Próximos pasos
1. Iniciar Fase 1 aplicando correcciones mínimas para restituir funcionalidad básica.
2. Tras cada fase, dejar constancia en `document/` y comunicar bloqueos relevantes.
