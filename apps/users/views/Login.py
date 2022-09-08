import datetime
import jwt
from rest_framework import mixins, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from validate_email import validate_email

from apps.users import serializers
from apps.users.models import User
from apps.users.serializers import ShortUserSerializer, LoginSerializer


class RegisterView(mixins.RetrieveModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):
    serializer_class = ShortUserSerializer
    queryset = User.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'register':
            return serializers.UserSerializer
        elif self.action == 'login':
            return serializers.LoginSerializer
        elif self.action == 'list':
            return serializers.ShortUserSerializer
        return serializers.UserSerializer

    @action(detail=False, methods=['post'], url_path=r'register')
    def register(self, request):
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        email = request.data.get('email')
        password = request.data.get('password')
        if not validate_email(email):
            raise AuthenticationFailed('Email is invalid!')

        if User.objects.filter(email=email).exists():
            raise AuthenticationFailed('Email is already in use!')

        user = User.objects.create_user(first_name=first_name, last_name=last_name, email=email, password=password)
        user.save()

        return Response(self.serializer_class(user).data, status=201)

    @action(detail=False, methods=['post'], url_path=r'login')
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')
        token = Token.objects.get_or_create(user=user)

        return Response({'token': token[0].key}, status=200)

    def logout(request):
        response = Response()

        response.delete_cookie('token')
        response.data = {
            'message': 'success'
        }

        return response
