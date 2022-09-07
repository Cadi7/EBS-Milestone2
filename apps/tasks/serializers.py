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
    title = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'created_at', 'updated_at', 'status', 'user']

    def create(self, validated_data):
        user = validated_data.pop('owner', None)
        instance = self.Meta.model(**validated_data)
        if user is not None:
            instance.owner = user
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
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Comment
        fields = ['id', 'comment', 'task', 'user']

    def create(self, validated_data):
        user = validated_data.pop('owner', None)
        instance = self.Meta.model(**validated_data)
        if user is not None:
            instance.owner = user
        instance.save()
        return instance

