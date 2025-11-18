import pytest
from rest_framework.test import APIRequestFactory
from rest_framework.serializers import Serializer
from rest_framework import viewsets

from django.conf import settings
from django.urls import resolve

from cadastral import views
from cadastral.serializers import (
    AddressSerializer,
    CadastralParcelSerializer,
    SettlementSerializer,
    StreetSerializer,
)

def test_layer_catalog_matches_settings() -> None:
    """
    Test that the layer catalog matches the settings.
    """
    factory = APIRequestFactory()
    request = factory.get("/api/layers/")
    response = views.LayerCatalogView.as_view()(request)
    assert response.status_code == 200
    assert response.data == settings.LAYER_CATALOG

@pytest.mark.parametrize(
    "viewset,serializer",
    [
        (views.CadastralParcelViewSet, CadastralParcelSerializer),
        (views.SettlementViewSet, SettlementSerializer),
        (views.StreetViewSet, StreetSerializer),
        (views.AddressViewSet, AddressSerializer),
    ],
)
def test_geo_viewsets_expose_geojson(
    viewset: viewsets.ReadOnlyModelViewSet,
    serializer: type[Serializer]
) -> None:
    """
    Test that the GeoJSON viewsets expose the correct serializer and bounding box filter field.

    Args:
        viewset (viewsets.ReadOnlyModelViewSet): The viewset to test.
        serializer (Serializer): The serializer to test.
    """
    assert viewset.serializer_class is serializer
    assert viewset.bbox_filter_field == "geom"

def test_router_registers_new_endpoints() -> None:
    """
    Test that the router registers the new endpoints.
    """
    assert resolve("/api/settlements/").func.cls is views.SettlementViewSet
    assert resolve("/api/streets/").func.cls is views.StreetViewSet
    assert resolve("/api/addresses/").func.cls is views.AddressViewSet


