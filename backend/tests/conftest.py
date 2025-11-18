"""
Pytest configuration and fixtures for cadastral app tests.
"""
import sys
from pathlib import Path
from datetime import datetime

import pytest
from django.contrib.gis.geos import (
    Point,
    Polygon,
    MultiPolygon,
)
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework.test import APIRequestFactory

backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

pytest_plugins = ["pytest_django"]

@pytest.fixture
def sample_point() -> Point:
    """Create a sample point geometry in EPSG:3765 (Croatia CRS)."""
    return Point(500000, 5000000, srid=3765)

@pytest.fixture
def sample_polygon() -> Polygon:
    """Create a sample polygon geometry in EPSG:3765."""
    coords = [
        (500000, 5000000),
        (501000, 5000000),
        (501000, 5001000),
        (500000, 5001000),
        (500000, 5000000),
    ]
    return Polygon(coords, srid=3765)

@pytest.fixture
def sample_multipolygon() -> MultiPolygon:
    """Create a sample multipolygon geometry in EPSG:3765."""
    coords = [
        (500000, 5000000),
        (501000, 5000000),
        (501000, 5001000),
        (500000, 5001000),
        (500000, 5000000),
    ]
    polygon = Polygon(coords, srid=3765)
    return MultiPolygon(polygon, srid=3765)

@pytest.fixture
def sample_bbox() -> str:
    """Create a sample bounding box string for testing."""
    return "500000,5000000,501000,5001000"

@pytest.fixture
def sample_datetime() -> datetime:
    """Create a sample datetime for testing."""
    return timezone.now()

@pytest.fixture
def api_client() -> APIClient:
    """Create an API client for testing."""
    return APIClient()

@pytest.fixture
def api_request_factory() -> APIRequestFactory:
    """Create an API request factory for testing."""
    return APIRequestFactory()
