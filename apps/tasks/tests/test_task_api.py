from rest_framework import status

from apps.tasks.models import Task, TaskPriority

from .base import BaseTaskAPITestCase


class TaskAPITest(BaseTaskAPITestCase):
    # __Auth__
    def test_list_without_auth_401_or_403(self):
        response = self.client.get(self.task_list_url())
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_detail_without_auth_401_or_403(self):
        response = self.client.get(self.task_detail_url())
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    # __Create__
    def test_member_can_create_task_201(self):
        self.auth(self.member)
        payload = {
            "title": "New Task",
            "description": "Task",
            "priority": TaskPriority.HIGH,
        }
        response = self.client.post(self.task_list_url(), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Task.objects.filter(workspace=self.workspace, title=payload["title"])
        )

    def test_create_missing_title_400(self):
        self.auth(self.member)
        response = self.client.post(
            self.task_list_url(), {"description": "Text"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)

    def test_create_invalid_status_400(self):
        self.auth(self.member)
        payload = {"title": "New Task", "status": "invalid"}
        response = self.client.post(self.task_list_url(), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", response.data)

    def test_viewer_cannot_create_task(self):
        self.auth(self.viewer)
        payload = {"title": "New Task", "description": "Task"}
        response = self.client.post(self.task_list_url(), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_outsider_cannot_create_task(self):
        self.auth(self.outsider)
        payload = {"title": "New Task", "description": "Task"}
        response = self.client.post(self.task_list_url(), payload, format="json")
        self.assertIn(
            response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
        )

    # __Patch__
    def test_patch_task_partial_update(self):
        self.auth(self.member)
        response = self.client.patch(
            self.task_detail_url(), {"description": "changed"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.description, "changed")

    # __Delete__
    def test_admin_can_delete_task(self):
        self.auth(self.admin)
        response = self.client.delete(self.task_detail_url())

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())

    def test_viewer_cannot_delete_task(self):
        self.auth(self.viewer)
        response = self.client.delete(self.task_detail_url())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
