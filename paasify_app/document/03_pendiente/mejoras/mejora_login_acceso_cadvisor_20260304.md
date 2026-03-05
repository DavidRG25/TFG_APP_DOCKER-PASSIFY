# Mejora de Diseño: Interfaz de Autenticación y Acceso a Cadvisor

**Fecha**: 2026-03-04
**Tipo**: Mejora de UX/UI
**Prioridad**: Media
**Estado**: Pendiente

## 📋 Descripción

Actualmente, el acceso a la monitorización de contenedores mediante Cadvisor presenta dos inconvenientes a nivel de experiencia de usuario y diseño:

1. La autenticación para acceder a Cadvisor muestra un prompt de autenticación básica HTTP estándar del navegador, el cual rompe por completo la estética de PaaSify.
2. No existe un acceso directo configurado en el panel de control, forzando al administrador a teclear la URL del contenedor a mano para consultar los consumos de recursos.

## 🎯 Objetivos de la Mejora

1. **Diseño Integrado**: Reemplazar o envolver la autenticación básica de Cadvisor mediante un proxy inverso (como Nginx o Traefik) o integrando una pantalla de login intermedia en Django que tenga el diseño corporativo de PaaSify (colores, logotipos, etc.) antes de redireccionar y proveer las credenciales.
2. **Botón de Acceso (Dashboard Admin)**: Añadir un botón visual y accesible en el panel de administrador que redirija automáticamente a la URL correcta del Cadvisor, sin necesidad de escribir el puerto o la ruta a mano.

## 💡 Solución técnica propuesta

- **Proxy inverso / Login Django**: Si Cadvisor sigue usando basic auth nativo, se puede montar una vista en Django protegida por el login de Admin que actúe de proxy con Cadvisor, inyectando los headers de autorización en backend. Así el usuario solo ve el login de PaaSify.
- **UI**:
  - En `templates/professor/dashboard.html` o la vista central del Admin, añadir un botón llamado **"Monitorización de Contenedores"** con un icono de gráfica que envíe al usuario a la ruta del proxy/Cadvisor.

## 🛠 Impacto

- Mejora la percepción de "producto profesional".
- Acelera el acceso al administrador para consultar el estado de salud y recursos consumidos de los contenedores subyacentes.
