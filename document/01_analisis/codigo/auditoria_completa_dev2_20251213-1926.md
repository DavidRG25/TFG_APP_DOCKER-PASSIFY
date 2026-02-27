# Auditoría Completa de Seguridad y Calidad - Rama dev2

**Fecha de Análisis:** 24 de Mayo de 2024  
**Última Actualización:** 13 de Diciembre de 2025  
**Analista:** Jules (AI Security Agent)  
**Rama Analizada:** `dev2`  
**Alcance:** Código completo, configuraciones, dependencias y arquitectura

---

## Resumen Ejecutivo

Esta auditoría identifica **10 problemas de seguridad y calidad** en la rama `dev2` de PaaSify, clasificados en 4 niveles de severidad:

- **CRÍTICAS:** 4 vulnerabilidades que permiten compromiso total del servidor
- **ALTAS:** 2 vulnerabilidades que exponen datos sensibles o control del sistema
- **MEDIAS:** 2 problemas que pueden derivar en vulnerabilidades bajo ciertas condiciones
- **BAJAS:** 2 aspectos de deuda técnica que dificultan el mantenimiento seguro

**Conclusión principal:** La aplicación NO debe desplegarse en producción hasta remediar las vulnerabilidades CRÍTICAS y ALTAS.

---

## VULNERABILIDADES CRÍTICAS

### 1. Host Takeover mediante Montaje de Volúmenes Docker

**Ubicación:** `containers/services.py`, `containers/views.py`  
**Severidad:** CRÍTICA (10/10)  
**Estado:** Pendiente de remediación

**Descripción del problema:**

La aplicación permite a los usuarios modificar la configuración de volúmenes de sus contenedores Docker sin ninguna validación. Un usuario malicioso puede configurar su contenedor para montar el sistema de archivos raíz del servidor host, obteniendo acceso completo de lectura y escritura a todos los archivos del sistema operativo.

**¿Por qué es crítico?**

- Permite escalada de privilegios de "alumno" a "root del servidor"
- No requiere conocimientos técnicos avanzados (solo editar un campo JSON)
- Es explotable por cualquier usuario autenticado
- El impacto es inmediato y total (control completo del servidor)

**Contexto técnico:**

Docker utiliza el concepto de "volúmenes" para compartir datos entre el host y los contenedores. Existen dos tipos:
1. **Volúmenes nombrados:** Gestionados por Docker, seguros
2. **Bind mounts:** Montan directorios del host directamente, peligrosos si no se controlan

La aplicación permite a los usuarios especificar bind mounts arbitrarios, lo que es equivalente a darles acceso SSH root al servidor.

**Indicadores de compromiso:**

Si esta vulnerabilidad ha sido explotada, podrías encontrar:
- Contenedores con volúmenes sospechosos montando `/`, `/etc`, `/var`, etc.
- Archivos del sistema modificados recientemente
- Usuarios o claves SSH no autorizadas
- Procesos sospechosos ejecutándose en el host

---

### 2. Ejecución Remota de Código vía Terminal Web

**Ubicación:** `containers/consumers.py` (clase `TerminalConsumer`)  
**Severidad:** CRÍTICA (10/10 combinada con #1, MEDIA (5/10) aislada)  
**Estado:** Pendiente de remediación

**Descripción del problema:**

La terminal web integrada abre una shell interactiva dentro del contenedor del usuario mediante un WebSocket. No hay restricciones sobre qué comandos puede ejecutar el usuario, ni limitaciones de recursos, ni monitoreo de actividad sospechosa.

**¿Por qué es crítico cuando se combina con #1?**

Cuando un usuario monta el sistema de archivos del host (vulnerabilidad #1) y luego abre la terminal web (vulnerabilidad #2), obtiene una shell root interactiva sobre el servidor de producción. Es el equivalente a darle acceso SSH root a cualquier alumno.

**Riesgos incluso sin la vulnerabilidad #1:**

- **Ataques de red lateral:** Si la red Docker no está aislada, el usuario puede escanear y atacar servicios internos (bases de datos, APIs internas, otros contenedores)
- **Consumo abusivo de recursos:** Ejecutar procesos que consuman toda la CPU/RAM y afecten a otros usuarios
- **Minería de criptomonedas:** Usar los recursos del servidor para minar sin autorización
- **Persistencia:** Instalar backdoors dentro del contenedor que sobrevivan a reinicios

**Buenas prácticas que faltan:**

- Whitelist de comandos permitidos
- Limitación de recursos (CPU, memoria, procesos)
- Auditoría de comandos ejecutados
- Rate limiting en el WebSocket
- Detección de patrones sospechosos (escaneos de puertos, intentos de escalada)

---

### 3. Inyección de Configuración en Docker Compose

**Ubicación:** `containers/services.py` (función `_run_compose_service`)  
**Severidad:** CRÍTICA (9/10)  
**Estado:** Pendiente de remediación

**Descripción del problema:**

Los usuarios pueden subir archivos `docker-compose.yml` que la aplicación ejecuta directamente con `docker compose up`. Solo se valida la extensión del archivo (`.yml`), pero no su contenido. Un archivo malicioso puede incluir configuraciones que otorguen privilegios elevados al contenedor.

**Configuraciones peligrosas en Docker Compose:**

1. **Modo privilegiado (`privileged: true`):**
   - Otorga al contenedor casi todas las capacidades del kernel Linux
   - Permite acceder a dispositivos del host
   - Puede modificar configuraciones del kernel

2. **Montaje del socket de Docker:**
   - `volumes: - /var/run/docker.sock:/var/run/docker.sock`
   - Permite controlar el daemon de Docker desde dentro del contenedor
   - Equivale a acceso root sobre todos los contenedores

3. **Red del host (`network_mode: host`):**
   - Elimina el aislamiento de red
   - El contenedor ve todas las interfaces de red del host
   - Puede interceptar tráfico de otros servicios

4. **PID del host (`pid: host`):**
   - Permite ver y manipular todos los procesos del sistema
   - Puede enviar señales (kill) a procesos del host

**Escenario de ataque:**

Un alumno sube un `docker-compose.yml` que despliega un contenedor con modo privilegiado y acceso al socket de Docker. Desde ese contenedor, puede:
1. Crear nuevos contenedores con cualquier configuración
2. Acceder a volúmenes de otros usuarios
3. Detener servicios críticos
4. Extraer secretos y variables de entorno de otros contenedores

**Solución requerida:**

Implementar un parser YAML que analice el contenido del archivo antes de ejecutarlo y rechace cualquier configuración peligrosa. Esto debe incluir:
- Lista negra de claves prohibidas
- Validación de valores permitidos
- Forzado de límites de recursos
- Registro de intentos de subida de archivos sospechosos

---

### 4. Tokens JWT Irrevocables y Sin Cifrar

**Ubicación:** `paasify/middleware/TokenAuthMiddleware.py`, `paasify/models/StudentModel.py`  
**Severidad:** ALTA (8/10)  
**Estado:** Pendiente de remediación

**Descripción del problema:**

El sistema de autenticación por tokens JWT presenta dos fallos graves:

**Fallo 1 - Tokens "zombie" (no revocables):**

El middleware valida los tokens verificando únicamente:
- Que la firma criptográfica sea válida
- Que no hayan expirado (365 días por defecto)

NO verifica si el token coincide con el almacenado en la base de datos. Esto significa que si un usuario regenera su token (por ejemplo, porque sospecha que fue robado), el token antiguo sigue funcionando hasta que expire naturalmente.

**Consecuencias:**
- Un token robado no puede ser invalidado
- Si un empleado es despedido, su token sigue activo por meses
- No hay forma de forzar el cierre de sesión de un usuario
- Los tokens comprometidos tienen una vida útil de un año

**Fallo 2 - Almacenamiento en texto plano:**

El campo `api_token` en la tabla `UserProfile` se guarda sin cifrar. Si un atacante obtiene acceso a la base de datos (mediante SQL injection, backup comprometido, o acceso físico), puede:
- Robar todos los tokens de todos los usuarios
- Autenticarse como cualquier usuario (alumnos, profesores, administradores)
- Mantener acceso persistente durante 365 días

**Comparación con buenas prácticas:**

Sistemas seguros de tokens:
- Almacenan solo el hash del token (bcrypt, Argon2)
- Implementan listas de revocación
- Usan tokens de corta duración (15-60 minutos) con refresh tokens
- Registran el uso de tokens para detectar anomalías
- Permiten invalidación manual de tokens

---

## VULNERABILIDADES ALTAS

### 5. Exposición del Socket de Docker

**Ubicación:** `containers/docker_client.py`  
**Severidad:** ALTA (7/10)  
**Descripción:** Acceso sin restricciones al daemon de Docker

**Explicación del riesgo:**

La aplicación Django se conecta al daemon de Docker usando `docker.from_env()`, lo que típicamente significa que tiene acceso al socket Unix `/var/run/docker.sock`. Este socket es equivalente a acceso root sobre el sistema, ya que quien controla Docker controla todos los contenedores y puede crear contenedores privilegiados.

**¿Por qué es peligroso?**

Si un atacante logra ejecutar código arbitrario en la aplicación Django (por ejemplo, mediante una vulnerabilidad en una dependencia, deserialización insegura, o template injection), automáticamente obtiene acceso al daemon de Docker y, por ende, al servidor completo.

**Escenarios de explotación:**

1. **Vulnerabilidad en dependencia:** Una librería Python usada por Django tiene una vulnerabilidad RCE. El atacante la explota y ejecuta código que interactúa con el socket de Docker.

2. **Template injection:** Un error en un template Django permite inyectar código Python. El atacante usa `docker.from_env()` para crear un contenedor privilegiado.

3. **Deserialización insegura:** La aplicación deserializa datos no confiables (pickle, YAML). El atacante inyecta código que accede a Docker.

**Mitigaciones recomendadas:**

- Ejecutar el daemon de Docker en un servidor separado y acceder vía API remota con autenticación
- Usar Docker en modo rootless
- Implementar un proxy entre Django y Docker que valide todas las operaciones
- Aplicar políticas de AppArmor/SELinux que restrinjan el acceso al socket
- Monitorear el acceso al socket y alertar sobre operaciones sospechosas

---

### 6. Tokens API Almacenados en Texto Plano

**Ubicación:** `paasify/models/StudentModel.py` (campo `api_token`)  
**Severidad:** ALTA (7/10)  
**Descripción:** Tokens de autenticación sin cifrar en base de datos

**Detalle del problema:**

Además del problema de revocación mencionado en la vulnerabilidad #4, el almacenamiento en texto plano de los tokens tiene implicaciones adicionales:

**Riesgos de exposición:**

1. **Backups comprometidos:** Los backups de la base de datos contienen todos los tokens en claro. Si un backup se filtra o es robado, el atacante tiene acceso permanente.

2. **Logs de base de datos:** Consultas SQL que incluyan el campo `api_token` quedarán registradas en logs, potencialmente exponiendo tokens.

3. **Acceso de administradores:** Cualquier DBA o administrador de sistemas puede ver todos los tokens y usarlos para suplantar identidades.

4. **Ataques de timing:** Sin hashing, las comparaciones de tokens son vulnerables a ataques de timing que podrían revelar información sobre el token.

**Impacto en cumplimiento normativo:**

Si la aplicación maneja datos personales (GDPR, LOPD), almacenar credenciales en texto plano puede constituir una violación de las normativas de protección de datos, ya que no se están aplicando "medidas técnicas y organizativas apropiadas" para proteger los datos.

**Solución estándar:**

Los tokens deben ser hasheados antes de almacenarse, similar a cómo se manejan las contraseñas. Al validar un token:
1. Hashear el token recibido
2. Comparar el hash con el almacenado en BD
3. Si coinciden, autenticar al usuario

Esto garantiza que incluso si la BD es comprometida, los tokens no pueden ser usados directamente.

---

## VULNERABILIDADES MEDIAS

### 7. Vulnerabilidad Zip Slip en Descompresión de Archivos

**Ubicación:** `containers/services.py` (función `_unpack_code_archive_to`)  
**Severidad:** MEDIA (6/10)  
**Descripción:** Descompresión de archivos sin sanitización de rutas

**¿Qué es Zip Slip?**

Zip Slip es una vulnerabilidad que ocurre cuando se descomprime un archivo (ZIP, TAR, RAR) sin validar las rutas de los archivos contenidos. Un archivo malicioso puede incluir rutas relativas como `../../etc/passwd` que, al descomprimirse, escriben archivos fuera del directorio de destino.

**Ejemplo de ataque:**

Un alumno crea un archivo ZIP con la siguiente estructura:
```
malicious.zip
├── ../../var/www/html/backdoor.php
└── ../../home/admin/.ssh/authorized_keys
```

Al descomprimirse en `/tmp/user_code/`, los archivos se escriben en:
- `/var/www/html/backdoor.php` (backdoor web)
- `/home/admin/.ssh/authorized_keys` (acceso SSH)

**Estado actual en PaaSify:**

La función usa `shutil.unpack_archive()` y llamadas a `unrar`. Las versiones modernas de Python mitigan parcialmente este problema, pero no completamente. Además, el uso de `unrar` externo puede tener sus propias vulnerabilidades.

**Mitigación requerida:**

1. Validar todas las rutas antes de extraer
2. Rechazar archivos con rutas absolutas o que contengan `..`
3. Usar librerías de descompresión seguras y actualizadas
4. Extraer en un directorio temporal aislado
5. Verificar que todos los archivos extraídos estén dentro del directorio esperado

---

### 8. Gestión Redundante de Sesiones

**Ubicación:** `security/views/SecurityViews.py` (función `login`)  
**Severidad:** MEDIA (5/10)  
**Descripción:** Sesiones manuales duplican funcionalidad de Django

**Problema de diseño:**

La vista de login escribe manualmente datos en `request.session`:
- `user_id`
- `is_staff`
- Posiblemente otros campos

Estos datos duplican la información que Django ya gestiona automáticamente a través de su sistema de autenticación (`request.user`). Esta redundancia crea varios riesgos:

**Riesgo 1 - Desincronización:**

Si el estado del usuario cambia (por ejemplo, se le quitan permisos de staff), la sesión manual podría mantener `is_staff=True` mientras que `request.user.is_staff=False`. Esto puede llevar a:
- Bypass de controles de acceso
- Comportamiento inconsistente de la aplicación
- Confusión en el código sobre cuál es la "fuente de verdad"

**Riesgo 2 - Complejidad innecesaria:**

Mantener dos sistemas de sesión paralelos:
- Aumenta la superficie de ataque
- Dificulta las auditorías de seguridad
- Complica el mantenimiento del código
- Puede introducir bugs sutiles

**Riesgo 3 - Falta de invalidación:**

Si se invalida la sesión de Django pero no la manual (o viceversa), el usuario podría mantener acceso parcial o experimentar comportamientos impredecibles.

**Solución recomendada:**

Eliminar la gestión manual de sesión y confiar completamente en el sistema de autenticación de Django, que es robusto, bien probado y mantenido por la comunidad.

---

## DEUDA TÉCNICA Y PROBLEMAS DE CALIDAD

### 9. Lógica de Negocio en Templates (JavaScript Inline)

**Ubicación:** `templates/containers/student_panel.html` y otros templates  
**Severidad:** BAJA (3/10)  
**Descripción:** JavaScript inline dificulta seguridad y mantenimiento

**Problemas de seguridad:**

**Content Security Policy (CSP):**
CSP es un mecanismo de seguridad que previene ataques XSS al controlar qué scripts pueden ejecutarse. Una política CSP estricta prohíbe scripts inline. La aplicación actual no puede implementar CSP estricto debido a la cantidad de JavaScript inline en los templates.

**Ataques XSS:**
Si existe una vulnerabilidad XSS en algún lugar de la aplicación, el JavaScript inline puede ser un vector de explotación. Es más difícil auditar y sanitizar código JavaScript mezclado con HTML que código en archivos separados.

**Problemas de mantenimiento:**

- Dificulta la reutilización de código
- Complica el testing automatizado
- Hace difícil aplicar linters y herramientas de análisis estático
- Mezcla responsabilidades (presentación + lógica)

**Recomendación:**

Migrar todo el JavaScript a archivos externos y usar un sistema de build (Webpack, Vite) para gestionar dependencias y optimizar el código.

---

### 10. Falta de Identidad Visual Propia (Bootstrap Genérico)

**Ubicación:** Todos los templates  
**Severidad:** BAJA (2/10)  
**Descripción:** Uso genérico de Bootstrap sin personalización

**Impacto en seguridad:**

Aunque principalmente es un problema de UX, tiene implicaciones de seguridad:

**Phishing:**
Una interfaz genérica es más fácil de clonar para ataques de phishing. Los usuarios no pueden distinguir fácilmente entre el sitio real y una copia maliciosa.

**Confianza del usuario:**
Una interfaz profesional y única aumenta la confianza del usuario, lo que puede hacer que reporten comportamientos sospechosos más rápidamente.

**Impacto en usabilidad:**

- Dificulta la adopción por parte de usuarios
- No transmite profesionalismo
- Puede confundirse con otras aplicaciones
- No refleja la identidad de la institución educativa

**Recomendación:**

Implementar un sistema de diseño propio (ver documento de propuesta de rediseño UI/UX) que incluya:
- Paleta de colores distintiva
- Tipografía personalizada
- Componentes únicos
- Animaciones y microinteracciones
- Tema oscuro moderno

---

## Matriz de Priorización

| # | Vulnerabilidad | Severidad | Impacto | Facilidad de Explotación | Prioridad |
|---|---|---|---|---|---|
| 1 | Host Takeover (Volúmenes) | CRÍTICA | Muy Alto | Muy Fácil | P0 - Inmediato |
| 2 | RCE Terminal Web | CRÍTICA | Muy Alto | Fácil | P0 - Inmediato |
| 3 | Docker Compose Injection | CRÍTICA | Muy Alto | Fácil | P0 - Inmediato |
| 4 | Tokens JWT Irrevocables | ALTA | Alto | Media | P1 - Urgente |
| 5 | Exposición Socket Docker | ALTA | Alto | Difícil | P1 - Urgente |
| 6 | Tokens en Texto Plano | ALTA | Alto | Media | P1 - Urgente |
| 7 | Zip Slip | MEDIA | Medio | Media | P2 - Importante |
| 8 | Sesiones Redundantes | MEDIA | Bajo | Difícil | P2 - Importante |
| 9 | JavaScript Inline | BAJA | Bajo | N/A | P3 - Deseable |
| 10 | Bootstrap Genérico | BAJA | Muy Bajo | N/A | P3 - Deseable |

---

## Roadmap de Remediación

### Fase 1: Seguridad Crítica (Semanas 1-2)
**Objetivo:** Eliminar vulnerabilidades que permiten compromiso del servidor

- [ ] Implementar validación estricta de volúmenes Docker
- [ ] Agregar parser y validador de Docker Compose
- [ ] Implementar restricciones en terminal web
- [ ] Configurar aislamiento de red Docker

**Criterio de éxito:** Penetration test no logra obtener acceso al host

### Fase 2: Autenticación y Autorización (Semana 3)
**Objetivo:** Asegurar el sistema de tokens

- [ ] Implementar revocación de tokens JWT
- [ ] Hashear tokens antes de almacenar
- [ ] Reducir tiempo de expiración de tokens
- [ ] Implementar refresh tokens

**Criterio de éxito:** Tokens robados pueden ser invalidados inmediatamente

### Fase 3: Hardening General (Semana 4)
**Objetivo:** Reducir superficie de ataque

- [ ] Implementar validación de archivos ZIP/TAR
- [ ] Eliminar gestión manual de sesiones
- [ ] Configurar CSP estricto
- [ ] Implementar rate limiting

**Criterio de éxito:** Auditoría de seguridad externa sin hallazgos críticos

### Fase 4: Mejoras de Calidad (Semanas 5-6)
**Objetivo:** Deuda técnica y UX

- [ ] Migrar JavaScript a archivos externos
- [ ] Implementar sistema de diseño propio
- [ ] Mejorar logging y monitoreo
- [ ] Documentar arquitectura de seguridad

**Criterio de éxito:** Código mantenible y profesional

---

## Herramientas de Testing Recomendadas

### Análisis Estático
- **Bandit:** Análisis de seguridad para Python
- **Safety:** Verificación de dependencias vulnerables
- **Semgrep:** Detección de patrones inseguros

### Análisis Dinámico
- **OWASP ZAP:** Scanner de vulnerabilidades web
- **Burp Suite:** Testing manual de seguridad
- **Docker Bench:** Auditoría de configuración Docker

### Monitoreo
- **Falco:** Detección de comportamiento anómalo en contenedores
- **Trivy:** Escaneo de vulnerabilidades en imágenes Docker
- **Sysdig:** Monitoreo de seguridad en tiempo real

---

## Conclusiones y Recomendaciones Finales

### Estado Actual
La aplicación presenta **vulnerabilidades críticas** que la hacen **no apta para producción**. Un atacante con conocimientos básicos puede obtener acceso root al servidor en cuestión de minutos.

### Acciones Inmediatas Requeridas
1. **NO desplegar en producción** hasta remediar vulnerabilidades P0
2. **Restringir acceso** a la instancia de desarrollo actual
3. **Auditar logs** para detectar posibles explotaciones pasadas
4. **Iniciar Sprint de Seguridad** enfocado en vulnerabilidades críticas

### Visión a Largo Plazo
Con las remediaciones propuestas, PaaSify puede convertirse en una plataforma segura y robusta para educación en contenedores. Se recomienda:
- Establecer un programa de seguridad continua
- Realizar auditorías trimestrales
- Mantener un proceso de divulgación responsable de vulnerabilidades
- Formar al equipo en desarrollo seguro (OWASP Top 10, Secure SDLC)

---

**Próximos Pasos:**
1. Revisar este documento con el equipo de desarrollo
2. Priorizar y asignar recursos para la remediación
3. Establecer un cronograma de implementación
4. Configurar entorno de testing de seguridad
5. Iniciar la Fase 1 del roadmap de remediación

**Documento preparado por:** Jules (AI Security Agent)  
**Revisado por:** [Pendiente]  
**Próxima auditoría:** Después de completar Fase 1-2 del roadmap
