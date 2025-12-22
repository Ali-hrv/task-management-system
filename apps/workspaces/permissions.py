from rest_framework.permissions import BasePermission

from .models import WorkspaceMember


class IsWorkspaceOwner(BasePermission):
    message = "Only workspace owner can modify this workspace"

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsWorkspaceMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        return WorkspaceMember.objects.filter(workspace=obj, user=request.user).exists()


class IsWorkspaceAdminOrOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return WorkspaceMember.objects.filter(
            workspace=obj, user=request.user, role__in=["owner", "admin"]
        ).exists()
