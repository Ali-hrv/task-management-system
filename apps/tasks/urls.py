from django.urls import path

from . import views

urlpatterns = [
    path("workspaces/<int:workspace_id>/tasks/", views.TaskListCreateView.as_view()),
    path("tasks/<int:pk>/", views.TaskDetailView.as_view()),
    path(
        "tasks/<int:task_id>/subtasks/",
        views.SubTaskCreateView.as_view(),
        name="task-subtask-list-create",
    ),
]
