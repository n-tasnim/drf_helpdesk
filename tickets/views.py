from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from tickets.pagination import TicketPagination
from tickets.permissions import IsAdminOrOwner
from .models import Ticket
from .serializers import TicketSerializer

class TicketList(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = TicketPagination

    def get(self, request):
        user = request.user

        if user.is_staff:
            tickets = Ticket.objects.select_related("created_by")
        else:
            tickets = Ticket.objects.filter(created_by=user)
        
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(tickets, request)

        serializer = TicketSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = TicketSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)
    
class TicketDetail(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrOwner]

    def get_object(self, pk):
        return get_object_or_404(Ticket, pk=pk)
    
    def get(self, request, pk):
        ticket = self.get_object(pk)
        self.check_object_permissions(request, ticket)

        serializer = TicketSerializer(ticket)
        return Response(serializer.data)
    
    def patch(self, request, pk):
        ticket = self.get_object(pk)
        self.check_object_permissions(request, ticket)

        serializer = TicketSerializer(ticket, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)
    
    def delete(self, request, pk):
        ticket = self.get_object(pk)
        self.check_object_permissions(request, ticket)
        ticket.delete()
        return Response(status=204)

 
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