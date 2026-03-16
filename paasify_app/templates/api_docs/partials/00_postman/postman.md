# 📮 Colección Postman

PaaSify facilita las pruebas de integración proporcionando un esquema oficial que puedes importar directamente en tus herramientas de testing favoritas.

---

### 📥 Descarga la Configuración

Utiliza el siguiente botón para generar y descargar el archivo JSON con la definición completa de la API. Este archivo sigue el estándar **OpenAPI 3.0** y es compatible con **Postman**, **Insomnia** y **Thunder Client**.

<div align="center" style="background: #ffffff; border: 2px solid #e2e8f0; border-radius: 20px; padding: 40px; margin: 30px 0; border-left: 10px solid #ff6c37;">
<div style="background: #fff; padding: 15px; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); display: inline-block; margin-bottom: 20px;">
<img src="https://www.vectorlogo.zone/logos/getpostman/getpostman-icon.svg" width="80" alt="Postman">
</div>
<h2 style="color: #ff6c37; margin-bottom: 15px; border: none; font-weight: 800;">Esquema API de PaaSify</h2>
<p style="color: #64748b; max-width: 500px; margin: 0 auto 30px; line-height: 1.6;">Genera un entorno de pruebas completo con todas las rutas, parámetros y ejemplos de respuesta configurados para tu aprendizaje.<br><br><b>💡 Nota:</b> Tras importar la colección en Postman, deberás pegar tu token personal en <i>Authorization → Bearer Token</i> para poder ejecutar las peticiones reales.</p>
<a href="/paasify/containers/api-docs/export/" style="background: #ff6c37; color: white; padding: 18px 45px; border-radius: 14px; font-weight: 800; text-decoration: none; display: inline-block; box-shadow: 0 8px 20px rgba(255,108,55,0.35); font-size: 1.2rem; transition: all 0.3s ease;">
<i class="fas fa-download"></i> &nbsp; Descargar para Postman
</a>
</div>

---

### 🚀 Cómo empezar en Postman

1.  **Importar**: Abre Postman, haz clic en el botón **Import** y arrastra el archivo JSON. Cuando pregunte cómo importar, selecciona siempre **"Postman Collection"** (no OpenAPI).
2.  **Base URL**: Al terminar, haz clic derecho sobre la nueva colección "PaaSify API", dale a **Edit** y ve a la pestaña **Variables**. Verás que `baseUrl` se ha creado automáticamente apuntando a tu servidor (ej. `http://localhost:8000/api`) porque forma parte del estándar OpenAPI.
3.  **Configurar Autenticación (Token)**:
    - Ve a la pestaña **Authorization** (dentro del mismo Edit de la colección).
    - En el menú desplegable *Type*, selecciona **Bearer Token**.
    - Pega tu token personal (sacado de **Mi Perfil**) en el campo de texto de la derecha. 
    - Guarda los cambios (Ctrl+S / Cmd+S).

<div style="background: #f8fafc; border: 1px solid #e2e8f0; border-left: 5px solid #3b82f6; padding: 15px; border-radius: 8px; margin-top: 15px; margin-bottom: 20px;">
    <p style="margin: 0; font-family: monospace; color: #1e293b; font-size: 0.9rem;">
        <strong>🤔 ¿Por qué debo pegarlo a mano?</strong><br>
        Por seguridad, el estándar OpenAPI no exporta contraseñas ni tokens en el archivo descargable. Debes inyectarlo tú manualmente para que Postman pueda validarse.
    </p>
</div>

¡Con esto listo ya puedes navegar por las carpetas y probar botones como **List containers** o **Create container** con un solo clic!

### 🛡️ Seguridad y Privacidad
Recuerda que estas herramientas guardan el historial de tus peticiones. **Nunca compartas tu token** ni captures capturas de pantalla donde se vea tu clave privada de acceso.

<div style="background: #fff7ed; border: 1px solid #ffedd5; border-left: 5px solid #ff6c37; padding: 20px; border-radius: 12px; margin-top: 25px; box-shadow: 0 4px 12px rgba(255,108,55,0.05);">
    <h4 style="color: #9a3412; margin: 0 0 10px 0; display: flex; align-items: center; border: none; font-size: 1.05rem; font-weight: 800;">
        <span style="margin-right: 10px;">💡</span> Recomendación de Seguridad
    </h4>
    <p style="color: #7c2d12; margin: 0; line-height: 1.6; font-size: 0.95rem;">
        Si por error compartes tu token o sospechas que alguien ha tenido acceso a él, te recomendamos <strong>generar uno nuevo inmediatamente</strong> desde la sección <strong>Mi Perfil</strong>. Recuerda que tras hacerlo deberás actualizar el campo Token en la pestaña <strong>Authorization</strong> de Postman para que tus peticiones sigan funcionando correctamente.
    </p>
</div>
