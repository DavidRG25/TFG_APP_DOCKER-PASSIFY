# BUG: Desactivar "Preservar Datos" borra los archivos del workspace Compose

**Fecha de detección:** 11/05/2026  
**Severidad:** Media-Alta  
**Estado:** Pendiente  

---

## Descripción

Cuando un servicio de tipo **Docker Compose Stack** tiene la opción **"Preservar Datos y Volúmenes"** desactivada, al redesplegar el servicio se borran no solo los volúmenes de Docker, sino también los **archivos fuente del workspace** (carpetas `api/`, `web/`, etc.) que fueron extraídos del `.zip` original.

Al intentar ejecutar `docker compose up --build`, Docker no encuentra las carpetas de build y falla con:

```
unable to prepare context: path "/app/media/services/11/api" not found
```

## Pasos para Reproducir

1. Crear un servicio Docker Compose subiendo un `.zip` que contenga carpetas con `build:` (ej: `build: ./api`, `build: ./web`).
2. Desplegar el servicio con "Preservar Datos" **activado** → Funciona correctamente.
3. **Desactivar** "Preservar Datos y Volúmenes".
4. Volver a desplegar (o editar y guardar el servicio).
5. **Resultado:** Error código 17 - `unable to prepare context: path not found`.

## Causa Raíz

El flujo de despliegue con persistencia desactivada ejecuta una limpieza que elimina los volúmenes **y los archivos extraídos del zip** en el directorio del servicio (`/app/media/services/<id>/`). Sin embargo, antes de hacer el `docker compose up --build`, **no se vuelve a extraer el `.zip`** para regenerar las carpetas de build necesarias.

## Comportamiento Esperado

Al desactivar "Preservar Datos":
- ✅ Se deben borrar los **volúmenes** de Docker (para resetear datos).
- ✅ Se debe **re-extraer el `.zip`** antes de ejecutar el build, para que las carpetas de contexto (`api/`, `web/`, etc.) estén disponibles.

## Workaround Actual

El usuario debe **borrar el servicio completamente** y volver a crearlo desde cero subiendo el `.zip` de nuevo.

## Archivos Probablemente Involucrados

- Buscar la lógica de despliegue Compose donde aparece el mensaje `"Persistencia desactivada: Eliminando volúmenes previos..."`.
- En ese mismo flujo, después de limpiar volúmenes, añadir un paso de re-extracción del zip antes del `docker compose up --build`.
