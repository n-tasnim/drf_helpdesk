from django.urls import path
from .views import LogoutView, ticket_list_create

urlpatterns = [
    path("", ticket_list_create),
    path("logout/", LogoutView.as_view()),
]