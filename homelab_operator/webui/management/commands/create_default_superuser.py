from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = 'Creates default superuser if not exists'

    def handle(self, *args, **kwargs):
        if os.getenv("SUPERUSER_USERNAME", False) is False or os.getenv("SUPERUSER_EMAIL", False) is False or os.getenv("SUPERUSER_PASSWORD", False) is False:
            self.stdout.write(self.style.WARNING("SUPERUSER environment variables are not set. Skipping superuser creation."))
            return
        User = get_user_model()
        username = os.getenv("SUPERUSER_USERNAME", "admin")
        email = os.getenv("SUPERUSER_EMAIL", "admin@example.com")
        password = os.getenv("SUPERUSER_PASSWORD", "admin_password")

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created."))
        else:
            self.stdout.write(f"Superuser '{username}' already exists.")
