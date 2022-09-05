from django.urls import path, include
from rest_framework import routers
from rest_framework.routers import DefaultRouter

from apps.tasks.views.Task import MyTaskView, TaskView, CompletedTaskView, UpdateOwner, CompleteTask, CommentToTask

router = DefaultRouter()
router.register(r'', TaskView, basename='')
router.register(r'update', UpdateOwner, basename='update_task')
router.register(r'mytasks', MyTaskView, basename='my_tasks')
router.register('', CompleteTask, basename='complete_task')
router.register(r'completed', CompletedTaskView, basename='completed')
router.register(r'comment', CommentToTask, basename='comment_task')


urlpatterns = router.urls

