# Mejora Baja Prioridad: Imagen de Perfil y Gestión de Contraseñas Temporales

**Fecha creación**: 2026-02-07  
**Estado**: Pendiente (Backlog)  
**Prioridad**: BAJA

---

## 🎯 OBJETIVO

Mejorar la visualización del perfil de usuario permitiendo la carga de imágenes personalizadas y proporcionar una herramienta a los administradores para gestionar la seguridad de las cuentas de los alumnos mediante contraseñas temporales.

---

## 📋 REQUERIMIENTO 1: Imagen de Perfil para Alumnos

Actualmente, el perfil muestra un círculo con las iniciales del nombre. Se propone permitir la carga de un archivo de imagen.

### **Tareas de Implementación:**

#### **1.1 Modelo `UserProfile`**
- [ ] Añadir campo `avatar` de tipo `ImageField` en `UserProfile` (en `paasify/models/StudentModel.py`).
- [ ] Configurar `upload_to='avatars/'`.
- [ ] Implementar borrado automático del archivo antiguo al actualizar/eliminar.

#### **1.2 Interfaz de Usuario (UI)**
- [ ] **Template `profile.html`**:
    - Añadir un modal o sección de formulario para subir la imagen.
    - Reemplazar la lógica de `.avatar-circle` para que muestre la imagen si existe, o el círculo de iniciales como fallback.
- [ ] **Preview**: Mostrar una previsualización de la imagen seleccionada antes de subirla.

#### **1.3 Lógica de Backend**
- [ ] Crear vista `upload_avatar` en `paasify/views.py` (o similar).
- [ ] Validar:
    - Tamaño máximo (ej: 2MB).
    - Formatos permitidos (JPG, PNG, WEBP).
    - Redimensionado automático (ej: 300x300px) para ahorrar espacio.

---

## 📋 REQUERIMIENTO 2: Contraseña Temporal y Cambio Obligatorio

Permitir que un administrador resetee la contraseña de un alumno a una temporal que expire tras el primer uso.

### **Tareas de Implementación:**

#### **2.1 Modelo y Estado**
- [ ] Añadir campo `must_change_password` (booleano) al modelo `UserProfile`.
- [ ] El administrador, al cambiar la contraseña desde el panel, marcará este campo como `True`.

#### **2.2 Gestión de Seguridad (Middleware/Decoradores)**
- [ ] Implementar un middleware que verifique en cada request si el usuario logueado tiene `must_change_password=True`.
- [ ] Si es así, redirigir forzosamente a la página `/profile/change-password/` hasta que complete el cambio.
- [ ] Excluir las rutas de logout y estáticos para evitar bloqueos.

#### **2.3 Validación de Complejidad**
Al establecer la nueva contraseña, se exigirán los siguientes requisitos (usando validadores de Django):
- [ ] Al menos una **Mayúscula**.
- [ ] Al menos una **Minúscula**.
- [ ] Al menos un **Número**.
- [ ] Al menos un **Símbolo** (carácter especial).

#### **2.4 Interfaz de Administrador**
- [ ] Añadir acción en el Django Admin para "Resetear contraseña a temporal" que genere una cadena aleatoria y marque el flag de cambio obligatorio.

---

## 📊 BENEFICIOS
- **Personalización**: Mejora el sentido de pertenencia del alumno a la plataforma.
- **Seguridad**: Permite recuperar cuentas de forma segura sin que el administrador conozca o mantenga la contraseña definitiva del alumno.

---

## 🔄 PRÓXIMOS PASOS
1. Evaluar tiempos de desarrollo.
2. Implementar los cambios en el modelo `UserProfile`.
3. Desarrollar la lógica de cambio obligatorio de password.
