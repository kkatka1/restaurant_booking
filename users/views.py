from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from users.forms import UserAuthenticationForm, UserCreateForm, UserProfileForm
from users.models import User
from users.use_cases import create_user_and_send_confirmation


class UserLoginView(LoginView):
    form_class = UserAuthenticationForm
    template_name = "users/login.html"


class UserCreateView(CreateView):
    model = User
    form_class = UserCreateForm
    template_name = "users/user_form.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        create_user_and_send_confirmation(form, self.request, User, send_email_confirm)
        messages.success(
            self.request, "Ссылка для подтверждения email отправлена на вашу почту."
        )
        return super().form_valid(form)


def email_verification(request, token):
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.save()
    messages.success(request, "Email успешно подтверждён!")
    return redirect(reverse("users:login"))


def send_email_confirm(user_email, url):
    subject = "Подтверждение регистрации"
    message = f"Спасибо за регистрацию! Подтвердите ваш email по ссылке: {url}"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "users/user_profile.html"
    context_object_name = "user"

    def get_object(self, queryset=None):
        if self.request.user.is_authenticated:
            return self.request.user
        raise Http404()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bookings_count"] = self.object.guest_reservations.count()
        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = "users/user_profile_edit.html"
    context_object_name = "user"

    def get_object(self, queryset=None):
        if self.request.user.is_authenticated:
            return self.request.user
        raise Http404()

    def get_success_url(self):
        return reverse_lazy("users:profile", kwargs={"pk": self.object.pk})


class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = "users/user_confirm_delete.html"
    success_url = reverse_lazy("users:login")
    context_object_name = "user"

    def get_object(self, queryset=None):
        if self.request.user.is_authenticated:
            return self.request.user
        raise Http404()


class UserListView(ListView):
    model = User
    template_name = "users/user_list.html"
    paginate_by = 10

    def get_queryset(self):
        return (
            User.objects.annotate(bookings_count=Count("guest_reservations"))
            .exclude(is_superuser=True)
            .order_by("-date_joined")
        )
