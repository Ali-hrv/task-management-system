from rest_framework import status

from apps.tasks.models import Task, TaskPriority, TaskStatus
from apps.workspaces.models import Workspace

from .base import BaseTaskAPITestCase


class TaskPermissionTests(BaseTaskAPITestCase):
    def test_viewer_can_read_task(self):
        self.auth(self.viewer)
        response = self.client.get(self.task_detail_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_viewer_cannot_update_task(self):
        self.auth(self.viewer)
        response = self.client.put(
            self.task_detail_url(),
            {"title": "new"},
            format="json",
        )
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_member_can_update_if_creator(self):
        self.auth(self.member)
        response = self.client.put(
            self.task_detail_url(),
            {"title": "updated by creator"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_update_task(self):
        self.auth(self.admin)
        response = self.client.put(
            self.task_detail_url(),
            {"title": "updated by admin"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_can_update_task(self):
        self.auth(self.owner)
        response = self.client.put(
            self.task_detail_url(),
            {"title": "updated by owner"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_outsider_cannot_read_task(self):
        self.auth(self.outsider)
        response = self.client.get(self.task_detail_url())
        self.assertIn(
            response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
        )

    def test_owner_can_list_workspace_tasks(self):
        self.auth(self.owner)
        response = self.client.get(self.task_list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_outsider_cannot_list_workspace_tasks(self):
        self.auth(self.outsider)
        response = self.client.get(self.task_list_url())

        self.assertIn(
            response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]
        )

        if response.status_code == status.HTTP_200_OK:
            self.assertEqual(response.data["count"], 0)
            self.assertEqual(len(response.data["results"]), 0)

    def test_list_is_scoped_to_workspace_id(self):
        ws2 = Workspace.objects.create(owner=self.owner, name="WS2")
        Task.objects.create(
            title="WS2 T2",
            workspace=ws2,
            creator=self.owner,
            assignee=self.owner,
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM,
            position=1,
        )

        self.auth(self.owner)
        res = self.client.get(self.task_list_url(workspace_id=self.workspace.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        titles = [t["title"] for t in res.data["results"]]
        self.assertNotIn("WS2 T2", titles)
