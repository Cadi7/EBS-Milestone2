import jwt
from django.contrib.auth.models import User
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from apps.tasks.models import Task
from apps.users.models import User
from apps.tasks.serializers import TaskSerializer, TaskShowSerializer, TaskSerializerID, TaskAssignSerializer


class TaskViewId(GenericAPIView):
    serializer_class = TaskSerializerID
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def get(self, request, pk):
        task = Task.objects.filter(id=pk).first()

        return Response(TaskSerializerID(task).data)


class AssignTaskView(GenericAPIView):
    serializer_class = TaskAssignSerializer
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def put(self, request):
        user = User.objects.filter(id=request.data['user']).first()
        task = Task.objects.filter(id=request.data['id']).first()
        task.user = user
        task.save()
        return Response(TaskSerializerID(task).data)


class MyTaskView(ListAPIView):
    serializer_class = TaskSerializerID
    permission_classes = (AllowAny,)
    authentication_classes = (SessionAuthentication, BasicAuthentication)

    def get_queryset(self):
        return Task.objects.all().filter(user=self.request.user.id)


class CompletedTaskView(ListAPIView):
    serializer_class = TaskSerializerID
    permission_classes = (AllowAny,)
    authentication_classes = (SessionAuthentication, BasicAuthentication)

    def get_queryset(self):
        return Task.objects.all().filter(user=self.request.user.id, status=True)


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
        serializer = TaskShowSerializer(tasks, many=True)
        return Response(serializer.data)

    @staticmethod
    def post(request):
        token = request.COOKIES.get()

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
        token = request.COOKIES.get()

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
