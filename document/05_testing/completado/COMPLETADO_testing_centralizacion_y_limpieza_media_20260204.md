# Plan de Testing - Centralización y Limpieza de Media

**Fecha**: 04/02/2026  
**Tipo**: Testing de Infraestructura y Archivos  
**Estado**: COMPLETADO

---

## 🏗️ **PREREQUISITOS**

1. ✅ Servidor Django corriendo con `bash run.sh`
2. ✅ Haber aplicado las últimas migraciones (`python manage.py migrate`)
3. ✅ No tener archivos críticos sueltos en `media/` fuera de `services/`

---

## 🧪 TESTING 1: CREACIÓN DE SERVICIO (DOCKERFILE + ZIP)

### **Test 1.1: Flujo de Subida Centralizado**

**Objetivo**: Verificar que los archivos subidos van directamente a la carpeta del servicio.

**Pasos**:

1. Crear un nuevo servicio desde la UI eligiendo modo **Dockerfile**.
2. Subir un `Dockerfile` y un `codigo.zip`.
3. Hacer clic en **Crear**.

**Verificación**:

- [SI] El servicio se crea y arranca sin errores.
- [SI] No aparece el error _"The file cannot be reopened"_ en la terminal o logs.
- [SI] Verificar físicamente la carpeta `media/services/<id>/`:
  - [SI] Existe el archivo `Dockerfile`.
  - [SI] Existe el archivo `source.zip`.
  - [SI] El código está descomprimido en la raíz de esa carpeta.

**Resultado Esperado**: ✅ Archivos organizados correctamente en la carpeta del servicio.

> **Nota Bug Fix (2026-02-04)**: Se detectó un problema donde los servicios con Dockerfile se quedaban en "PENDING" al re-iniciarlos. Se ha corregido añadiendo protección contra tareas duplicadas y aumentando el número de hilos de ejecución simultáneos.

---

## 🧪 TESTING 2: CREACIÓN DE SERVICIO (DOCKER COMPOSE)

### **Test 2.1: Almacenamiento Atómico**

**Objetivo**: Verificar que el `docker-compose.yml` se guarda con su nombre original en la carpeta correcta.

**Pasos**:

1. Crear un nuevo servicio eligiendo modo **Docker Compose**.
2. Subir un archivo `.yml`.
3. Hacer clic en **Crear**.

**Verificación**:

- [SI] El archivo se guarda en `media/services/<id>/docker-compose.yml`.
- [SI] No existe el archivo con sufijos aleatorios (ej: `docker-compose_abc123.yml`) en la raíz de `media/`.

**Resultado Esperado**: ✅ Archivo guardado con nombre atómico en su workspace.

---

## 🧪 TESTING 3: LIMPIEZA TOTAL

### **Test 3.1: Borrado Físico**

**Objetivo**: Verificar que al eliminar un servicio no quedan rastros en el disco.

**Pasos**:

1. Eliminar un servicio recién creado desde la UI.

**Verificación**:

- [SI] La carpeta `media/services/<id>/` desaparece COMPLETAMENTE del disco.
- [SI] No quedan archivos huérfanos en ninguna otra subcarpeta.

**Resultado Esperado**: ✅ Borrado total del workspace.

---

## 🧪 TESTING 4: COMANDO DE GESTIÓN

### **Test 4.1: Barredora Legacy y Temporales**

**Objetivo**: Verificar que el comando `cleanup_media` mantiene el orden.

**Pasos**:

1. Abrir una terminal y ejecutar:
   ```powershell
   $env:DJANGO_DEBUG="True"; python manage.py cleanup_media
   ```

**Verificación**:

- [SI] El comando informa que los directorios antiguos (`user_code`, `dockerfiles`, `compose_files`) han sido eliminados.
- [SI] La carpeta `media/services/tmp/` se limpia de archivos antiguos.

**Resultado Esperado**: ✅ Directorio media limpio de carpetas heredades.

### **Test 4.2: Verificación de directorios limpios**

**Objetivo**: Confirmar que NO se crean carpetas legacy.

**Pasos**:

1. Iniciar un servicio cualquiera que ya existiera previamente.
2. Verificar la carpeta `media/`.

**Verificación**:

- [SI] No aparece la carpeta `user_code/`.
- [SI] No aparece la carpeta `dockerfiles/`.
- [SI] No aparece la carpeta `compose_files/`.

**Resultado Esperado**: ✅ Directorio media limpio tras operaciones habituales.

---

## 📊 RESUMEN DE TESTING

### **Total de Tests**: 4

**Estado**:

- Tests ejecutados: 4/4
- Tests pasados: 4/4
- Tests fallidos: 0/4

---

## 🎯 CRITERIOS DE ACEPTACIÓN

- [SI] Todos los archivos de un servicio viven únicamente en `media/services/<id>/`.
- [SI] Se eliminan las carpetas `user_code/`, `dockerfiles/` y `compose_files/` por ser legacy.
- [SI] No hay errores de "file locked" o "cannot be reopened" en Windows.
- [SI] El comando de limpieza funciona correctamente.

---

**Última actualización**: 2026-02-04 22:20  
**Estado**: COMPLETADO
