from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CadastralParcelViewSet, AdministrativeBoundaryViewSet

router = DefaultRouter()
router.register(
    r"parcels",
    CadastralParcelViewSet,
    basename="parcel"
)
router.register(
    r"admin_boundaries",
    AdministrativeBoundaryViewSet,
    basename="admboundary"
)

urlpatterns = [
    path("", include(router.urls)),
]

