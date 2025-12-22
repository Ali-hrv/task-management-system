from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Workspace
from .permissions import IsWorkspaceAdminOrOwner
from .serializers import WorkspaceSerializer


class WorkspaceListCreateView(APIView):
    def get(self, request):
        workspaces = Workspace.objects.all()
        serializer = WorkspaceSerializer(workspaces, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = WorkspaceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WorkspaceDetailView(APIView):
    permission_classes = [IsAuthenticated, IsWorkspaceAdminOrOwner]

    def get_object(self, pk):
        return Workspace.objects.get(pk=pk)

    def get(self, request, pk):
        workspace = self.get_object(pk)
        serializer = WorkspaceSerializer(workspace)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        workspace = self.get_object(pk)
        self.check_object_permissions(request, workspace)

        serializer = WorkspaceSerializer(workspace, request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, pk):
        workspace = self.get_object(pk)
        self.check_object_permissions(request, workspace)
        workspace.delete()
        return Response({"Response": "Deleted"}, status=status.HTTP_204_NO_CONTENT)
