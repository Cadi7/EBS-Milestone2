from rest_framework.test import APITestCase, APIRequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.test import force_authenticate


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def force_authenticate_request(request, user):
    factory = APIRequestFactory()
    user = User.objects.get(email='finicacr7@gmail.com', password='1234')

    # Make an authenticated request to the view...
    request = factory.get('/users/register')
    force_authenticate(request, user=user, token=user.auth_token)


def auth(user):
    refresh = RefreshToken.for_user(user)
    return {
        "HTTP_AUTHORIZATION": f'Bearer {refresh.access_token}'
    }


def setUp(self):
    self.email = 'finicacr7@gmail.com'
    self.password = '1234'
    self.simple_user = User.objects.create_user(self.email, self.email, self.password)
    self.simple_user.save()

    class AccountTests(APITestCase):
        def test_user_register(self):
            data = {
                "first_name": "string",
                "last_name": "string",
                "username": "string",
                "email": "faer.faer.2006@mail.ru",
                "password": "string"
            }

            response = self.client.post('/users/register/', data, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        def test_create_access_token(self):
            """Create a user"""

            username = "finicacr7@gmail.com"
            password = "1234"
            self.user = User.objects.create_user(username, username, password)
            jwt_fetch_data = {
                'username': username,
                'password': password
            }

            response = self.client.post('/users/login/', jwt_fetch_data, 'json')

            """Test access token"""

            token = get_tokens_for_user(self.user).get('access')
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

            """Test refresh token"""

            self.refresh_token = response.data['refresh']

            data = {
                'refresh': self.refresh_token
            }
            response = self.client.post('/user/refresh/', data, 'json')
            access_token = get_tokens_for_user(self.user).get('access')
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        def test_get_all_users(self):
            response = self.client.get('/users/', data={'format': 'json'})
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
