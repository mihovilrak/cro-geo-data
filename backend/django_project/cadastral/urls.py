"""URL configuration for the cadastral app.

This module defines the URL routes for cadastral-related API endpoints,
including management of parcels, administrative boundaries, settlements,
streets, addresses, and layer catalog views.

Routes:
    - /parcels/
    - /admin_boundaries/
    - /settlements/
    - /streets/
    - /addresses/
    - /layers/
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AddressViewSet,
    AdministrativeBoundaryViewSet,
    CadastralParcelViewSet,
    LayerCatalogView,
    SettlementViewSet,
    StreetViewSet,
)

router = DefaultRouter()
router.register(r"parcels", CadastralParcelViewSet, basename="parcel")
router.register(
    r"admin_boundaries",
    AdministrativeBoundaryViewSet,
    basename="admboundary",
)
router.register(r"settlements", SettlementViewSet, basename="settlement")
router.register(r"streets", StreetViewSet, basename="street")
router.register(r"addresses", AddressViewSet, basename="address")

urlpatterns = [
    path("", include(router.urls)),
    path("layers/", LayerCatalogView.as_view(), name="layer-catalog"),
]
