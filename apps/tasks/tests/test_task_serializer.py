from apps.tasks.models import Task, TaskPriority, TaskStatus
from apps.tasks.serializers import SubTaskCreateSerializer, TaskSerializer

from .base import BaseTaskSerializerTest


class TestTaskSerializer(BaseTaskSerializerTest):
    def test_only_assignee_can_mark_done(self):
        request = self.request_for(self.outsider)

        serializer = TaskSerializer(
            instance=self.task,
            data={"status": TaskStatus.DONE},
            context={"request": request},
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("Only the assignee can mark this task", str(serializer.errors))

    def test_assignee_can_mark_done(self):
        request = self.request_for(self.member)

        serializer = TaskSerializer(
            instance=self.task,
            data={"status": TaskStatus.DONE},
            context={"request": request},
            partial=True,
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        obj = serializer.save()
        self.assertEqual(obj.status, TaskStatus.DONE)

    def test_admin_can_archive_task(self):
        request = self.request_for(self.admin)

        serializer = TaskSerializer(
            instance=self.task,
            data={"status": TaskStatus.ARCHIVED},
            context={"request": request},
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        obj = serializer.save()
        self.assertEqual(obj.status, TaskStatus.ARCHIVED)

    def test_member_cannot_archive_task(self):
        request = self.request_for(self.member)

        serializer = TaskSerializer(
            instance=self.task,
            data={"status": TaskStatus.ARCHIVED},
            context={"request": request},
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn(
            "Only owner or admin can archive this task.", str(serializer.errors)
        )

    def test_owner_can_archive_task(self):
        request = self.request_for(self.owner)

        serializer = TaskSerializer(
            instance=self.task,
            data={"status": TaskStatus.ARCHIVED},
            context={"request": request},
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        obj = serializer.save()
        self.assertEqual(obj.status, TaskStatus.ARCHIVED)


class TestSubTaskSerializer(BaseTaskSerializerTest):
    def test_cannot_create_subtask_for_subtask(self):
        parent_subtask = Task.objects.create(
            title="Sub1",
            workspace=self.workspace,
            creator=self.member,
            assignee=self.member,
            status=TaskStatus.DOING,
            priority=TaskPriority.HIGH,
            position=2,
            parent=self.task,
        )
        request = self.request_for(self.member, method="POST")

        serializer = SubTaskCreateSerializer(
            data={
                "title": "Sub of sub",
                "description": "test",
                "priority": TaskPriority.MEDIUM,
            },
            context={"request": request, "parent_task": parent_subtask},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn(
            "You can not create a subtask for another subtask", str(serializer.errors)
        )

    def test_create_subtask_sets_fields_correctly(self):
        Task.objects.create(
            title="S1",
            workspace=self.workspace,
            creator=self.member,
            assignee=self.member,
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM,
            position=2,
            parent=self.task,
        )

        Task.objects.create(
            title="S2",
            workspace=self.workspace,
            creator=self.member,
            assignee=self.member,
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM,
            position=3,
            parent=self.task,
        )

        request = self.request_for(self.admin, method="POST")

        serializer = SubTaskCreateSerializer(
            data={
                "title": "S3",
                "description": "Test3",
                "assignee": self.viewer.id,
                "priority": TaskPriority.HIGH,
            },
            context={"request": request, "parent_task": self.task},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        obj = serializer.save()

        self.assertEqual(obj.workspace_id, self.workspace.id)
        self.assertEqual(obj.creator_id, self.admin.id)
        self.assertEqual(obj.assignee_id, self.viewer.id)
        self.assertEqual(obj.status, TaskStatus.TODO)
        self.assertEqual(obj.priority, TaskPriority.HIGH)
        self.assertEqual(obj.position, 4)
        self.assertEqual(obj.parent_id, self.task.id)
