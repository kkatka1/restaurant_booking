from django.contrib.auth.views import LogoutView
from django.urls import path

from users.views import (UserCreateView, UserDeleteView, UserDetailView,
                         UserListView, UserLoginView, UserUpdateView,
                         email_verification)

app_name = "users"

urlpatterns = [
    path("", UserListView.as_view(), name="users_list"),
    path("profile/<int:pk>/", UserDetailView.as_view(), name="profile"),
    path("profile/edit/<int:pk>/", UserUpdateView.as_view(), name="profile_edit"),
    path("profile/delete/", UserDeleteView.as_view(), name="profile_delete"),
    path(
        "login/", UserLoginView.as_view(template_name="users/login.html"), name="login"
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", UserCreateView.as_view(), name="register"),
    path("email-confirm/<str:token>/", email_verification, name="email_confirm"),
]
