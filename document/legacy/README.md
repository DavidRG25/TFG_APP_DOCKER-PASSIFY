# Guía de Documentación del Proyecto
_Referencias y convenciones para mantener los registros técnicos dentro de `/document/`._

## 📋 Tipos de archivos
- `analisis-integrado-<rama>-AAAAMMDD.md`: consolidado diario de hallazgos por rama activa.
- `propuestas-<rama>-AAAAMMDD.md`: lista de cambios recomendados con detalle técnico y justificación.
- `cambio-<archivo>-<rama>-AAAAMMDD.md`: evidencia de modificaciones aprobadas, validaciones y resultados.
- `test-resultados-<rama>-AAAAMMDD.md`: bitácora de ejecuciones de pruebas y métricas obtenidas.
- `fallos-detectados-<rama>-AAAAMMDD.md`: registro de incidencias o errores derivados de pruebas.
- `pre-merge-report-AAAAMMDD.md`: análisis previo a fusiones hacia `main`, con riesgos y conflictos.
- `sincronizacion-<rama>-AAAAMMDD.md`: resumen de pulls o sincronizaciones con ramas auxiliares.
- `contexto-rama-AAAAMMDD.md`: inicio de cada ciclo documental indicando rama, estado y responsable.
- `sugerencias-fix-views-AAAAMMDD.md`: observaciones exclusivas para la rama `fix/views-adjustments`.

## 🧩 Reglas operativas
- Detecta la rama activa con `git branch --show-current` y trabaja solo sobre ella.
- Mantén versiones fechadas; no sobrescribas archivos existentes salvo para actualizar históricos autorizados.
- Solicita confirmación antes de modificar código, especialmente si la rama es `main`.
- Documenta cada acción con fecha y hora en el formato indicado por el plan maestro.
- Vincula cada cambio de código con su análisis, propuesta y validación correspondientes.

## 🧠 Flujo recomendado
1. Registrar el contexto diario (`contexto-rama-AAAAMMDD.md`).
2. Revisar documentación existente y crear `analisis-integrado-<rama>-AAAAMMDD.md`.
3. Elaborar `propuestas-<rama>-AAAAMMDD.md` y esperar aprobación.
4. Tras la aprobación, documentar la implementación mediante `cambio-<archivo>-<rama>-AAAAMMDD.md`.
5. Ejecutar o planificar pruebas y registrar resultados en `test-resultados-<rama>-AAAAMMDD.md`.
6. Si se detectan errores, crear o actualizar `fallos-detectados-<rama>-AAAAMMDD.md`.
7. Antes de solicitar merge hacia `main`, preparar `pre-merge-report-AAAAMMDD.md`.

## ✅ Buenas prácticas
- Utiliza títulos claros y secciones con emojis para mantener coherencia visual.
- Referencia rutas y commits cuando sea necesario para facilitar la auditoría.
- Adjunta conclusiones y próximos pasos en cada documento para guiar iteraciones futuras.
- Sincroniza los resultados con los registros en `/prompts/` cuando se emitan nuevas instrucciones.

## 🧾 Historial
- [2025-11-04] [David]: Creación de la guía de documentación siguiendo la nueva política de gestión en `/document/`.
