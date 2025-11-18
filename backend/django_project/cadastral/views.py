from django.conf import settings
from django.db.models import QuerySet
from django.utils.functional import cached_property
from django_filters.rest_framework import DjangoFilterBackend
import django_filters
from rest_framework import filters, viewsets
from rest_framework.request import Request
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_gis.filters import InBBoxFilter

from .filters import (
    AddressFilterSet,
    CadastralParcelFilterSet,
    CountyBoundaryFilterSet,
    MunicipalityBoundaryFilterSet,
    SettlementFilterSet,
    StreetFilterSet,
)
from .models import Address, CadastralParcel, County, Municipality, Settlement, StreetFeature
from .serializers import (
    AddressSerializer,
    AdministrativeBoundarySerializer,
    CadastralParcelSerializer,
    SettlementSerializer,
    StreetSerializer,
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

    def get_queryset(self) -> QuerySet[County | Municipality]:
        """
        Returns the queryset of counties or municipalities
        depending on the ``admin_type`` query parameter.

        Returns:
            QuerySet[County | Municipality]: The queryset of counties or municipalities.
        """
        if self.admin_type == "county":
            return County.objects.all().order_by("name")
        return (
            Municipality.objects.select_related("county")
            .order_by("name")
        )

    def get_filterset_class(self) -> type[django_filters.FilterSet]:
        """
        Returns the filterset class for counties or municipalities
        depending on the ``admin_type`` query parameter.

        Returns:
            type[django_filters.FilterSet]: The filterset class
                    for counties or municipalities.
        """
        if self.admin_type == "county":
            return CountyBoundaryFilterSet
        return MunicipalityBoundaryFilterSet

    @cached_property
    def admin_type(self) -> str:
        """
        Normalize the ``admin_type`` query parameter once per request.

        Returns:
            str: The normalized ``admin_type`` query parameter.
        """

        value = self.request.query_params.get("admin_type", "municipality")
        value = value.lower().strip()
        if value not in {"municipality", "county"}:
            return "municipality"
        return value

class SettlementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only GeoJSON endpoint backed by ``rpj.settlements``.
    Supports bbox queries, attribute filters, and fuzzy search.
    """
    queryset = (
        Settlement.objects.select_related("municipality__county")
        .order_by("name")
    )
    serializer_class = SettlementSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, InBBoxFilter]
    filterset_class = SettlementFilterSet
    search_fields = ("name", "municipality__name", "municipality__county__name")
    bbox_filter_field = "geom"
    bbox_filter_include_overlapping = True

class StreetViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only GeoJSON endpoint backed by ``gs.mv_streets``.
    Supports bbox queries, attribute filters, and fuzzy search.
    """
    queryset = StreetFeature.objects.all().order_by("name")
    serializer_class = StreetSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, InBBoxFilter]
    filterset_class = StreetFilterSet
    search_fields = (
        "name",
        "settlement_name",
        "municipality_name",
        "county_name",
    )
    bbox_filter_field = "geom"
    bbox_filter_include_overlapping = True


class AddressViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only GeoJSON endpoint backed by ``rpj.addresses``.
    Supports bbox queries, attribute filters, and fuzzy search.
    """
    queryset = (
        Address.objects.select_related(
            "street",
            "street__settlement",
            "street__settlement__municipality",
            "street__settlement__municipality__county",
        ).order_by("id")
    )
    serializer_class = AddressSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, InBBoxFilter]
    filterset_class = AddressFilterSet
    search_fields = (
        "house_number",
        "street__name",
        "street__settlement__name",
    )
    bbox_filter_field = "geom"
    bbox_filter_include_overlapping = True

class LayerCatalogView(APIView):
    """
    View to serve the layer catalog consumed by the frontend layer switcher
    and the ETL/GeoServer automation.
    """
    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        """
        Returns the layer catalog consumed by the frontend layer switcher
        and the ETL/GeoServer automation.
        """
        return Response(settings.LAYER_CATALOG)
