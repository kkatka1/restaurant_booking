# Generated by Django 5.2.3 on 2025-06-29 14:42

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("booking", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="reservation",
            name="staff_user",
            field=models.ForeignKey(
                blank=True,
                help_text="Если бронь оформлялась персоналом",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
                verbose_name="Менеджер/админ",
            ),
        ),
        migrations.AddField(
            model_name="reservation",
            name="table",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="reservations",
                to="booking.table",
                verbose_name="Столик",
            ),
        ),
    ]
