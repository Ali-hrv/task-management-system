from django.urls import path

from . import views

urlpatterns = [
    path("", views.WorkspaceListCreateView.as_view(), name="workspace_list_create"),
    path("<int:pk>", views.WorkspaceDetailView.as_view(), name="workspace_detail"),
]
