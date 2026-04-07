# 🌐 Despliegue con DNS Externo y Certificados Automáticos (Let's Encrypt)

## Resumen

Esta guía cubre el caso de uso en el que PaaSify se despliega en un servidor (típicamente una VM universitaria) y el **dominio DNS se gestiona externamente** (ej: Cloudflare, Namecheap, Google Domains), sin disponer de certificados SSL/TLS propios en la máquina.

En este escenario, **Traefik** (el reverse proxy ya incluido en la arquitectura de PaaSify) se encarga de:
1. Obtener certificados SSL de **Let's Encrypt** automáticamente.
2. Renovarlos cada 90 días sin intervención humana.
3. Generar certificados individuales para cada subdominio de alumno de forma dinámica.

> 📂 **Guía detallada paso a paso:** Consulta [`deploy/DNS_EXTERNO_SIN_CERTIFICADOS.md`](../deploy/DNS_EXTERNO_SIN_CERTIFICADOS.md) para instrucciones completas con bloques de código y troubleshooting.

---

## Arquitectura TLS

```
                    ┌─────────────────────────┐
                    │     CLOUDFLARE / DNS     │
                    │  *.paasify.maes.dev → IP │
                    │   (modo DNS Only / gris) │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │      TRAEFIK v3.0       │
                    │  • Puertos 80 y 443     │
                    │  • Let's Encrypt (TLS)  │
                    │  • Redirección HTTP→HTTPS│
                    │  • Enrutamiento dinámico│
                    └───┬─────────────────┬───┘
                        │                 │
         Host(paasify)  │                 │ Host(app-5.paasify)
                        ▼                 ▼
                 ┌────────────┐   ┌──────────────┐
                 │   NGINX    │   │  Contenedor  │
                 │  (HTTP:80) │   │  del alumno  │
                 │  → Django  │   │ (cert auto)  │
                 └────────────┘   └──────────────┘
```

**Punto clave:** Traefik **termina el TLS** (descifra la conexión HTTPS) y le pasa tráfico HTTP plano a Nginx. Esto elimina la necesidad de que Nginx tenga certificados físicos `.crt`/`.key`.

---

## Archivos a modificar

Se necesitan cambios en **3 archivos** dentro de `deploy/`:

### 1. `deploy/.env` — Variables de entorno

```ini
# Permitir subdominios con el punto (.) delante
DJANGO_ALLOWED_HOSTS=.paasify.maes.dev,paasify.maes.dev,localhost,127.0.0.1

# NUEVO: Autorizar formularios HTTPS (evita error 403 CSRF en login)
DJANGO_CSRF_TRUSTED_ORIGINS=https://paasify.maes.dev,https://*.paasify.maes.dev

# URL base con HTTPS
PAASIFY_BASE_URL=https://paasify.maes.dev
```

### 2. `deploy/nginx/conf.d/paasify.conf` — Proxy inverso

**Eliminar** el bloque `listen 443 ssl` y los certificados. Dejar solo:

```nginx
server {
    listen 80;
    server_name paasify.maes.dev;

    location / {
        proxy_pass http://paasify_core:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto https;  # Forzar HTTPS, no $scheme
        # ... resto de headers ...
    }
}
```

> ⚠️ **Cambio crítico:** `X-Forwarded-Proto` debe ser `https` (fijo), no `$scheme` (dinámico). Sin esto, Django ve "http" y rechaza el CSRF.

### 3. `deploy/docker-compose.yml` — Orquestación

**En Traefik:** Activar Let's Encrypt con TLS Challenge:
```yaml
command:
  # Redirección global HTTP → HTTPS
  - "--entrypoints.web.http.redirections.entrypoint.to=websecure"
  - "--entrypoints.web.http.redirections.entrypoint.scheme=https"
  # Let's Encrypt vía puerto 443 (funciona con firewall en puerto 80)
  - "--certificatesresolvers.letsencrypt.acme.tlschallenge=true"
```

**En Nginx:** Cambiar labels TCP por HTTP:
```yaml
labels:
  - "traefik.http.routers.paasify_https.rule=Host(`paasify.maes.dev`)"
  - "traefik.http.routers.paasify_https.tls.certresolver=letsencrypt"
  - "traefik.http.services.paasify_https.loadbalancer.server.port=80"
```

---

## ¿TLS Challenge en vez de HTTP Challenge?

Las redes universitarias suelen **bloquear el puerto 80** con su firewall institucional, pero dejan abierto el 443. Let's Encrypt ofrece dos métodos de validación:

| Método | Puerto | ¿Funciona con firewall? |
|--------|--------|------------------------|
| `httpchallenge` | 80 | ❌ No |
| `tlschallenge` | 443 | ✅ Sí |

Por eso usamos `tlschallenge` en esta configuración.

---

## Requisitos para Cloudflare

Si el dominio está en Cloudflare, el registro DNS **debe estar en modo "DNS Only" (nube gris)**:

| Configuración | ¿Funciona? | Motivo |
|---------------|-----------|--------|
| 🟠 Proxy (nube naranja) | ❌ | Cloudflare intercepta el tráfico y bloquea la validación de Let's Encrypt |
| ⚪ DNS Only (nube gris) | ✅ | El tráfico llega directamente a tu servidor |

---

## Certificados de subdominios de alumnos

PaaSify genera automáticamente las labels de Traefik para cada contenedor de alumno (ver `containers/services.py`). Cuando un alumno crea un servicio, el código inyecta:

```python
labels.extend([
    f"traefik.http.routers.{router_name}.tls.certresolver=letsencrypt",
])
```

Esto hace que Traefik solicite un certificado individual a Let's Encrypt para cada subdominio nuevo (ej: `mi-app-5.paasify.maes.dev`), de forma **completamente automática**.

---

## Errores frecuentes y soluciones rápidas

| Error | Causa | Solución |
|-------|-------|----------|
| `nginx: [emerg] no ssl_certificate` | Nginx tiene `listen 443 ssl` sin certificados | Eliminar bloque SSL, dejar solo puerto 80 |
| `403 CSRF verification failed` | Falta `CSRF_TRUSTED_ORIGINS` o `X-Forwarded-Proto` incorrecto | Añadir variable al `.env` y fijar header en Nginx |
| `Timeout during connect (firewall)` | Puerto 80 bloqueado por firewall | Usar `tlschallenge` (puerto 443) |
| `ERR_SSL_UNRECOGNIZED_NAME_ALERT` | Traefik no tiene certificado listo | Borrar `acme.json`, reiniciar Traefik, abrir en incógnito |
| `rateLimited` en logs de Traefik | Demasiados intentos fallidos | Esperar 1h, borrar `acme.json`, reintentar |

---

## Referencias

- [Guía operativa completa](../deploy/DNS_EXTERNO_SIN_CERTIFICADOS.md) — Instrucciones paso a paso con configuraciones completas
- [Guía de despliegue general](./DEPLOYMENT.md) — Despliegue estándar con certificados propios
- [Traefik ACME Documentation](https://doc.traefik.io/traefik/https/acme/) — Documentación oficial de Traefik para Let's Encrypt
- [Let's Encrypt Rate Limits](https://letsencrypt.org/docs/rate-limits/) — Límites de peticiones de Let's Encrypt
