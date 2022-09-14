from django.urls import path, include
from rest_framework_nested.routers import (
    NestedSimpleRouter,
    DefaultRouter
)

from apps.tasks.views.Task import (
    TaskViewSet,
    TaskCommentViewSet,
)

base_router = DefaultRouter()

base_router.register(
    prefix=r'tasks',
    viewset=TaskViewSet,
    basename='tasks'
)

nested_router = NestedSimpleRouter(
    parent_router=base_router,
    parent_prefix=r'tasks',
    lookup='task'
)
nested_router.register(
    prefix=r'comments',
    viewset=TaskCommentViewSet,
    basename='comments'
)

urlpatterns = [
    path('', include(base_router.urls)),
    path('', include(nested_router.urls)),
]