from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import WorkspaceViewSet

router = DefaultRouter()
router.register(r"", WorkspaceViewSet, basename="workspaces")

urlpatterns = [
    path("", include(router.urls)),
]
