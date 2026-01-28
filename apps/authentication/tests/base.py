from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

User = get_user_model()


class BaseJWTTest(TestCase):
    login_url = "/api/auth/login/"
    refresh_url = "/api/auth/refresh/"
    logout_url = "/api/auth/logout/"
    email = "user@gmail.com"
    password = "123456"

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            email=self.email,
            username="user",
            password=self.password,
        )

    def login(self, email=None, password=None):
        return self.client.post(
            self.login_url,
            {
                "email": email or self.user.email,
                "password": password or self.password,
            },
            format="json",
        )
