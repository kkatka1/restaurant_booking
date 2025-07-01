from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name="email")
    token = models.CharField(
        max_length=150, verbose_name="Токен", blank=True, null=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        permissions = [("block_users", "Может блокировать пользователей сервиса")]

    def get_booking_count(self):
        return self.guest_reservations.count()

    def __str__(self):
        return self.email
