import datetime
import coverage

import time

from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.test import APITestCase

from apps.tasks.models import Task, Comment, Timelog
from apps.users.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class TasksTests(APITestCase):
    fixtures = ['tasks_fixtures.json', 'users_fixtures.json', 'comments_fixtures.json', 'timelogs_fixtures.json']

    def test_access_token(self):
        email = "finicacr7@gmail.com"
        password = "1234"
        self.user = User.objects.create_user(email, email, password)
        jwt_fetch_data = {
            'email': email,
            'password': password
        }

        response = self.client.post('/users/login/', jwt_fetch_data, 'json')
        token = get_tokens_for_user(self.user).get('access')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_create_task(self):
        self.test_access_token()
        data = {
            "title": "string",
            "description": "string",
            "status": False,
        }
        response = self.client.post('/tasks/', data, 'json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_all_tasks(self):
        self.test_access_token()
        response = self.client.get('/tasks/', data={'format': 'json'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_my_task(self):
        self.test_access_token()
        response = self.client.get('/tasks/my_task/', data={'format': 'json'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_completed_tasks(self):
        self.test_access_token()
        response = self.client.get('/tasks/completed_tasks/', data={'format': 'json'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_task(self):
        self.test_access_token()
        data = {
            "title": "string",
            "description": "string",
            "status": False
        }

        response = self.client.post('/tasks/', data, 'json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        response = self.client.post('/tasks/', data, 'json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        response = self.client.get('/tasks/1/', data={'format': 'json'})
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_assign_task(self):
        self.test_create_task()

        data = {
            "first_name": "Ciocalau",
            "last_name": "Marin",
            "email": "cadihack7@gmail.com",
            "password": "string"
        }

        response = self.client.post('/users/register/', data, format='json')
        self.assertEqual(response.status_code, HTTP_200_OK)
        data = {
            'assigned': 1
        }
        response = self.client.patch('/tasks/1/assign/', data, 'json')
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_complete_task(self):
        self.test_access_token()

        data = {
            "title": "stringstring",
            "description": "string",
            "status": False
        }

        response = self.client.post('/tasks/', data, 'json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        response_json = response.json()
        completed = response_json.get('status')
        self.assertEqual(completed, False)

        response = self.client.get('/tasks/1/update/')
        self.assertEqual(response.status_code, HTTP_200_OK)
        task = Task.objects.get(id=1)
        self.assertEqual(task.status, True)

    def test_delete_task(self):
        self.test_access_token()
        data = {
            "title": "string",
            "description": "string",
            "status": False
        }

        response = self.client.post('/tasks/', data, 'json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        response = self.client.delete('/tasks/1/')
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)


class CommentTest(APITestCase):
    fixtures = ['tasks_fixtures.json', 'users_fixtures.json', 'comments_fixtures.json']

    def test_access_token(self):
        email = "cristianfnc7@gmail.com"
        password = "1234"
        self.user = User.objects.create_user(email, email, password)
        jwt_fetch_data = {
            'email': email,
            'password': password
        }

        response = self.client.post('/users/login/', jwt_fetch_data, 'json')
        token = get_tokens_for_user(self.user).get('access')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_create_task(self):
        self.test_access_token()
        data = {
            "title": "string",
            "description": "string",
            "status": True
        }
        response = self.client.post('/tasks/', data, 'json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_post_comment(self):
        self.test_create_task()

        data = {
            "text": "string"
        }

        response = self.client.post('/tasks/1/comments/', data, 'json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_get_comments(self):
        self.test_post_comment()

        response = self.client.get('/tasks/1/comments/', data={'format': 'json'})
        self.assertEqual(response.status_code, HTTP_200_OK)


class TimeLogsTests(APITestCase):
    fixtures = ['tasks_fixtures.json', 'users_fixtures.json', 'timelogs_fixtures.json']

    def test_access_token(self):
        email = "krystiano@mail.ru"
        password = "1234"
        self.user = User.objects.create_user(email, email, password)
        jwt_fetch_data = {
            'email': email,
            'password': password
        }

        response = self.client.post('/users/login/', jwt_fetch_data, 'json')
        token = get_tokens_for_user(self.user).get('access')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_create_task(self):
        self.test_access_token()
        data = {
            "title": "string",
            "description": "string",
            "status": False,
        }
        response = self.client.post('/tasks/', data, 'json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_manual_time_log(self):
        self.test_create_task()

        data = {
            "started_at": "2022-03-01T12:34:05.705Z",
            "duration": 2
        }

        response = self.client.post('/tasks/1/timelogs/', data, 'json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_top_task_by_last_month(self):
        self.test_create_task()

        time.sleep(1)

        response = self.client.get('/timelogs/top20/')
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_timelogs_last_month(self):
        self.test_create_task()

        time.sleep(1)

        response = self.client.get('/timelogs/time_logs_month/')
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_timelogs_summary(self):
        self.test_create_task()

        response = self.client.get('/tasks/1/timelogs/summary/')
        self.assertEqual(response.status_code, HTTP_200_OK)
