"""
Comprehensive tests for cadastral serializers.
Tests serialization, field validation, and nested relationships.
"""
import pytest
from django.contrib.gis.geos import Point, MultiPolygon, Polygon
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory

from cadastral.serializers import (
    CountrySerializer,
    CountySerializer,
    MunicipalitySerializer,
    SettlementSerializer,
    StreetSerializer,
    AddressSerializer,
    CadastralMunicipalitySerializer,
    CadastralParcelSerializer,
    BuildingSerializer,
    PostalOfficeSerializer,
    UsageSerializer,
)
from cadastral.models import (
    Country,
    County,
    Municipality,
    Settlement,
    StreetFeature,
    Address,
    CadastralMunicipality,
    CadastralParcel,
    Building,
    PostalOffice,
    Usage,
)

@pytest.mark.django_db
class TestCountrySerializer:
    """Tests for CountrySerializer."""

    def test_country_serializer_fields(self) -> None:
        """Test CountrySerializer includes all expected fields."""
        serializer = CountrySerializer()
        expected_fields = {"id", "national_code", "name", "updated_at", "geom"}
        assert set(serializer.fields.keys()) == expected_fields

    def test_country_serializer_geo_field(self) -> None:
        """Test CountrySerializer uses correct geometry field."""
        serializer = CountrySerializer()
        assert serializer.Meta.geo_field == "geom"
        assert serializer.Meta.model == Country

@pytest.mark.django_db
class TestCountySerializer:
    """Tests for CountySerializer."""

    def test_county_serializer_fields(self) -> None:
        """Test CountySerializer includes all expected fields."""
        serializer = CountySerializer()
        expected_fields = {"id", "national_code", "name", "updated_at", "geom"}
        assert set(serializer.fields.keys()) == expected_fields

    def test_county_serializer_geo_field(self) -> None:
        """Test CountySerializer uses correct geometry field."""
        serializer = CountySerializer()
        assert serializer.Meta.geo_field == "geom"
        assert serializer.Meta.model == County

@pytest.mark.django_db
class TestMunicipalitySerializer:
    """Tests for MunicipalitySerializer."""

    def test_municipality_serializer_fields(self) -> None:
        """Test MunicipalitySerializer includes all expected fields."""
        serializer = MunicipalitySerializer()
        expected_fields = {
            "id",
            "national_code",
            "name",
            "county_code",
            "county_name",
            "updated_at",
            "geom",
        }
        assert set(serializer.fields.keys()) == expected_fields

    def test_municipality_serializer_includes_county_info(self) -> None:
        """Test MunicipalitySerializer includes county information."""
        serializer = MunicipalitySerializer()
        assert "county_code" in serializer.fields
        assert "county_name" in serializer.fields
        assert serializer.fields["county_code"].read_only is True
        assert serializer.fields["county_name"].read_only is True

    def test_municipality_serializer_geo_field(self) -> None:
        """Test MunicipalitySerializer uses correct geometry field."""
        serializer = MunicipalitySerializer()
        assert serializer.Meta.geo_field == "geom"
        assert serializer.Meta.model == Municipality

@pytest.mark.django_db
class TestSettlementSerializer:
    """Tests for SettlementSerializer."""

    def test_settlement_serializer_fields(self) -> None:
        """Test SettlementSerializer includes all expected fields."""
        serializer = SettlementSerializer()
        expected_fields = {
            "id",
            "national_code",
            "name",
            "municipality_name",
            "county_name",
            "updated_at",
            "geom",
        }
        assert set(serializer.fields.keys()) == expected_fields

    def test_settlement_serializer_includes_parent_info(self) -> None:
        """Test SettlementSerializer includes municipality and county information."""
        serializer = SettlementSerializer()
        assert "municipality_name" in serializer.fields
        assert "county_name" in serializer.fields
        assert serializer.fields["municipality_name"].read_only is True
        assert serializer.fields["county_name"].read_only is True

    def test_settlement_serializer_geo_field(self) -> None:
        """Test SettlementSerializer uses correct geometry field."""
        serializer = SettlementSerializer()
        assert serializer.Meta.geo_field == "geom"
        assert serializer.Meta.model == Settlement

@pytest.mark.django_db
class TestStreetSerializer:
    """Tests for StreetSerializer."""

    def test_street_serializer_fields(self) -> None:
        """Test StreetSerializer includes all expected fields."""
        serializer = StreetSerializer()
        expected_fields = {
            "id",
            "name",
            "unique_identifier",
            "settlement_code",
            "settlement_name",
            "municipality_name",
            "county_name",
            "geom",
        }
        assert set(serializer.fields.keys()) == expected_fields

    def test_street_serializer_uses_street_feature_model(self) -> None:
        """Test StreetSerializer uses StreetFeature model."""
        serializer = StreetSerializer()
        assert serializer.Meta.model == StreetFeature
        assert serializer.Meta.geo_field == "geom"

@pytest.mark.django_db
class TestAddressSerializer:
    """Tests for AddressSerializer."""

    def test_address_serializer_fields(self) -> None:
        """Test AddressSerializer includes all expected fields."""
        serializer = AddressSerializer()
        expected_fields = {
            "id",
            "house_number",
            "street_name",
            "settlement_name",
            "municipality_name",
            "county_name",
            "updated_at",
            "geom",
        }
        assert set(serializer.fields.keys()) == expected_fields

    def test_address_serializer_includes_hierarchy_info(self) -> None:
        """
        Test AddressSerializer includes street, settlement,
        municipality, and county information.
        """
        serializer = AddressSerializer()
        assert "street_name" in serializer.fields
        assert "settlement_name" in serializer.fields
        assert "municipality_name" in serializer.fields
        assert "county_name" in serializer.fields
        assert all(
            serializer.fields[field].read_only
            for field in ["street_name", "settlement_name", "municipality_name", "county_name"]
        )

    def test_address_serializer_geo_field(self) -> None:
        """Test AddressSerializer uses correct geometry field."""
        serializer = AddressSerializer()
        assert serializer.Meta.geo_field == "geom"
        assert serializer.Meta.model == Address

@pytest.mark.django_db
class TestCadastralMunicipalitySerializer:
    """Tests for CadastralMunicipalitySerializer."""

    def test_cadastral_municipality_serializer_fields(self) -> None:
        """Test CadastralMunicipalitySerializer includes all expected fields."""
        serializer = CadastralMunicipalitySerializer()
        expected_fields = {
            "id",
            "national_code",
            "name",
            "harmonization_status",
            "updated_at",
            "geom",
        }
        assert set(serializer.fields.keys()) == expected_fields

    def test_cadastral_municipality_serializer_geo_field(self) -> None:
        """Test CadastralMunicipalitySerializer uses correct geometry field."""
        serializer = CadastralMunicipalitySerializer()
        assert serializer.Meta.geo_field == "geom"
        assert serializer.Meta.model == CadastralMunicipality

@pytest.mark.django_db
class TestCadastralParcelSerializer:
    """Tests for CadastralParcelSerializer."""

    def test_cadastral_parcel_serializer_fields(self) -> None:
        """Test CadastralParcelSerializer includes all expected fields."""
        serializer = CadastralParcelSerializer()
        expected_fields = {
            "id",
            "parcel_code",
            "graphical_area",
            "updated_at",
            "cadastral_municipality_code",
            "cadastral_municipality_name",
            "geom",
        }
        assert set(serializer.fields.keys()) == expected_fields

    def test_cadastral_parcel_serializer_includes_municipality_info(self) -> None:
        """Test CadastralParcelSerializer includes municipality information."""
        serializer = CadastralParcelSerializer()
        assert "cadastral_municipality_code" in serializer.fields
        assert "cadastral_municipality_name" in serializer.fields
        assert serializer.fields["cadastral_municipality_code"].read_only is True
        assert serializer.fields["cadastral_municipality_name"].read_only is True

    def test_cadastral_parcel_serializer_geo_field(self) -> None:
        """Test CadastralParcelSerializer uses correct geometry field."""
        serializer = CadastralParcelSerializer()
        assert serializer.Meta.geo_field == "geom"
        assert serializer.Meta.model == CadastralParcel

@pytest.mark.django_db
class TestBuildingSerializer:
    """Tests for BuildingSerializer."""

    def test_building_serializer_fields(self) -> None:
        """Test BuildingSerializer includes all expected fields."""
        serializer = BuildingSerializer()
        expected_fields = {
            "id",
            "building_number",
            "cadastral_municipality_code",
            "cadastral_municipality_name",
            "usage_code",
            "usage_name",
            "updated_at",
            "geom",
        }
        assert set(serializer.fields.keys()) == expected_fields

    def test_building_serializer_includes_related_info(self) -> None:
        """Test BuildingSerializer includes municipality and usage information."""
        serializer = BuildingSerializer()
        assert "cadastral_municipality_code" in serializer.fields
        assert "cadastral_municipality_name" in serializer.fields
        assert "usage_code" in serializer.fields
        assert "usage_name" in serializer.fields
        assert all(
            serializer.fields[field].read_only
            for field in [
                "cadastral_municipality_code",
                "cadastral_municipality_name",
                "usage_code",
                "usage_name",
            ]
        )

    def test_building_serializer_geo_field(self) -> None:
        """Test BuildingSerializer uses correct geometry field."""
        serializer = BuildingSerializer()
        assert serializer.Meta.geo_field == "geom"
        assert serializer.Meta.model == Building

@pytest.mark.django_db
class TestPostalOfficeSerializer:
    """Tests for PostalOfficeSerializer."""

    def test_postal_office_serializer_fields(self) -> None:
        """Test PostalOfficeSerializer includes all expected fields."""
        serializer = PostalOfficeSerializer()
        expected_fields = {"id", "postal_code", "name", "updated_at"}
        assert set(serializer.fields.keys()) == expected_fields

    def test_postal_office_serializer_no_geometry(self) -> None:
        """Test PostalOfficeSerializer does not include geometry (no spatial data)."""
        serializer = PostalOfficeSerializer()
        assert "geometry" not in serializer.fields
        assert serializer.Meta.model == PostalOffice

@pytest.mark.django_db
class TestUsageSerializer:
    """Tests for UsageSerializer."""

    def test_usage_serializer_fields(self) -> None:
        """Test UsageSerializer includes all expected fields."""
        serializer = UsageSerializer()
        expected_fields = {"code", "name", "updated_at"}
        assert set(serializer.fields.keys()) == expected_fields

    def test_usage_serializer_no_geometry(self) -> None:
        """Test UsageSerializer does not include geometry (no spatial data)."""
        serializer = UsageSerializer()
        assert "geometry" not in serializer.fields
        assert serializer.Meta.model == Usage
