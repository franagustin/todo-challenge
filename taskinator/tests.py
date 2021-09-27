"""
Test Taskinator Django app.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from conftest import create_task, create_task_group, create_user
from taskinator.models import Task, TaskGroup
from taskinator.views import TaskViewSet
from utils.datetime import utc_now


# Allow db usage for all tests within this module
pytestmark = pytest.mark.django_db

User = get_user_model()


@pytest.fixture
def client():
    """Unauthenticated client to make API requests."""
    return APIClient()


@pytest.fixture
def authenticated_client(token):  # pylint: disable=redefined-outer-name
    """Token authenticated client to make API requests."""
    auth_client = APIClient()
    auth_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return auth_client


@pytest.fixture
def token(user):  # noqa: F811, pylint: disable=redefined-outer-name
    """Use the user fixture and create a DRF Token for authorization."""
    example_token = Token.objects.create(user=user)
    yield example_token
    example_token.delete()


def is_object_in_response(obj, response):
    """Check if a given object was returned by the API."""
    response_task_names = [o['name'] for o in response.data['results']]
    return obj.name in response_task_names


def test_task_string():
    """Test the string representation of a Task."""
    assert str(Task(name='Do something')) == 'Do something'


def test_task_group_string():
    """Test the string representation of a TaskGroup."""
    assert str(TaskGroup(name='Top', user=User(username='Test'))) == 'Task group Top of Test'


def test_endpoints_need_authentication(client, authenticated_client):  # pylint: disable=redefined-outer-name
    """Ensure the data can only be retrieved by authenticated users."""
    response = client.get('/api/tasks/')
    assert response.status_code == 401
    response = client.get('/api/task-groups/')
    assert response.status_code == 401
    response = authenticated_client.get('/api/tasks/')
    assert response.status_code == 200
    response = authenticated_client.get('/api/task-groups/')
    assert response.status_code == 200


def test_no_task_groups(authenticated_client):  # pylint: disable=redefined-outer-name
    """Checks that an empty list is returned by the API."""
    response = authenticated_client.get('/api/task-groups/')
    assert response.data['count'] == 0
    assert response.data['results'] == []


def test_single_task_groups(authenticated_client, task_group):  # pylint: disable=redefined-outer-name
    """Checks that the task group is returned by the API."""
    response = authenticated_client.get('/api/task-groups/')
    assert response.status_code == 200
    assert is_object_in_response(task_group, response)


def test_many_task_groups(authenticated_client, task_group):  # pylint: disable=redefined-outer-name
    """Checks that all task groups are returned by the API."""
    second_task_group = create_task_group(task_group.user, task_group_name='Other task group')
    response = authenticated_client.get('/api/task-groups/')
    assert response.status_code == 200
    assert is_object_in_response(task_group, response)
    assert is_object_in_response(second_task_group, response)


def test_task_viewset_filters():
    """Ensure the TaskViewSet has the correct filters configuration."""
    task_viewset_filters = {f.__class__.__name__: f for f in TaskViewSet.filters}
    date_filter = task_viewset_filters.get('DateFilter')
    assert date_filter
    assert date_filter.fields_mapping.get('date') == 'created_at'
    assert date_filter.fields_mapping.get('finished_at') == 'finished_at'
    finished_filter = task_viewset_filters.get('CheckNoneFilter')
    assert finished_filter
    assert finished_filter.fields_mapping.get('finished') == 'finished_at'
    text_filter = task_viewset_filters.get('TextFilter')
    assert text_filter
    assert text_filter.fields_mapping.get('search') == {'name', 'description'}


def test_no_tasks(authenticated_client):  # pylint: disable=redefined-outer-name
    """Checks that an empty list is returned by the API."""
    response = authenticated_client.get('/api/tasks/')
    assert response.status_code == 200
    assert response.data['count'] == 0
    assert response.data['results'] == []


def test_single_task(authenticated_client, task):  # pylint: disable=redefined-outer-name
    """Checks that the task group is returned by the API."""
    response = authenticated_client.get('/api/tasks/')
    assert response.status_code == 200
    assert is_object_in_response(task, response)


def test_many_tasks(authenticated_client, task):  # pylint: disable=redefined-outer-name
    """Checks that all task groups are returned by the API."""
    second_task = create_task(task.user, task_name='Other task group')
    response = authenticated_client.get('/api/tasks/')
    assert response.status_code == 200
    assert is_object_in_response(task, response)
    assert is_object_in_response(second_task, response)


def test_tasks_are_filtered_by_user(authenticated_client, task):  # pylint: disable=redefined-outer-name
    """Ensure the API only returns each user's tasks."""
    second_user = create_user('Someone else')
    second_task = create_task(second_user, task_name='Other task')
    response = authenticated_client.get('/api/tasks/')
    assert response.status_code == 200
    assert is_object_in_response(task, response)
    assert not is_object_in_response(second_task, response)


def test_date_filtered_task(authenticated_client, task):  # pylint: disable=redefined-outer-name
    """Check all filtering by date is enabled for the tasks endpoint."""
    second_task = create_task(task.user, task_name='Other task')
    response = authenticated_client.get('/api/tasks/', data={'date__lt': task.created_at})
    assert response.data['count'] == 0
    response = authenticated_client.get('/api/tasks/', data={'date__lte': task.created_at})
    assert is_object_in_response(task, response)
    assert not is_object_in_response(second_task, response)
    response = authenticated_client.get('/api/tasks/', data={'date': task.created_at})
    assert is_object_in_response(task, response)
    assert not is_object_in_response(second_task, response)
    response = authenticated_client.get('/api/tasks/', data={'date__gt': task.created_at})
    assert not is_object_in_response(task, response)
    assert is_object_in_response(second_task, response)
    response = authenticated_client.get('/api/tasks/', data={'date__gte': task.created_at})
    assert is_object_in_response(task, response)
    assert is_object_in_response(second_task, response)


def test_finished_filtered_task(authenticated_client, task):  # pylint: disable=redefined-outer-name
    """Test that the finished filter is enabled for the tasks endpoint."""
    second_task = create_task(task.user, task_name='Other task')
    response = authenticated_client.get('/api/tasks/', data={'finished': True})
    assert response.data['count'] == 0
    task.finished_at = utc_now()
    task.save()
    response = authenticated_client.get('/api/tasks/', data={'finished': True})
    assert is_object_in_response(task, response)
    assert not is_object_in_response(second_task, response)
    response = authenticated_client.get('/api/tasks/', data={'finished': False})
    assert not is_object_in_response(task, response)
    assert is_object_in_response(second_task, response)


def test_search_filtered_task(authenticated_client, task):  # pylint: disable=redefined-outer-name
    """Test that the text filter is enabled for the tasks endpoint."""
    second_task = create_task(task.user, task_name='Other task')
    third_task = create_task(task.user, task_name='HIDDEN')
    response = authenticated_client.get('/api/tasks/', data={'search': 'task'})
    assert is_object_in_response(task, response)
    assert is_object_in_response(second_task, response)
    assert not is_object_in_response(third_task, response)


def test_task_mark_as_completed(authenticated_client, task):  # pylint: disable=redefined-outer-name
    """Test that the mark_as_completed endpoint works."""
    assert task.finished_at is None
    response = authenticated_client.post(f'/api/tasks/{task.id}/complete/')
    assert response.status_code == 200
    assert Task.objects.get(id=task.id).finished_at is not None


def test_create_task(authenticated_client):  # pylint: disable=redefined-outer-name
    """Makes sure the task creation endpoint is working."""
    assert not Task.objects.filter(name='Some task').exists()
    response = authenticated_client.post('/api/tasks/', data={'name': 'Some task', 'description': 'Do something'})
    assert response.status_code == 201
    assert Task.objects.filter(name='Some task').exists()


def test_delete_task(authenticated_client, task):  # pylint: disable=redefined-outer-name
    """Makes sure the task deletion endpoint is working."""
    assert Task.objects.filter(id=task.id).exists()
    response = authenticated_client.delete(f'/api/tasks/{task.id}/')
    assert response.status_code == 204
    assert not Task.objects.filter(id=task.id).exists()
