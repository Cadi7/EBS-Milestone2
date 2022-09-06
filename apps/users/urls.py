
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.users.views.Login import  RegisterView
from apps.users.views.User import UserView

router = DefaultRouter()
router.register(r'', RegisterView, basename='')
router.register(r'', UserView, basename='')

urlpatterns = [
    path('', include(router.urls)),
]

