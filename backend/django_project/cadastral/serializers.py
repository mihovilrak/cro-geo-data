from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

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

class CadastralParcelSerializer(GeoFeatureModelSerializer):
    cadastral_municipality_code = serializers.IntegerField(
        source="cadastral_municipality.national_code", read_only=True
    )
    cadastral_municipality_name = serializers.CharField(
        source="cadastral_municipality.name", read_only=True
    )

    class Meta:
        model = CadastralParcel
        geo_field = "geom"
        fields = (
            "id",
            "parcel_code",
            "graphical_area",
            "updated_at",
            "cadastral_municipality_code",
            "cadastral_municipality_name",
        )

class AddressSerializer(GeoFeatureModelSerializer):
    street_name = serializers.CharField(source="street.name", read_only=True)
    settlement_name = serializers.CharField(
        source="street.settlement.name", read_only=True
    )
    municipality_name = serializers.CharField(
        source="street.settlement.municipality.name", read_only=True
    )
    county_name = serializers.CharField(
        source="street.settlement.municipality.county.name", read_only=True
    )

    class Meta:
        model = Address
        geo_field = "geom"
        fields = (
            "id",
            "house_number",
            "street_name",
            "settlement_name",
            "municipality_name",
            "county_name",
            "updated_at",
        )

class SettlementSerializer(GeoFeatureModelSerializer):
    municipality_name = serializers.CharField(
        source="municipality.name", read_only=True
    )
    county_name = serializers.CharField(
        source="municipality.county.name", read_only=True
    )

    class Meta:
        model = Settlement
        geo_field = "geom"
        fields = (
            "id",
            "national_code",
            "name",
            "municipality_name",
            "county_name",
            "updated_at",
        )

class StreetSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = StreetFeature
        geo_field = "geom"
        fields = (
            "id",
            "name",
            "unique_identifier",
            "settlement_code",
            "settlement_name",
            "municipality_name",
            "county_name",
        )

class CountrySerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Country
        geo_field = "geom"
        fields = (
            "id",
            "national_code",
            "name",
            "updated_at",
        )

class CountySerializer(GeoFeatureModelSerializer):
    class Meta:
        model = County
        geo_field = "geom"
        fields = (
            "id",
            "national_code",
            "name",
            "updated_at",
        )

class MunicipalitySerializer(GeoFeatureModelSerializer):
    county_name = serializers.CharField(
        source="county.name", read_only=True
    )
    county_code = serializers.IntegerField(
        source="county.national_code", read_only=True
    )

    class Meta:
        model = Municipality
        geo_field = "geom"
        fields = (
            "id",
            "national_code",
            "name",
            "county_code",
            "county_name",
            "updated_at",
        )

class CadastralMunicipalitySerializer(GeoFeatureModelSerializer):
    class Meta:
        model = CadastralMunicipality
        geo_field = "geom"
        fields = (
            "id",
            "national_code",
            "name",
            "harmonization_status",
            "updated_at",
        )

class PostalOfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostalOffice
        fields = (
            "id",
            "postal_code",
            "name",
            "updated_at",
        )

class BuildingSerializer(GeoFeatureModelSerializer):
    cadastral_municipality_code = serializers.IntegerField(
        source="cadastral_municipality.national_code", read_only=True
    )
    cadastral_municipality_name = serializers.CharField(
        source="cadastral_municipality.name", read_only=True
    )
    usage_code = serializers.IntegerField(
        source="usage.code", read_only=True
    )
    usage_name = serializers.CharField(
        source="usage.name", read_only=True
    )

    class Meta:
        model = Building
        geo_field = "geom"
        fields = (
            "id",
            "building_number",
            "cadastral_municipality_code",
            "cadastral_municipality_name",
            "usage_code",
            "usage_name",
            "updated_at",
        )

class UsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usage
        fields = (
            "code",
            "name",
            "updated_at",
        )
