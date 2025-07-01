from django.urls import path

from .views import (AboutView, BookingHistoryView, BookingListView,
                    ContactsView, DeleteReservationView, FeedbackThanksView,
                    FeedbackView, IndexView, MenuView, ReservationCreateView,
                    ThanksView, UpdateReservationView)

app_name = "booking"

urlpatterns = [
    path("main/", IndexView.as_view(), name="home"),
    path("", BookingListView.as_view(), name="list"),
    path("table/<int:pk>/reserve/", ReservationCreateView.as_view(), name="create"),
    path("contacts/", ContactsView.as_view(), name="contacts"),
    path("thanks/", ThanksView.as_view(), name="thanks"),
    path("menu/", MenuView.as_view(), name="menu"),
    path("about/", AboutView.as_view(), name="about"),
    path("feedback/", FeedbackView.as_view(), name="feedback"),
    path("feedback/thanks/", FeedbackThanksView.as_view(), name="feedback_thanks"),
    path("history/", BookingHistoryView.as_view(), name="history"),
    path(
        "reservation/<int:pk>/edit/",
        UpdateReservationView.as_view(),
        name="update_reservation",
    ),
    path(
        "reservation/<int:pk>/delete/",
        DeleteReservationView.as_view(),
        name="delete_reservation",
    ),
]
