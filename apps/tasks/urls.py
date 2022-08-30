
from django.urls import path, include
from apps.tasks.views.Task import MyTaskView, TaskView, TaskViewId, CompletedTaskView, AssignTaskView
from apps.users.views.User import UsersView

urlpatterns = [
    path('', TaskView.as_view()),
    path('mytask', MyTaskView.as_view()),
    path('<int:pk>', TaskViewId.as_view()),
    path('completed', CompletedTaskView.as_view()),
    path('assign', AssignTaskView.as_view()),
   # path('<int:pk>', UserView.as_view()),
    path('', UsersView.as_view()),
]
