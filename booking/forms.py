from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Reservation


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ["guest_name", "guest_phone", "guests_count", "time_start"]

    def clean_guest_phone(self):
        phone = self.cleaned_data.get("guest_phone")
        # Удаляем пробелы и лишние символы
        cleaned_phone = "".join(c for c in phone if c.isdigit())

        if not cleaned_phone.isdigit():
            raise forms.ValidationError("Номер телефона должен содержать только цифры.")

        if not (10 <= len(cleaned_phone) <= 15):
            raise forms.ValidationError(
                "Номер телефона должен содержать от 10 до 15 цифр."
            )

        return cleaned_phone

    def clean_time_start(self):
        time = self.cleaned_data["time_start"]
        if time < timezone.now():
            raise ValidationError("Нельзя бронировать на прошедшее время.")
        return time

    def form_valid(self, form):
        return super().form_valid(form)


class FeedbackForm(forms.Form):
    name = forms.CharField(max_length=100, label="Ваше имя")
    email = forms.EmailField(label="Email")
    message = forms.CharField(widget=forms.Textarea, label="Сообщение")
