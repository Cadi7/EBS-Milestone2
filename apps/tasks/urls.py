from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.tasks.views.Task import TaskView, CompleteTask

router = DefaultRouter()
router.register(r'', TaskView, basename=''),
router.register(r'', CompleteTask, basename='')

urlpatterns = [
    path('', include(router.urls)),
]
