from typing import Union
from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.db.models import QuerySet
from django.utils import timezone

__all__ = [
    "Task",
    "Comment",
    "Timelog",
]

from apps.users.models import User


class Task(models.Model):
    title = models.CharField(
        max_length=50,
    )
    description = models.TextField()
    status = models.BooleanField(default=False, verbose_name="Completed")
    assigned = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="assigned_tasks"
    )

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    @staticmethod
    def send_user_email(
        message: str, subject: str, recipient: Union[QuerySet, set, str]
    ) -> None:
        send_mail(
            message=message,
            subject=subject,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[recipient],
            fail_silently=False,
        )


class Comment(models.Model):
    text = models.TextField()
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, null=True, related_name="comment_task"
    )
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comment_owner"
    )

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    @staticmethod
    def send_user_email(
        message: str, subject: str, recipient: Union[QuerySet, set, str]
    ) -> None:
        send_mail(
            message=message,
            subject=subject,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[recipient],
            fail_silently=False,
        )


class Timelog(models.Model):
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, null=True, related_name="task_logs"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, related_name="user_logs"
    )
    started_at = models.DateTimeField(default=timezone.now, blank=True)
    is_started = models.BooleanField(default=False)
    is_stopped = models.BooleanField(default=False)
    duration = models.IntegerField(default=0, blank=True)

    class Meta:
        verbose_name = "Time Log"
        verbose_name_plural = "Time Logs"
