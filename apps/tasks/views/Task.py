import jwt
from django.contrib.auth.models import User
from drf_util.decorators import serialize_decorator
from rest_framework import viewsets, status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed

from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.tasks.models import Task, Comment
from apps.users.models import User
from apps.tasks.serializers import TaskSerializer, TaskShowSerializer, TaskSerializerID, TaskAssignSerializer, \
    TaskSerializerComplete, CommentSerializer


class MyTaskView(viewsets.ViewSet):
    serializer_class = TaskSerializerID
    permission_classes = (AllowAny,)
    queryset = Task.objects.all()
    authentication_classes = (SessionAuthentication, BasicAuthentication)

    def list(self):
        return Task.objects.all().filter(user=self.request.user.id)


class CompletedTaskView(viewsets.ViewSet):
    serializer_class = TaskSerializerID
    permission_classes = (AllowAny,)
    queryset = Task.objects.all().filter(status=True)
    authentication_classes = (SessionAuthentication, BasicAuthentication)

    def get_object(self):
        obj = get_object_or_404(pk=self.request.GET.get('pk'))
        return obj

    @staticmethod
    def list(pk=None):
        queryset = Task.objects.all().filter(status=True)
        serializer = TaskSerializerID(queryset, many=True)
        return Response(serializer.data)


class UpdateOwner(viewsets.ViewSet):
    queryset = Task.objects.all()

    def get_object(self):
        serializer_class = TaskAssignSerializer
        permission_classes = (AllowAny,)
        authentication_classes = ()
        obj = get_object_or_404(pk=self.request.GET.get('pk'))
        return obj


@action(detail=True, methods=['put'])
def assign(request):
    user = User.objects.filter(id=request.data['user']).first()
    task = Task.objects.filter(id=request.data['id']).first()
    task.user = user
    task.save()
    return Response(TaskSerializerID(task), status=status.HTTP_200_OK)


class CompleteTask(viewsets.ViewSet):
    serializer_class = TaskSerializerComplete
    permission_classes = (AllowAny,)
    authentication_classes = (SessionAuthentication, BasicAuthentication)

    @action(detail=True, methods=['put'])
    def complete(self, request, pk=None):
        task = Task.objects.get(id=pk)
        serializer_class = TaskSerializerComplete
        serializer = TaskSerializerComplete(task, data={"id": task.id, "status": True})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class TaskView(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = (AllowAny,)
    queryset = Task.objects.all()
    authentication_classes = [SessionAuthentication, BasicAuthentication]

    @serialize_decorator(TaskSerializer)
    def create(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        validated_data = request.serializer.validated_data
        task = Task.objects.create(
            title=validated_data['title'],
            description=validated_data['description'],
            status=validated_data['status'],
            user=User.objects.filter(id=payload['id']).first()
        )

        return Response(TaskSerializer(task).data)

    def list(self, request, **kwargs):
        queryset = Task.objects.all()
        serializer = TaskShowSerializer(queryset, many=True)
        return Response(serializer.data)

    @staticmethod
    def retrieve(request, pk=None, **kwargs):
        task = get_object_or_404(Task, pk=pk)
        return Response(TaskSerializerID(task).data)

    def destroy(self, pk=None, **kwargs):
        task = get_object_or_404(Task, pk=pk)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentToTask(viewsets.ViewSet):
    serializer_class = CommentSerializer
    permission_classes = (AllowAny,)
    queryset = Comment.objects.all()
    authentication_classes = (SessionAuthentication, BasicAuthentication)

    def get_object(self):
        obj = get_object_or_404(pk=self.request.GET.get('pk'))
        return obj

    @staticmethod
    def create(request, pk=None):
        validated_data = request.serializer.validated_data
        comment = Comment.objects.create(
            comment=validated_data['comment'],
            task=validated_data['task'],
        )
        return Response(TaskSerializer(comment).data)
