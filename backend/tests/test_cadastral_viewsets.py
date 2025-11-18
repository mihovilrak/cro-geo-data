import pytest
from rest_framework.test import APIRequestFactory
from rest_framework.serializers import Serializer
from rest_framework import viewsets

from django.conf import settings
from django.urls import resolve

from cadastral import views
from cadastral.serializers import (
    AddressSerializer,
    BuildingSerializer,
    CadastralMunicipalitySerializer,
    CadastralParcelSerializer,
    CountrySerializer,
    CountySerializer,
    MunicipalitySerializer,
    PostalOfficeSerializer,
    SettlementSerializer,
    StreetSerializer,
    UsageSerializer,
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
    "viewset,serializer,has_bbox",
    [
        (views.CountryViewSet, CountrySerializer, True),
        (views.CountyViewSet, CountySerializer, True),
        (views.MunicipalityViewSet, MunicipalitySerializer, True),
        (views.SettlementViewSet, SettlementSerializer, True),
        (views.StreetViewSet, StreetSerializer, True),
        (views.AddressViewSet, AddressSerializer, True),
        (views.CadastralMunicipalityViewSet, CadastralMunicipalitySerializer, True),
        (views.CadastralParcelViewSet, CadastralParcelSerializer, True),
        (views.BuildingViewSet, BuildingSerializer, True),
        (views.PostalOfficeViewSet, PostalOfficeSerializer, False),
        (views.UsageViewSet, UsageSerializer, False),
    ],
)
def test_viewsets_expose_correct_serializer(
    viewset: viewsets.ReadOnlyModelViewSet,
    serializer: type[Serializer],
    has_bbox: bool,
) -> None:
    """
    Test that viewsets expose the correct serializer and bbox filter field.

    Args:
        viewset (viewsets.ReadOnlyModelViewSet): The viewset to test.
        serializer (Serializer): The serializer to test.
        has_bbox (bool): Whether the viewset should have bbox filtering.
    """
    assert viewset.serializer_class is serializer
    if has_bbox:
        assert viewset.bbox_filter_field == "geom"
    else:
        assert not hasattr(viewset, "bbox_filter_field") or viewset.bbox_filter_field is None

def test_router_registers_all_endpoints() -> None:
    """
    Test that the router registers all endpoints matching the database schema.
    """
    assert resolve("/api/country/").func.cls is views.CountryViewSet
    assert resolve("/api/counties/").func.cls is views.CountyViewSet
    assert resolve("/api/municipalities/").func.cls is views.MunicipalityViewSet
    assert resolve("/api/settlements/").func.cls is views.SettlementViewSet
    assert resolve("/api/streets/").func.cls is views.StreetViewSet
    assert resolve("/api/addresses/").func.cls is views.AddressViewSet
    assert resolve("/api/postal_offices/").func.cls is views.PostalOfficeViewSet
    assert resolve("/api/cadastral_municipalities/").func.cls is views.CadastralMunicipalityViewSet
    assert resolve("/api/cadastral_parcels/").func.cls is views.CadastralParcelViewSet
    assert resolve("/api/buildings/").func.cls is views.BuildingViewSet
    assert resolve("/api/usages/").func.cls is views.UsageViewSet


