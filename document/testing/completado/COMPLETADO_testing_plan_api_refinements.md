# Documento de Pruebas: Mejoras de UI, Swagger API y Docker Cleanup (Refinements)

**Objetivo:** Verificar exhaustivamente de principio a fin los componentes añadidos para la mejora de calidad de software descritos y empaquetados en esta iteración. Todas estas pruebas han de superarse con un rotundo éxito.

---

## 🏗️ 1. Test: Documentación Interconectada (Swagger/ReDoc APIDocs)

**Validación Práctica:**

- [SI] Con la sesión iniciada, accede a la documentación técnica dedicada ([http://localhost:8000/paasify/containers/api-docs/](http://localhost:8000/paasify/containers/api-docs/)).
- [SI] Dale un vistazo a los endpoints protegidos bajo `/api/containers/`.
  - [SI] **POST (`/containers/`)**: Revisa las propiedades del Request Parameters. El campo `name` ahora debería lucir con su propio cajón semántico, detallando explicativamente la norma `"Tolerante a fallos humanos: Convierte espacios y caracteres no válidos a formato snake_case automáticamente."`
  - [SI] **PATCH (`/containers/{id}/`)**: Examina el campo `mode`. Debería indicar explícitamente y en un tono firme en la capa superior la ordenanza `"['dockerhub', 'custom']. Una vez definido en POST, el sistema bloquea con un error 400 Bad Request cualquier intento de mutarlo vía PATCH."`
  - [SI] **Comandos (`/start`, `/stop`, `/restart`, `/logs`)**: Deberían estar completamente documentadas ya que se han inyectado en el Schema. Podrás pre-visualizar el Status `200` y `500` configurados.
- [SI] Confirma por último que en el cajón de autorizaciones a nivel global, se usa internamente `ExpiringToken`, por lo que las peticiones desde el navegador nativas del panel estarán cubiertas sin romperse.

---

## 🧹 2. Test: Recolección y Limpieza de Imágenes Subyacentes de Docker

**Validación Práctica:**

- [SI] Construir intencionadamente en blanco un Contenedor de un fichero local dentro del Panel `Mis Servicios`. (Puedes subir un proyecto comprimido simulado rápido, o generar un `Dockerfile` base con Nginx/Python en limpio, dale a **Crear e Iniciar**).
- [SI] Dirígete rápidamente mediante Consola Externa / Visual al interior físico del sistema Host. Ejecuta en Terminal `docker images`.
- [SI] Observa y rastrea el hash identificativo local. Identificarás fácilmente cómo nació el _"Container Image"_ (`svc_<id>_<slug>_image`). Confirma en caliente que pesa X MB.
- [SI] Regresa al Frontend (Dashboard de PaaSify) y presiona en color Rojo Eliminar sobre este contenedor `Custom`. Espera un segundo a que corra internamente.
- [SI] Regresa y lanza de nuevo el comando CLI puro de la máquina física: `docker images`.
- [SI] Confirmar de manera inequívoca que la fila identificativa etiquetada de ese proyecto específico o imagen asociada ha sido radical y exitosamente vaporizada. Se ha liberado la memoria física a escala Host mediante la orden `client.images.remove` correctamente inyectada. (A su vez la instrucción oculta `prune` se debería de haber llevado residuos muertos `<none>:<none>` de este o anteriores proyectos).

---

## 🔔 3. Test: Feedbacks de HTMX e Interfaz de Alertas Integrada (SweetAlert)

**Validación Práctica:**

- [SI] **Trigger Positivo / Éxito Rotundo (Success Toast)**:
  - En la vista del Panel Administrativo de PaaSify (`http://localhost:8000/paasify/containers/`), pon la mirada en la esquina superior/inferior derecha.
  - Sobre un servicio funcional, haz click en _"Reiniciar"_, _"Start"_ o _"Stop"_.
  - En el mismo momento en el que el Servidor Python devuelve el status `200` y la Row de la tabla HTMX actualiza su indicador (LED Verde), se debe invocar limpiamente en pantalla superpuesta **UN TOAST PREMIUM (Notificación contextual verde neón/clara indicando Éxito en ejecución)** con efecto difuminado.
  - Durará 4 segundos aproximadamente perdiéndose a los lados por sí solo.
- [SI] **Trigger Negativo / Fallo Controlado (Error Toast)**:
  - Sobre un segundo servicio basado en `PostgreSQL` o similares (los cuales bloquean el script de entrada intencionadamente en seco por temas de contraseña vacía): Bórrale el `POSTGRES_PASSWORD` desde el Lápiz.
  - Dale la instrucción de correr el contenedor.
  - La respuesta fallará (el script lo detendrá tras crearlo o rechazará levantarlo). En su lugar de romper la página en blanco o crashear el servidor, deberías vislumbrar la alerta HTMX interpretada:
  - Un **TOAST ROJO ALARMISTA** estallará asomándose advirtiendo a la vista del usuario: `Error de Operación - Ocurrió un error inesperado al contactar.../Error de Docker nativo.` Todo, de forma estética, nativa e instintiva.
