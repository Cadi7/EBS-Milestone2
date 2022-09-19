from django.contrib.auth import get_user_model
from django.db.models import Sum
from rest_framework import serializers

from apps.tasks.models import (
    Task,
    Comment, Timelog,
)

User = get_user_model()

__all__ = [
    'TaskSerializer',
    'TaskListSerializer',
    'TaskAssignNewUserSerializer',
    'TaskUpdateStatusSerializer',
    'CommentSerializer',
    'TimeLogSerializer',
    'TimeLogCreateSerializer',
    'TimeLogUserDetailSerializer',
    'TopTasksSerializer',
    'TaskTimeLogSerializer',
]


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        extra_kwargs = {
            'assigned': {'read_only': True},
        }


class TaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'title')


class TaskAssignNewUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('assigned',)


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


class TimeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timelog
        fields = '__all__'


class TimeLogCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timelog
        fields = '__all__'

        extra_kwargs = {
            'user': {'read_only': True},
            'task': {'read_only': True}
        }


class TimeLogUserDetailSerializer(serializers.ModelSerializer):
    total_time = serializers.DurationField(read_only=True)

    class Meta:
        model = Timelog
        fields = ('id', 'total_time', 'started_at', 'duration')
        extra_kwargs = {
            'started_at': {'read_only': True}
        }


class TopTasksSerializer(serializers.ModelSerializer):
    total_time = serializers.DurationField(read_only=True)

    class Meta:
        model = Task
        fields = ('id', 'title', 'total_time')
        extra_kwargs = {'total_time': {'read_only': True}}


class TaskTimeLogSerializer(serializers.ModelSerializer):
    time_logs = serializers.SerializerMethodField()

    @staticmethod
    def get_time_logs(task_id: int) -> int:
        return Timelog.objects.filter(
            task_id=task_id
        ).aggregate(
            Sum('duration')
        )['duration__sum'] or 0

    class Meta:
        model = Task
        fields = ('id', 'title', 'time_logs')
        extra_kwargs = {
            'time_logs': {'read_only': True}
        }
