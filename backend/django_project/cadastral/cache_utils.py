"""
Caching utilities for spatial API endpoints.

Provides decorators and mixins for caching bbox queries and other
spatial operations using Redis.
"""

from __future__ import annotations
import hashlib
from functools import wraps
from typing import Any, TYPE_CHECKING

from django.core.cache import cache
from django.utils.decorators import method_decorator
from rest_framework.request import Request

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

def cache_bbox_query(
    timeout: int = 300,
    key_prefix: str = "bbox",
    vary_on_params: Sequence[str] | None = None,
) -> Callable:
    """
    Decorator to cache API responses based on bbox and other query parameters.

    Args:
        timeout: Cache timeout in seconds (default: 5 minutes)
        key_prefix: Prefix for cache keys
        vary_on_params: Additional query parameters to include in cache key

    Usage:
        @cache_bbox_query(timeout=600, vary_on_params=['limit', 'offset'])
        def list(self, request):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, request: Request, *args: Any, **kwargs: Any) -> Any:

            cache_key_parts = [key_prefix]

            bbox = request.query_params.get("bbox")
            if bbox:
                try:
                    bbox_coords = [float(x) for x in bbox.split(",")]
                    if len(bbox_coords) >= 4:
                        bbox_normalized = (
                            round(bbox_coords[0], 4),
                            round(bbox_coords[1], 4),
                            round(bbox_coords[2], 4),
                            round(bbox_coords[3], 4),
                        )
                        cache_key_parts.append(f"bbox_{bbox_normalized}")
                except (ValueError, IndexError):
                    pass

            if vary_on_params:
                for param in vary_on_params:
                    value = request.query_params.get(param)
                    if value:
                        cache_key_parts.append(f"{param}_{value}")

            view_name = self.__class__.__name__
            action = getattr(self, "action", "list")
            cache_key_parts.append(f"{view_name}_{action}")

            cache_key_str = "_".join(str(part) for part in cache_key_parts)
            cache_key = hashlib.md5(cache_key_str.encode()).hexdigest()
            full_cache_key = f"api_cache_{cache_key}"

            cached_response = cache.get(full_cache_key)
            if cached_response is not None:
                return cached_response

            response = func(self, request, *args, **kwargs)

            if (
                request.method == "GET"
                and hasattr(response, "status_code")
                and response.status_code == 200
            ):
                cache.set(full_cache_key, response, timeout)

            return response

        return wrapper
    return decorator

class CacheBBoxMixin:
    """
    Mixin class for viewsets to enable bbox query caching.

    Usage:
        class MyViewSet(CacheBBoxMixin, viewsets.ReadOnlyModelViewSet):
            cache_timeout = 600  # 10 minutes
            cache_vary_on = ['limit', 'offset']
    """

    cache_timeout: int = 300
    cache_vary_on: Sequence[str] | None = None

    @method_decorator(
        cache_bbox_query(timeout=300, key_prefix="bbox", vary_on_params=None)
    )
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Any:
        """
        List endpoint with bbox caching.
        Override this in subclasses if needed.
        """
        return super().list(request, *args, **kwargs)

    def get_cache_timeout(self) -> int:
        """Get cache timeout, can be overridden in subclasses."""
        return getattr(self, "cache_timeout", 300)

    def get_cache_vary_on(self) -> Sequence[str] | None:
        """Get cache vary parameters, can be overridden in subclasses."""
        return getattr(self, "cache_vary_on", None)
