from rest_framework import serializers

from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            "id",
            "title",
            "description",
            "status",
            "priority",
            "start_date",
            "due_date",
            "completed_at",
            "position",
            "assignee",
            "parent",
            "workspace",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "workspace", "created_at", "updated_at")
