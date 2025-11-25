"""
Comando para poblar la base de datos con imágenes de ejemplo de cada tipo.
"""
from django.core.management.base import BaseCommand
from containers.models import AllowedImage


class Command(BaseCommand):
    help = 'Crea imágenes de ejemplo de cada tipo en AllowedImage'

    def add_arguments(self, parser):
        parser.add_argument(
            '--noinput',
            action='store_true',
            help='No solicita confirmación del usuario',
        )

    def handle(self, *args, **options):
        images_to_create = [
            # Web / Frontend
            {
                'name': 'nginx',
                'tag': 'latest',
                'description': 'Servidor web de alto rendimiento',
                'image_type': 'web'
            },
            {
                'name': 'httpd',
                'tag': 'latest',
                'description': 'Servidor web Apache HTTP',
                'image_type': 'web'
            },
            
            # Base de Datos
            {
                'name': 'mysql',
                'tag': 'latest',
                'description': 'Base de datos MySQL',
                'image_type': 'database'
            },
            {
                'name': 'postgres',
                'tag': 'latest',
                'description': 'Base de datos PostgreSQL',
                'image_type': 'database'
            },
            {
                'name': 'mongo',
                'tag': 'latest',
                'description': 'Base de datos MongoDB',
                'image_type': 'database'
            },
            {
                'name': 'redis',
                'tag': 'latest',
                'description': 'Base de datos en memoria Redis',
                'image_type': 'database'
            },
            
            # Generador de API
            {
                'name': 'strapi/strapi',
                'tag': 'latest',
                'description': 'CMS Headless y generador de API',
                'image_type': 'api'
            },
            {
                'name': 'hasura/graphql-engine',
                'tag': 'latest',
                'description': 'Motor GraphQL instantáneo',
                'image_type': 'api'
            },
            {
                'name': 'postgrest/postgrest',
                'tag': 'latest',
                'description': 'API REST automática para PostgreSQL',
                'image_type': 'api'
            },
            
            # Miscelánea
            {
                'name': 'python',
                'tag': '3.12',
                'description': 'Imagen de contenedor Python',
                'image_type': 'misc'
            },
            {
                'name': 'node',
                'tag': 'lts',
                'description': 'Entorno de ejecución Node.js',
                'image_type': 'misc'
            },
        ]

        created_count = 0
        skipped_count = 0

        for img_data in images_to_create:
            # Verificar si ya existe
            existing = AllowedImage.objects.filter(
                name=img_data['name'],
                tag=img_data['tag']
            ).first()

            if existing:
                self.stdout.write(
                    self.style.WARNING(
                        f"⏭️  Ya existe: {img_data['name']}:{img_data['tag']}"
                    )
                )
                skipped_count += 1
            else:
                AllowedImage.objects.create(**img_data)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Creada: {img_data['name']}:{img_data['tag']} ({img_data['image_type']})"
                    )
                )
                created_count += 1

        self.stdout.write("\n" + "="*60)
        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Proceso completado:\n"
                f"   - Imágenes creadas: {created_count}\n"
                f"   - Imágenes omitidas (ya existían): {skipped_count}\n"
            )
        )
