"""
Useful things stored apart for testing, as pytest encourages.
"""
import pytest
from django.contrib.auth import get_user_model

from taskinator.models import Task, TaskGroup


# Allow db usage for all tests within this module
pytestmark = pytest.mark.django_db

User = get_user_model()


def create_user(username='Test'):
    """Create a user with provided username."""
    return User.objects.create(username=username)


@pytest.fixture
def user():
    """Get a user."""
    return create_user()


def create_task(user, task_name='Test task'):  # pylint: disable=redefined-outer-name
    """Create a task with provided user and name."""
    return Task.objects.create(name=task_name, user=user)


@pytest.fixture
def task(user):  # pylint:disable=redefined-outer-name
    """Get a task."""
    return create_task(user)


def create_task_group(user, task_group_name='Test task group'):  # pylint: disable=redefined-outer-name
    """Create a task group with provided user and name."""
    return TaskGroup.objects.create(name=task_group_name, user=user)


@pytest.fixture
def task_group(user):  # pylint:disable=redefined-outer-name
    """Get a task group."""
    return create_task_group(user)


@pytest.fixture(autouse=True, scope='function')
def clean_db():
    """Delete both tasks and users after every test."""
    yield
    Task.objects.all().delete()
    TaskGroup.objects.all().delete()
    User.objects.all().delete()
