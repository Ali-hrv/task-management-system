from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

User = get_user_model()


class BaseJWTTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.password = "123456"

        self.user = User.objects.create_user(
            email="user@gmail.com",
            username="user",
            password=self.password,
        )

        self.login_url = "/api/auth/login/"
        self.refresh_url = "/api/auth/refresh/"
        self.logout_url = "/api/auth/logout/"

    def login(self, email=None, password=None):
        return self.client.post(
            self.login_url,
            {
                "email": email or self.user.email,
                "password": password or self.password,
            },
            format="json",
        )
