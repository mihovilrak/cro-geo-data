from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from .models import (
    Address,
    CadastralParcel,
    County,
    Municipality,
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


class AdministrativeBoundarySerializer(GeoFeatureModelSerializer):
    admin_type = serializers.SerializerMethodField()
    parent_code = serializers.SerializerMethodField()
    parent_name = serializers.SerializerMethodField()

    class Meta:
        model = Municipality
        geo_field = "geom"
        fields = (
            "id",
            "national_code",
            "name",
            "updated_at",
            "admin_type",
            "parent_code",
            "parent_name",
        )

    def get_admin_type(self, obj) -> str:
        if isinstance(obj, County):
            return "county"
        return "municipality"

    def get_parent_code(self, obj):
        if isinstance(obj, Municipality) and obj.county_id is not None:
            return obj.county_id
        return None

    def get_parent_name(self, obj):
        if isinstance(obj, Municipality) and obj.county:
            return obj.county.name
        return None


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


