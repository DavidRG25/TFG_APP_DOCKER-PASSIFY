import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app_passify.settings')
os.environ['DJANGO_DEBUG'] = 'True'
django.setup()

from containers.models import Service

print("ID | Nombre | Estado | Creado | Imagen")
print("-" * 50)
for s in Service.objects.all().order_by('-id'):
    print(f"{s.id} | {s.name} | {s.status} | {s.created_at} | {s.image}")
