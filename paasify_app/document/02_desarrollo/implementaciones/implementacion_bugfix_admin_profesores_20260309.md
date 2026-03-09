# Bugfix: Admin de Profesores - Perfiles vacíos en VM

**Fecha:** 09/03/2026  
**Estado:** ✅ Completado  
**Referencia Plan:** `plan_reunion_03032026.md` → Bugs / Fixes detectados → Admin de profesores

---

## 📋 Problema detectado

En el panel de administración (`/admin/paasify/teacherprofile/`), la sección **"Perfiles de profesores"** mostraba **0 resultados** en la VM de producción (`paas.tfg.etsii.urjc.es`), aunque existía un usuario con rol `Profesor` visible en la lista general de Usuarios.

En localhost, en cambio, funcionaba correctamente y mostraba 2 perfiles de profesores.

## 🔍 Causa raíz

El modelo `TeacherProfile` es un **proxy model** de `UserProfile`. El admin de profesores (`TeacherProfileAdmin`) filtra en su `get_queryset()` los registros de la tabla `UserProfile` cuyo usuario asociado pertenezca al grupo "Teacher" (o variantes como "Profesor", "profesor", etc.).

El problema residía en el **management command `create_demo_users.py`**:

```python
# Para alumnos: ✅ Se creaba el grupo Y el UserProfile
if role == "student":
    roles.ensure_user_group(user, ...)
    roles.ensure_user_profile(user)  # ← Sí existía

# Para profesores: ❌ Solo se creaba el grupo, NO el UserProfile
elif role == "teacher":
    roles.ensure_user_group(user, ...)
    # ← Faltaba roles.ensure_user_profile(user)
```

**Resultado:** Al ejecutar `create_demo_users` en la VM, el usuario `profesor` se creaba con el grupo correcto, pero **sin registro en la tabla `UserProfile`**. Como `TeacherProfileAdmin.get_queryset()` filtra por `UserProfile` con usuario de grupo Teacher, la query devolvía **0 resultados**.

En localhost funcionaba porque los profesores fueron creados manualmente desde el formulario del admin (`TeacherProfileAdminForm.save()`), que sí crea el `UserProfile` internamente.

## ✅ Solución aplicada

### Archivo modificado: `paasify/management/commands/create_demo_users.py`

```diff
 elif role == "teacher":
     roles.ensure_user_group(
         user,
         roles.TEACHER_GROUP_NAMES,
         roles.DEFAULT_TEACHER_GROUP,
     )
+    roles.ensure_user_profile(user)
```

Se añadió la llamada `roles.ensure_user_profile(user)` para el rol `teacher`, garantizando que todos los usuarios de tipo profesor creados por el command también tengan su fila correspondiente en `UserProfile`.

## 🧪 Verificación

Para aplicar el fix en la VM:

1. Redesplegar el código actualizado
2. Ejecutar de nuevo el management command:
   ```bash
   python manage.py create_demo_users
   ```
3. Verificar en `/admin/paasify/teacherprofile/` que ahora aparece el perfil del profesor

## 📁 Archivos modificados

| Archivo                                            | Cambio                                                    |
| -------------------------------------------------- | --------------------------------------------------------- |
| `paasify/management/commands/create_demo_users.py` | Añadido `roles.ensure_user_profile(user)` para profesores |
| `document/04_planes/plan_reunion_03032026.md`      | Marcado como completado ✅                                |
