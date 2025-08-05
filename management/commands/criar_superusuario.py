from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = 'Cria um superusuário automaticamente se não existir'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'danilosouza')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'danilosouzaavare@gmail.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Danilo0012!')

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS('Superusuário criado com sucesso.'))
        else:
            self.stdout.write(self.style.WARNING('Superusuário já existe.'))
