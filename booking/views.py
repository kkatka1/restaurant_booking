from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.timezone import is_aware, localtime, make_aware
from django.views.generic import (CreateView, DeleteView, ListView,
                                  TemplateView, UpdateView)
from django.views.generic.edit import FormView

from config import settings

from .forms import FeedbackForm, ReservationForm
from .models import Reservation, Table


class BookingListView(LoginRequiredMixin, ListView):
    model = Table
    template_name = "booking/booking_list.html"
    context_object_name = "tables"
    login_url = "/users/login/"
    redirect_field_name = "next"

    def dispatch(self, request, *args, **kwargs):
        if request.path.startswith(f"/{settings.ADMIN_PATH}"):
            return redirect(settings.ADMIN_LOGIN_URL + f"?next={request.path}")
        if not request.user.is_authenticated:
            messages.warning(
                request,
                "Для самостоятельного бронирования вам необходимо зарегистрироваться",
            )
            return redirect(reverse("users:login") + f"?next={request.path}")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        selected = self.request.GET.get("booking_time")
        result = []

        if selected:
            try:
                selected_time = timezone.datetime.fromisoformat(selected)
                selected_time = timezone.make_aware(selected_time)

                if selected_time < timezone.now():
                    return result  # Не показываем столики, если выбрано прошедшее время

            except ValueError:
                return result  # если некорректная дата

            for table in Table.objects.all():
                # Проверка есть ли бронь, перекрывающая выбранное время
                overlapping = table.reservations.filter(
                    time_start__lte=selected_time,
                    time_start__gte=selected_time - timedelta(hours=3),
                ).exists()

                if overlapping:
                    color = "red"
                    warning = None
                else:
                    # Предупреждение, если бронь начнется в ближайшие 1.5 часа
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

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        left_tables = []
        mid_tables = []
        right_tables = []

        tables = self.get_queryset()
        for t in tables:
            table_id = t["table"].id
            if table_id in [1, 2, 3]:
                left_tables.append(t)
            elif table_id in [4, 5]:
                mid_tables.append(t)
            elif table_id in [6, 7, 8]:
                right_tables.append(t)

        ctx["left_tables"] = left_tables
        ctx["mid_tables"] = mid_tables
        ctx["right_tables"] = right_tables
        return ctx


class ReservationCreateView(LoginRequiredMixin, CreateView):
    model = Reservation
    form_class = ReservationForm
    template_name = "booking/reservation_create.html"
    login_url = "/users/login/"

    def dispatch(self, request, *args, **kwargs):
        if request.path.startswith(f"/{settings.ADMIN_PATH}"):
            return super().dispatch(request, *args, **kwargs)

        if not request.user.is_authenticated:
            return redirect(reverse("users:login") + f"?next={request.path}")
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        booking_time = self.request.GET.get("booking_time")
        if booking_time:
            try:
                dt = timezone.datetime.fromisoformat(booking_time)
                initial["time_start"] = timezone.make_aware(dt)
            except ValueError:
                pass
        return initial

    def form_valid(self, form):
        table_id = self.kwargs["pk"]
        booking_time = form.cleaned_data["time_start"]

        # Привязка к пользователю
        form.instance.user = self.request.user
        form.instance.source = "guest"
        form.instance.table_id = table_id

        # Автоматическое заполнение имени/телефона
        form.instance.guest_name = (
            self.request.user.first_name or self.request.user.email
        )
        form.instance.guest_phone = self.request.user.username or "Не указан"

        # Проверка перекрытия
        if Reservation.objects.filter(
            table_id=table_id,
            time_start__lte=booking_time,
            time_start__gte=booking_time - timedelta(hours=3),
        ).exists():
            form.add_error(None, "Этот столик уже забронирован на выбранное время.")
            return self.form_invalid(form)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["table"] = Table.objects.get(pk=self.kwargs["pk"])
        booking_time = self.request.GET.get("booking_time")
        if booking_time:
            try:
                dt = timezone.datetime.fromisoformat(booking_time)
                ctx["booking_time"] = timezone.make_aware(dt)
            except ValueError:
                ctx["booking_time"] = None
        return ctx

    def get_success_url(self):
        return reverse_lazy("booking:thanks")


class IndexView(TemplateView):
    template_name = "index.html"


class ContactsView(TemplateView):
    template_name = "contacts.html"


class ThanksView(TemplateView):
    template_name = "booking/thanks.html"


class MenuView(TemplateView):
    template_name = "menu.html"


class AboutView(TemplateView):
    template_name = "booking/about.html"


class BookingHistoryView(LoginRequiredMixin, ListView):
    model = Reservation
    template_name = "booking/history.html"
    context_object_name = "reservations"

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user).order_by(
            "-time_start"
        )


class UpdateReservationView(LoginRequiredMixin, UpdateView):
    model = Reservation
    fields = ["table", "time_start", "guests_count"]
    template_name = "booking/history_edit_reservation.html"
    success_url = reverse_lazy("booking:history")

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)


class DeleteReservationView(LoginRequiredMixin, DeleteView):
    model = Reservation
    template_name = "booking/history_delete_reservation.html"
    success_url = reverse_lazy("booking:history")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"] = timezone.now()
        return context

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)


class FeedbackView(FormView):
    template_name = "booking/feedback.html"
    form_class = FeedbackForm
    success_url = reverse_lazy("booking:feedback_thanks")

    def form_valid(self, form):
        messages.success(self.request, "Спасибо за ваше сообщение!")
        return super().form_valid(form)


class FeedbackThanksView(TemplateView):
    template_name = "booking/feedback_thanks.html"
