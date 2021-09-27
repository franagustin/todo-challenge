"""
Tests for reusable common utils.
"""
from datetime import datetime
from unittest.mock import Mock
from django.contrib.auth import get_user_model

import pytest
import pytz

from conftest import create_user, create_task
from taskinator.models import Task
from utils.datetime import utc_now
from utils.viewsets import CheckNoneFilter, DateFilter, Filter, FilterableViewSetMixin, OwnedObjectMixin, TextFilter


# Allow db usage for all tests within this module
pytestmark = pytest.mark.django_db

User = get_user_model()


class FakeRequest:  # pylint: disable=too-few-public-methods
    """Simple dummy to mimic DRF Requests"""
    def __init__(self, user=None, data=None, **query_params):
        self.query_params = query_params or {}
        self.user = user
        self.data = data


class FakeViewSet:  # pylint: disable=too-few-public-methods
    """Simple dummy to mimic DRF ViewSets"""
    queryset = Task.objects.all()

    def __init__(self, **query_params):
        self.request = FakeRequest(**query_params)

    def get_queryset(self):
        """Return the queryset with all objects."""
        return self.queryset

    def create(self, request, *args, **kwargs):
        """Create an object."""
        self.queryset.model.objects.create(**request.data)


class MyFilter(Filter):  # pylint: disable=too-few-public-methods
    """Simple filter to test basic functionalities"""
    def __call__(self, queryset, request):  # pylint: disable=unused-argument
        pass


class ExampleViewSet(FilterableViewSetMixin, OwnedObjectMixin, FakeViewSet):
    """Simple ViewSet to use in multiple tests and check the mixins are actually working."""
    queryset = Task.objects.all()
    filters = []


def test_utc_now():
    """Test the utc_now function is accurate and has tzinfo."""
    naive_datetime = datetime.utcnow()
    aware_datetime = utc_now()
    assert (aware_datetime - pytz.timezone('UTC').localize(naive_datetime)).total_seconds() < 1
    assert aware_datetime.tzinfo == pytz.UTC


def test_filter_is_abstract():
    """Ensures Filter class must be subclassed and __call__ method implemented."""
    with pytest.raises(TypeError):
        Filter()  # pylint: disable=abstract-class-instantiated
    MyFilter({'parameter': 'field'})(None, None)


def test_filter_no_field_mappings():
    """Makes sure filters can't be instantiated without mapping."""
    with pytest.raises(ValueError):
        MyFilter()


def test_filter_default_field_mappings():
    """Ensures filters can have a default mapping."""
    MyFilter.DEFAULT_FIELDS_MAPPING = {'parameter': 'field'}
    MyFilter()
    del MyFilter.DEFAULT_FIELDS_MAPPING


def test_filterable_mixin():
    """Tests filters are called when subclassing FilterableViewSetMixin."""
    mock1 = Mock()
    mock2 = Mock()
    ExampleViewSet.filters = [mock1, mock2]
    ExampleViewSet().get_queryset()
    mock1.assert_called_once()
    mock2.assert_called_once()
    ExampleViewSet.filters = []


def test_filterable_mixin_are_applied(user, task):
    """Checks that filters are actually being applied and work."""
    second_task = create_task(user, 'Other task')
    third_task = create_task(user, 'Different name')
    ExampleViewSet.filters = [TextFilter({'search': {'name'}})]
    queryset = ExampleViewSet(user=user, search='TASK').get_queryset()
    assert task in queryset
    assert second_task in queryset
    assert third_task not in queryset
    ExampleViewSet.filters = []


def test_owned_object_mixin_filtered(user, task):
    """Makes sure the OwnedObjectMixin is filtering by user."""
    second_user = create_user('Someone else')
    second_task = create_task(second_user, 'Other task')
    queryset = ExampleViewSet(user=user).get_queryset()
    assert task in queryset
    assert second_task not in queryset


def test_owned_object_mixin_create(user):
    """Test the created object has the right user assigned."""
    ExampleViewSet(user=user).create(FakeRequest(user=user, data={'name': 'Some task'}))
    assert Task.objects.get(name='Some task').user == user


def test_date_filter(user, task):
    """Ensures DateFilter works."""
    current_datetime = utc_now()
    second_task = create_task(user, 'Other task')
    ExampleViewSet.filters = [DateFilter({'date': 'created_at'})]
    queryset = ExampleViewSet(user=user, date=task.created_at).get_queryset()
    assert task in queryset
    assert second_task not in queryset
    queryset = ExampleViewSet(user=user, date__lt=current_datetime).get_queryset()
    assert task in queryset
    assert second_task not in queryset
    queryset = ExampleViewSet(user=user, date__lte=task.created_at).get_queryset()
    assert task in queryset
    assert second_task not in queryset
    queryset = ExampleViewSet(user=user, date__gt=current_datetime).get_queryset()
    assert task not in queryset
    assert second_task in queryset
    queryset = ExampleViewSet(user=user, date__gte=second_task.created_at).get_queryset()
    assert task not in queryset
    assert second_task in queryset
    ExampleViewSet.filters = []


def test_check_none_filter(user, task):
    """Ensures CheckNoneFilter works."""
    second_task = create_task(user, 'Other task')
    second_task.finished_at = utc_now()
    second_task.save()
    ExampleViewSet.filters = [CheckNoneFilter({'finished': 'finished_at'})]
    queryset = ExampleViewSet(user=user, finished='TRUE').get_queryset()
    assert task not in queryset
    assert second_task in queryset
    queryset = ExampleViewSet(user=user, finished='FALSE').get_queryset()
    assert task in queryset
    assert second_task not in queryset
    ExampleViewSet.filters = []


def test_text_filter(user, task):
    """Ensures TextFilter works."""
    second_task = create_task(user, 'FINDME')
    ExampleViewSet.filters = [TextFilter({'search': ['name']})]
    queryset = ExampleViewSet(user=user, search='FINDME').get_queryset()
    assert task not in queryset
    assert second_task in queryset
