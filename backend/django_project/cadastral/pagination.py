"""
Custom pagination classes for large spatial datasets.

Provides optimized pagination that handles large result sets efficiently
and includes metadata about total counts and spatial bounds.
"""

from typing import Any, TYPE_CHECKING

from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.db.models import QuerySet
    from rest_framework.request import Request
    from rest_framework.views import APIView

class LargeDatasetPagination(LimitOffsetPagination):
    """
    Custom pagination for large spatial datasets.

    Extends LimitOffsetPagination with:
    - Configurable default and max page sizes
    - Efficient count estimation for very large datasets
    - Optional metadata about spatial bounds
    """

    default_limit = 100
    limit_query_param = "limit"
    offset_query_param = "offset"
    max_limit = 1000

    def get_paginated_response(self, data: Sequence[Any]) -> Response:
        """
        Return a paginated style Response object with metadata.
        """
        return Response({
            "count": self.count,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "limit": self.limit,
            "offset": self.offset,
            "results": data,
        })

    def paginate_queryset(
        self,
        queryset: QuerySet,
        request: Request,
        view: APIView | None = None,
    ) -> list[Any] | None:
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.

        Args:
            queryset: The queryset to paginate.
            request: The request object.
            view: The view object.

        Returns:
            A list of objects, or `None` if pagination is not configured for this view.
        """
        if request.query_params.get("skip_count") == "true":
            self.count = None
        else:
            self.count = self.get_count(queryset)

        if self.count == 0:
            return []

        limit = self.get_limit(request)
        if limit is None:
            return None

        offset = self.get_offset(request)
        self.limit = limit
        self.offset = offset

        if self.count is not None and offset >= self.count:
            return []

        return list(queryset[offset:offset + limit])
