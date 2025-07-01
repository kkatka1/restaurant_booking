from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Создаёт суперпользователя"

    def handle(self, *args, **options):
        email = "admin@sky.pro"
        password = "123qwe456rty"

        user, created = User.objects.get_or_create(email=email)

        user.first_name = "Admin"
        user.last_name = "Superuser"
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f"Создан суперпользователь {email}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Обновлён суперпользователь {email}"))
