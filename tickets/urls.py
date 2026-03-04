from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TicketViewSet, LogoutView
from django.conf import settings

router = DefaultRouter()
router.register(r'', TicketViewSet, basename='ticket')

urlpatterns = [
    path('', include(router.urls)),
    path('logout/', LogoutView.as_view(), name='logout'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns+= [
        path('__debug__/', include(debug_toolbar.urls)),
    ]