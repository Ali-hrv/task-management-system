from rest_framework import status

from apps.tasks.models import Task, TaskStatus

from .base import BaseTaskAPITestCase


class TestPaginationTask(BaseTaskAPITestCase):
    def test_pagination_page_size(self):
        for i in range(2, 13):
            Task.objects.create(
                title=f"Task {i}",
                workspace=self.workspace,
                creator=self.member,
                assignee=self.member,
                status=TaskStatus.TODO,
                position=i,
            )
        self.auth(self.member)
        response = self.client.get(self.task_list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 12)
        self.assertEqual(len(response.data["results"]), 10)

        response2 = self.client.get(self.task_list_url() + "?page=2")
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response2.data["results"]), 2)
