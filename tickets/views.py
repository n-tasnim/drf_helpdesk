from django.shortcuts import get_object_or_404, render
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from tickets.pagination import TicketPagination
from tickets.permissions import IsAdminOrOwner
from .models import Ticket
from .serializers import TicketSerializer
from django.contrib.auth import authenticate, get_user_model
from django.views import View
from django.db.models import Q

User = get_user_model() 


class LoginPageView(View):
    def get(self, request):
        return render(request, 'login.html') 

class LoginView(APIView):
    permission_classes = []
    
    def get(self, request):
        return render(request, 'login.html')
    
    def post(self, request):
        email_or_phone = request.data.get("email_or_phone")
        password = request.data.get("password")

        try:
            user = User.objects.get(
                Q(email=email_or_phone) | Q(phone=email_or_phone)
            )
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=400)
        
        user = authenticate(username=user.username, password=password)

        if user is None:
            return Response({"error": "Invalid credentials"}, status=401)
        
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        })


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