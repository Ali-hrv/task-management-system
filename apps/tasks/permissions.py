from rest_framework.permissions import BasePermission

from apps.workspaces.models import WorkspaceMember


class TaskPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            member = WorkspaceMember.objects.get(
                workspace=obj.workspace,
                user=request.user,
            )
        except WorkspaceMember.DoesNotExist:
            return False

        if member.role in ["owner", "admin"]:
            return True

        if member.role == "member":
            if request.method in ["GET"]:
                return True
            return obj.creator == request.user

        if member.role == "viewer":
            return request.method == "GET"

        return False
