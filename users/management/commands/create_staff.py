from django.contrib.auth.models import Group
from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    help = "Создаёт тестовых пользователей с правильными группами и паролями"

    def handle(self, *args, **kwargs):
        users_info = [
            {
                "email": "admin@test.com",
                "first_name": "Admin",
                "last_name": "User",
                "group": "administrator",
                "is_staff": True,
                "is_superuser": False,
            },
            {
                "email": "manager@test.com",
                "first_name": "Manager",
                "last_name": "User",
                "group": "manager",
                "is_staff": True,
                "is_superuser": False,
            },
            {
                "email": "marketer@test.com",
                "first_name": "Marketer",
                "last_name": "User",
                "group": "marketer",
                "is_staff": True,
                "is_superuser": False,
            },
        ]

        for user_info in users_info:
            if not User.objects.filter(email=user_info["email"]).exists():
                user = User.objects.create(
                    email=user_info["email"],
                    first_name=user_info["first_name"],
                    last_name=user_info["last_name"],
                    is_staff=user_info["is_staff"],
                    is_superuser=user_info["is_superuser"],
                )
                user.set_password("123qwe456rty")
                user.save()

                if user_info["group"]:
                    group = Group.objects.get(name=user_info["group"])
                    user.groups.add(group)

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Пользователь {user_info['email']} в {user_info['group'] or 'superuser'}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Пользователь {user_info['email']} уже существует"
                    )
                )
