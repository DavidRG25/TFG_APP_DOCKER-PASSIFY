# 🚀 PaaSify Mega Stack: Arquitectura Distribuida (4 Contenedores)

Este ejemplo está diseñado para demostrar las capacidades avanzadas de orquestación de **PaaSify**, manejando un microservicio completo con múltiples capas de infraestructura.

## 🏗️ Arquitectura del Stack

El stack se compone de 4 servicios interconectados a través de una red virtual privada:

1.  **Gateway (Nginx Alpine)**:
    - **Puerto**: 80 (mapeado dinámicamente por PaaSify).
    - **Función**: Servidor web principal que entrega la interfaz de usuario estática.
    - **Dashboard**: Incluye una interfaz moderna con Tailwind CSS.

2.  **API Backend (Python/Flask)**:
    - **Puerto**: 5000 (mapeado dinámicamente).
    - **Función**: Procesa la lógica de negocio y se comunica con Redis.
    - **Interactividad**: Incrementa un contador de visitas cada vez que se consulta su endpoint `/api/status`.

3.  **Cache Layer (Redis Alpine)**:
    - **Puerto**: 6379 (interno).
    - **Función**: Almacena el contador de visitas en memoria para respuestas ultra rápidas.

4.  **Database (PostgreSQL 15)**:
    - **Puerto**: 5432 (interno).
    - **Función**: Capa de persistencia para datos críticos (aunque en este demo es puramente estructural).

## 🛠️ Instrucciones de Despliegue

1.  Comprime todo el contenido de esta carpeta (`04_compose_mega_stack`) en un archivo `.zip`.
2.  En el panel de PaaSify, ve a **"Nuevo Servicio"**.
3.  Selecciona la opción **"Personalizado"** y luego el modo **"Docker Compose"**.
4.  Sube el archivo `.zip`.
5.  PaaSify detectará automáticamente los 4 servicios y asignará puertos externos para que puedas acceder a ellos.

## 📊 Qué Probar

- **Pipeline Interactivo**: Accede al `gateway` y usa el formulario **"Inyectar Datos"**. Verás en tiempo real cómo el mensaje:
  1. Llega a **Nginx** (Gateway).
  2. Se procesa en **Flask** (API).
  3. Se persiste en **PostgreSQL** (Database).
  4. Se guarda en **Redis** (Cache).
- **Mapeo de Puertos**: Observa cómo PaaSify asigna puertos distintos a cada contenedor en la tabla de servicios.
- **Logs en Tiempo Real**: Abre los logs y observa cómo interactúan los contenedores entre sí.
- **Terminal**: Accede a la terminal del `api-backend` y prueba a hacer un `ping cache-layer` para verificar la red interna.
- **Persistencia Visual**: Detén el stack y verifica que los puertos asignados siguen siendo visibles en la UI.

---

_Ejemplo creado para validación de TFG - PaaSify Cloud Platform_
