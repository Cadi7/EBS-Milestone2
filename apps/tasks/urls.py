from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.tasks.views.Task import TaskView, CommentView

router = DefaultRouter()
router.register(r'', TaskView, basename=''),
router.register(r'', CommentView, basename=''),

urlpatterns = [
    path('', include(router.urls)),
]
