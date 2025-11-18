"""
Reusable ``django-filter`` filter sets for GeoDjango viewsets.
"""
import django_filters

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

class CadastralParcelFilterSet(django_filters.FilterSet):
    """
    Filter set for cadastral parcels.
    """
    parcel_id = django_filters.CharFilter(
        field_name="parcel_code",
        lookup_expr="iexact",
        label="Parcel identifier",
    )
    cadastral_municipality_code = django_filters.NumberFilter(
        field_name="cadastral_municipality__national_code",
        label="Cadastral municipality code",
    )
    cadastral_municipality = django_filters.CharFilter(
        field_name="cadastral_municipality__name",
        lookup_expr="icontains",
        label="Cadastral municipality name",
    )
    updated_after = django_filters.IsoDateTimeFilter(
        field_name="updated_at",
        lookup_expr="gte",
        label="Updated after (ISO 8601)",
    )
    updated_before = django_filters.IsoDateTimeFilter(
        field_name="updated_at",
        lookup_expr="lte",
        label="Updated before (ISO 8601)",
    )

    class Meta:
        model = CadastralParcel
        fields = (
            "parcel_id",
            "cadastral_municipality_code",
            "cadastral_municipality",
            "updated_after",
            "updated_before",
        )

class MunicipalityBoundaryFilterSet(django_filters.FilterSet):
    """
    Filter set for municipality boundaries.
    """
    national_code = django_filters.NumberFilter(field_name="national_code")
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    county_code = django_filters.NumberFilter(
        field_name="county__national_code",
        label="Parent county code",
    )
    county_name = django_filters.CharFilter(
        field_name="county__name",
        lookup_expr="icontains",
        label="Parent county name",
    )

    class Meta:
        model = Municipality
        fields = (
            "national_code",
            "name",
            "county_code",
            "county_name",
        )

class CountyBoundaryFilterSet(django_filters.FilterSet):
    """
    Filter set for county boundaries.
    """
    national_code = django_filters.NumberFilter(field_name="national_code")
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = County
        fields = (
            "national_code",
            "name",
        )

class SettlementFilterSet(django_filters.FilterSet):
    """
    Filter set for settlements.
    """
    national_code = django_filters.NumberFilter(field_name="national_code")
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    municipality_code = django_filters.NumberFilter(
        field_name="municipality__national_code"
    )
    county_code = django_filters.NumberFilter(
        field_name="municipality__county__national_code"
    )

    class Meta:
        model = Settlement
        fields = (
            "national_code",
            "name",
            "municipality_code",
            "county_code",
        )

class StreetFilterSet(django_filters.FilterSet):
    """
    Filter set for streets.
    """
    settlement_code = django_filters.NumberFilter(field_name="settlement_code")
    settlement_name = django_filters.CharFilter(
        field_name="settlement_name", lookup_expr="icontains"
    )
    municipality_name = django_filters.CharFilter(
        field_name="municipality_name", lookup_expr="icontains"
    )
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = StreetFeature
        fields = (
            "settlement_code",
            "settlement_name",
            "municipality_name",
            "name",
        )

class AddressFilterSet(django_filters.FilterSet):
    """
    Filter set for addresses.
    """
    street_id = django_filters.NumberFilter(field_name="street_id")
    house_number = django_filters.CharFilter(
        field_name="house_number", lookup_expr="icontains"
    )
    settlement_code = django_filters.NumberFilter(
        field_name="street__settlement__national_code"
    )
    municipality_code = django_filters.NumberFilter(
        field_name="street__settlement__municipality__national_code"
    )

    class Meta:
        model = Address
        fields = (
            "street_id",
            "house_number",
            "settlement_code",
            "municipality_code",
        )

class CountryFilterSet(django_filters.FilterSet):
    """
    Filter set for country.
    """
    national_code = django_filters.NumberFilter(field_name="national_code")
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Country
        fields = (
            "national_code",
            "name",
        )

class CadastralMunicipalityFilterSet(django_filters.FilterSet):
    """
    Filter set for cadastral municipalities.
    """
    national_code = django_filters.NumberFilter(field_name="national_code")
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    harmonization_status = django_filters.NumberFilter(field_name="harmonization_status")

    class Meta:
        model = CadastralMunicipality
        fields = (
            "national_code",
            "name",
            "harmonization_status",
        )

class PostalOfficeFilterSet(django_filters.FilterSet):
    """
    Filter set for postal offices.
    """
    postal_code = django_filters.NumberFilter(field_name="postal_code")
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = PostalOffice
        fields = (
            "postal_code",
            "name",
        )

class BuildingFilterSet(django_filters.FilterSet):
    """
    Filter set for buildings.
    """
    building_number = django_filters.NumberFilter(field_name="building_number")
    cadastral_municipality_code = django_filters.NumberFilter(
        field_name="cadastral_municipality__national_code"
    )
    cadastral_municipality = django_filters.CharFilter(
        field_name="cadastral_municipality__name",
        lookup_expr="icontains"
    )
    usage_code = django_filters.NumberFilter(field_name="usage__code")

    class Meta:
        model = Building
        fields = (
            "building_number",
            "cadastral_municipality_code",
            "cadastral_municipality",
            "usage_code",
        )

class UsageFilterSet(django_filters.FilterSet):
    """
    Filter set for usage codes.
    """
    code = django_filters.NumberFilter(field_name="code")
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Usage
        fields = (
            "code",
            "name",
        )
