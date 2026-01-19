import django_filters as filters

from .models import Task


class TaskFilter(filters.FilterSet):
    status = filters.CharFilter(field_name="status")
    priority = filters.CharFilter(field_name="priority")
    assignee = filters.NumberFilter(field_name="assignee_id")

    class Meta:
        model = Task
        fields = ["status", "priority", "assignee"]
