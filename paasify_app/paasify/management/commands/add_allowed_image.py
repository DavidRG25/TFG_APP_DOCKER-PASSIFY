from django.core.management.base import BaseCommand

from containers.models import AllowedImage


class Command(BaseCommand):
    help = "Registra o actualiza una imagen permitida en el catálogo."

    def add_arguments(self, parser):
        parser.add_argument("--name", default="hello-world", help="Nombre de la imagen (sin tag).")
        parser.add_argument("--tag", default="latest", help="Tag de la imagen.")
        parser.add_argument(
            "--description",
            default="Imagen de prueba",
            help="Descripción opcional para mostrar en la UI.",
        )

    def handle(self, *args, **options):
        name = options["name"]
        tag = options["tag"]
        description = options["description"]

        obj, created = AllowedImage.objects.get_or_create(
            name=name,
            tag=tag,
            defaults={"description": description},
        )
        if not created and description and obj.description != description:
            obj.description = description
            obj.save(update_fields=["description"])

        if created:
            self.stdout.write(self.style.SUCCESS(f'Se agregó "{name}:{tag}" al catálogo.'))
        else:
            self.stdout.write(self.style.WARNING(f'"{name}:{tag}" ya existía; se actualizó la descripción.'))
