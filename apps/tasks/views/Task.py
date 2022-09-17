from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Sum
from django.utils import timezone
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
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
    Comment, Timelog,
)
from apps.tasks.serializers import (
    TaskSerializer,
    TaskListSerializer,
    TaskAssignNewUserSerializer,
    TaskUpdateStatusSerializer,
    CommentSerializer, TimeLogSerializer, TimeLogCreateSerializer,
    TimeLogUserDetailSerializer,
)
from config import settings
from config.settings import EMAIL_HOST_USER

User = get_user_model()

__all__ = [
    'TaskViewSet',
    'TaskCommentViewSet',
    'TaskTimeLogViewSet',
    'TimeLogViewSet',
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
        serializer.save(assigned_id=self.request.user.id)

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
            assigned=request.user.id
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
        user_email: str = instance.assigned.email
        print(user_email)
        instance.send_user_email(
            subject=f'Task with id:{instance.id} and title: {instance.title} is assigned to you',
            message='Task assign to you, please check your task list',
            recipient=user_email
        )
        return Response(status=status.HTTP_200_OK)

    @action(
        methods=['get'],
        detail=True,
        url_path='update',
        serializer_class=TaskUpdateStatusSerializer
    )
    def update_status(self, request, *args, pk=None, **kwargs):
        task = Task.objects.get(id=pk)
        task.status = True
        serializer = TaskUpdateStatusSerializer(task, data={"id": task.id, "status": True})

        if serializer.is_valid():
            queryset = Comment.objects.all().filter(task_id=pk)

            emails = []
            for com in queryset:
                if com.owner.email not in emails:
                    emails.append(com.owner.email)
            send_mail("Task Completed", "The task where you added a comment is completed - " + task.title,
                      EMAIL_HOST_USER, emails)

            serializer.save()

            return Response("Task completed", status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


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
        task_id = self.kwargs.get('task_pk')
        task_title = Task.objects.get(id=task_id).title
        serializer.save(owner_id=self.request.user.id, task_id=task_id)
        self.send_task_created_email(task_id, task_title, recipient=self.request.user.email)

    @classmethod
    def send_task_created_email(cls, task_id, task_title, recipient):
        send_mail('Your task is commented',
                  f'Your task with id {task_id} and title' + task_title + 'is commented',
                  settings.EMAIL_HOST_USER, [recipient], fail_silently=False)


class TimeLogSummarySerializer:
    def __init__(self, user_id, total_time):
        self.user_id = user_id
        self.total_time = total_time


class TaskTimeLogViewSet(
    ListModelMixin,
    CreateModelMixin,
    GenericViewSet
):
    queryset = Timelog.objects.all()
    serializer_class = TimeLogSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == 'create':
            return TimeLogCreateSerializer
        return super(TaskTimeLogViewSet, self).get_serializer_class()

    def list(self, request, *args, **kwargs):
        task_id = self.kwargs.get('task_pk')
        queryset = self.get_queryset(
        ).filter(
            task_id=task_id
        )
        serializer = self.get_serializer(
            queryset,
            many=True
        )
        return Response(serializer.data)

    def perform_create(self, serializer):
        task_id = self.kwargs.get('task_pk')
        print(task_id)
        serializer.save(
            task_id=task_id,
            user=self.request.user,
            is_started=True,
            is_stopped=True,
        )

    @action(
        methods=['post'],
        url_path='start',
        detail=False
    )
    def start(self, request, *args, **kwargs):
        task_id = self.kwargs.get('task_pk')
        existing_unstopped_timelog: Timelog = self.queryset.filter(
            task_id=task_id,
            user=self.request.user,
            duration=None,
            is_started=True,
            is_stopped=False,
        ).last()
        if not existing_unstopped_timelog:
            self.queryset.create(
                task_id=task_id,
                user=self.request.user,
                started_at=timezone.now(),
                is_started=True,
                is_stopped=False,
            )
            return Response(status=status.HTTP_201_CREATED)
        else:
            raise NotFound('You have some unstopped tasks')

    @action(
        methods=['post'],
        url_path='stop',
        detail=False
    )
    def stop(self, request, *args, **kwargs):
        task_id = self.kwargs.get('task_pk')
        instance: Timelog = self.queryset.filter(
            task_id=task_id,
            is_started=True,
            is_stopped=False,
            duration=None,
            user=self.request.user
        ).first()
        if instance:
            instance.duration = timezone.now() - instance.started_at
            instance.is_stopped = True
            instance.is_started = False
            instance.save()
            return Response(status=status.HTTP_200_OK)
        else:
            raise NotFound("You don't have started time logs")

    @action(
        methods=['get'],
        url_path='summary',
        detail=False)
    def summary(self, request, *args, **kwargs):
        task_id = self.kwargs.get('task_pk')
        queryset = self.queryset.filter(
            task_id=task_id
        )
        serializer = TimeLogSummarySerializer(queryset.first().user.id, queryset.aggregate(Sum('duration')))
        return Response(serializer.__dict__)


class TimeLogViewSet(
    ListModelMixin,
    GenericViewSet
):
    queryset = Timelog.objects.all()
    serializer_class = TimeLogUserDetailSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)
    filter_backends = [filters.OrderingFilter]
    ordering = ['-duration']

    @action(
        methods=['get'],
        detail=False,
        url_path='time_logs_month'
    )
    def time_log_month(self, request, *args, **kwargs):
        queryset = self.queryset.filter(
            user=self.request.user,
            started_at__month=timezone.now().strftime('%m'),
        )
        return Response(
            queryset.with_total_time()
        )

    @action(
        methods=['get'],
        detail=False,
        url_path='top20',
        serializer_class=TimeLogSerializer
    )
    def top20(self, request, *args, **kwargs):
        queryset = self.queryset.filter(
            user=self.request.user,
            started_at__month=timezone.now().strftime('%m'),
        ).order_by('-duration')[:20]
        return Response(
            queryset
        )
