from rest_framework import serializers
from .models import Ticket, Comment, UserProfile, User

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["phone", "address"]

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only = True)

    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = ["user", "ticket","created_at"]

class TicketSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source="created_by.username")
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "created_by",
            "created_at",
        ]

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()
    tickets = TicketSerializer(many=True, read_only=True)
    ticket_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ["id", "username", "email", "profile", "tickets", "ticket_count"]

    def get_ticket_count(self, obj):
        return obj.tickets.count()

