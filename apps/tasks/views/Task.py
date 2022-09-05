import jwt
from django.contrib.auth.models import User
from drf_util.decorators import serialize_decorator
from rest_framework import viewsets, status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed

from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.tasks.models import Task, Comment
from apps.users.models import User
from apps.tasks.serializers import TaskSerializer, TaskShowSerializer, TaskSerializerID, TaskAssignSerializer, \
    TaskSerializerComplete, CommentSerializer


class TaskView(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]

    def get_object(self):
        obj = get_object_or_404(pk=self.request.GET.get('pk'))
        return obj

    @serialize_decorator(TaskSerializer)
    def create(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        validated_data = request.serializer.validated_data
        task = Task.objects.create(
            title=validated_data['title'],
            description=validated_data['description'],
            status=validated_data['status'],
            user=User.objects.filter(id=payload['id']).first()
        )

        return Response(TaskSerializer(task).data)

    def list(self, request, **kwargs):
        queryset = Task.objects.all()
        serializer = TaskShowSerializer(queryset, many=True)
        return Response(serializer.data)

    @staticmethod
    def retrieve(request, pk=None, **kwargs):
        task = get_object_or_404(Task, pk=pk)
        return Response(TaskSerializerID(task).data)

    def destroy(self, pk=None, **kwargs):
        task = get_object_or_404(Task, pk=pk)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, url_path=r'mytasks')
    def my_tasks(self, request):
        queryset = Task.objects.all().filter(user=self.request.user.id)
        serializer = TaskSerializer(queryset, many=True)

        return Response(serializer.data)

    @action(detail=False, url_path=r'completed')
    def completed_tasks(self, request):
        queryset = Task.objects.all().filter(status=True)
        serializer = TaskSerializer(queryset, many=True)

        return Response(serializer.data)

    @action(detail=True, methods=['put'])
    def complete(self, request, pk=None):
        task = Task.objects.get(id=pk)
        serializer = TaskSerializerComplete(task, data={"id": task.id, "status": True})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['put'], url_path=r'assign')
    def updateowner(self, request):

        user = User.objects.filter(id=request.data['user']).first()
        task = Task.objects.filter(id=request.data['id']).first()
        serializer = TaskAssignSerializer(task)
        task.user = user
        task.save()
        return Response(serializer.data)


class Comments(viewsets.ViewSet):
    serializer_class = CommentSerializer
    permission_classes = (AllowAny,)
    queryset = Comment.objects.all()
    authentication_classes = (SessionAuthentication, BasicAuthentication)

    def get_object(self):
        obj = get_object_or_404(pk=self.request.GET.get('pk'))
        return obj

    @serialize_decorator(CommentSerializer)
    @action(detail=False, methods=['post'])
    def comment(self, request):
        validated_data = request.serializer.validated_data
        comment = Comment.objects.create(
            comment=validated_data['comment'],
            task=validated_data['task'],
        )
        return Response(TaskSerializer(comment).data)

    def list(self, request):
        queryset = Comment.objects.all().filter(task=self.request.task.id)
        serializer = CommentSerializer(queryset, many=True)

        return Response(serializer.data)


