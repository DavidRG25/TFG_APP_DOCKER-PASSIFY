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
<p style="color: #64748b; max-width: 500px; margin: 0 auto 30px; line-height: 1.6;">Genera un entorno de pruebas completo con todas las rutas, parámetros y ejemplos de respuesta configurados para tu aprendizaje.</p>
<a href="/paasify/containers/api-docs/export/" style="background: #ff6c37; color: white; padding: 18px 45px; border-radius: 14px; font-weight: 800; text-decoration: none; display: inline-block; box-shadow: 0 8px 20px rgba(255,108,55,0.35); font-size: 1.2rem; transition: all 0.3s ease;">
<i class="fas fa-download"></i> &nbsp; Descargar para Postman
</a>
</div>

---

### 🚀 Cómo empezar en Postman

1.  **Importar**: Abre Postman, haz clic en el botón **Import** y arrastra el archivo JSON descargado.
2.  **Variables**: Una vez importado, ve a la pestaña **Variables** de la colección.
3.  **Token**: Localiza la variable `paasifyToken` (o el campo Authorization) y pega tu token personal generado en la sección **Mi Perfil**.
4.  **Base URL**: Asegúrate de que la variable `baseUrl` apunte a `http://localhost:8000` (o la URL de tu instancia).

### 🛡️ Seguridad y Privacidad
Recuerda que estas herramientas guardan el historial de tus peticiones. **Nunca compartas tu token** ni captures capturas de pantalla donde se vea tu clave privada de acceso.

<div style="background: #fff7ed; border: 1px solid #ffedd5; border-left: 5px solid #ff6c37; padding: 20px; border-radius: 12px; margin-top: 25px; box-shadow: 0 4px 12px rgba(255,108,55,0.05);">
    <h4 style="color: #9a3412; margin: 0 0 10px 0; display: flex; align-items: center; border: none; font-size: 1.05rem; font-weight: 800;">
        <span style="margin-right: 10px;">💡</span> Recomendación de Seguridad
    </h4>
    <p style="color: #7c2d12; margin: 0; line-height: 1.6; font-size: 0.95rem;">
        Si por error compartes tu token o sospechas que alguien ha tenido acceso a él, te recomendamos <strong>generar uno nuevo inmediatamente</strong> desde la sección <strong>Mi Perfil</strong>. Recuerda que tras hacerlo deberás actualizar la variable <code>paasifyToken</code> en Postman para que tus peticiones sigan funcionando correctamente.
    </p>
</div>
