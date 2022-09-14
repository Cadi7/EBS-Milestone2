from pathlib import Path
from typing import Union

from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.db import models
from django.db.models import QuerySet, Sum
from django.db.models.signals import post_save
from django.dispatch import receiver

User = settings.AUTH_USER_MODEL

__all__ = [
    'Task',
    'Comment',
]


class Task(models.Model):
    title = models.CharField(
        max_length=50,
    )
    description = models.TextField()
    status = models.BooleanField(
        default=False,
        verbose_name='Completed'
    )
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')

    class Meta:
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        ordering = ['id']

    def __str__(self):
        return self.title

    @staticmethod
    def send_user_email(message: str, subject: str, recipient: Union[QuerySet, set, str]) -> None:
        send_mail(
            message=message,
            subject=subject,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[recipient],
            fail_silently=False
        )


class Comment(models.Model):
    text = models.TextField()
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        null=True,
        related_name='comments'
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )

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
            user_email = Task.objects.filter(
                pk=instance.id
            ).select_related(
                'assigned_to'
            ).values_list(
                'assigned_to__email',
                flat=True
            )
            send_mail(
                message=f'Admin changed you task status to Undone!',
                subject=f'You have one undone Task. Id:{instance.id}',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=list(user_email),
                fail_silently=False
            )
