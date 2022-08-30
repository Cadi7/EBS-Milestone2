import jwt
from django.contrib.auth.models import User
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response
from apps.users.models import User
from apps.users.serializers import UserSerializer, ShortUserSerializer


class UsersView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = ShortUserSerializer


class UserView(GenericAPIView):

    def get(self, request):
        token = request.COOKIES.get()

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)
        return Response(serializer.data)