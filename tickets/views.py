from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from tickets.pagination import TicketPagination
from tickets.permissions import IsAdminOrOwner
from .models import Ticket, User, UserProfile, Comment
from .serializers import CommentSerializer, TicketSerializer, UserProfileSerializer, UserSerializer
from django.views import View
from django.db.models import Q
from django.contrib.auth import authenticate

class LoginView(APIView):
    permission_classes = []
    
    def post(self, request):
        email_or_phone = request.data.get("email_or_phone")
        password = request.data.get("password")

        try:
            user = User.objects.get(
                Q(email=email_or_phone) | Q(profile__phone=email_or_phone)
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


class RegistrationView(APIView):
    permission_classes = []
    
    def post(self, request):
        email= request.data.get("email")
        phone = request.data.get("phone")
        password = request.data.get("password")
        confirm_password = request.data.get("confirm_password")
        username = request.data.get("username")

        if password != confirm_password:
            return Response({"error": "Passwords do not match"}, status=400)
        
        if len(password) < 8:
            return Response({"error": "Password must be at least 8 characters"}, status=400)
        
        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already registered"}, status=400)
        
        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already taken"}, status=400)
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.phone = phone
        profile.save()
        
        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Registration successful",
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }, status=201)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def patch(self, request):
        profile = request.user.profile
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

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

class CommentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, ticket_id):
        comments = Comment.objects.filter(ticket_id=ticket_id).select_related("user")
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, id=ticket_id)
        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user, ticket=ticket)
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        total_tickets = Ticket.objects.filter(created_by=user).count()
        open_tickets = Ticket.objects.filter(created_by=user, status=Ticket.Status.OPEN).count()
        in_progress_tickets = Ticket.objects.filter(created_by=user, status=Ticket.Status.IN_PROGRESS).count()
        closed_tickets = Ticket.objects.filter(created_by=user, status=Ticket.Status.CLOSED).count()

        return Response({
            "total_tickets": total_tickets,
            "open_tickets": open_tickets,
            "in_progress_tickets": in_progress_tickets,
            "closed_tickets": closed_tickets
        })
    
    
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