# Plan de Implementación: Edición Avanzada y Persistencia de Volúmenes

**Fecha:** 2026-02-21  
**Versión:** 1.0.0  
**Estado:** ✅ Completado

---

## 🎯 Objetivo

Cambiar el paradigma actual del proceso de "Edición" en el backend. Actualmente, la edición funciona de manera destructiva (el servicio viejo se elimina de la base de datos y se crea uno nuevo desde cero). El objetivo es que la pantalla de edición tenga una **funcionalidad real de modificación (editar)** sin ser destructiva por defecto, permitiendo actualizar propiedades como la **Imagen de DockerHub** y dando al usuario control total sobre la **Persistencia de Volúmenes** para no perder sus datos (mediante un switch).

---

## ⚠️ Reglas Fundamentales

### 1. **Paradigma de Edición (No Destructivo)**

El registro del servicio en la base de datos (`ContainerConfiguration` / `Service`) NO debe ser eliminado durante la edición. Se debe actualizar el registro existente.

### 2. **Prioridad a la Seguridad de Datos**

- El switch de "Preservar Volúmenes de Datos" DEBE estar **activado por defecto** (`keep_volumes = True`).
- Nunca se deben borrar volúmenes de usuario (bases de datos, repositorios) a menos que el usuario apague el switch explícitamente y pulse guardar.

### 3. **Consistencia Transaccional**

- Si se cambia la imagen y el proceso de reconstrucción (hacer `pull` de la nueva y levantar el contenedor) falla, el servicio no debe quedar inutilizado de forma irreversible. El backend debe gestionar y reportar el error con claridad.

---

## 📦 Nuevas Funcionalidades: Edición y Persistencia

### 🖼️ Funcionalidad 1: Editar Imagen (Modo DockerHub)

**Afecta a:** Servicios de tipo `dockerhub`

**Descripción:**

- El campo `Imagen` (ej. `mysql:8`) actual, que se encuentra bloqueado (`readonly`/`disabled`), pasa a ser editable para este modo de despliegue.
- Permite actualizar la versión de una aplicación de forma natural (ej. `mysql:8` -> `mysql:latest`).

### 💾 Funcionalidad 2: Switch "Preservar Volúmenes"

**Afecta a:** Todos los modos (Custom, DockerHub...)

**Descripción:**

- Un interruptor final en el formulario.
- **Activado (`ON`)**: Al guardar cambios (ej. cambiar puerto o imagen), Docker detendrá el contenedor, le aplicará la nueva configuración y lo levantará reconectando los mismos volúmenes anteriores.
- **Desactivado (`OFF`)**: Borrón y cuenta nueva. Se purgan los volúmenes antiguos junto con el contenedor y se levanta en blanco.

**Ubicación en UI (Modal/Página de Edición):**

```text
┌──────────────────────────────────────────────┐
│ [ Nombre de Servicio ] [ Proyecto ]          │
│                                              │
│ [ Tipo (DockerHub) v] [ Imagen: nginx:latest]│ ← Nuevo: Editable
│                                              │
│ [ Puertos y Variables de Entorno ... ]       │
├──────────────────────────────────────────────┤
│ 💾 Opciones de Reconstrucción                   │
│                                              │
│ [x] Preservar Volúmenes de Datos             │ ← Nuevo Switch
│     (Mantenlo activado para no perder bd...) │
│                                              │
│                         [ Cancelar ] [ Guardar]│
└──────────────────────────────────────────────┘
```

---

## 🏗️ Arquitectura de Implementación

### 1. **Modificación de Serializadores (Backend API)**

**En `api/serializers.py`:**

```python
class ContainerConfigurationUpdateSerializer(serializers.ModelSerializer):
    # Nuevo campo transitorio para capturar la intención de persistencia
    keep_volumes = serializers.BooleanField(default=True, write_only=True, required=False)

    class Meta:
        model = ContainerConfiguration
        # La 'image' pasa a poder incluirse en la actualización
        fields = ['name', 'image', 'internal_port', 'env_vars', 'keep_volumes', ...]

    def update(self, instance, validated_data):
        # 1. Extraer boolean temporal
        keep_volumes = validated_data.pop('keep_volumes', True)

        # 2. Actualizar instancia de forma normal (Edición real)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 3. Llamar al manager para reiniciar aplicando / no aplicando volúmenes
        docker_manager.rebuild_service(instance, keep_volumes=keep_volumes)

        return instance
```

### 2. **Lógica de Reconstrucción (Docker Manager)**

**En `services.py` o backend de docker:**

```python
def rebuild_service(service, keep_volumes=True):
    if service.mode == 'custom' and service.has_compose_file():
        if keep_volumes:
            run_cmd("docker-compose down") # Preserva volúmenes nombrados
        else:
            run_cmd("docker-compose down -v") # Purga todo

        run_cmd("docker-compose up -d --build")
    else:
        # Modo DockerHub / Simple Dockerfile
        run_cmd(f"docker stop {service.container_name}")
        if keep_volumes:
            run_cmd(f"docker rm {service.container_name}") # Seguro
        else:
            run_cmd(f"docker rm -v {service.container_name}") # Purgar

        # Re-levantar con run usando la nueva .image y configs
        start_container_logic(service)
```

---

## 📋 Orden de Implementación

### Fase 1: API y Logica de Negocio (Backend)

- [ ] Modificar `serializers.py` para aceptar `keep_volumes` y permitir la edición de `image`.
- [ ] Modificar `views.py` o `services.py` para adaptar el paradigma a (Update Real) en lugar de Delete->Create.
- [ ] Implementar la condicional de flags `-v` en los comandos de borrado de Docker.

### Fase 2: Interfaz de Usuario (Frontend HTML/HTMX)

- [ ] Quitar el atributo `disabled`/`readonly` del campo de imagen cuando la vista sea en modo edición (solo si permite editar imagen por lógica de negocio).
- [ ] Añadir la sección de Configuración Avanzada con el Switch estilo Toggle.
- [ ] Añadir los textos de alerta correspondientes al switch.
- [ ] Asegurarse de que HTMX recolecta y envía el campo `keep_volumes` en la petición `PATCH`.

### Fase 3: Testing y Comprobación

- [ ] Ejecutar prueba de actualización de versión (ej. Nginx) comprobando los logs y la nueva interfaz de API.
- [ ] Ejecutar prueba encendiendo/apagando el switch con una base de datos de prueba para asegurar su persistencia.

---

## 🧪 Casos de Prueba

### Caso 1: Actualización Menor (Persistente)

```
Servicio: mysql:5.7
Acción UI: Cambiar a mysql:8.0 y dejar Switch (ON).
Comportamiento: El contenedor se reinicia. En los logs se ve la carga de mysql:8.0. Una query a la DB muestra que todos los datos siguen ahí.
```

### Caso 2: Reconstrucción Limpia (Destructivo)

```
Servicio: App Node.js con logs y fallos.
Acción UI: Se apaga el Switch de volúmenes (OFF). Guardar.
Comportamiento: `docker rm -v` ejecutado. El nuevo contenedor no tiene datos almacenados históricamente.
```

---

## 📝 Notas Importantes

1. **Gestión de Errores de Imagen**: Si el usuario introduce una imagen de DockerHub inventada (`pepito:falsa`), Docker dará error al hacer pull. Debemos capturar esa excepción en la reconstrucción y en la medida de lo posible notificar al frontend.
2. **Restricción Catalog**: Evitar que el campo de imagen se pueda habilitar para servicios del catálogo (imágenes bloqueadas y gestionadas por profesores).

---

**Fecha de creación:** 2026-02-21  
**Versión:** 1.0.0  
**Estado:** 📋 Planificación completa, listo para implementación
