#!/bin/sh
echo "[PAASIFY-LOG] Iniciando servidor Nginx estático..."
echo "[PAASIFY-LOG] Cargando archivos de configuración en /etc/nginx/conf.d/"
echo "[PAASIFY-LOG] Sitio listo en puerto 8080"

# Bucle en segundo plano para generar un log cada 10 segundos
(
  while true; do
    echo "[LIVE-STAY-ALIVE] Registro de prueba: $(date)"
    sleep 30
  done
) &

# Ejecutar Nginx
exec nginx -g "daemon off;"
