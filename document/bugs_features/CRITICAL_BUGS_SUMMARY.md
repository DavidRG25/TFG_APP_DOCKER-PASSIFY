# Vulnerabilidades Críticas - PaaSify (dev2)

**Fecha:** 2024-05-24  
**Estado:** PENDIENTE DE REMEDIACIÓN  
**Severidad:** CRÍTICA - Compromiso Total del Servidor

---

## 1. Escalada de Privilegios a Root (Host Takeover)

**Archivo:** `containers/views.py` (L~570), `containers/services.py`  
**CVE Equivalente:** Similar a CVE-2019-5736 (Docker Escape)

**Descripción:**
La vista `edit_service` acepta JSON en campo `volumes` sin validación. Docker ejecuta contenedor con estos volúmenes.

**PoC:**
```json
POST /containers/edit_service/<id>/
{
  "volumes": "{"/host_root": {"bind": "/", "mode": "rw"}}"
}
```

**Impacto:** Acceso root completo al servidor host

**Remediación:**
```python
# Eliminar capacidad de volúmenes arbitrarios
volumes = {service.volume_name: {"bind": "/data", "mode": "rw"}}
```

---

## 2. Inyección Docker Compose

**Archivo:** `containers/services.py` (`_run_compose_service`)

**Descripción:**
Ejecución de `docker compose up` sobre archivo subido sin validación de contenido.

**Remediación:**
- Parser YAML con whitelist
- Prohibir: `privileged`, `network_mode: host`, `pid: host`
- Forzar límites de recursos

---

## 3. Tokens JWT Zombies (Irrevocables)

**Archivo:** `paasify/middleware/TokenAuthMiddleware.py`

**Descripción:**
Middleware solo verifica firma, ignora revocación en BD.

**Remediación:**
```python
if user.user_profile.api_token != token:
    return JsonResponse({"detail": "Token revocado"}, status=401)
```

---

## 4. RCE Terminal Web

**Archivo:** `containers/consumers.py` (`TerminalConsumer`)

**Descripción:**
WebSocket abre shell sin restricciones. Combinado con volúmenes = root shell.

**Remediación:**
- Restricciones de comandos
- Aislamiento de red Docker
- Limitar capabilities

---

**ACCIÓN REQUERIDA:** Implementar FASE 1 del Plan Maestro antes de producción
