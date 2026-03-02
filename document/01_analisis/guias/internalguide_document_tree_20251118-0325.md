# internalguide_document_tree_20251118-0325

## Objetivo
Dejar registro de la nueva estructura del directorio `document/` para facilitar auditorias.

## Alcance
Incluye la reorganizacion de archivos existentes y la creacion de carpetas dedicadas (analisis, implementacion, testing, plan, cambio, mini_ajustes, legacy, internal_guides). No modifica el contenido de los Markdown.

## Impacto
- Cada tipo de documento tiene ubicacion fija y respeta la convencion `<tipo>_<descripcion>_<YYYYMMDD>-<HHMM>.md`.
- Scripts o flujos que consumen documentacion deben actualizar sus rutas.

## Pasos
1. Se movieron todos los `analisis_*` a `document/analisis/`.
2. Los `implementacion_*` se trasladaron a `document/implementacion/`.
3. Se crearon `document/testing/`, `document/plan/` y `document/cambio/` para los prefijos respectivos.
4. `document/internal_guides/` aloja guias estructurales como esta y la del wrapper SSH.
5. Se elimino la carpeta `document/features/` una vez vacia.

## Validacion
- Comandos `ls document/<carpeta>` muestran los archivos esperados.
- `git status` refleja los movimientos (elim/res + nuevas rutas) para seguimiento en commit.

## Changelog
- 2025-11-18 03:25: Reorganizacion inicial.
