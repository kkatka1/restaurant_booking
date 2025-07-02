from datetime import timedelta

from django.utils import timezone
from django.utils.timezone import is_aware, localtime, make_aware


def calculate_table_availability(tables_queryset, selected):
    """
    Логика из BookingListView.get_queryset вынесена сюда.
    Принимает queryset столов и выбранное время.
    Возвращает список dict с info по столам: table, color, warning
    """
    result = []

    if selected:
        try:
            selected_time = timezone.datetime.fromisoformat(selected)
            selected_time = make_aware(selected_time)
            if selected_time < timezone.now():
                return result  # Не показываем столики, если выбрано прошедшее время
        except ValueError:
            return result  # если некорректная дата

        for table in tables_queryset:
            # Проверка есть ли бронь, перекрывающая выбранное время
            overlapping = table.reservations.filter(
                time_start__lte=selected_time,
                time_start__gte=selected_time - timedelta(hours=3),
            ).exists()

            if overlapping:
                color = "red"
                warning = None
            else:
                warning = None
                for reservation in table.reservations.all():
                    if not is_aware(reservation.time_start):
                        reservation_start = make_aware(reservation.time_start)
                    else:
                        reservation_start = reservation.time_start

                    delta = reservation_start - selected_time
                    if timedelta(0) < delta <= timedelta(hours=1.5):
                        warning = (
                            f"⚠️ Столик занят с {localtime(reservation_start):%H:%M}. "
                            f"Если вы планируете задержаться - выберите другой столик или позвоните нам"
                        )
                        break
                color = "green"

            result.append({"table": table, "color": color, "warning": warning})

    return result


def validate_reservation_conflict(table_id, booking_time, ReservationModel):
    """
    Логика проверки перекрытия брони из ReservationCreateView.form_valid.
    Возвращает True, если конфликт есть.
    """
    return ReservationModel.objects.filter(
        table_id=table_id,
        time_start__lte=booking_time,
        time_start__gte=booking_time - timedelta(hours=3),
    ).exists()
