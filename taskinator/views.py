"""
API Endpoints for the TODO list.
"""
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from taskinator.models import Task, TaskGroup
from taskinator.serializers import TaskSerializer, TaskGroupSerializer
from utils.viewsets import CheckNoneFilter, DateFilter, FilterableViewSetMixin, OwnedObjectMixin, TextFilter
from utils.datetime import utc_now


class TaskGroupViewSet(OwnedObjectMixin, viewsets.ModelViewSet):  # pylint: disable=too-many-ancestors
    """CRUD for TaskGroup model."""
    serializer_class = TaskGroupSerializer
    queryset = TaskGroup.objects.all()


class TaskViewSet(FilterableViewSetMixin, OwnedObjectMixin, viewsets.ModelViewSet):
    # pylint: disable=too-many-ancestors
    """CRUD for Task model."""
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    filters = (
        DateFilter({'date': 'created_at', 'finished_at': 'finished_at'}),
        CheckNoneFilter({'finished': 'finished_at'}),
        TextFilter({'search': {'name', 'description'}})
    )

    @action(detail=True, methods=['POST', 'PATCH'], url_path='complete')
    def mark_as_completed(self, request, pk=None):  # pylint: disable=invalid-name
        """Shortcut to mark a task as done, preferred to using Update endpoint to set finished_at."""
        task = get_object_or_404(Task, pk=pk)
        task.finished_at = utc_now()
        task.save()
        return Response(self.serializer_class(instance=task, context={'request': request}).data)
