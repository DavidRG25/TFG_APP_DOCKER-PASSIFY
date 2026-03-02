# 🛠️ Modo Custom: Dockerfile

Sube tu código fuente (`.zip`) y define cómo construirlo mediante un `Dockerfile`.

#### Parámetros Base para Modo Custom:

- **mode**: `custom` ✅
- **code**: Archivo `.zip` con el código. ✅
- **dockerfile**: Archivo `Dockerfile`. ✅

---

#### 📝 Ejemplo: Básico (Sin variables)

Para despliegues estándar que no requieren configuración externa:

```bash
CURL -X POST {{ PAASIFY_API_URL }}/containers/ \
  -H "Authorization: Bearer <TOKEN>" \
  -F "name=mi-app-node" \
  -F "mode=custom" \
  -F "code=@app.zip" \
  -F "dockerfile=@Dockerfile" \
  -F "project=1" \
  -F "subject=1" \
  -F "container_type=web"
```

#### ✅ Ventajas:

- 🎯 **Control**: Tú defines exactamente qué software corre dentro.
- 🔐 **Privacidad**: Tu código nunca se hace público en DockerHub.
