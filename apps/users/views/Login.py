import datetime

import jwt
from django.contrib.auth.models import User
from validate_email import validate_email
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from apps.users.models import User
from apps.users.serializers import LoginSerializer


class LoginView(GenericAPIView):
    allowed_methods = ["POST"]
    serializer_class = LoginSerializer

    def post(self, request, **kwargs):

        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if validate_email(email) is False:
            raise AuthenticationFailed('Invalid email!')

        if user is None:
            raise AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256').decode('utf-8')

        response = Response()

        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token
        }
        return response


class LogoutView(GenericAPIView):
    allowed_methods = ["POST"]

    def post(self, request, **kwargs):

        response = Response()

        response.delete_cookie(key='jwt')
        response.data = {
            'message': 'Logout successful!'
        }
        return response