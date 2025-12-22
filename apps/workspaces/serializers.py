from rest_framework import serializers

from .models import Workspace


class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = ("id", "name", "description", "is_personal", "created_at")
        read_only_field = ["id", "created_at"]
