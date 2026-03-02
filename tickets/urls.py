from django.urls import path
from .views import LogoutView, ticket_detail, ticket_list_create

urlpatterns = [
    path("", ticket_list_create),
    path("logout/", LogoutView.as_view()),
    path("tickets/<int:pk>/", ticket_detail)
]