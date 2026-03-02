from django.urls import path
from .views import ticket_list_create

urlpatterns = [
    path("", ticket_list_create),
]