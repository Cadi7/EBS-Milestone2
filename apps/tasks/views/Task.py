from django_filters.rest_framework import DjangoFilterBackend
from drf_util.decorators import serialize_decorator
from rest_framework import viewsets, status, filters, mixins
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.tasks import serializers
from django.core.mail import send_mail
from apps.tasks.models import Task, Comment
from apps.tasks.serializers import TaskSerializer, TaskAssignSerializer, \
    TaskSerializerComplete, CommentSerializer
from apps.users.models import User
from config import settings


class TaskView(mixins.RetrieveModelMixin,
               mixins.DestroyModelMixin,
               mixins.ListModelMixin,
               mixins.UpdateModelMixin,
               GenericViewSet,
               filters.SearchFilter, ):
    queryset = Task.objects.all()
    authentication_classes = [JWTAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status']
    search_fields = ['title']

    def get_permissions(self):
        if self.action in ('create', 'list', 'retrieve', 'update'):
            self.permission_classes = [IsAuthenticated]
        return super(TaskView, self).get_permissions()

    def get_serializer_class(self):

        if self.action == 'assign':
            return serializers.TaskAssignSerializer
        elif self.action == 'my_tasks':
            return serializers.TaskSerializer
        elif self.action == 'completed_tasks':
            return serializers.TaskShowSerializer
        elif self.action == 'list':
            return serializers.TaskShowSerializer
        elif self.action == 'retrieve':
            return serializers.TaskShowSerializer
        elif self.action == 'create':
            return serializers.TaskSerializer
        elif self.action == 'task_create':
            return serializers.TaskSerializer
        elif self.action == 'complete':
            return serializers.TaskSerializerComplete
        return serializers.TaskShowSerializer

    @serialize_decorator(TaskSerializer)
    @action(detail=False, methods=['post'], url_path=r'add')
    def task_create(self, request):
        validated_data = request.serializer.validated_data
        task = Task.objects.create(
            title=validated_data['title'],
            description=validated_data['description'],
            user=self.request.user,
        )
        return Response(TaskSerializer(task).data)

    @action(detail=False, methods=['get'], url_path=r'mytasks')
    def my_tasks(self, request):
        queryset = Task.objects.all().filter(user=self.request.user.id)
        serializer = TaskSerializer(queryset, many=True)

        return Response(serializer.data)

    @action(detail=False, url_path=r'completed')
    def completed_tasks(self, request):
        queryset = Task.objects.all().filter(status=True)
        serializer = TaskSerializer(queryset, many=True)

        return Response(serializer.data)

    @action(detail=True, methods=['put'])
    def complete(self, request, pk=None):
        task = Task.objects.get(id=pk)
        instance = self.get_object()
        serializer = TaskSerializerComplete(task, data={"id": task.id, "status": True})
        self.send_task_completed_email(instance.id, instance.user.email)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['patch'], detail=True, url_path='assign', permission_classes=[IsAuthenticated])
    def assign(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance.assigned_to = serializer.validated_data.get('assigned_to')
        instance.save()
        self.send_task_assigned_email(instance.id, instance.assigned_to.email)
        return Response(status=status.HTTP_200_OK)

    @classmethod
    def send_task_completed_email(cls, task_id, recipient):
        send_mail('Task is completed',
                  f'Task {task_id} is completed',
                  settings.EMAIL_HOST_USER, [recipient], fail_silently=False)

    @classmethod
    def send_task_assigned_email(cls, task_id, recipient):
        send_mail('Task is assigned',
                  f'Task {task_id} is assigned to you',
                  settings.EMAIL_HOST_USER, [recipient], fail_silently=False)


class CommentView(mixins.RetrieveModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.ListModelMixin,
                  GenericViewSet,
                  filters.SearchFilter, ):
    queryset = Comment.objects.all()
    authentication_classes = [JWTAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['title']
    serializer_class = CommentSerializer

    @serialize_decorator(CommentSerializer)
    @action(detail=False, methods=['post'], url_path=r'comments/add')
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

    @action(detail=True, methods=['get'], url_path=r'comments')
    def comment(self, request, pk=None):
        queryset = Comment.objects.all().filter(task=self.kwargs['pk'])
        serializer = CommentSerializer(queryset, many=True)
        return Response(serializer.data)
