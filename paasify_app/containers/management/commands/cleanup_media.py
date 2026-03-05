from django.core.management.base import BaseCommand
from django.conf import settings
from containers.models import Service
from pathlib import Path
import shutil
import os


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
        
        # 1. Limpiar media/services/ (Workspaces y Archivos Centralizados)
        self.stdout.write("\n🔍 Limpiando media/services/...")
        services_dir = media_root / "services"
        if services_dir.exists():
            for item in services_dir.iterdir():
                if item.is_dir():
                    if item.name == 'tmp':
                        # Limpiar archivos temporales de más de 1 hora
                        import time
                        now = time.time()
                        for tmp_item in item.iterdir():
                            if tmp_item.stat().st_mtime < now - 3600:
                                if dry_run: self.stdout.write(f"  [DRY-RUN] Eliminaría temporal: {tmp_item}")
                                else:
                                    if tmp_item.is_dir(): shutil.rmtree(tmp_item, ignore_errors=True)
                                    else: tmp_item.unlink()
                                total_deleted += 1
                        continue

                    try:
                        service_id = int(item.name)
                        if service_id not in active_ids:
                            size = self._get_dir_size(item)
                            total_size += size
                            
                            if dry_run:
                                self.stdout.write(f"  [DRY-RUN] Eliminaría workspace: {item} ({size / 1024 / 1024:.2f} MB)")
                            else:
                                shutil.rmtree(item, ignore_errors=True)
                                self.stdout.write(self.style.SUCCESS(f"  ✅ Eliminado: {item}"))
                            total_deleted += 1
                    except ValueError:
                        continue
        
        # 2. Limpiar y eliminar directorios ANTIGUOS (Legacy)
        old_dirs = ["dockerfiles", "compose_files", "user_code"]
        active_files = set()
        for service in Service.objects.all():
            if service.dockerfile: active_files.add(service.dockerfile.name)
            if service.compose: active_files.add(service.compose.name)
            if service.code: active_files.add(service.code.name)

        for dir_name in old_dirs:
            directory = media_root / dir_name
            if not directory.exists(): continue
            
            self.stdout.write(f"\n🔍 Limpiando directorio antiguo: {dir_name}...")
            deleted_count = self._cleanup_directory(directory, active_files, dry_run, dir_name)
            total_deleted += deleted_count
            
            # Si el directorio está vacío (o casi), intentar borrarlo
            if not dry_run:
                try:
                    # Borrar subcarpeta services si existe
                    if (directory / "services").exists():
                        shutil.rmtree(directory / "services", ignore_errors=True)
                    # Borrar carpeta raíz si está vacía
                    if not any(directory.iterdir()):
                        directory.rmdir()
                        self.stdout.write(self.style.SUCCESS(f"  🗑️ Directorio raíz eliminado: {dir_name}"))
                except: pass
        
        # Resumen
        self.stdout.write("\n" + "="*50)
        if dry_run:
            self.stdout.write(self.style.WARNING(f"[DRY-RUN] Se eliminarían {total_deleted} elementos"))
        else:
            self.stdout.write(self.style.SUCCESS(f"✅ Eliminados {total_deleted} elementos"))
        self.stdout.write(f"💾 Espacio liberado: {total_size / 1024 / 1024:.2f} MB")
    
    def _cleanup_directory(self, directory, active_files, dry_run, dir_name):
        """Limpia archivos y carpetas de servicios huérfanos en un directorio"""
        if not directory.exists():
            return 0
        
        deleted = 0
        # 1. Limpiar subcarpeta 'services/' si existe (basada en ID)
        services_subdir = directory / "services"
        if services_subdir.exists() and services_subdir.is_dir():
            from containers.models import Service
            db_ids = set(Service.objects.values_list('id', flat=True))
            
            for item in services_subdir.iterdir():
                if item.is_dir():
                    try:
                        sid = int(item.name)
                        if sid not in db_ids:
                            if dry_run:
                                self.stdout.write(f"  [DRY-RUN] Eliminaría carpeta: {item}")
                            else:
                                shutil.rmtree(item, ignore_errors=True)
                                self.stdout.write(self.style.SUCCESS(f"  ✅ Carpeta eliminada: {item}"))
                            deleted += 1
                    except ValueError:
                        continue

        # 2. Limpiar archivos sueltos en la raíz del directorio
        for item in directory.iterdir():
            if item.is_file():
                relative_path = f"{dir_name}/{item.name}"
                if relative_path not in active_files:
                    if dry_run:
                        self.stdout.write(f"  [DRY-RUN] Eliminaría archivo: {item.name}")
                    else:
                        try:
                            item.unlink()
                            self.stdout.write(self.style.SUCCESS(f"  ✅ Archivo eliminado: {item.name}"))
                        except:
                            pass
                    deleted += 1
        
        return deleted
    
    def _get_dir_size(self, path):
        """Calcula el tamaño total de un directorio"""
        total = 0
        for item in path.rglob('*'):
            if item.is_file():
                total += item.stat().st_size
        return total
