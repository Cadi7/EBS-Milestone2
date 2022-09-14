from django.contrib.auth import get_user_model
from django.template.defaultfilters import filesizeformat
from rest_framework import serializers

from apps.tasks.models import (
    Task,
    Comment,
)

User = get_user_model()

__all__ = [
    'TaskSerializer',
    'TaskListSerializer',
    'TaskAssignNewUserSerializer',
    'TaskUpdateStatusSerializer',
    'CommentSerializer',
]


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        extra_kwargs = {
            'assigned_to': {'read_only': True},
        }


class TaskListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ('id', 'title')


class TaskAssignNewUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('assigned_to',)


class TaskUpdateStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('status',)
        extra_kwargs = {
            'status': {'read_only': True}
        }


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        extra_kwargs = {
            'task': {'read_only': True},
            'owner': {'read_only': True}
        }
