from datetime import timedelta

from django import forms
from django.contrib import admin
from django.contrib.admin import widgets
from django.utils import timezone

from .models import Promotion, Reservation, Table


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = (
        "number",
        "display_name",
        "seats_total",
        "x",
        "y",
        "status",
    )
    list_filter = ("status",)
    search_fields = (
        "number",
        "display_name",
        "seats_total",
    )


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "description",
        "discount_percent",
        "start_date",
        "end_date",
        "is_active",
    )
    search_fields = (
        "title",
        "start_date",
        "end_date",
        "is_active",
    )


class CustomReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = "__all__"
        widgets = {
            "time_start": widgets.AdminSplitDateTime(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Только активные акции, отсортированные по дате
        self.fields["upsell_option"].queryset = Promotion.objects.filter(
            is_active=True
        ).order_by("-start_date")

    def clean(self):
        cleaned_data = super().clean()
        time_start = cleaned_data.get("time_start")
        table = cleaned_data.get("table")

        if not time_start or not table:
            return cleaned_data

        if time_start < timezone.now():
            self.add_error("time_start", "Нельзя бронировать на прошедшее время.")

        # Проверка на пересечение с существующими бронями (±3 часа)
        overlapping = Reservation.objects.filter(
            table=table,
            time_start__lte=time_start,
            time_start__gte=time_start - timedelta(hours=3),
        )

        # Исключаем текущую бронь при редактировании
        if self.instance.pk:
            overlapping = overlapping.exclude(pk=self.instance.pk)

        if overlapping.exists():
            self.add_error(None, "Этот столик уже забронирован на выбранное время.")

        return cleaned_data


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    form = CustomReservationForm

    list_display = (
        "table",
        "guest_name",
        "guest_phone",
        "email",
        "guests_count",
        "time_start",
        "duration",
        "extended_by_admin",
        "source",
        "staff_user",
        "upsell_amount",
        "upsell_option",
        "created_at",
    )
    list_filter = ("table",)
    search_fields = (
        "table__number",
        "guest_name",
        "guest_phone",
        "time_start",
        "source",
    )
