"""
Models representing tasks in a TODO list.
"""
from django.contrib.auth import get_user_model
from django.db import models

from utils.datetime import utc_now


User = get_user_model()


class TaskGroup(models.Model):  # pylint: disable=too-few-public-methods
    """Link related tasks so they could be, for example, shown in a single column in a board."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'Task group {self.name} of {self.user.username}'

    class Meta:  # pylint: disable=too-few-public-methods
        """Options for the TaskGroup model"""
        unique_together = ('name', 'user')
        ordering = ('-id', 'name', 'user')


class Task(models.Model):  # pylint: disable=too-few-public-methods
    """Represents a single task. If finished_at is not none, then the task is completed."""
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=utc_now)
    finished_at = models.DateTimeField(null=True, blank=True)
    group = models.ForeignKey('TaskGroup', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name}'

    class Meta:  # pylint: disable=too-few-public-methods
        """Options for the task model"""
        unique_together = ('name', 'user', 'group')
        ordering = ('-id', '-due_date', '-created_at', 'name', 'user')
