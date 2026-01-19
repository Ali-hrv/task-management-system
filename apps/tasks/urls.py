from django.urls import path

from .views import SubTaskViewSet, TaskViewSet

task_list_create = TaskViewSet.as_view({"get": "list", "post": "create"})
task_detail = TaskViewSet.as_view(
    {"get": "retrieve", "put": "update", "patch": "update", "delete": "destroy"}
)

subtask_list_create = SubTaskViewSet.as_view({"get": "list", "post": "create"})

urlpatterns = [
    path("workspaces/<int:workspace_id>/tasks/", task_list_create),
    path("tasks/<int:pk>/", task_detail),
    path(
        "tasks/<int:task_id>/subtasks/",
        subtask_list_create,
        name="task-subtask-list-create",
    ),
]
