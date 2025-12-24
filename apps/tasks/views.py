from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.workspaces.models import Workspace

from .models import Task
from .permissions import TaskPermission
from .serializers import SubTaskCreateSerializer, TaskSerializer


class TaskListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, workspace_id):
        tasks = Task.objects.filter(workspace_id=workspace_id)

        status_param = request.query_params.get("status")
        if status_param:
            tasks = tasks.filter(status=status_param)

        priority_param = request.query_params.get("priority")
        if priority_param:
            tasks = tasks.filter(priority=priority_param)

        assignee_param = request.query_params.get("assignee")
        if assignee_param:
            tasks = tasks.filter(assignee_id=assignee_param)

        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginated_tasks = paginator.paginate_queryset(tasks, request)
        serializer = TaskSerializer(paginated_tasks, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, workspace_id):
        workspace = get_object_or_404(Workspace, id=workspace_id)

        serializer = TaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(creator=request.user, workspace=workspace)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TaskDetailView(APIView):
    permission_classes = [IsAuthenticated, TaskPermission]

    def get_object(self, pk):
        return get_object_or_404(Task, pk=pk)

    def get(self, request, pk):
        task = self.get_object(pk)
        self.check_object_permissions(request, task)

        serializer = TaskSerializer(task)
        return Response(serializer.data)

    def put(self, request, pk):
        task = self.get_object(pk)
        self.check_object_permissions(request, task)

        serializer = TaskSerializer(
            task, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    def delete(self, request, pk):
        task = self.get_object(pk)
        self.check_object_permissions(request, task)

        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubTaskCreateView(APIView):
    permission_classes = [TaskPermission]

    def get(self, request, task_id):
        parent = get_object_or_404(Task, id=task_id, parent__isnull=True)
        subtasks = parent.subtasks.all()

        paginator = PageNumberPagination()
        paginator.page_size = 10

        paginated_subtasks = paginator.paginate_queryset(subtasks, request)
        serializer = TaskSerializer(paginated_subtasks, many=True)

        return paginator.get_paginated_response(serializer.data)

    def post(self, request, task_id):
        parent = get_object_or_404(Task, id=task_id, parent__isnull=True)

        serializer = SubTaskCreateSerializer(
            data=request.data,
            context={
                "request": request,
                "parent_task": parent,
            },
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
