import datetime
import jwt
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User, Task
from .serializers import UserSerializer, LoginSerializer, TaskSerializer


# Create your views here.
class RegisterView(GenericAPIView):
    allowed_methods = ["POST"]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class LoginView(GenericAPIView):
    allowed_methods = ["POST"]
    serializer_class = LoginSerializer

    @staticmethod
    def post(request, **kwargs):

        email = request.data['email']
        password = request.data['password']

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

        token = jwt.encode(payload, 'secret', algorithm='HS256').decode('utf-8')

        response = Response()

        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token
        }
        return response


class UsersView(GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    authentication_classes = ()
    allowed_methods = ["GET"]

    @staticmethod
    def get(request):
        users = User.objects.values_list('id', 'first_name', 'last_name')

        return Response(users)


class UserView(GenericAPIView):

    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)
        return Response(serializer.data)


class LogoutView(GenericAPIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success'
        }
        return response


class TaskViewId(GenericAPIView):
    serializer_class = TaskSerializer
    permission_classes = (AllowAny,)
    authentication_classes = ()
    allowed_methods = ["GET"]

    @staticmethod
    def get(request, pk):
        task = Task.objects.all().filter(id=pk)

        return Response(TaskSerializer(task).data)


class TaskView(GenericAPIView):
    serializer_class = TaskSerializer
    permission_classes = (AllowAny,)
    authentication_classes = ()
    allowed_methods = ["GET", "POST"]

    @staticmethod
    def get(request):

        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        user = User.objects.filter(id=payload['id']).first()
        tasks = Task.objects.all().filter(user=user)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    @staticmethod
    def post(request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        user = User.objects.filter(id=payload['id']).first()

        serializer = TaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)
        return Response(serializer.data)

    queryset = Task.objects.all()

    @staticmethod
    def put(request, pk):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        user = User.objects.filter(id=payload['id']).first()
        task = user.tasks.filter(id=pk).first()
        serializer = TaskSerializer(task, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
