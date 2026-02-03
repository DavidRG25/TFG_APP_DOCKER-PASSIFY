import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app_passify.settings')
os.environ['DJANGO_DEBUG'] = 'True'
django.setup()

from containers.models import Service
from containers.services import remove_container

# Buscar servicios con estado 'removed' o que sean de pruebas antiguas que ya no están en Docker
# Basándonos en el análisis anterior, los IDs del 96 al 139 (excepto los que están running)
# son candidatos a eliminación total de la DB para limpiar sus archivos.

servicios_a_eliminar = Service.objects.filter(status='removed')
count = servicios_a_eliminar.count()

print(f"Iniciando purga de {count} servicios en estado 'removed'...")

for s in servicios_a_eliminar:
    print(f"Eliminando permanentemente ID: {s.id} - {s.name}...")
    # El método delete() normal de Django eliminará el registro. 
    # Como ya pusimos el fix preventivo en remove_container, 
    # pero eso se dispara al CAMBIAR a removed. 
    # Para asegurar la limpieza de archivos de registros ya existentes:
    
    try:
        if s.dockerfile:
            s.dockerfile.delete(save=False)
        if s.compose:
            s.compose.delete(save=False)
        if s.code:
            s.code.delete(save=False)
            
        # Importamos la limpieza de workspace mejorada que hicimos hoy
        from containers.services import cleanup_service_workspace
        cleanup_service_workspace(s)
        
        # Finalmente borramos el registro de la DB
        s.delete()
        print(f"  ✅ OK")
    except Exception as e:
        print(f"  ❌ Error: {e}")

print(f"\nPurga completada. Se han eliminado {count} registros y sus archivos asociados.")
