from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.tasks.models import (
    Task,
    Comment,
)
from apps.tasks.serializers import (
    TaskSerializer,
    TaskListSerializer,
    TaskAssignNewUserSerializer,
    TaskUpdateStatusSerializer,
    CommentSerializer,
)
from config import settings
from config.settings import EMAIL_HOST_USER

User = get_user_model()

__all__ = [
    'TaskViewSet',
    'TaskCommentViewSet',
]


class TaskViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
    GenericViewSet
):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]
    filter_backends = [filters.SearchFilter]
    # filterset_fields = ['status']
    search_fields = ['title']

    def perform_create(self, serializer):
        serializer.save(assigned_to=[self.request.user])

    def get_serializer_class(self):
        if self.action == 'list':
            return TaskListSerializer
        return super(TaskViewSet, self).get_serializer_class()

    @action(
        methods=['get'],
        url_path='my_task',
        detail=False,
        serializer_class=TaskListSerializer
    )
    def my_task(self, request, *args, **kwargs):
        queryset = self.queryset.filter(
            assigned_to=request.user
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        methods=['get'],
        url_path='completed_tasks',
        detail=False,
        serializer_class=TaskListSerializer
    )
    def complete_task(self, request, *args, **kwargs):
        queryset = self.queryset.filter(
            status=True
        )
        serializer = self.get_serializer(
            queryset,
            many=True
        )
        return Response(serializer.data)

    @action(
        methods=['patch'],
        detail=True,
        url_path='assign',
        serializer_class=TaskAssignNewUserSerializer
    )
    def assign(self, request, *args, **kwargs):
        instance: Task = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data
        )
        serializer.is_valid(
            raise_exception=True
        )
        serializer.save()
        user_email: str = request.task.assigned_to.email
        print(user_email)
        instance.send_user_email(
            subject=f'Task with id:{instance.id} is assigned to you',
            message='Task assign to you',
            recipient=user_email
        )
        return Response(status=status.HTTP_200_OK)

    @action(
        methods=['get'],
        detail=True,
        url_path='update',
        serializer_class=TaskUpdateStatusSerializer
    )
    def update_status(self, request, *args, **kwargs):
        instance: Task = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data
        )
        serializer.is_valid(
            raise_exception=True
        )
        serializer.save(
            status=True
        )
        user_email: str = self.request.user.email
        if user_email:
            instance.send_user_email(
                message='commented task is completed',
                subject='commented task is completed',
                recipient=user_email
            )
        return Response(status=status.HTTP_200_OK)

    @classmethod
    def send_task_assigned_email(cls, task_id, recipient):
        send_mail('Task is assigned',
                  f'Task {task_id} is assigned to you',
                  settings.EMAIL_HOST_USER, [recipient], fail_silently=False)


class TaskCommentViewSet(
    ListModelMixin,
    CreateModelMixin,
    GenericViewSet
):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]

    def list(self, request, *args, **kwargs):
        task_id: int = self.kwargs.get(
            'task__pk'
        )
        queryset = self.queryset.filter(
            task_id=task_id
        )
        serializer = self.get_serializer(
            queryset,
            many=True
        )
        return Response(serializer.data)

    def perform_create(self, serializer):
        task_id: int = self.kwargs.get(
            'task__pk'
        )
        instance: Comment = serializer.save(
            owner=self.request.user,
            task_id=task_id
        )
        user_email: str = self.request.user.email
        instance.task.send_user_email(
            message=f'You task with id:{task_id} is commented',
            subject='Your task is commented',
            recipient=user_email
        )
