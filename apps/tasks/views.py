from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.workspaces.models import Workspace

from .models import Task
from .permissions import TaskPermission
from .serializers import SubTaskCreateSerializer, TaskSerializer


class TaskListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "priority", "assignee"]

    def get(self, request, workspace_id):
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

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

        serializer = TaskSerializer(task, data=request.data, partial=True)
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

        serializer = TaskSerializer(subtasks, many=True)
        return Response(serializer.data)

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
