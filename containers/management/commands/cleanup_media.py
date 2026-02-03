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
        
        # 1. Limpiar media/services/ (Workspaces)
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
        
        # Limpiar directorios estándar
        for dir_name in ["dockerfiles", "compose_files", "user_code"]:
            deleted_count = self._cleanup_directory(
                media_root / dir_name,
                active_files,
                dry_run,
                dir_name
            )
            total_deleted += deleted_count
        
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
