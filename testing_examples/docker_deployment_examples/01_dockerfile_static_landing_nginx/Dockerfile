# Ejemplo Dockerfile (Simplificado): landing estática con Nginx
# Usamos una imagen específica para entornos sin privilegios (non-root)
# para evitar complicaciones de permisos con carpetas de sistema.

FROM nginxinc/nginx-unprivileged:alpine

# Config Nginx personalizada (escuchando en 8080)
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# Contenido estático
COPY site/ /usr/share/nginx/html/

# No hace falta crear usuarios ni cambiar PIDs, la imagen ya viene lista
EXPOSE 8080

HEALTHCHECK --interval=10s --timeout=2s --retries=3 CMD wget -qO- http://127.0.0.1:8080/healthz || exit 1
