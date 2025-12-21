from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "status",
        "priority",
        "workspace",
        "assignee",
        "created_at",
    )

    list_filter = ("status", "priority", "workspace")
    search_fields = ("title",)
    ordering = ("position", "-created_at")
