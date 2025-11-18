"""
Reusable ``django-filter`` filter sets for GeoDjango viewsets.
"""
import django_filters

from .models import CadastralParcel, County, Municipality


class CadastralParcelFilterSet(django_filters.FilterSet):
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
    national_code = django_filters.NumberFilter(field_name="national_code")
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = County
        fields = (
            "national_code",
            "name",
        )


