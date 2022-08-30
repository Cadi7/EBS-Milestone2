
from rest_framework.generics import ListCreateAPIView

from apps.users.models import User
from apps.users.serializers import UserSerializer


class RegisterView(ListCreateAPIView):
    allowed_methods = ["POST"]
    queryset = User.objects.all()
    serializer_class = UserSerializer
