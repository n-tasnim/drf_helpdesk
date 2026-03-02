from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Ticket
from .serializers import TicketSerializer


class TicketViewSet(ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    # Control what tickets user can see
    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Ticket.objects.all()
        return Ticket.objects.filter(created_by=user)

    # Automatically set created_by
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    # Restrict updates (status + assignment rules)
    def update(self, request, *args, **kwargs):
        ticket = self.get_object()

        # Normal user restrictions
        if not request.user.is_staff:
            if "status" in request.data:
                return Response(
                    {"error": "You cannot change ticket status"},
                    status=status.HTTP_403_FORBIDDEN
                )

            if "assigned_to" in request.data:
                return Response(
                    {"error": "You cannot assign tickets"},
                    status=status.HTTP_403_FORBIDDEN
                )

        return super().update(request, *args, **kwargs)

    # Restrict delete
    def destroy(self, request, *args, **kwargs):
        ticket = self.get_object()

        if not request.user.is_staff and ticket.created_by != request.user:
            return Response(
                {"error": "You cannot delete this ticket"},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().destroy(request, *args, **kwargs)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully"}, status=200)
        except Exception:
            return Response({"error": "Invalid token"}, status=400)