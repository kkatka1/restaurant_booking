import secrets

from django.contrib.auth.models import Group


def create_user_and_send_confirmation(
    form, request, UserModel, send_email_confirm_func
):
    """
    Логика из UserCreateView.form_valid
    """
    user = form.save(commit=False)
    user.is_active = False
    token = secrets.token_hex(16)
    user.token = token
    user.save()

    regular_user_group, _ = Group.objects.get_or_create(name="regular_user")
    user.groups.add(regular_user_group)

    host = request.get_host()
    confirm_url = f"http://{host}/users/email-confirm/{token}"
    send_email_confirm_func(user.email, confirm_url)

    return user
