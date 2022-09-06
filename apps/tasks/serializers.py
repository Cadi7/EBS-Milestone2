from rest_framework import serializers
from apps.tasks.models import Task, Comment


class TaskShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title']


class TaskSerializerID(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'user']


class TaskAssignSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)

    class Meta:
        model = Task
        fields = ['id', 'user']


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'created_at', 'updated_at', 'status', 'user']
        extra_kwargs = {
            'owner': {'write_only': True}
        }

    def create(self, validated_data):
        owner = validated_data.pop('owner', None)
        instance = self.Meta.model(**validated_data)
        if owner is not None:
            instance.owner = owner
        instance.save()
        return instance


class TaskSerializerComplete(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'status']

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'comment', 'task']

    def create(self, validated_data):
        task = validated_data.pop('task', None)
        instance = self.Meta.model(**validated_data)
        if task is not None:
            instance.task = task
        instance.save()
        return instance