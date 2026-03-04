# Vulnerabilidades Críticas de Seguridad - PaaSify (dev2)

**Fecha de Análisis:** 24 de Mayo de 2024  
**Última Actualización:** 13 de Diciembre de 2025  
**Estado:** COMPLETADO  
**Nivel de Riesgo:** CRÍTICO - Compromiso Total del Servidor Host

---

## ⚠️ Advertencia de Seguridad

Este documento detalla vulnerabilidades que permiten a un atacante autenticado (incluso con rol de alumno) obtener **acceso root completo** al servidor que aloja la aplicación. Estas vulnerabilidades deben ser remediadas **antes de cualquier despliegue en producción o entorno accesible desde internet**.

---

## 1. Escalada de Privilegios a Root mediante Montaje de Volúmenes

### Clasificación

- **Severidad:** CRÍTICA (10/10)
- **CVE Equivalente:** Similar a CVE-2019-5736 (Docker Container Escape)
- **Archivos Afectados:** `containers/views.py` (línea ~570), `containers/services.py`
- **Vector de Ataque:** Autenticación requerida (cualquier alumno)

### Descripción Técnica

La aplicación permite a los usuarios editar la configuración de sus servicios Docker a través de la vista `edit_service`. Uno de los campos editables es `volumes`, que se almacena como un campo JSON en la base de datos. Cuando el contenedor se reinicia o se crea, la aplicación utiliza este diccionario directamente en la llamada a la API de Docker sin ningún tipo de validación o sanitización.

**El flujo del ataque es el siguiente:**

1. Un alumno autenticado accede a la página de edición de uno de sus servicios
2. Modifica el campo `volumes` para incluir un montaje del sistema de archivos raíz del host
3. Al reiniciar el contenedor, Docker monta la raíz del servidor host (`/`) dentro del contenedor
4. El alumno abre la terminal web integrada en la aplicación
5. Desde la terminal, tiene acceso de lectura/escritura a todo el sistema de archivos del servidor

### Impacto Real

Un atacante puede:

- **Leer archivos sensibles:** Claves SSH, credenciales de base de datos, secretos de Django, certificados SSL
- **Modificar el sistema operativo:** Instalar backdoors, crear usuarios root, modificar configuraciones
- **Borrar el servidor completo:** Ejecutar `rm -rf /` desde dentro del contenedor afectaría al host
- **Robar datos de otros usuarios:** Acceder a volúmenes Docker de otros contenedores
- **Persistir el acceso:** Modificar `/etc/passwd`, agregar claves SSH autorizadas

### Escenario de Explotación

Imagina que un alumno llamado "Juan" tiene un servicio con ID 42. Juan envía una petición HTTP POST a `/containers/edit_service/42/` con el siguiente payload en el campo `volumes`:

```
{"/host_root": {"bind": "/", "mode": "rw"}}
```

Cuando Juan reinicia su contenedor y abre la terminal web, ve el directorio `/host_root` que contiene:

- `/host_root/etc/` - Configuraciones del sistema
- `/host_root/home/` - Directorios de usuarios
- `/host_root/var/lib/docker/` - Datos de Docker, incluyendo otros contenedores

Juan puede ejecutar: `cat /host_root/etc/shadow` y obtener los hashes de contraseñas de todos los usuarios del sistema.

### Solución Propuesta

**Enfoque 1 - Eliminar la funcionalidad (Recomendado):**
Los usuarios no deberían poder definir volúmenes arbitrarios. La aplicación debe gestionar internamente los volúmenes necesarios, mapeando únicamente directorios seguros y controlados.

**Enfoque 2 - Validación estricta (Si se requiere la funcionalidad):**

- Implementar una whitelist de rutas permitidas
- Validar que ninguna ruta comience con `/`, `/etc`, `/var`, `/home`, etc.
- Forzar que todos los volúmenes sean volúmenes Docker nombrados (no bind mounts)
- Auditar y registrar cualquier intento de montaje sospechoso

---

## 2. Inyección de Configuración en Docker Compose

### Clasificación

- **Severidad:** CRÍTICA (9/10)
- **Archivos Afectados:** `containers/services.py` (función `_run_compose_service`)
- **Vector de Ataque:** Subida de archivo malicioso

### Descripción Técnica

La aplicación permite a los usuarios subir un archivo `docker-compose.yml` para desplegar servicios complejos. El problema es que la aplicación ejecuta `docker compose up` directamente sobre este archivo sin analizar ni validar su contenido. Solo se verifica la extensión del archivo (`.yml` o `.yaml`), pero no su contenido.

**Configuraciones peligrosas en Docker Compose:**

1. **Modo privilegiado:** `privileged: true` otorga al contenedor casi todas las capacidades del kernel
2. **Montajes de host:** `volumes: - /:/host` permite acceso al sistema de archivos
3. **Red del host:** `network_mode: host` elimina el aislamiento de red
4. **PID del host:** `pid: host` permite ver y manipular procesos del host
5. **Capabilities:** `cap_add: - ALL` otorga todas las capacidades del kernel

### Impacto Real

Un archivo `docker-compose.yml` malicioso puede:

- Ejecutar contenedores con privilegios elevados
- Acceder a la red interna del servidor
- Montar el socket de Docker (`/var/run/docker.sock`) y controlar todos los contenedores
- Ejecutar código arbitrario con privilegios del daemon de Docker (generalmente root)

### Escenario de Explotación

Un alumno sube un archivo `docker-compose.yml` que contiene:

```yaml
services:
  malicious:
    image: alpine
    privileged: true
    network_mode: host
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
```

Este contenedor tiene:

- Acceso completo al daemon de Docker
- Puede crear/eliminar cualquier contenedor
- Puede acceder a la red del host sin restricciones
- Puede ejecutar comandos privilegiados

### Solución Propuesta

**Implementar un parser y validador de YAML:**

1. Parsear el archivo usando una librería segura (PyYAML con `safe_load`)
2. Validar contra una lista negra de configuraciones peligrosas
3. Rechazar archivos que contengan claves prohibidas
4. Forzar límites de recursos (CPU, memoria) en todos los servicios
5. Registrar y alertar sobre intentos de subida de archivos sospechosos

**Configuraciones que deben ser prohibidas:**

- `privileged`
- `network_mode: host`
- `pid: host` o `pid: container:...`
- `volumes` que apunten a rutas del host
- `cap_add` con capacidades peligrosas
- `security_opt` que deshabilite AppArmor/SELinux

---

## 3. Tokens JWT Irrevocables ("Tokens Zombie")

### Clasificación

- **Severidad:** ALTA (8/10)
- **Archivos Afectados:** `paasify/middleware/TokenAuthMiddleware.py`, `paasify/models/StudentModel.py`
- **Vector de Ataque:** Robo de token, compromiso de sesión

### Descripción Técnica

El sistema de autenticación por token JWT presenta dos problemas graves:

**Problema 1 - Tokens no revocables:**
El middleware de autenticación valida los tokens únicamente verificando su firma criptográfica y fecha de expiración. No compara el token recibido con el token almacenado en la base de datos. Esto significa que si un usuario regenera su token (por ejemplo, porque sospecha que fue comprometido), el token antiguo sigue siendo válido hasta su expiración natural (365 días por defecto).

**Problema 2 - Almacenamiento en texto plano:**
El campo `api_token` en el modelo `UserProfile` se guarda en texto plano en la base de datos. Si un atacante obtiene acceso a la base de datos (por ejemplo, mediante SQL injection o backup comprometido), puede robar todos los tokens y usarlos para autenticarse como cualquier usuario.

### Impacto Real

**Escenario 1 - Token robado:**

- Un alumno pierde su laptop con el token guardado en el navegador
- El alumno regenera su token desde su perfil
- El ladrón puede seguir usando el token antiguo durante 365 días
- No hay forma de invalidar el token comprometido

**Escenario 2 - Compromiso de base de datos:**

- Un atacante explota otra vulnerabilidad y obtiene acceso a la BD
- Extrae todos los tokens en texto plano
- Puede autenticarse como cualquier usuario (alumnos, profesores, administradores)
- Los tokens son válidos por un año completo

### Solución Propuesta

**Para la revocación:**
Modificar el middleware para que, además de validar la firma, compare el token recibido con el almacenado en la base de datos. Si no coinciden, rechazar la autenticación.

**Para el almacenamiento:**

- Hashear los tokens antes de guardarlos (usando bcrypt o Argon2)
- Al validar, hashear el token recibido y comparar con el hash almacenado
- Alternativamente, usar un sistema de tokens de sesión con expiración corta y refresh tokens

---

## 4. Ejecución Remota de Código vía Terminal Web

### Clasificación

- **Severidad:** CRÍTICA (10/10 cuando se combina con vulnerabilidad #1)
- **Archivos Afectados:** `containers/consumers.py` (clase `TerminalConsumer`)
- **Vector de Ataque:** WebSocket autenticado

### Descripción Técnica

La aplicación proporciona una terminal web interactiva que permite a los usuarios ejecutar comandos dentro de sus contenedores Docker. Esta funcionalidad se implementa mediante un WebSocket que abre una sesión de shell (`/bin/sh` o `/bin/bash`) dentro del contenedor sin ningún tipo de restricción, filtrado de comandos o jaula (chroot/jail).

**Por sí sola, esta vulnerabilidad es de severidad MEDIA**, ya que el usuario solo puede ejecutar comandos dentro de su propio contenedor aislado. Sin embargo, cuando se combina con la vulnerabilidad #1 (montaje de volúmenes), se convierte en CRÍTICA.

### Impacto Real

**Escenario combinado (Vulnerabilidad #1 + #4):**

1. Un alumno monta el sistema de archivos del host en su contenedor
2. Abre la terminal web
3. Ejecuta comandos que afectan directamente al servidor host
4. Tiene una shell root interactiva sobre el servidor de producción

**Incluso sin la vulnerabilidad #1, la terminal permite:**

- **Ataques de red lateral:** Si la red Docker no está aislada, puede escanear y atacar otros servicios internos
- **Consumo de recursos:** Ejecutar procesos que consuman CPU/RAM y afecten a otros usuarios
- **Minería de criptomonedas:** Usar los recursos del servidor para minar
- **Ataques de fuerza bruta:** Contra otros servicios accesibles desde la red Docker

### Solución Propuesta

**Medidas de mitigación:**

1. **Restricción de comandos:**
   - Implementar una whitelist de comandos permitidos
   - Bloquear comandos peligrosos (rm, dd, fork bombs, etc.)
   - Limitar el uso de redirecciones y pipes

2. **Aislamiento de red:**
   - Configurar redes Docker aisladas por usuario/asignatura
   - Implementar reglas de firewall (iptables) que limiten la conectividad
   - Prohibir acceso a la red del host

3. **Limitación de recursos:**
   - Configurar límites de CPU y memoria por contenedor
   - Implementar quotas de disco
   - Limitar el número de procesos simultáneos

4. **Auditoría y monitoreo:**
   - Registrar todos los comandos ejecutados en la terminal
   - Alertar sobre patrones sospechosos (escaneos de red, intentos de escalada)
   - Implementar rate limiting en el WebSocket

---

## Recomendaciones Generales

### Priorización de Remediación

1. **Inmediato (Antes de producción):**
   - Vulnerabilidad #1: Montaje de volúmenes
   - Vulnerabilidad #2: Docker Compose injection

2. **Urgente (Dentro de 1 semana):**
   - Vulnerabilidad #3: Tokens JWT
   - Vulnerabilidad #4: Terminal web

3. **Importante (Dentro de 1 mes):**
   - Implementar auditoría completa de seguridad
   - Penetration testing externo
   - Revisión de código por experto en seguridad

### Medidas de Seguridad Adicionales

- Implementar WAF (Web Application Firewall)
- Configurar IDS/IPS para detectar intentos de explotación
- Separar el daemon de Docker en un servidor dedicado
- Usar Docker en modo rootless cuando sea posible
- Implementar 2FA para cuentas de administrador
- Realizar backups cifrados y regulares
- Mantener logs de auditoría inmutables

---

**Documento preparado para:** Equipo de desarrollo PaaSify  
**Próxima revisión:** Después de implementar las remediaciones  
**Contacto de seguridad:** [Pendiente de asignar]
