from typing import Union
from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.db.models import QuerySet, Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

__all__ = [
    'Task',
    'Comment',
    'Timelog',
]

User = settings.AUTH_USER_MODEL


class Task(models.Model):
    title = models.CharField(
        max_length=50,
    )
    description = models.TextField()
    status = models.BooleanField(
        default=False,
        verbose_name='Completed'
    )
    assigned = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks')

    class Meta:
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        ordering = ['id']

    def __str__(self):
        return self.title

    @staticmethod
    def send_user_email(message: str, subject: str, recipient: Union[QuerySet, set, str]) -> None:
        send_mail(message=message, subject=subject, from_email=settings.EMAIL_HOST_USER, recipient_list=[recipient], fail_silently=False)


class Comment(models.Model):
    text = models.TextField()
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name='comments')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ['id']

    def __str__(self):
        return f'{self.id}'


@receiver(post_save, sender=Task, dispatch_uid='send_email_user')
def send_email_user(sender, instance, **kwargs) -> None:
    change_data = kwargs['update_fields']
    status = instance.status
    if change_data is not None:
        if 'status' in change_data and status is False:
            user_email = Task.objects.filter(pk=instance.id).select_related('assigned_to').values_list('assigned_to__email', flat=True)
            send_mail(
                message=f'Admin changed you task status to Undone!',
                subject=f'You have one undone Task. Id:{instance.id}',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=list(user_email),
                fail_silently=False
            )


class TimeLogQuerySet(QuerySet):
    def with_total_time(self) -> 'TimeLogQuerySet':
        return self.aggregate(
            total_time=Sum('duration')
        )

    def get_total_duration_each_user(self):
        return self.values(
            'task__id', 'task__title',
        ).annotate(
            total_time=Sum('duration')
        )


class Timelog(models.Model):
    objects = TimeLogQuerySet.as_manager()

    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name='time_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='time_logs')
    started_at = models.DateTimeField(default=timezone.now, blank=True)
    is_started = models.BooleanField(default=False)
    is_stopped = models.BooleanField(default=False)
    duration = models.IntegerField(default=0, blank=True)

    @staticmethod
    def get_total_duration_by_user(user_id: int) -> int:
        return Timelog.objects.filter(
            task__assigned_id=user_id
        ).aggregate(
            Sum('duration')
        )['duration__sum'] or 0

    @staticmethod
    def get_total_duration_by_user_and_task(user_id: int, task_id: int) -> int:
        return Timelog.objects.filter(
            task__assigned_id=user_id,
            task_id=task_id
        ).aggregate(
            Sum('duration')
        )['duration__sum'] or 0

    @staticmethod
    def get_total_duration_by_user_and_task_and_date(user_id: int, task_id: int, date: str) -> int:
        return Timelog.objects.filter(
            task__assigned_id=user_id,
            task_id=task_id,
            start_time__date=date
        ).aggregate(
            Sum('duration')
        )['duration]sum'] or 0

    class Meta:
        verbose_name = 'Time Log'
        verbose_name_plural = 'Time Logs'
        ordering = ['id']

    def __str__(self):
        return f'{self.id}'
