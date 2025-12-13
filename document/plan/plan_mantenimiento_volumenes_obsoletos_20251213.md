# Plan de Mantenimiento - Limpieza de Volúmenes Obsoletos

**Fecha de Creación:** 2025-12-13  
**Prioridad:** BAJA - Mantenimiento Post-Implementación  
**Dependencia:** Debe ejecutarse DESPUÉS de completar Plan de Seguridad Crítica

---

## Objetivo

Auditar y eliminar volúmenes Docker obsoletos creados antes de la implementación de la nueva política de volúmenes (solo volúmenes nombrados en Compose, sin volúmenes en contenedores simples).

---

## Contexto

Después de implementar la nueva política de seguridad que elimina la capacidad de crear volúmenes por defecto en contenedores simples, es necesario limpiar los volúmenes existentes que fueron creados bajo el sistema anterior.

**IMPORTANTE:** Esta tarea solo debe ejecutarse DESPUÉS de:
1. Completar la implementación de la nueva política de volúmenes (Plan de Seguridad, punto 1.1)
2. Migrar todos los servicios activos al nuevo sistema
3. Verificar que no hay servicios en producción usando volúmenes antiguos

---

## Tareas de Auditoría

### 1. Inventario de Volúmenes Actuales

**Objetivo:** Identificar todos los volúmenes Docker existentes en el sistema

**Comandos:**
```bash
# Listar todos los volúmenes
docker volume ls

# Inspeccionar volúmenes con detalles
docker volume inspect $(docker volume ls -q)

# Identificar volúmenes huérfanos (sin contenedor asociado)
docker volume ls -f dangling=true
```

**Tareas:**
- [ ] Ejecutar inventario completo de volúmenes
- [ ] Documentar volúmenes encontrados (nombre, tamaño, fecha de creación)
- [ ] Identificar volúmenes asociados a servicios activos
- [ ] Identificar volúmenes huérfanos
- [ ] Clasificar volúmenes por usuario/asignatura

---

### 2. Análisis de Volúmenes

**Objetivo:** Determinar qué volúmenes son seguros de eliminar

**Criterios de Clasificación:**

**Volúmenes a CONSERVAR:**
- Volúmenes nombrados creados por Docker Compose (formato: `proyecto_volume_name`)
- Volúmenes con datos de servicios activos
- Volúmenes de bases de datos o datos persistentes importantes

**Volúmenes a ELIMINAR:**
- Volúmenes huérfanos (sin contenedor asociado)
- Volúmenes de servicios eliminados
- Volúmenes creados manualmente por usuarios (bind mounts antiguos)
- Volúmenes de pruebas o desarrollo

**Tareas:**
- [ ] Crear lista de volúmenes a conservar
- [ ] Crear lista de volúmenes a eliminar
- [ ] Verificar con usuarios/profesores sobre volúmenes dudosos
- [ ] Documentar decisiones de eliminación

---

### 3. Backup de Datos Importantes

**Objetivo:** Respaldar datos antes de eliminar volúmenes

**CRÍTICO:** Hacer backup de TODOS los volúmenes antes de eliminar, incluso los que parecen vacíos

**Procedimiento:**
```bash
# Crear directorio de backup
mkdir -p /backups/volumes_$(date +%Y%m%d)

# Backup de volumen específico
docker run --rm -v VOLUME_NAME:/data -v /backups/volumes_$(date +%Y%m%d):/backup alpine tar czf /backup/VOLUME_NAME.tar.gz /data
```

**Tareas:**
- [ ] Crear directorio de backups con fecha
- [ ] Hacer backup de TODOS los volúmenes a eliminar
- [ ] Verificar integridad de backups (checksum)
- [ ] Documentar ubicación de backups
- [ ] Establecer política de retención de backups (ej: 90 días)

---

### 4. Eliminación Gradual

**Objetivo:** Eliminar volúmenes obsoletos de forma controlada

**Estrategia:**
1. Empezar con volúmenes huérfanos (sin contenedor)
2. Continuar con volúmenes de servicios eliminados
3. Finalizar con volúmenes de pruebas

**Procedimiento:**
```bash
# Eliminar volumen específico
docker volume rm VOLUME_NAME

# Eliminar volúmenes huérfanos (CUIDADO)
docker volume prune -f
```

**Tareas:**
- [ ] Fase 1: Eliminar volúmenes huérfanos (después de backup)
- [ ] Esperar 48 horas y verificar que no hay problemas
- [ ] Fase 2: Eliminar volúmenes de servicios eliminados
- [ ] Esperar 48 horas y verificar
- [ ] Fase 3: Eliminar volúmenes de pruebas
- [ ] Documentar volúmenes eliminados

---

### 5. Monitoreo Post-Eliminación

**Objetivo:** Verificar que la eliminación no causó problemas

**Tareas:**
- [ ] Monitorear logs de Docker por 7 días
- [ ] Verificar que servicios activos funcionan correctamente
- [ ] Revisar quejas de usuarios sobre datos perdidos
- [ ] Restaurar desde backup si es necesario
- [ ] Documentar lecciones aprendidas

---

## Script de Automatización

**Crear script:** `scripts/cleanup_volumes.sh`

**Funcionalidades:**
- Listar volúmenes con clasificación automática
- Generar reporte de volúmenes a eliminar
- Hacer backup automático antes de eliminar
- Eliminar con confirmación manual
- Logging de todas las operaciones

**Tareas:**
- [ ] Desarrollar script de limpieza
- [ ] Probar en entorno de desarrollo
- [ ] Documentar uso del script
- [ ] Ejecutar en producción con supervisión

---

## Cronograma

**Semana 1: Auditoría**
- Día 1-2: Inventario completo
- Día 3-4: Análisis y clasificación
- Día 5: Revisión con equipo

**Semana 2: Backup y Eliminación**
- Día 1-2: Backup de todos los volúmenes
- Día 3: Fase 1 - Eliminar huérfanos
- Día 4-5: Espera y monitoreo

**Semana 3: Eliminación Final**
- Día 1: Fase 2 - Servicios eliminados
- Día 2-3: Espera y monitoreo
- Día 4: Fase 3 - Volúmenes de pruebas
- Día 5: Documentación final

---

## Criterios de Éxito

- [ ] Inventario completo documentado
- [ ] Backups de todos los volúmenes eliminados
- [ ] Volúmenes obsoletos eliminados sin incidentes
- [ ] 0 quejas de usuarios sobre datos perdidos
- [ ] Documentación de proceso completada
- [ ] Script de limpieza funcional y documentado
- [ ] Política de mantenimiento de volúmenes establecida

---

## Riesgos y Mitigaciones

### Riesgo 1: Eliminar volumen con datos importantes
**Mitigación:** Backup obligatorio de TODO antes de eliminar, verificación manual de volúmenes críticos

### Riesgo 2: Servicios dejan de funcionar
**Mitigación:** Eliminación gradual con períodos de espera, rollback plan con backups

### Riesgo 3: Backups corruptos
**Mitigación:** Verificar integridad con checksums, probar restauración antes de eliminar

---

## Notas Importantes

- **NO ejecutar** hasta completar Plan de Seguridad Crítica
- **SIEMPRE hacer backup** antes de eliminar
- **Eliminar gradualmente** con períodos de monitoreo
- **Documentar TODO** (qué se eliminó, cuándo, por qué)
- **Comunicar** a usuarios sobre mantenimiento programado
- **Mantener backups** por al menos 90 días

---

## Política de Mantenimiento Continuo

Después de la limpieza inicial, establecer rutina de mantenimiento:

**Mensual:**
- [ ] Auditar volúmenes nuevos
- [ ] Identificar volúmenes huérfanos
- [ ] Eliminar volúmenes de servicios eliminados (después de 30 días)

**Trimestral:**
- [ ] Revisión completa de volúmenes
- [ ] Limpieza de backups antiguos (> 90 días)
- [ ] Actualizar documentación de política

**Anual:**
- [ ] Auditoría completa de almacenamiento
- [ ] Revisión de política de volúmenes
- [ ] Optimización de uso de disco
