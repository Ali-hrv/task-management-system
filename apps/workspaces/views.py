from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Workspace
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
