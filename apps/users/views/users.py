from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users import serializers
from apps.users.models import User
from apps.users.serializers import ShortUserSerializer, UserSerializer


class RegisterView(mixins.ListModelMixin, GenericViewSet):
    serializer_class = ShortUserSerializer
    queryset = User.objects.all()

    @action(
        methods=["post"],
        detail=False,
        permission_classes=[AllowAny],
        serializer_class=UserSerializer,
    )
    def register(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.create(
            first_name=serializer.validated_data["first_name"],
            last_name=serializer.validated_data["last_name"],
            email=serializer.validated_data["email"],
            is_superuser=False,
        )

        user.set_password(serializer.validated_data["password"])
        user.save()

        refresh = RefreshToken.for_user(user)

        return Response({"refresh": str(refresh), "access": str(refresh.access_token)})
