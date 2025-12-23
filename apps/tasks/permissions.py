from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.workspaces.models import WorkspaceMember


class TaskPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        try:
            member = WorkspaceMember.objects.get(
                workspace=obj.workspace,
                user=request.user,
            )
        except WorkspaceMember.DoesNotExist:
            return False

        if member.role in ["owner", "admin"]:
            return True

        if member.role == "viewer":
            return False

        if obj.creator == request.user:
            return True

        if obj.assignee and obj.assignee == request.user:
            return True

        return False
