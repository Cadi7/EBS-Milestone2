# Create your views here.
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


class HealthView(GenericAPIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)

    def get(self, request):
        return Response({
            'live': True,
        })


class ProtectedTestView(GenericAPIView):

    def get(self, request):
        return Response({
            'live': True,
        })

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            # queryset just for schema generation metadata
            return ProtectedTestView.objects.none()
