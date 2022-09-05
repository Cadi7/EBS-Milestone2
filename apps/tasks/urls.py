from rest_framework.routers import DefaultRouter

from apps.tasks.views.Task import TaskView, Comments

router = DefaultRouter()
router.register(r'', TaskView, basename='')
router.register(r'', Comments, basename=' ')

urlpatterns = router.urls
