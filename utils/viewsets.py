"""
Extended features for DRF viewsets isolated for reusability.
"""
from abc import ABC, abstractmethod

from django.db.models import Q


class Filter(ABC):  # pylint: disable=too-few-public-methods
    """Base class for queryset filtering in a viewset."""
    @abstractmethod
    def __call__(self, queryset, request):
        """Basically a callable which takes the queryset and request and returns the filtered queryset."""

    def __init__(self, fields_mapping=None):
        if fields_mapping is None:
            default_mapping = getattr(self, 'DEFAULT_FIELDS_MAPPING', None)
            if default_mapping is not None:
                fields_mapping = default_mapping
            else:
                raise ValueError('Must provide fields mapping for this filter.')
        self.fields_mapping = fields_mapping


class FilterableViewSetMixin:
    """Easily implement dynamic queryset filtering on any viewset by just setting the filters attribute."""
    @property
    @abstractmethod
    def filters(self):
        """Filters to apply. Can be set as attributes."""

    def get_queryset(self):
        """Apply all filters to queryset and return it."""
        queryset = super().get_queryset()
        for queryset_filter in self.filters:
            queryset = queryset_filter(queryset, self.request)
        return queryset


class OwnedObjectMixin:
    """Viewsets inheriting from this class only display the objects owned by the authenticated user."""
    def get_queryset(self):
        """Filter queryset by user field."""
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """When creating objects, assign the user."""
        make_mutable = not getattr(request.data, '_mutable', True)
        if make_mutable:
            request.data._mutable = True  # pylint: disable=protected-access
        request.data['user_id'] = request.user.id
        if make_mutable:
            request.data._mutable = False  # pylint: disable=protected-access
        return super().create(request, *args, **kwargs)


class DateFilter(Filter):  # pylint: disable=too-few-public-methods
    """Filter by a list date. Other than exact, relative values (lt, lte, gt, gte) are supported."""
    DEFAULT_FIELDS_MAPPING = {
        'date': 'date'
    }

    def __call__(self, queryset, request):
        for parameter_name, field_name in self.fields_mapping.items():
            if parameter_name in request.query_params:
                queryset = queryset.filter(**{field_name: request.query_params[parameter_name]})
            elif f'{parameter_name}__lt' in request.query_params:
                queryset = queryset.filter(**{f'{field_name}__lt': request.query_params[f'{parameter_name}__lt']})
            elif f'{parameter_name}__lte' in request.query_params:
                queryset = queryset.filter(**{f'{field_name}__lte': request.query_params[f'{parameter_name}__lte']})
            elif f'{parameter_name}__gt' in request.query_params:
                queryset = queryset.filter(**{f'{field_name}__gt': request.query_params[f'{parameter_name}__gt']})
            elif f'{parameter_name}__gte' in request.query_params:
                queryset = queryset.filter(**{f'{field_name}__gte': request.query_params[f'{parameter_name}__gte']})
        return queryset


class CheckNoneFilter(Filter):  # pylint: disable=too-few-public-methods
    """Allow filtering objects based on whether a field is empty or not."""
    EXISTS_KEYWORDS = {'true', 'exists', 'not none', 'not-none', 'not_none', 'notnone', 'filled', 'populated'}
    EMPTY_KEYWORDS = {'false', 'not exists', 'notexists', 'not-exists', 'not_exists', 'none', 'empty'}

    def __call__(self, queryset, request):
        for parameter_name, field_name in self.fields_mapping.items():
            filter_value = request.query_params.get(parameter_name, '').lower()
            if filter_value in self.EXISTS_KEYWORDS:
                queryset = queryset.filter(**{f'{field_name}__isnull': False})
            elif filter_value in self.EMPTY_KEYWORDS:
                queryset = queryset.filter(**{f'{field_name}__isnull': True})
        return queryset


class TextFilter(Filter):  # pylint: disable=too-few-public-methods
    """Check if provided fields contain the provided text."""
    def __call__(self, queryset, request):
        for parameter_name, field_names in self.fields_mapping.items():
            filter_value = request.query_params.get(parameter_name, '').lower()
            if filter_value:
                query = Q()
                for field_name in field_names:
                    query |= Q(**{f'{field_name}__icontains': filter_value})
                queryset = queryset.filter(query).distinct()
        return queryset
