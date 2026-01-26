from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient, APIRequestFactory

from apps.tasks.models import Task, TaskPriority, TaskStatus
from apps.workspaces.models import Workspace, WorkspaceMember

User = get_user_model()


class BaseTaskAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.owner = User.objects.create_user(
            email="owner@gmail.com",
            username="owner",
            password="123456",
        )
        self.admin = User.objects.create_user(
            email="admin@gmail.com",
            username="admin",
            password="123456",
        )
        self.member = User.objects.create_user(
            email="member@gmail.com",
            username="member",
            password="123456",
        )
        self.viewer = User.objects.create_user(
            email="viewer@gmail.com",
            username="viewer",
            password="123456",
        )
        self.outsider = User.objects.create_user(
            email="outsider@gmail.com",
            username="outsider",
            password="123456",
        )

        self.workspace = Workspace.objects.create(
            name="WS",
            description="it's for test",
            owner=self.owner,
            is_personal=False,
        )

        WorkspaceMember.objects.create(
            workspace=self.workspace, user=self.admin, role=WorkspaceMember.ROLE_ADMIN
        )
        WorkspaceMember.objects.create(
            workspace=self.workspace, user=self.member, role=WorkspaceMember.ROLE_MEMBER
        )
        WorkspaceMember.objects.create(
            workspace=self.workspace, user=self.viewer, role=WorkspaceMember.ROLE_VIEWER
        )

        self.task = Task.objects.create(
            title="T1",
            description="test t1",
            workspace=self.workspace,
            creator=self.member,
            assignee=self.member,
            status=TaskStatus.TODO,
            position=1,
        )

    def auth(self, user):
        self.client.force_authenticate(user=user)

    def task_detail_url(self, task_id=None):
        return f"/api/tasks/{task_id or self.task.id}/"

    def task_list_url(self, workspace_id=None):
        return f"/api/workspaces/{workspace_id or self.workspace.id}/tasks/"


class BaseTaskSerializerTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

        self.owner = User.objects.create_user(
            email="owner@gmail.com",
            username="owner",
            password="123456",
        )
        self.admin = User.objects.create_user(
            email="admin@gmail.com",
            username="admin",
            password="123456",
        )
        self.member = User.objects.create_user(
            email="member@gmail.com",
            username="member",
            password="123456",
        )
        self.viewer = User.objects.create_user(
            email="viewer@gmail.com",
            username="viewer",
            password="123456",
        )
        self.outsider = User.objects.create_user(
            email="outsider@gmial.com",
            username="outsider",
            password="123456",
        )

        self.workspace = Workspace.objects.create(
            name="WS", description="test", owner=self.owner, is_personal=False
        )

        WorkspaceMember.objects.create(
            workspace=self.workspace,
            user=self.admin,
            role=WorkspaceMember.ROLE_ADMIN,
        )
        WorkspaceMember.objects.create(
            workspace=self.workspace,
            user=self.member,
            role=WorkspaceMember.ROLE_MEMBER,
        )
        WorkspaceMember.objects.create(
            workspace=self.workspace,
            user=self.viewer,
            role=WorkspaceMember.ROLE_VIEWER,
        )

        self.task = Task.objects.create(
            title="T1",
            description="Test1",
            workspace=self.workspace,
            creator=self.member,
            assignee=self.member,
            status=TaskStatus.TODO,
            priority=TaskPriority.LOW,
            position=1,
        )

    def request_for(self, user, method="post", path="/fake/"):
        request = getattr(self.factory, method.lower())(path, {}, format="json")
        request.user = user
        return request
