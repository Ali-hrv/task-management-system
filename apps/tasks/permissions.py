from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.workspaces.models import WorkspaceMember


class TaskPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if obj.workspace.owner_id == user.id:
            return True

        role = (
            WorkspaceMember.objects.filter(workspace=obj.workspace, user=request.user)
            .values_list("role", flat=True)
            .first()
        )

        if role is None:
            return False

        if request.method in SAFE_METHODS:
            return True

        if role == WorkspaceMember.ROLE_ADMIN:
            return True

        if role == WorkspaceMember.ROLE_VIEWER:
            return False

        if obj.creator_id == request.user.id:
            return True

        if obj.assignee_id == request.user.id:
            return True

        return False
