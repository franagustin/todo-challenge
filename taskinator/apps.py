"""
Django app implementing a TODO list API.
"""
from django.apps import AppConfig


class TaskinatorConfig(AppConfig):
    """Django app configuration."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'taskinator'
