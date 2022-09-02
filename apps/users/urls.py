
from django.urls import path
from apps.users.views.Login import LoginView, LogoutView
from apps.users.views.Register import RegisterView
from apps.users.views.User import UsersView

urlpatterns = [
    path('register', RegisterView.as_view()),
    path('login', LoginView.as_view()),
   # path('<int:pk>', UserView.as_view()),
    path('', UsersView.as_view()),
    #path('logout', LogoutView.as_view()),
]
