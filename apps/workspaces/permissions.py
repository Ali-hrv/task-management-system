from rest_framework.permissions import BasePermission


class IsWorkspaceOwner(BasePermission):
    message = "Only workspace owner can modify this workspace"

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
