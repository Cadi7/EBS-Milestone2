from django.contrib.auth.models import User
from drf_util.decorators import serialize_decorator
from rest_framework import viewsets, status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.tasks import serializers
from apps.tasks.models import Task, Comment
from apps.tasks.serializers import TaskSerializer, TaskAssignSerializer, \
    TaskSerializerComplete, CommentSerializer
from apps.users.models import User


class TaskView(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]

    def get_serializer_class(self):

        if self.action == 'assign':
            return serializers.TaskAssignSerializer
        elif self.action == 'my_tasks':
            return serializers.TaskSerializer
        elif self.action == 'completed_tasks':
            return serializers.TaskShowSerializer
        elif self.action == 'comments':
            return serializers.CommentSerializer
        elif self.action == 'create_comment':
            return serializers.CommentSerializer
        elif self.action == 'list':
            return serializers.TaskShowSerializer
        elif self.action == 'retrieve':
            return serializers.TaskShowSerializer
        return serializers.TaskSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, url_path=r'mytasks')
    def my_tasks(self, request):
        queryset = Task.objects.all().filter(user=self.request.user.id)
        serializer = TaskSerializer(queryset, many=True)

        return Response(serializer.data)

    @action(detail=False, url_path=r'completed')
    def completed_tasks(self, request):
        queryset = Task.objects.all().filter(status=True)
        serializer = TaskSerializer(queryset, many=True)

        return Response(serializer.data)

    @serialize_decorator(CommentSerializer)
    @action(detail=False, methods=['post'], url_path=r'comments')
    def comment_create(self, request):
        validated_data = request.serializer.validated_data
        comment = Comment.objects.create(
            comment=validated_data['comment'],
            task=validated_data['task'],
        )
        return Response(TaskSerializer(comment).data)

    @action(detail=False, methods=['get'], url_path=r'comments')
    def comments(self, request):
        queryset = Comment.objects.all()
        serializer = CommentSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['put'], url_path=r'assign')
    def assign(self, request, pk=None):
        task = Task.objects.get(id=request.data['id'])
        user = User.objects.get(id=request.data['user'])
        serializer = TaskAssignSerializer(task, data={"id": task.id, "user": request.data['user']})

        task.user = user
        task.save()
        return Response(serializer.data)


class CompleteTask(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Task.objects.all()
    serializer_class = TaskSerializerComplete
    authentication_classes = [SessionAuthentication, BasicAuthentication]

    @action(detail=True, methods=['put'])
    def complete(self, request, pk=None):
        task = Task.objects.get(id=pk)
        serializer = TaskSerializerComplete(task, data={"id": task.id, "status": True})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
