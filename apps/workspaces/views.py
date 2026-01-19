from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .models import Workspace
from .permissions import IsWorkspaceAdminOrOwner
from .serializers import WorkspaceSerializer


class WorkspacePagination(PageNumberPagination):
    page_size = 2


class WorkspaceViewSet(ModelViewSet):
    serializer_class = WorkspaceSerializer
    pagination_class = WorkspacePagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Workspace.objects.all()

    def get_permissions(self):
        if self.action in ["retrieve", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsWorkspaceAdminOrOwner()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
