from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from paasify.models.SubjectModel import Subject
from paasify.models.ProjectModel import UserProject
from containers.models import Service

class Command(BaseCommand):
    help = "Crea asignaturas, proyectos y servicios de ejemplo para el usuario alumno y profesor"

    def handle(self, *args, **options):
        User = get_user_model()
        
        try:
            alumno = User.objects.get(username='alumno')
            profesor = User.objects.get(username='profesor')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("Error: Ejecuta primero 'python manage.py create_demo_users'"))
            return

        # 1. Crear Asignaturas (y asignarlas al profesor)
        sub1, created1 = Subject.objects.get_or_create(
            name='Desarrollo Web Fullstack',
            defaults={
                'teacher_user': profesor,
                'genero': '2026',
                'category': 'Frontend/Backend',
                'color': '#4e73df',
                'players': 'Profesor Demo'
            }
        )
        
        sub2, created2 = Subject.objects.get_or_create(
            name='Sistemas Cloud y Contenedores',
            defaults={
                'teacher_user': profesor,
                'genero': '2026',
                'category': 'Sistemas',
                'color': '#1cc88a',
                'players': 'Profesor Demo'
            }
        )

        # Matricular al alumno virtualmente
        sub1.students.add(alumno)
        sub2.students.add(alumno)

        self.stdout.write(self.style.SUCCESS(f"+ Asignaturas verificadas/creadas"))

        # 2. Crear Proyectos
        try:
            profile = alumno.userprofile
        except Exception:
            self.stdout.write(self.style.ERROR("Error: El usuario alumno no tiene UserProfile. Inicia sesión con él una vez o ejecuta el save()."))
            # Forzando creación en caso de que no exista
            from paasify.models.StudentModel import UserProfile
            profile, _ = UserProfile.objects.get_or_create(user=alumno, defaults={'nombre': 'Alumno Demo'})


        proj_web, _ = UserProject.objects.get_or_create(
            place='Proyecto Final E-commerce',
            user_profile=profile,
            subject=sub1
        )
        
        proj_cloud, _ = UserProject.objects.get_or_create(
            place='Despliegue Multi-contenedor',
            user_profile=profile,
            subject=sub2
        )

        self.stdout.write(self.style.SUCCESS(f"+ Proyectos verificados/creados"))

        # 3. Crear Servicios (Contenedores Simulados)
        # Servicio 1: Frontend (React/Nginx)
        Service.objects.get_or_create(
            name='frontend-cliente',
            owner=alumno,
            subject=sub1,
            project=proj_web,
            defaults={
                'image': 'nginx:alpine',
                'status': 'stopped',
                'container_type': 'web',
                'mode': 'dockerhub',
                'is_web': True,
                'assigned_port': 40001
            }
        )
        
        # Servicio 2: Backend (Node.js/Python)
        Service.objects.get_or_create(
            name='api-backend',
            owner=alumno,
            subject=sub1,
            project=proj_web,
            defaults={
                'image': 'python:3.10',
                'status': 'stopped',
                'container_type': 'api',
                'mode': 'dockerhub',
            }
        )

        # Servicio 3: Base de Datos (Postgres)
        Service.objects.get_or_create(
            name='database-master',
            owner=alumno,
            subject=sub2,
            project=proj_cloud,
            defaults={
                'image': 'postgres:15',
                'status': 'stopped',
                'container_type': 'database',
                'mode': 'dockerhub'
            }
        )

        self.stdout.write(self.style.SUCCESS(f"+ Servicios de ejemplo creados en estado detenido"))
        self.stdout.write(self.style.SUCCESS(f"¡Semillado de datos para testing de API completado!"))
