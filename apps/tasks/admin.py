from django.contrib import admin

from .models import Task


class SubTaskInline(admin.TabularInline):
    model = Task
    extra = 0
    fk_name = "parent"


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
    inlines = [SubTaskInline]
