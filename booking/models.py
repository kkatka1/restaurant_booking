from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

STATUS_CHOICES = (
    ("available", "Свободен"),
    ("unavailable", "Недоступен"),
)


class Table(models.Model):
    number = models.CharField(
        verbose_name="Номер столика",
        max_length=20,
        unique=True,
        help_text="Уникальный код: T1, VIP-2, Окно 3",
    )
    display_name = models.CharField(
        verbose_name="Название для отображения",
        max_length=50,
        blank=True,
        null=True,
        help_text="Отображается на карте зала: 'Окно 4', 'Центр'",
    )
    seats_total = models.PositiveIntegerField(
        verbose_name="Количество мест за столом", default=1
    )
    x = models.PositiveIntegerField(verbose_name="Координата X", default=0)
    y = models.PositiveIntegerField(verbose_name="Координата Y", default=0)
    status = models.CharField(
        verbose_name="Статус",
        max_length=20,
        choices=STATUS_CHOICES,
        default="available",
        help_text="Вычисляется автоматически на основе бронирований",
    )

    class Meta:
        verbose_name = "Столик"
        verbose_name_plural = "Столики"
        ordering = ["seats_total", "number"]

    def __str__(self):
        return f"Столик {self.number} ({self.seats_total} мест)"

    def get_status_and_warning(self):
        """
        Вычисляет текущий статус столика:
        Если сейчас занято или начнется бронь в ближайшие 1.5 часа
        Если свободен на длительное время (или есть только отдалённые брони)
        Возвращает кортеж (статус, предупреждение или None)
        """
        now = timezone.now()

        for reservation in self.reservations.all():
            start = reservation.time_start
            end = start + reservation.duration

            if start <= now <= end:
                return "unavailable", None

            delta = start - now
            if timedelta(0) < delta <= timedelta(hours=1.5):
                warning = (
                    f"⚠️ Этот столик будет занят с {start:%H:%M}. "
                    f"Если вы планируете задержаться — выберите другой или позвоните нам"
                )
                return "available", warning

        return "available", None


class Promotion(models.Model):
    title = models.CharField(verbose_name="Название акции", max_length=100)
    description = models.TextField(verbose_name="Описание")
    discount_percent = models.PositiveIntegerField(verbose_name="Скидка (%)")
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")
    is_active = models.BooleanField(verbose_name="Активна?", default=True)

    class Meta:
        verbose_name = "Акция"
        verbose_name_plural = "Акции"
        ordering = ["-start_date", "title"]

    def __str__(self):
        return f"{self.title} ({self.discount_percent}%)"

    def is_current(self):
        today = timezone.now().date()
        return self.is_active and self.start_date <= today <= self.end_date


class Reservation(models.Model):
    table = models.ForeignKey(
        Table,
        on_delete=models.CASCADE,
        related_name="reservations",
        verbose_name="Столик",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="guest_reservations",
        verbose_name="Пользователь",
        null=True,
        blank=True,
    )
    guest_name = models.CharField(verbose_name="Имя гостя", max_length=100)
    guest_phone = models.CharField(verbose_name="Телефон гостя", max_length=20)
    email = models.EmailField(verbose_name="Email", blank=True, null=True)
    guests_count = models.PositiveIntegerField(
        verbose_name="Количество гостей", default=1
    )
    time_start = models.DateTimeField(verbose_name="Время начала брони")
    duration = models.DurationField(
        verbose_name="Длительность брони",
        default=timedelta(hours=3),
        help_text="По умолчанию 3 часа. Меняется только админом",
    )
    extended_by_admin = models.BooleanField(
        verbose_name="Продлена вручную", default=False
    )
    source = models.CharField(
        verbose_name="Источник брони",
        max_length=20,
        choices=(
            ("guest", "Гость через сайт"),
            ("admin", "Администратор вручную"),
        ),
        default="guest",
        help_text="Кем оформлена бронь (определяется автоматически)",
    )
    staff_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Менеджер/админ",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Если бронь оформлялась персоналом",
    )
    upsell_amount = models.PositiveIntegerField(
        verbose_name="Апсейл: Дополнительный доход (в рублях)",
        default=0,
        help_text=" Сумма в рублях за доп продажу",
    )
    upsell_option = models.ForeignKey(
        Promotion,
        verbose_name="Апсейл-опция (Акция)",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Выберите дополнительную опцию из списка активных акций",
    )
    created_at = models.DateTimeField(verbose_name="Создано", auto_now_add=True)

    class Meta:
        verbose_name = "Бронь"
        verbose_name_plural = "Брони"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.guest_name} ({self.time_start:%Y-%m-%d %H:%M})"

    def is_active(self):
        now = timezone.now()
        if self.extended_by_admin:
            return True
        return self.time_start <= now <= self.time_start + self.duration

    def is_guest_reservation(self):
        return self.source == "guest"

    def is_admin_reservation(self):
        return self.source == "admin"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
