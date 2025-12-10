# Bug: Archivos huérfanos en media/ al eliminar servicios
**Fecha**: 2025-12-09 22:52  
**Actualizado**: 2025-12-09 22:56  
**Prioridad**: MEDIA  
**Estado**: PENDIENTE

---

## 🐛 DESCRIPCIÓN DEL BUG

**Problema**: Al eliminar un servicio, los archivos en `media/` NO se limpian completamente.

**Directorios afectados**:
- `media/dockerfiles/` - Dockerfiles subidos
- `media/compose_files/` - docker-compose.yml subidos
- `media/user_code/` - Archivos .zip/.rar de código
- `media/services/<id>/` - Workspace del servicio

**Comportamiento observado**:
- Usuario elimina servicio desde UI
- Contenedor se elimina de Docker Desktop ✅
- Imagen se elimina (si fue construida) ✅
- Volumen se elimina ✅
- **Archivos en media/ NO se eliminan** ❌

**Comportamiento esperado**:
- Todo debería eliminarse, incluyendo todos los archivos en `media/`

---

## 🔍 ANÁLISIS DETALLADO

### **Problema 1: FileFields huérfanos**

El modelo `Service` tiene FileFields que suben archivos a diferentes directorios:

```python
# containers/models.py
class Service(models.Model):
    dockerfile = models.FileField("Dockerfile", upload_to="dockerfiles/", ...)
    compose = models.FileField("docker-compose.yml", upload_to="compose_files/", ...)
    code = models.FileField("Codigo fuente (zip)", upload_to="user_code/", ...)
```

Cuando eliminas el servicio, **estos archivos NO se borran automáticamente**.

### **Problema 2: Workspace no se limpia**

```python
def cleanup_service_workspace(service: Service) -> None:
    workspace = SERVICE_WORKSPACES_ROOT / str(service.pk)
    if workspace.exists():
        shutil.rmtree(workspace, ignore_errors=True)  # ⚠️ Falla silenciosamente
```

`ignore_errors=True` hace que falle sin avisar si hay:
- Archivos bloqueados por Docker
- Permisos insuficientes (Windows)
- Archivos de solo lectura

---

## 💡 SOLUCIÓN COMPLETA

### **PARTE 1: Fix Preventivo (evitar nueva basura)**

#### **1.1 Eliminar FileFields al borrar servicio**

```python
def remove_container(service: Service):
    """
    Elimina el servicio completamente.
    """
    docker_client = get_docker_client()
    if docker_client is None:
        raise RuntimeError("Docker no está disponible para eliminar el servicio.")

    # ... código actual de eliminación de contenedor/imagen/volumen ...
    
    # ========== NUEVO: Eliminar FileFields ==========
    try:
        if service.dockerfile:
            service.dockerfile.delete(save=False)
        if service.compose:
            service.compose.delete(save=False)
        if service.code:
            service.code.delete(save=False)
    except Exception as e:
        _append_log(service, f"⚠️ Error al eliminar archivos: {e}")
        service.save(update_fields=["logs"])
    
    # Limpiar workspace (mejorado)
    cleanup_service_workspace(service)
    
    service.container_id = None
    service.assigned_port = None
    service.volume_name = None
    service.status = "removed"
    service.save()
```

#### **1.2 Mejorar cleanup_service_workspace con retry**

```python
def cleanup_service_workspace(service: Service) -> None:
    """Elimina completamente el workspace del servicio con retry"""
    import time
    import stat
    
    workspace = SERVICE_WORKSPACES_ROOT / str(service.pk)
    if not workspace.exists():
        return
    
    # Intentar eliminar hasta 3 veces
    for attempt in range(3):
        try:
            # En Windows, cambiar permisos antes de eliminar
            if os.name == 'nt':
                for root, dirs, files in os.walk(workspace):
                    for d in dirs:
                        try:
                            os.chmod(os.path.join(root, d), stat.S_IRWXU)
                        except:
                            pass
                    for f in files:
                        try:
                            os.chmod(os.path.join(root, f), stat.S_IRWXU)
                        except:
                            pass
            
            shutil.rmtree(workspace)
            _append_log(service, f"✅ Workspace eliminado: {workspace}")
            return
            
        except PermissionError as e:
            if attempt < 2:
                time.sleep(2)  # Esperar 2 segundos y reintentar
                continue
            _append_log(service, f"⚠️ No se pudo eliminar workspace: {e}")
            service.save(update_fields=["logs"])
            
        except Exception as e:
            _append_log(service, f"⚠️ Error al eliminar workspace: {e}")
            service.save(update_fields=["logs"])
            break
```

---

### **PARTE 2: Comando de Limpieza (purgar basura existente)**

#### **2.1 Comando para limpiar archivos huérfanos**

```python
# containers/management/commands/cleanup_media.py
from django.core.management.base import BaseCommand
from django.conf import settings
from containers.models import Service
from pathlib import Path
import shutil

class Command(BaseCommand):
    help = 'Limpia archivos huérfanos en media/ de servicios eliminados'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostrar qué se eliminaría sin hacerlo',
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        media_root = Path(settings.MEDIA_ROOT)
        
        # Obtener IDs de servicios activos
        active_ids = set(Service.objects.values_list('id', flat=True))
        
        total_deleted = 0
        total_size = 0
        
        # 1. Limpiar media/services/
        self.stdout.write("\n🔍 Limpiando media/services/...")
        services_dir = media_root / "services"
        if services_dir.exists():
            for item in services_dir.iterdir():
                if item.is_dir():
                    try:
                        service_id = int(item.name)
                        if service_id not in active_ids:
                            size = self._get_dir_size(item)
                            total_size += size
                            
                            if dry_run:
                                self.stdout.write(f"  [DRY-RUN] Eliminaría: {item} ({size / 1024 / 1024:.2f} MB)")
                            else:
                                shutil.rmtree(item, ignore_errors=True)
                                self.stdout.write(self.style.SUCCESS(f"  ✅ Eliminado: {item}"))
                            total_deleted += 1
                    except ValueError:
                        continue
        
        # 2. Limpiar FileFields huérfanos
        self.stdout.write("\n🔍 Limpiando FileFields huérfanos...")
        
        # Obtener todos los archivos referenciados por servicios activos
        active_files = set()
        for service in Service.objects.all():
            if service.dockerfile:
                active_files.add(service.dockerfile.name)
            if service.compose:
                active_files.add(service.compose.name)
            if service.code:
                active_files.add(service.code.name)
        
        # Limpiar dockerfiles/
        self._cleanup_directory(
            media_root / "dockerfiles",
            active_files,
            dry_run,
            "dockerfiles"
        )
        
        # Limpiar compose_files/
        self._cleanup_directory(
            media_root / "compose_files",
            active_files,
            dry_run,
            "compose_files"
        )
        
        # Limpiar user_code/
        self._cleanup_directory(
            media_root / "user_code",
            active_files,
            dry_run,
            "user_code"
        )
        
        # Resumen
        self.stdout.write("\n" + "="*50)
        if dry_run:
            self.stdout.write(self.style.WARNING(f"[DRY-RUN] Se eliminarían {total_deleted} elementos"))
        else:
            self.stdout.write(self.style.SUCCESS(f"✅ Eliminados {total_deleted} elementos"))
        self.stdout.write(f"💾 Espacio liberado: {total_size / 1024 / 1024:.2f} MB")
    
    def _cleanup_directory(self, directory, active_files, dry_run, dir_name):
        """Limpia archivos huérfanos en un directorio"""
        if not directory.exists():
            return
        
        deleted = 0
        for item in directory.iterdir():
            if item.is_file():
                # Construir path relativo desde MEDIA_ROOT
                relative_path = f"{dir_name}/{item.name}"
                
                if relative_path not in active_files:
                    size = item.stat().st_size
                    
                    if dry_run:
                        self.stdout.write(f"  [DRY-RUN] Eliminaría: {item.name} ({size / 1024:.2f} KB)")
                    else:
                        item.unlink()
                        self.stdout.write(self.style.SUCCESS(f"  ✅ Eliminado: {item.name}"))
                    deleted += 1
        
        if deleted > 0:
            self.stdout.write(f"  📁 {dir_name}: {deleted} archivos limpiados")
    
    def _get_dir_size(self, path):
        """Calcula el tamaño total de un directorio"""
        total = 0
        for item in path.rglob('*'):
            if item.is_file():
                total += item.stat().st_size
        return total
```

#### **2.2 Uso del comando**

```bash
# Ver qué se eliminaría (sin eliminar)
python manage.py cleanup_media --dry-run

# Eliminar archivos huérfanos
python manage.py cleanup_media
```

---

## 📋 IMPLEMENTACIÓN

### **Tareas:**

#### **Fix Preventivo:**
- [ ] Modificar `remove_container` para eliminar FileFields
- [ ] Mejorar `cleanup_service_workspace` con retry
- [ ] Testing de eliminación

#### **Comando de Limpieza:**
- [ ] Crear `containers/management/commands/cleanup_media.py`
- [ ] Testing con --dry-run
- [ ] Ejecutar en producción
- [ ] Documentar comando

#### **Automatización (opcional):**
- [ ] Añadir tarea cron/celery para limpieza periódica
- [ ] Añadir botón en admin para ejecutar limpieza

---

## 🎯 IMPACTO

**Severidad**: MEDIA  
**Funcionalidad afectada**: Limpieza de archivos al eliminar servicios  
**Espacio en disco**: Puede acumularse significativamente

**Beneficios del fix**:
- ✅ No más archivos huérfanos
- ✅ Ahorro de espacio en disco
- ✅ Mejor organización de media/
- ✅ Comando para limpiar basura existente

---

## 🧪 TESTING

### **Test 1: Fix preventivo**
1. Crear servicio con Dockerfile + código
2. Verificar archivos en `media/dockerfiles/` y `media/user_code/`
3. Eliminar servicio
4. **Verificar**: Archivos eliminados de todos los directorios

### **Test 2: Comando de limpieza**
1. Ejecutar `python manage.py cleanup_media --dry-run`
2. Verificar lista de archivos a eliminar
3. Ejecutar `python manage.py cleanup_media`
4. **Verificar**: Archivos eliminados correctamente

---

**Última actualización**: 2025-12-09 22:56  
**Estado**: Documentado, listo para implementación
