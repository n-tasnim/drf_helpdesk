from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TicketViewSet, LogoutView

router = DefaultRouter()
router.register(r'', TicketViewSet, basename='ticket')

urlpatterns = [
    path('', include(router.urls)),
    path('logout/', LogoutView.as_view(), name='logout'),
]