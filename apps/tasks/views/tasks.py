from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db.models import Sum
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
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

from apps.tasks.models import (
    Task,
    Comment,
    Timelog,
)
from apps.tasks.serializers import (
    TaskSerializer,
    TaskListSerializer,
    TaskAssignNewUserSerializer,
    TaskUpdateStatusSerializer,
    CommentSerializer,
    TimeLogSerializer,
    TimeLogCreateSerializer,
    TimeLogUserDetailSerializer,
    TopTasksSerializer,
    TaskTimeLogSerializer,
)
from config import settings
from config.settings import EMAIL_HOST_USER

User = get_user_model()

__all__ = [
    "TaskViewSet",
    "TaskCommentViewSet",
    "TaskTimeLogViewSet",
    "TimeLogViewSet",
]


class TaskViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    queryset = Task.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskSerializer
    search_fields = ["title"]

    def get_serializer_class(self):
        if self.action == "list":
            return TaskTimeLogSerializer
        if self.action == "assign":
            return TaskAssignNewUserSerializer
        if self.action == "create":
            return TaskSerializer
        if self.action == "update_status":
            return TaskUpdateStatusSerializer
        if self.action == "retrieve":
            return TaskSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        if self.action == "my_task":
            return Task.objects.filter(assigned=self.request.user)
        if self.action == "list":
            return Task.objects.annotate(time_logs=Sum("task_logs__duration"))
        return Task.objects.all()

    def perform_create(self, serializer):
        serializer.save(assigned_id=self.request.user.id)

    @action(
        methods=["get"],
        url_path="my-tasks",
        detail=False,
        serializer_class=TaskListSerializer,
    )
    def my_task(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["get"],
        url_path="completed-tasks",
        detail=False,
        serializer_class=TaskListSerializer,
    )
    def completed_tasks(self, request, *args, **kwargs):
        queryset = self.queryset.filter(status=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["patch"], detail=True, url_path="assign")
    def assign(self, request, *args, **kwargs):
        instance: Task = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            user_email: str = instance.assigned.email
            instance.send_user_email(
                subject=f"Task with id:{instance.id} and title: {instance.title} is assigned to you",
                message="Task assign to you, please check your task list",
                recipient=user_email,
            )
            serializer.save()
            return Response(
                {"detail ": "Task assigned successfully and email was send."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["patch"],
        detail=True,
        url_path="update",
        serializer_class=TaskUpdateStatusSerializer,
    )
    def update_status(self, request, pk):
        try:
            task = Task.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(
                {"detail": "This task doesn't exist"}, status=status.HTTP_404_NOT_FOUND
            )
        else:
            task.status = True
            task.save()

            task.comment_task.values_list("owner__email", flat=True)
            emails = [
                email
                for email in task.comment_task.values_list("owner__email", flat=True)
            ]
            emails.append(task.assigned.email)
            emails = list(set(emails))
            send_mail(
                "Task Completed",
                "The task where you added a comment is completed - " + task.title,
                EMAIL_HOST_USER,
                emails,
            )
            return Response(
                {"detail ": "Task has been completed and email was send."},
                status=status.HTTP_200_OK,
            )


class TaskCommentViewSet(CreateModelMixin, GenericViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(task_id=kwargs["task_pk"])
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        task_id = self.kwargs.get("task_pk")
        task_title = Task.objects.get(id=task_id).title
        serializer.save(owner_id=self.request.user.id, task_id=task_id)
        instance = serializer.instance
        instance.send_user_email(
            subject=f"New comment on task with id:{task_id} and title {task_title}",
            message="New comment on task",
            recipient=instance.owner.email,
        )
        return Response(
            {"detail ": "Comment has been posted! Email was send to owner"},
            status=status.HTTP_200_OK,
        )


class TaskTimeLogViewSet(CreateModelMixin, GenericViewSet):
    queryset = Timelog.objects.all()
    serializer_class = TimeLogSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return TimeLogCreateSerializer
        if self.action == "list":
            return TimeLogUserDetailSerializer
        return super().get_serializer_class()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(task_id=kwargs["task_pk"])
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        task_id = self.kwargs.get("task_pk")
        serializer.save(
            task_id=task_id, user=self.request.user, is_started=True, is_stopped=True
        )

    @action(methods=["post"], url_path="start", detail=False)
    def start(self, request, *args, **kwargs):
        task_id = self.kwargs.get("task_pk")
        existing_unstopped_timelog: Timelog = self.queryset.filter(
            task_id=task_id,
            user=self.request.user,
            duration=0,
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
            return Response(
                {"Detail: ": "Timelog has been started"}, status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"Detail: ": "Timelog has been already started"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(methods=["post"], url_path="stop", detail=False)
    def stop(self, request, *args, **kwargs):
        task_id = self.kwargs.get("task_pk")
        instance: Timelog = self.queryset.filter(
            task_id=task_id,
            is_started=True,
            is_stopped=False,
            duration=0,
            user=self.request.user,
        ).first()
        if instance:
            instance.duration = duration = int(
                (timezone.now() - instance.started_at).total_seconds() / 60
            )
            instance.is_stopped = True
            instance.is_started = False
            instance.save()
            return Response(
                {"Detail: ": "Timelog has been stopped", f"Duration": {duration}},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"Detail: ": "Timelog has been already stopped"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(methods=["get"], url_path="summary", detail=False)
    def summary(self, request, *args, **kwargs):
        task_id = self.kwargs.get("task_pk")
        queryset = self.queryset.filter(task_id=task_id).aggregate(
            total_time=Sum("duration")
        )
        return Response(
            {
                "Detail: ": "Total time spent on this task",
                "Total time": queryset["total_time"],
            },
            status=status.HTTP_200_OK,
        )


class TimeLogViewSet(ListModelMixin, GenericViewSet):
    serializer_class = TimeLogSerializer
    queryset = Timelog.objects.all()

    def get_queryset(self):
        if self.action == "top_20":
            last_month = timezone.now() - timezone.timedelta(days=timezone.now().day)
            return (
                self.queryset.filter(started_at__gt=last_month)
                .annotate(total_time=Sum("duration"))
                .order_by("-total_time")[:20]
            )
        if self.action == "list":
            return Timelog.objects.all()
        return super().get_queryset()

    def get_serializer_class(self):
        if self.action == "list":
            return TimeLogSerializer
        if self.action == "top_20":
            return TopTasksSerializer
        return super().get_serializer_class()

    @method_decorator(cache_page(60))
    @action(
        methods=["get"],
        url_path="top-20",
        detail=False,
        serializer_class=TopTasksSerializer,
    )
    def top_20(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        return Response(
            queryset.values("task_id", "task__title").annotate(
                total_time=Sum("duration")
            ),
            status=status.HTTP_200_OK,
        )

    @action(methods=["get"], url_path="month", detail=False)
    def month(self, request):
        last_month = timezone.now() - timezone.timedelta(days=timezone.now().day)
        queryset = Timelog.objects.filter(
            started_at__gt=last_month, user=request.user.id
        ).aggregate(sum=Sum("duration"))

        return Response({"logged_time": queryset.values()}, status=status.HTTP_200_OK)
