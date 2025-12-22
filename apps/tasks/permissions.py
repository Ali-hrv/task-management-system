from rest_framework.permissions import BasePermission

from apps.workspaces.models import WorkspaceMember


class CanManageTask(BasePermission):
    def has_object_permission(self, request, view, obj):
        return WorkspaceMember.objects.filter(
            workspace=obj.workspace,
            user=request.user,
            role__in=["owner", "admin", "member"],
        ).exists()
