import jwt
from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from apps.users.models import User
from apps.users.serializers import UserSerializer, ShortUserSerializer


class UserView(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    @staticmethod
    def get_user(request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        user = User.objects.filter(id=payload['id']).first()
        serializer = ShortUserSerializer(user)

        return Response(serializer.data, status=200)
