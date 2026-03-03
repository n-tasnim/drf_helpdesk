from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import Ticket

class TicketTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="password123"
        )

    def test_ticket_list_requires_authentication(self):
        response = self.client.get("/tickets/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_create_ticket(self):
        self.client.login(username="testuser", password="password123")

        data = {
            "title": "Login Issue",
            "description": "Cannot login"
        }

        response = self.client.post("/tickets/", data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ticket.objects.count(), 1)


    def test_user_sees_only_own_tickets(self):
        other_user = User.objects.create_user(
            username="other",
            password="pass123"
        )

        Ticket.objects.create(
            title="User1 Ticket",
            description="Test",
            created_by=self.user
        )

        Ticket.objects.create(
            title="User2 Ticket",
            description="Test",
            created_by=other_user
        )

        self.client.login(username="testuser", password="password123")
        response = self.client.get("/tickets/")

        self.assertEqual(len(response.data["results"]), 1)