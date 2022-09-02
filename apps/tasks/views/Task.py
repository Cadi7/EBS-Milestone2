import jwt
from django.contrib.auth.models import User
from drf_util.decorators import serialize_decorator
from rest_framework import viewsets, status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import GenericAPIView, ListAPIView, get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, ModelViewSet

from apps.tasks.models import Task
from apps.users.models import User
from apps.tasks.serializers import TaskSerializer, TaskShowSerializer, TaskSerializerID, TaskAssignSerializer


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


class ModifyOwner(viewsets.ViewSet):
    serializer_class = TaskAssignSerializer
    permission_classes = (AllowAny,)
    authentication_classes = (SessionAuthentication, BasicAuthentication)

    def update(self, request):
        user = User.objects.filter(id=request.data['user']).first()
        task = Task.objects.filter(id=request.data['id']).first()
        task.user = user
        task.save()
        return Response(TaskSerializerID(task).data)


class TaskView(ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = (AllowAny,)
    queryset = Task.objects.all()
    authentication_classes = [SessionAuthentication, BasicAuthentication]

    @serialize_decorator(TaskSerializer)
    def create(self, request):
        validated_data = request.serializer.validated_data

        task = Task.objects.create(
            title=validated_data['title'],
            description=validated_data['description'],
            status=validated_data['status'],
            user=User(id=request.user.id)
        )

        return Response(TaskSerializer(task).data)

    @staticmethod
    def list(request, **kwargs):
        tasks = Task.objects.all()
        return Response(TaskShowSerializer(tasks, many=True).data)

    @staticmethod
    def retrieve(request, pk=None, **kwargs):
        task = get_object_or_404(Task, pk=pk)
        return Response(TaskSerializerID(task).data)

    @staticmethod
    def destroy(request, pk=None, **kwargs):
        task = get_object_or_404(Task, pk=pk)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
