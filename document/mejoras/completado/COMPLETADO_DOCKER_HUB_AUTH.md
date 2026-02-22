# Configuración de Docker Hub Authentication

## 🎯 Objetivo

Aumentar el límite de pulls de imágenes de Docker Hub de **100 a 200 por cada 6 horas** mediante autenticación.

## 📋 Requisitos

1. Una cuenta gratuita en [Docker Hub](https://hub.docker.com/)
2. Acceso al archivo `.env` del proyecto

## 🔧 Configuración

### Paso 1: Crear cuenta en Docker Hub (si no tienes)

1. Ve a https://hub.docker.com/signup
2. Crea una cuenta gratuita
3. Verifica tu email

### Paso 2: Añadir credenciales al archivo `.env`

Edita el archivo `.env` en la raíz del proyecto y añade:

```bash
# === Docker Hub Authentication (Opcional) ===
DOCKER_HUB_USERNAME=tu_usuario_dockerhub
DOCKER_HUB_PASSWORD=tu_contraseña_dockerhub
```

**⚠️ IMPORTANTE:**

- Nunca subas el archivo `.env` al repositorio
- El archivo `.env` ya está en `.gitignore` para proteger tus credenciales

### Paso 3: Reiniciar el servidor

```bash
# Detener el servidor actual (Ctrl+C)
# Volver a ejecutar
bash run.sh
```

## ✅ Verificación

Al iniciar el servidor, deberías ver en los logs:

```
✓ Autenticado en Docker Hub como 'tu_usuario'
```

Si ves este mensaje, la autenticación fue exitosa y ahora tienes el límite aumentado.

## 🔒 Seguridad

### Alternativa: Usar Access Token en lugar de contraseña

Para mayor seguridad, puedes usar un **Access Token** en lugar de tu contraseña:

1. Ve a https://hub.docker.com/settings/security
2. Click en "New Access Token"
3. Dale un nombre descriptivo (ej: "PaaSify Production")
4. Selecciona permisos: **Read-only** es suficiente
5. Copia el token generado
6. Usa el token como contraseña en el `.env`:

```bash
DOCKER_HUB_USERNAME=tu_usuario_dockerhub
DOCKER_HUB_PASSWORD=dckr_pat_xxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Ventajas del Access Token:**

- Puedes revocarlo sin cambiar tu contraseña
- Puedes crear múltiples tokens para diferentes entornos
- Más seguro si el `.env` se filtra accidentalmente

## 📊 Límites de Docker Hub

| Tipo de cuenta  | Pulls anónimos | Pulls autenticados |
| --------------- | -------------- | ------------------ |
| Sin cuenta      | 100 / 6 horas  | N/A                |
| Cuenta gratuita | 100 / 6 horas  | **200 / 6 horas**  |
| Pro/Team        | N/A            | Ilimitado\*        |

\*Sujeto a fair use policy

## ❓ Troubleshooting

### Error: "unauthorized: incorrect username or password"

- Verifica que el usuario y contraseña sean correctos
- Si usas 2FA, debes usar un Access Token en lugar de la contraseña

### Error: "Get https://registry-1.docker.io/v2/: dial tcp: lookup registry-1.docker.io"

- Problema de conexión a internet
- Verifica tu firewall o proxy

### No veo el mensaje de autenticación

- Verifica que las variables estén correctamente configuradas en `.env`
- Asegúrate de haber reiniciado el servidor después de modificar `.env`
- Revisa que no haya espacios extra en las credenciales

## 🔄 Desactivar autenticación

Si quieres volver a usar Docker sin autenticación, simplemente:

1. Elimina o comenta las líneas en `.env`:

   ```bash
   # DOCKER_HUB_USERNAME=
   # DOCKER_HUB_PASSWORD=
   ```

2. Reinicia el servidor

El sistema funcionará normalmente con el límite estándar de 100 pulls/6h.
