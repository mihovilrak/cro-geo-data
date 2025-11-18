from django.utils.functional import cached_property
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework_gis.filters import InBBoxFilter

from .filters import (
    CadastralParcelFilterSet,
    CountyBoundaryFilterSet,
    MunicipalityBoundaryFilterSet,
)
from .models import CadastralParcel, County, Municipality
from .serializers import (
    AdministrativeBoundarySerializer,
    CadastralParcelSerializer,
)


class CadastralParcelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only GeoJSON endpoint backed by ``dkp.cadastral_parcels``.
    Supports bbox queries, attribute filters, and fuzzy search.
    """

    queryset = (
        CadastralParcel.objects.select_related("cadastral_municipality")
        .order_by("id")
    )
    serializer_class = CadastralParcelSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, InBBoxFilter]
    filterset_class = CadastralParcelFilterSet
    search_fields = ("parcel_code", "cadastral_municipality__name")
    bbox_filter_field = "geom"
    bbox_filter_include_overlapping = True


class AdministrativeBoundaryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Serves either counties or municipalities depending on ``admin_type`` query
    parameter. Defaults to municipalities to match the frontend expectations.
    """

    serializer_class = AdministrativeBoundarySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, InBBoxFilter]
    search_fields = ("name",)
    bbox_filter_field = "geom"
    bbox_filter_include_overlapping = True

    def get_queryset(self):
        if self.admin_type == "county":
            return County.objects.all().order_by("name")
        return (
            Municipality.objects.select_related("county")
            .order_by("name")
        )

    def get_filterset_class(self):
        if self.admin_type == "county":
            return CountyBoundaryFilterSet
        return MunicipalityBoundaryFilterSet

    @cached_property
    def admin_type(self) -> str:
        """
        Normalize the ``admin_type`` query parameter once per request.
        """

        value = self.request.query_params.get("admin_type", "municipality")
        value = value.lower().strip()
        if value not in {"municipality", "county"}:
            return "municipality"
        return value


