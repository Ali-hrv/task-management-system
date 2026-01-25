from django.db.models import Q
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet

from apps.workspaces.models import Workspace, WorkspaceMember

from .filters import TaskFilter
from .models import Task
from .permissions import TaskPermission
from .serializers import SubTaskCreateSerializer, TaskSerializer


class TaskPagination(PageNumberPagination):
    page_size = 10


class TaskViewSet(ModelViewSet):
    serializer_class = TaskSerializer
    pagination_class = TaskPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskFilter

    def get_queryset(self):
        user = self.request.user
        qs = Task.objects.select_related("workspace", "assignee", "parent", "creator")

        if not user.is_authenticated:
            return qs.none()

        allowed_workspace_ids = WorkspaceMember.objects.filter(
            user_id=user.id
        ).values_list("workspace_id", flat=True)

        qs = qs.filter(
            Q(workspace__owner_id=user.id) | Q(workspace_id__in=allowed_workspace_ids)
        ).distinct()

        workspace_id = self.kwargs.get("workspace_id")
        if workspace_id is not None:
            qs = qs.filter(workspace_id=workspace_id)

        return qs

    def get_permissions(self):
        if self.action in ["list", "create"]:
            return [IsAuthenticated()]
        return [IsAuthenticated(), TaskPermission()]

    def create(self, request, *args, **kwargs):
        workspace_id = self.kwargs.get("workspace_id")
        workspace = get_object_or_404(Workspace, id=workspace_id)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save(creator=request.user, workspace=workspace)

        return Response(serializer.data, status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = True
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status.HTTP_200_OK)


class SubTaskPagination(PageNumberPagination):
    page_size = 10


class SubTaskViewSet(ViewSet):
    permission_classes = [IsAuthenticated, TaskPermission]
    pagination_class = SubTaskPagination

    def list(self, request, task_id=None):
        parent = get_object_or_404(Task, id=task_id, parent__isnull=True)
        self.check_object_permissions(request, parent)
        subtasks = parent.subtasks.select_related(
            "workspace", "assignee", "parent", "creator"
        )

        paginator = self.pagination_class
        page = paginator.paginate_queryset(subtasks, request)
        serializer = TaskSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)

    def create(self, request, task_id):
        parent = get_object_or_404(Task, id=task_id, parent__isnull=True)
        self.check_object_permissions(request, parent)

        serializer = SubTaskCreateSerializer(
            data=request.data, context={"request": request, "parent_task": parent}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_201_CREATED)
