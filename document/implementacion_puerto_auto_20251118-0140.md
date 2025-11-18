Implementacion - Puerto auto (20251118-0140)

Objetivo
- Asignar automaticamente un puerto aleatorio (40000-50000) cuando el usuario no indica ninguno en la creacion del servicio.

Detalles tecnicos
- `containers/services.py`: nuevo helper `generate_random_port` y `_reserve_random_port` para reservar un puerto aleatorio con fallback al scan secuencial si hay colisiones.
- El puerto asignado se guarda en `service.assigned_port` antes de lanzar el contenedor para reflejarlo en la tabla.
- Se mantiene la reserva explicita cuando el usuario provee `custom_port`.

Comportamiento antes
- Si el usuario no indicaba puerto, se tomaba el siguiente libre secuencialmente vía `PortReservation.reserve_free_port()`.

Comportamiento despues
- Si no hay puerto especificado, se reserva uno aleatorio dentro del rango y se persiste antes del run; compose sigue gestionando puertos via YAML.

Pruebas sugeridas
- Crear servicio sin puerto: debe mostrar un puerto aleatorio en la tabla y en `docker inspect` el mapeo adecuado.
- Crear con puerto indicado: respeta el valor solicitadosi esta libre.
- Dockerfile sin puerto: autoasignado y reflejado en logs/terminal/ssh.
