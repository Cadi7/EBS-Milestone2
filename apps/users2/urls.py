from django.conf.urls import url
from django.urls import path

from apps.common.helpers import schema_view
from apps.users2.views import RegisterView, LoginView, UserView, LogoutView, UsersView

urlpatterns = [url(r'^$', schema_view), url(r'register$', RegisterView.as_view(), name=''),
               url(r'^$', schema_view), url(r'login$', LoginView.as_view(), name='')]
urlpatterns += [
    # path('register', RegisterView.as_view()),
    # path('login', LoginView.as_view()),
    path('user', UserView.as_view()),
    path('users', UsersView.as_view()),
    path('logout', LogoutView.as_view()),
]
