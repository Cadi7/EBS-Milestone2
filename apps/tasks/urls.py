from django.urls import path, include
from rest_framework import routers
from rest_framework.routers import DefaultRouter

from apps.tasks.views.Task import MyTaskView, TaskView, CompletedTaskView, ModifyOwner
from apps.users.views.User import UsersView

router = DefaultRouter()
router.register('', TaskView, basename='')
router.register('update', ModifyOwner, basename='update_task')

urlpatterns = [
    path('', include(router.urls)),
    path('mytask', MyTaskView.as_view()),
    # path('<int:pk>', TaskViewId.as_view()),
    path('completed', CompletedTaskView.as_view()),
    # path('<int:pk>', UserView.as_view()),
    path('', UsersView.as_view()),
]
