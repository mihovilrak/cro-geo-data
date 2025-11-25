"""URL configuration for the cadastral app.

This module defines the URL routes for cadastral-related API endpoints,
matching the database schema structure.

Routes:
    - /country/
    - /counties/
    - /municipalities/
    - /settlements/
    - /streets/
    - /addresses/
    - /postal_offices/
    - /cadastral_municipalities/
    - /cadastral_parcels/
    - /buildings/
    - /usages/
    - /layers/
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AddressViewSet,
    BuildingViewSet,
    CadastralMunicipalityViewSet,
    CadastralParcelViewSet,
    CountryViewSet,
    CountyViewSet,
    ETLRunViewSet,
    LayerCatalogView,
    MunicipalityViewSet,
    PostalOfficeViewSet,
    SettlementViewSet,
    StreetViewSet,
    UsageViewSet,
)

router = DefaultRouter()
router.register(r"country", CountryViewSet, basename="country")
router.register(r"counties", CountyViewSet, basename="county")
router.register(r"municipalities", MunicipalityViewSet, basename="municipality")
router.register(r"settlements", SettlementViewSet, basename="settlement")
router.register(r"streets", StreetViewSet, basename="street")
router.register(r"addresses", AddressViewSet, basename="address")
router.register(r"postal_offices", PostalOfficeViewSet, basename="postaloffice")
router.register(
    r"cadastral_municipalities",
    CadastralMunicipalityViewSet,
    basename="cadastralmunicipality",
)
router.register(
    r"cadastral_parcels", CadastralParcelViewSet, basename="cadastralparcel"
)
router.register(r"buildings", BuildingViewSet, basename="building")
router.register(r"usages", UsageViewSet, basename="usage")
router.register(r"etl/runs", ETLRunViewSet, basename="etlrun")

urlpatterns = [
    path("", include(router.urls)),
    path("layers/", LayerCatalogView.as_view(), name="layer-catalog"),
]
