from django.urls import path

from . import views

urlpatterns = [
    path("workspaces/<int:workspace_id>/tasks/", views.TaskListCreateView.as_view()),
    path("tasks/<int:pk>/", views.TaskDetailView.as_view()),
]
