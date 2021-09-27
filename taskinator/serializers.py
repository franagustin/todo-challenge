"""
Serializers for Taskinator views. They handle how models are represented in the API.
"""
from rest_framework import serializers

from taskinator.models import Task, TaskGroup


class TaskSerializer(serializers.HyperlinkedModelSerializer):  # pylint: disable=too-few-public-methods
    """Represents each Task. Show all fields except User (CONFIDENTIAL DATA) for which just id is displayed."""
    user_id = serializers.IntegerField()

    class Meta:
        model = Task
        exclude = ('user', )
        depth = 2


class TaskGroupSerializer(serializers.HyperlinkedModelSerializer):  # pylint: disable=too-few-public-methods
    """Represents each TaskGroup. Show all fields except User (CONFIDENTIAL DATA) for which just id is displayed."""
    user_id = serializers.IntegerField()

    class Meta:
        model = TaskGroup
        exclude = ('user', )
        depth = 1
