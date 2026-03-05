from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Crea un superusuario de pruebas con credenciales conocidas."

    def add_arguments(self, parser):
        parser.add_argument("--username", default="testuser", help="Nombre de usuario.")
        parser.add_argument("--email", default="test@example.com", help="Correo electrónico.")
        parser.add_argument("--password", default="testpassword", help="Contraseña del superusuario.")

    def handle(self, *args, **options):
        User = get_user_model()
        username = options["username"]
        email = options["email"]
        password = options["password"]

        if User.objects.filter(username=username).exists():
            raise CommandError(f'El usuario "{username}" ya existe.')

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f'Se creó el superusuario "{username}".'))
