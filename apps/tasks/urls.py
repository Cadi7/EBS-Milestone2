from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.tasks.views.Task import TaskView
router = DefaultRouter()
router.register(r'', TaskView, basename=''),

urlpatterns = [
    path('', include(router.urls)),
]
