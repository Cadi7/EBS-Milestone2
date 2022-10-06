from rest_framework.test import APITestCase
from apps.users.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class AccountTests(APITestCase):
    def test_user_register(self):
        data = {
            "first_name": "string",
            "last_name": "string",
            "username": "string",
            "email": "faer.faer.2006@mail.ru",
            "password": "string",
        }

        response = self.client.post("/users/register/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = {
            "first_name": "string",
            "last_name": "string",
            "username": "string",
            "email": "",
            "password": "string",
        }
        response = self.client.post("/users/register/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_access_token(self):
        """Create a user"""

        email = "finicacr7@gmail.com"
        password = "1234"
        self.user = User.objects.create_user(email, email, password)
        jwt_fetch_data = {"username": email, "password": password}

        response = self.client.post("/users/login/", jwt_fetch_data, "json")

        """Test access token"""

        token = get_tokens_for_user(self.user).get("access")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        """Test refresh token"""

        self.refresh_token = get_tokens_for_user(self.user).get("refresh")

        data = {"refresh": self.refresh_token}
        response = self.client.post("/user/refresh/", data, "json")
        access_token = get_tokens_for_user(self.user).get("access")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    def test_get_all_users(self):
        response = self.client.get("/users/", data={"format": "json"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
