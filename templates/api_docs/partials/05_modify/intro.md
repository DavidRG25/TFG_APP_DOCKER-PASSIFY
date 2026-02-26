# 🛠️ 5. Modificar Servicio

PaaSify permite la evolución de tus servicios sin necesidad de borrarlos y recrearlos manualmente. El método `PATCH` es tu aliado para el mantenimiento continuo de tus aplicaciones.

---

### 🔄 Ciclo de Vida de la Modificación

Cuando realizas un `PATCH`, PaaSify ejecuta internamente:

1.  **Validación**: Comprueba cambios en la imagen o variables.
2.  **Preparación**: Realiza un `Stop` seguro del contenedor actual.
3.  **Actualización**: Aplica los nuevos parámetros y descarga la nueva imagen si es necesario.
4.  **Re-arranque**: Levanta el contenedor en la misma red y con el mismo puerto.

---

### 📊 Matriz de Mutabilidad

| Campo         | Editable | Efecto                                            |
| :------------ | :------: | :------------------------------------------------ |
| **Nombre**    |  ✅ Sí   | Cambia la URL de acceso web y alias de red.       |
| **Imagen**    |  ✅ Sí   | Descarga la nueva versión y recrea el contenedor. |
| **Variables** |  ✅ Sí   | Reinicia el proceso interno con el nuevo entorno. |
| **Tipo**      |  ✅ Sí   | Actualiza la categoría visual en el dashboard.    |
| **Proyecto**  |  ❌ No   | El servicio es inamovible de su contexto inicial. |

Pulsando en **5.1 Configuración** podrás ver la guía completa de parámetros editables y el flujo de re-despliegue.
