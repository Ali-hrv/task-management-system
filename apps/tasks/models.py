from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.workspaces.models import Workspace


class TaskStatus(models.TextChoices):
    TODO = "todo", "Todo"
    DOING = "doing", "Doing"
    DONE = "done", "Done"
    ARCHIVED = "archived", "Archived"


class TaskPriority(models.TextChoices):
    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"
    CRITICAL = "critical", "Critical"


class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20, choices=TaskStatus.choices, default=TaskStatus.TODO
    )

    priority = models.CharField(
        max_length=20, choices=TaskPriority.choices, default=TaskPriority.MEDIUM
    )

    start_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    position = models.PositiveIntegerField(default=0)

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="created_tasks"
    )

    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )

    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="subtasks"
    )

    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="tasks"
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["workspace", "position"],
                name="unique_task_position_per_workspace",
            )
        ]
        indexes = [
            models.Index(fields=["workspace", "status"]),
            models.Index(fields=["workspace", "priority"]),
            models.Index(fields=["workspace", "assignee"]),
            models.Index(fields=["parent"]),
        ]

    def __str__(self):
        return self.title

    def clean(self):
        if self.parent and self.parent.parent:
            raise ValidationError("Subtasks can not have another subtask as parent.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
