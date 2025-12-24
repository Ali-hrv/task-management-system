from rest_framework import serializers

from ..workspaces.models import WorkspaceMember
from .models import Task, TaskStatus


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

    def validate(self, attrs):
        request = self.context["request"]
        user = request.user
        task = self.instance

        if task and "status" in attrs:
            new_task = attrs["status"]

            if new_task == TaskStatus.DONE and task.assignee != user:
                raise serializers.ValidationError(
                    "Only the assignee can mark this task  as done."
                )

            if new_task == TaskStatus.ARCHIVED:
                member = WorkspaceMember.objects.get(
                    workspace=task.workspace, user=user
                )

                if member.role not in ["owner", "admin"]:
                    raise serializers.ValidationError(
                        "Only owner or admin can archive this task."
                    )
        return attrs


class SubTaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ("title", "description", "assignee", "priority")
        read_only_fields = ["id"]

    def validate(self, attrs):
        parent = self.context.get("parent_task")

        if parent.parent is not None:
            raise serializers.ValidationError(
                "You can not create a subtask for another subtask!"
            )
        return attrs

    def create(self, validated_data):
        parent = self.context["parent_task"]
        request = self.context["request"]

        subtasks = Task.objects.filter(parent=parent)

        last_position = 0
        if subtasks.exists():
            last_position = subtasks.order_by("-position").first().position

        return Task.objects.create(
            **validated_data,
            creator=request.user,
            workspace=parent.workspace,
            parent=parent,
            position=last_position + 1,
            status=TaskStatus.TODO,
        )
