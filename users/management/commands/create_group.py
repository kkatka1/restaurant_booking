from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Создает группы пользователей и назначает соответствующие права"

    def handle(self, *args, **kwargs):
        groups_permissions = {
            "admin": [],
            "administrator": [  # Полный доступ к Reservation
                "booking.add_reservation",
                "booking.change_reservation",
                "booking.delete_reservation",
                "booking.view_reservation",
            ],
            "manager": [
                # Управление столиками (Table)
                "booking.add_table",
                "booking.change_table",
                "booking.delete_table",
                "booking.view_table",
                # Управление акциями (Promotion)
                "booking.add_promotion",
                "booking.change_promotion",
                "booking.delete_promotion",
                "booking.view_promotion",
                # Просмотр бронирований
                "booking.view_reservation",
            ],
            "marketer": [
                # Только управление акциями
                "booking.add_promotion",
                "booking.change_promotion",
                "booking.delete_promotion",
                "booking.view_promotion",
            ],
        }

        for group_name, permissions in groups_permissions.items():
            group, created = Group.objects.get_or_create(name=group_name)

            for perm in permissions:
                try:
                    app_label, codename = perm.split(".")
                    permission = Permission.objects.get(
                        codename=codename, content_type__app_label=app_label
                    )
                    group.permissions.add(permission)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Добавлено право: {perm} в группу {group_name}"
                        )
                    )
                except Permission.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Право {perm} не найдено для группы {group_name}."
                        )
                    )

            group.save()
            self.stdout.write(
                self.style.SUCCESS(f"Группа {group_name} обновлена с правами.")
            )
