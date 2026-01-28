from rest_framework import status

from .base import BaseTaskAPITestCase


class TaskJWTIntegrationTest(BaseTaskAPITestCase):
    def get_access_token(self):
        response = self.client.post(
            "/api/auth/login/",
            {
                "email": self.member.email,
                "username": self.member.username,
                "password": "123456",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access = response.data.get("access")
        self.assertIsNotNone(access, response.data)
        return access

    def test_task_list_requires_jwt(self):
        response = self.client.get(self.task_list_url())
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_task_list_with_jwt_returns_200(self):
        token = self.get_access_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get(self.task_list_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertGreaterEqual(response.data["count"], 1)

    def test_task_detail_with_jwt_returns_200(self):
        token = self.get_access_token()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get(self.task_detail_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["id"], self.task.id, getattr(response, "data", None)
        )
