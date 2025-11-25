from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework_gis.filters import InBBoxFilter

from .filters import (
    AddressFilterSet,
    BuildingFilterSet,
    CadastralMunicipalityFilterSet,
    CadastralParcelFilterSet,
    CountryFilterSet,
    CountyBoundaryFilterSet,
    ETLRunFilterSet,
    MunicipalityBoundaryFilterSet,
    PostalOfficeFilterSet,
    SettlementFilterSet,
    StreetFilterSet,
    UsageFilterSet,
)
from .models import (
    Address,
    Building,
    CadastralMunicipality,
    CadastralParcel,
    Country,
    County,
    Municipality,
    PostalOffice,
    Settlement,
    StreetFeature,
    Usage,
)
from .etl_models import ETLRun
from .etl_serializers import ETLRunSerializer
from .serializers import (
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

class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only GeoJSON endpoint backed by ``rpj.country``.
    Supports bbox queries, attribute filters, and fuzzy search.
    """
    queryset = Country.objects.all().order_by("name")
    serializer_class = CountrySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, InBBoxFilter]
    filterset_class = CountryFilterSet
    search_fields = ("name",)
    bbox_filter_field = "geom"
    bbox_filter_include_overlapping = True

class CountyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only GeoJSON endpoint backed by ``rpj.counties``.
    Supports bbox queries, attribute filters, and fuzzy search.
    """
    queryset = County.objects.all().order_by("name")
    serializer_class = CountySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, InBBoxFilter]
    filterset_class = CountyBoundaryFilterSet
    search_fields = ("name",)
    bbox_filter_field = "geom"
    bbox_filter_include_overlapping = True

class MunicipalityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only GeoJSON endpoint backed by ``rpj.municipalities``.
    Supports bbox queries, attribute filters, and fuzzy search.
    """
    queryset = (
        Municipality.objects.select_related("county")
        .order_by("name")
    )
    serializer_class = MunicipalitySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, InBBoxFilter]
    filterset_class = MunicipalityBoundaryFilterSet
    search_fields = ("name", "county__name")
    bbox_filter_field = "geom"
    bbox_filter_include_overlapping = True

class CadastralMunicipalityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only GeoJSON endpoint backed by ``dkp.cadastral_municipalities``.
    Supports bbox queries, attribute filters, and fuzzy search.
    """
    queryset = CadastralMunicipality.objects.all().order_by("name")
    serializer_class = CadastralMunicipalitySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, InBBoxFilter]
    filterset_class = CadastralMunicipalityFilterSet
    search_fields = ("name",)
    bbox_filter_field = "geom"
    bbox_filter_include_overlapping = True

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

class BuildingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only GeoJSON endpoint backed by ``dkp.buildings``.
    Supports bbox queries, attribute filters, and fuzzy search.
    """
    queryset = (
        Building.objects.select_related("cadastral_municipality", "usage")
        .order_by("id")
    )
    serializer_class = BuildingSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, InBBoxFilter]
    filterset_class = BuildingFilterSet
    search_fields = ("building_number", "cadastral_municipality__name", "usage__name")
    bbox_filter_field = "geom"
    bbox_filter_include_overlapping = True

class PostalOfficeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only endpoint backed by ``rpj.postal_offices``.
    Supports attribute filters and fuzzy search.
    Note: Postal offices do not have geometry.
    """
    queryset = PostalOffice.objects.all().order_by("postal_code")
    serializer_class = PostalOfficeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = PostalOfficeFilterSet
    search_fields = ("name", "postal_code")

class UsageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only endpoint backed by ``dkp.usages``.
    Supports attribute filters and fuzzy search.
    Note: Usage codes do not have geometry.
    """
    queryset = Usage.objects.all().order_by("code")
    serializer_class = UsageSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = UsageFilterSet
    search_fields = ("name",)

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

class ETLRunViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only endpoint for ETL pipeline run history.

    Provides access to journal.etl_runs table showing:
    - Run start/completion times
    - Success/failure status
    - Record counts (inserted/deleted/updated)
    - Duration and error messages
    """
    queryset = ETLRun.objects.all()
    serializer_class = ETLRunSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ETLRunFilterSet
    search_fields = ["error_message"]
