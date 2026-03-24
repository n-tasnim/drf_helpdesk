from django.urls import path, include
from .views import CommentView, LoginView, TicketDetail, TicketList, LogoutView, RegistrationView, UserProfileView
from django.conf import settings

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegistrationView.as_view(), name='register'),
    path('', TicketList.as_view(), name='ticket-list'),
    path('<int:pk>/', TicketDetail.as_view(), name='ticket-detail'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('<int:ticket_id>/comments/', CommentView.as_view(), name='ticket-comments'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns+= [
        path('__debug__/', include(debug_toolbar.urls)),
    ]