import datetime

import jwt
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from validate_email import validate_email
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from apps.users.models import User
from apps.users.serializers import LoginSerializer, UserSerializer


class RegisterView(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    @action(detail=False, methods=['post'], url_path=r'register')
    def register(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        if not validate_email(email):
            raise AuthenticationFailed('Email is invalid!')

        if User.objects.filter(email=email).exists():
            raise AuthenticationFailed('Email is already in use!')

        user = User.objects.create_user(email=email, password=password)
        user.save()

        return Response(self.serializer_class(user).data, status=201)

    serializer_class = LoginSerializer
    permission_classes = (AllowAny,)

    @action(detail=False, methods=['post'], url_path=r'login')
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')

        response = Response()

        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token
        }

        return response

    @staticmethod
    def logout(request):
        response = Response()

        response.delete_cookie('jwt')
        response.data = {
            'message': 'success'
        }

        return response


