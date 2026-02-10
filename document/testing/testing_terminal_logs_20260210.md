# Testing Completo: Terminal y Logs Mejorados v6.1.0

**Fecha:** 10/02/2026  
**Versión:** v6.1.0  
**Tester:** David RG  
**Estado:** PENDIENTE

---

## 📋 INSTRUCCIONES

Marca con `[x]` cada test que pase correctamente.  
Si un test falla, añade comentarios en la sección de bugs.

---

## 1. TERMINAL WEB

### Test 1.1: Conexión Básica

- [ ] Navegar a servicio con estado "running"
- [ ] Click en botón 🖥️ Terminal
- [ ] Se abre `/containers/terminal-v2/<id>/`
- [ ] Aparece mensaje: "✓ Conectado a [nombre_servicio]"
- [ ] Aparece mensaje: "Shell: /bin/bash" (o sh/ash)
- [ ] Ejecutar comando `ls` y ver output
- [ ] Output se muestra correctamente

**Comentarios:**

---

### Test 1.2: Detección de Shells

- [ ] Probar con contenedor Ubuntu/Debian → detecta `/bin/bash`
- [ ] Probar con contenedor Alpine → detecta `/bin/sh` o `/bin/ash`
- [ ] Mensaje de shell correcto en cada caso

**Comentarios:**

---

### Test 1.3: Timeout y Reconexión

- [ ] Conectar a terminal
- [ ] Esperar 5 minutos sin actividad
- [ ] Aparece mensaje: "[TIMEOUT] Sesión cerrada por inactividad"
- [ ] Cerrar y reconectar
- [ ] Reconexión automática funciona (máx 5 intentos)

**Comentarios:**

---

### Test 1.4: Servicios Compose

- [ ] Crear servicio Compose con 2+ contenedores
- [ ] Abrir terminal del servicio
- [ ] Se conecta al contenedor correcto
- [ ] Nombre de contenedor correcto en header

**Comentarios:**

---

### Test 1.5: Permisos

- [ ] Usuario owner puede acceder
- [ ] Usuario admin puede acceder
- [ ] Usuario teacher puede acceder
- [ ] Usuario sin permisos recibe error

**Comentarios:**

---

### Test 1.6: Indicador de Estado

- [ ] Indicador muestra "Conectando..." al inicio
- [ ] Cambia a "Conectado" cuando conecta
- [ ] Cambia a "Desconectado" si se pierde conexión
- [ ] Animación pulse funciona

**Comentarios:**

---

### Test 1.7: Botón Reconectar

- [ ] Botón "Reconectar" deshabilitado cuando conectado
- [ ] Botón habilitado cuando desconectado
- [ ] Click en "Reconectar" vuelve a conectar

**Comentarios:**

---

## 2. PÁGINA DE LOGS

### Test 2.1: Visualización Básica

- [ ] Click en botón 📋 Logs
- [ ] Se abre `/containers/logs/<id>/`
- [ ] Logs se muestran con colorización
- [ ] Contador de líneas correcto
- [ ] Indicador de caché visible

**Comentarios:**

---

### Test 2.2: Filtro por Nivel

- [ ] Seleccionar "🔴 ERROR" → solo líneas con "error"
- [ ] Seleccionar "🟡 WARN" → solo líneas con "warn"
- [ ] Seleccionar "🟢 INFO" → solo líneas con "info"
- [ ] Seleccionar "🔵 DEBUG" → solo líneas con "debug"
- [ ] Seleccionar "Todos los niveles" → todas las líneas
- [ ] Contador actualizado correctamente

**Comentarios:**

---

### Test 2.3: Búsqueda de Texto

- [ ] Escribir "error" en búsqueda
- [ ] Esperar 500ms (debounce)
- [ ] Se filtran logs correctamente
- [ ] Búsqueda es case-insensitive
- [ ] Borrar búsqueda restaura todos los logs
- [ ] Contador actualizado

**Comentarios:**

---

### Test 2.4: Selector de Cantidad

- [ ] Seleccionar "100 líneas" → máximo 100
- [ ] Seleccionar "500 líneas" → máximo 500
- [ ] Seleccionar "1000 líneas" → máximo 1000
- [ ] Seleccionar "Todas" → sin límite
- [ ] Contador correcto en cada caso

**Comentarios:**

---

### Test 2.5: Botón Copiar

- [ ] Click en "📋 Copiar"
- [ ] Botón cambia a "✅ Copiado!"
- [ ] Logs copiados al portapapeles
- [ ] Pegar en editor → contenido correcto (sin HTML)
- [ ] Feedback desaparece después de 2s

**Comentarios:**

---

### Test 2.6: Botón Descargar

- [ ] Click en "💾 Descargar"
- [ ] Se descarga archivo `logs-[servicio]-[fecha].log`
- [ ] Abrir archivo → contenido correcto
- [ ] Formato texto plano
- [ ] Feedback visual en botón

**Comentarios:**

---

### Test 2.7: Botón Refrescar

- [ ] Generar nuevos logs en contenedor
- [ ] Click en "🔄 Refrescar"
- [ ] Logs se actualizan
- [ ] Indicador caché cambia a "🔄 Actualizado"
- [ ] Filtros se mantienen

**Comentarios:**

---

### Test 2.8: Botón Ir al Inicio

- [ ] Scroll hacia abajo
- [ ] Click en "⬆️ Inicio"
- [ ] Scroll suave al inicio
- [ ] Funciona correctamente

**Comentarios:**

---

### Test 2.9: Colorización Rich

- [ ] Logs con JSON muestran syntax highlighting
- [ ] ERROR en rojo con 🔴
- [ ] WARN en amarillo con 🟡
- [ ] INFO en verde con 🟢
- [ ] DEBUG en azul con 🔵
- [ ] Headers de contenedores (Compose) resaltados

**Comentarios:**

---

### Test 2.10: Caché

- [ ] Abrir logs (primera vez) → "🔄 Actualizado"
- [ ] Cerrar y volver a abrir (< 5 min) → "⚡ Desde caché"
- [ ] Esperar 5 minutos y refrescar → "🔄 Actualizado"

**Comentarios:**

---

### Test 2.11: Servicios Compose

- [ ] Servicio Compose con 2+ contenedores
- [ ] Logs muestran headers: "CONTENEDOR: [nombre]"
- [ ] Logs de todos los contenedores visibles
- [ ] Separación clara entre contenedores

**Comentarios:**

---

## 3. STREAMING EN VIVO

### Test 3.1: Iniciar Streaming

- [ ] Click en "📡 Seguir en vivo"
- [ ] Botón cambia a "⏸️ Pausar streaming"
- [ ] Botón con animación pulse (rosa)
- [ ] Mensaje: "🔴 STREAMING EN VIVO - Conectado"
- [ ] Generar logs → aparecen en tiempo real
- [ ] Auto-scroll al final funciona

**Comentarios:**

---

### Test 3.2: Pausar Streaming

- [ ] Streaming activo
- [ ] Click en "⏸️ Pausar streaming"
- [ ] Streaming se detiene
- [ ] Botón vuelve a "📡 Seguir en vivo"
- [ ] Animación pulse desaparece
- [ ] Generar logs → NO aparecen

**Comentarios:**

---

### Test 3.3: Colorización en Vivo

- [ ] Streaming activo
- [ ] Generar log con "error" → aparece en rojo
- [ ] Generar log con "warn" → aparece en amarillo
- [ ] Generar log con "info" → aparece en verde
- [ ] Logs normales en gris

**Comentarios:**

---

### Test 3.4: Servicios Compose

- [ ] Servicio Compose con 2+ contenedores
- [ ] Iniciar streaming
- [ ] Headers: "📦 CONTENEDOR: [nombre]"
- [ ] Logs de todos los contenedores en vivo
- [ ] Separación clara

**Comentarios:**

---

### Test 3.5: Reconexión

- [ ] Streaming activo
- [ ] Detener contenedor
- [ ] Mensaje: "[DESCONECTADO] Streaming finalizado"
- [ ] Botón vuelve a estado normal
- [ ] Reiniciar contenedor y reconectar manualmente

**Comentarios:**

---

## 4. RESPONSIVE DESIGN

### Test 4.1: Móvil (< 768px)

- [ ] Abrir en móvil o DevTools responsive
- [ ] Terminal responsive
- [ ] Logs responsive
- [ ] Toolbar en columna
- [ ] Botones accesibles
- [ ] Sin overflow horizontal

**Comentarios:**

---

### Test 4.2: Tablet (768px - 1024px)

- [ ] Abrir en tablet
- [ ] Layout correcto
- [ ] Todas las funcionalidades accesibles

**Comentarios:**

---

## 5. SEGURIDAD Y PERMISOS

### Test 5.1: Autenticación

- [ ] Logout
- [ ] Intentar acceder a `/containers/terminal-v2/1/` → redirect a login
- [ ] Intentar acceder a `/containers/logs/1/` → redirect a login

**Comentarios:**

---

### Test 5.2: Autorización

- [ ] Usuario A crea servicio
- [ ] Usuario B (sin permisos) intenta acceder
- [ ] Recibe error 403 o 404
- [ ] Mensaje claro de error

**Comentarios:**

---

## 6. PERFORMANCE

### Test 6.1: Logs Grandes

- [ ] Servicio con >1000 líneas de logs
- [ ] Abrir página de logs
- [ ] Carga < 3 segundos
- [ ] Scroll fluido
- [ ] Filtros responden rápido

**Comentarios:**

---

### Test 6.2: Múltiples Usuarios

- [ ] 2+ usuarios abren terminal simultáneamente
- [ ] Todos funcionan sin interferencias
- [ ] Performance aceptable

**Comentarios:**

---

## 7. COMPATIBILIDAD

### Test 7.1: Navegadores

- [ ] Chrome/Edge: Todo funciona
- [ ] Firefox: Todo funciona
- [ ] Safari: Todo funciona (si aplica)

**Comentarios:**

---

## 8. CÓDIGO ANTIGUO (DEPRECATED)

### Test 8.1: Verificación

- [ ] `TerminalConsumer` marcado como DEPRECATED
- [ ] Comentario indica usar `DockerTerminalConsumer`
- [ ] Ruta `/ws/terminal/` aún funciona (compatibilidad)
- [ ] Nueva ruta `/ws/terminal-v2/` funciona

**Comentarios:**

---

## 📊 RESUMEN DE RESULTADOS

**Total de tests:** 40  
**Completados:** [ ] / 40  
**Fallidos:** [ ] / 40

### **Por categoría:**

- Terminal Web: [ ] / 7
- Página de Logs: [ ] / 11
- Streaming en Vivo: [ ] / 5
- Responsive: [ ] / 2
- Seguridad: [ ] / 2
- Performance: [ ] / 2
- Compatibilidad: [ ] / 1
- Código Antiguo: [ ] / 1

---

## 🐛 BUGS ENCONTRADOS

### Bug #1:

**Descripción:**  
**Pasos para reproducir:**  
**Resultado esperado:**  
**Resultado actual:**  
**Prioridad:** Alta / Media / Baja

---

### Bug #2:

**Descripción:**  
**Pasos para reproducir:**  
**Resultado esperado:**  
**Resultado actual:**  
**Prioridad:** Alta / Media / Baja

---

## ✅ APROBACIÓN FINAL

- [ ] Todos los tests críticos pasados
- [ ] Bugs documentados (si los hay)
- [ ] Funcionalidades core verificadas
- [ ] Performance aceptable
- [ ] Listo para commit

**Firma:** **\*\***\_\_\_**\*\***  
**Fecha:** **\*\***\_\_\_**\*\***

---

**Última actualización:** 2026-02-10 22:35
