# 🏗️ 8. Integración CI/CD

La integración continua y el despliegue continuo (CI/CD) permiten que tu aplicación en PaaSify se actualice automáticamente cada vez que realizas un cambio en tu repositorio de código.

---

### Conceptos Clave

- **Automatización**: No necesitas entrar a la web de PaaSify para actualizar tu app.
- **Trazabilidad**: Cada "Push" a tu repo genera un despliegue asociado a un commit.
- **Seguridad**: Los despliegues se realizan mediante Tokens de API seguros.

### Plataformas Soportadas

Actualmente, esta guía incluye ejemplos detallados para las dos plataformas más usadas en el ámbito académico y profesional, más la Action oficial de PaaSify:

<div class="alert alert-primary shadow-sm border-primary mb-3" role="alert" style="border-left-width: 4px;">
    <strong><i class="fas fa-star text-warning me-2"></i> 8.0 Action Oficial de PaaSify (Recomendado):</strong><br> 
    La forma más sencilla y potente de desplegar. Una sola línea <code>uses:</code> en tu workflow de GitHub hace todo el trabajo de compilar, empaquetar y llamar a la API de PaaSify. Soporta código directo, Dockerfiles y Docker Compose.
</div>

<div class="alert alert-dark shadow-sm border-dark mb-3" role="alert" style="border-left-width: 4px; background-color: #f8f9fa;">
    <strong><i class="fab fa-github text-dark me-2"></i> 8.1 GitHub Actions:</strong><br>
    Guía manual y detallada usando llamadas nativas a la API de PaaSify con comandos como <code>curl</code> y <code>jq</code>. Ideal para entender cómo funciona la API por debajo.
</div>

<div class="alert alert-warning shadow-sm border-warning mb-4" role="alert" style="border-left-width: 4px; background-color: #fff8e1;">
    <strong><i class="fab fa-gitlab text-warning me-2" style="color: #fc6d26 !important;"></i> 8.2 GitLab CI:</strong><br>
    Opción preferida por muchas facultades y empresas por su potencia nativa. Guía de integración para pipelines <code>.gitlab-ci.yml</code>.
</div>

Pulsando en los menús de la izquierda podrás ver el flujo completo, ejemplos de YAML y configuración de secretos para cada una de estas opciones.
