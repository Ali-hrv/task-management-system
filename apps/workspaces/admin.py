from django.contrib import admin

from .models import Board, TaskList, Workspace, WorkspaceMember


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "is_personal")


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "workspace", "position")


@admin.register(TaskList)
class TaskListAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "board", "position")


@admin.register(WorkspaceMember)
class WorkspaceMemberAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "workspace", "role")
