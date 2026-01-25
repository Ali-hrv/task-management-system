from rest_framework import status

from apps.tasks.models import Task, TaskPriority, TaskStatus

from .test_permissions import BaseTaskAPITestCase


class TestTaskFilter(BaseTaskAPITestCase):
    def test_filter_by_status(self):
        Task.objects.create(
            title="Done task",
            workspace=self.workspace,
            creator=self.member,
            assignee=self.member,
            status=TaskStatus.DONE,
            position=2,
        )
        self.auth(self.member)
        response = self.client.get(self.task_list_url() + "?status=done")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            all(item["status"] == "done" for item in response.data["results"])
        )

    def test_filter_by_priority(self):
        Task.objects.create(
            title="Priority task",
            workspace=self.workspace,
            creator=self.member,
            assignee=self.member,
            status=TaskStatus.TODO,
            priority=TaskPriority.HIGH,
            position=3,
        )
        self.auth(self.member)
        response = self.client.get(self.task_list_url() + "?priority=high")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            all(item["priority"] == "high" for item in response.data["results"])
        )

    def test_filter_by_assignee(self):
        Task.objects.create(
            title="Priority task",
            workspace=self.workspace,
            creator=self.member,
            assignee=self.admin,
            status=TaskStatus.DOING,
            position=2,
        )
        self.auth(self.member)
        response = self.client.get(self.task_list_url() + f"?assignee={self.admin.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            all(item["assignee"] == self.admin.id for item in response.data["results"])
        )
