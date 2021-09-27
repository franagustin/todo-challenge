"""
Register Taskinator models so they'll be available in the admin site.
"""
from django.contrib import admin

from taskinator.models import Task, TaskGroup


admin.site.register(Task)
admin.site.register(TaskGroup)
