from rest_framework import status

from .base import BaseJWTTest


class JWTAuthTest(BaseJWTTest):
    def get_token(self):
        response = self.login()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        access = response.data.get("access")
        refresh = response.data.get("refresh")

        self.assertIsNotNone(access, response.data)
        self.assertIsNotNone(refresh, response.data)

        return access, refresh

    # -->Login<--
    def test_login_success_returns_access_and_refresh(self):
        response = self.login()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_fail_wrong_password(self):
        response = self.login(password="wrong")
        self.assertIn(
            response.status_code,
            [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED],
            getattr(response, "data", None),
        )

    # -->Refresh<--
    def test_refresh_success_returns_new_access(self):
        _, refresh = self.get_token()

        response = self.client.post(
            self.refresh_url, {"refresh": refresh}, format="json"
        )

        self.assertEqual(
            response.status_code, status.HTTP_200_OK, getattr(response, "data", None)
        )
        self.assertIn("access", response.data)

    def test_refresh_fail_with_invalid_refresh(self):
        response = self.client.post(
            self.refresh_url, {"refresh": "no-real-token"}, format="json"
        )

        self.assertIn(
            response.status_code,
            [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED],
            getattr(response, "data", None),
        )

    def test_logout_requires_authentication(self):
        _, refresh = self.get_token()

        response = self.client.post(
            self.logout_url,
            {"refresh": refresh},
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            getattr(response, "data", None),
        )

    def test_logout_requires_in_payload(self):
        access, _ = self.get_token()

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = self.client.post(self.logout_url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)
        self.assertEqual(response.data["detail"], "refresh token is required")

    def test_logout_blocklist_refresh(self):
        access, refresh = self.get_token()

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        response = self.client.post(
            self.logout_url, {"refresh": refresh}, format="json"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
            getattr(response, "data", None),
        )

        response2 = self.client.post(
            self.refresh_url, {"refresh": refresh}, format="json"
        )
        self.assertIn(
            response2.status_code,
            [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED],
            getattr(response2, "data", None),
        )
