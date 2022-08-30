from rest_framework import serializers
from apps.tasks.models import Task


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
