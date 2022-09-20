from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

User = get_user_model()


def auth(user):
    refresh = RefreshToken.for_user(user)
    return {
        "HTTP_AUTHORIZATION": f'Bearer {refresh.access_token}'
    }


class UserTestCase(APITestCase):
    # fixtures = ['user_fixtures.json']

    def setUp(self):
        self.simple_user = User.objects.get(email='finicacr7@gmail.com' )
        self.simple_user_refresh = RefreshToken.for_user(self.simple_user)

    def test_simple_user_access_token(self):
        # Simple user get access token
        data = {
            'email': self.simple_user.email,
            'password': 'string'
        }
        response = self.client.post(
            path='/users/login/',
            data=data,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_simple_user_refresh_token(self):
        # Simple user get refresh token
        data = {
            'refresh': str(self.simple_user_refresh)
        }
        response = self.client.post(
            path='/users/refresh/',
            data=data,
            **auth(self.simple_user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_simple_user_users_list(self):
        # Simple user get list of users
        response = self.client.get(
            path='/users/',
            **auth(self.simple_user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthorized_user_register_used_user_data(self):
        # Unauthorized user register new account with already used user data
        data = {
            'first_name': self.simple_user.first_name,
            'last_name': self.simple_user.last_name,
            'email': self.simple_user.email,
            'password': 'string'
        }
        response = self.client.post(
            path='/users/register/',
            data=data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthorized_user_register_new_user_data(self):
        # Unauthorized user register new account with new user data
        data = {
            'first_name': 'test_first_name',
            'last_name': 'test_last_name',
            'email': 'test@gmail.com',
            'password': '000000'
        }
        response = self.client.post(
            path='/users/register/',
            data=data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
