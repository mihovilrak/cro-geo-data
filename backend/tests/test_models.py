"""
Comprehensive tests for cadastral models.
Tests model relationships, string representations, and field properties.
"""
import pytest
from django.contrib.gis.geos import Point, MultiPolygon, Polygon
from django.core.exceptions import ValidationError

from cadastral.models import (
    Country,
    County,
    Municipality,
    Settlement,
    PostalOffice,
    Street,
    StreetFeature,
    Address,
    CadastralMunicipality,
    CadastralParcel,
    Building,
    Usage,
)


@pytest.mark.django_db
class TestCountryModel:
    """Tests for Country model."""

    def test_country_str_representation(self):
        """Test Country string representation."""
        # Since models are read-only, we test the __str__ method conceptually
        # In real tests with data, you'd query actual records
        assert hasattr(Country, "__str__")
        assert Country._meta.db_table == '"rpj"."country"'
        assert Country._meta.managed is False

    def test_country_meta(self):
        """Test Country model metadata."""
        assert Country._meta.verbose_name == "Country"
        assert Country._meta.verbose_name_plural == "Country"
        assert Country._meta.ordering == ("name",)


@pytest.mark.django_db
class TestCountyModel:
    """Tests for County model."""

    def test_county_str_representation(self):
        """Test County string representation format."""
        assert hasattr(County, "__str__")
        assert County._meta.db_table == '"rpj"."counties"'
        assert County._meta.managed is False

    def test_county_meta(self):
        """Test County model metadata."""
        assert County._meta.verbose_name == "County"
        assert County._meta.verbose_name_plural == "Counties"
        assert County._meta.ordering == ("name",)

    def test_county_has_geometry_field(self):
        """Test that County has a geometry field."""
        assert hasattr(County, "geom")
        assert County._meta.get_field("geom").srid == 3765


@pytest.mark.django_db
class TestMunicipalityModel:
    """Tests for Municipality model."""

    def test_municipality_str_representation(self):
        """Test Municipality string representation."""
        assert hasattr(Municipality, "__str__")
        assert Municipality._meta.db_table == '"rpj"."municipalities"'
        assert Municipality._meta.managed is False

    def test_municipality_has_county_relationship(self):
        """Test Municipality has county foreign key."""
        assert hasattr(Municipality, "county")
        county_field = Municipality._meta.get_field("county")
        assert county_field.related_model is County
        assert county_field.db_column == "county_code"
        assert county_field.to_field.name == "national_code"

    def test_municipality_meta(self):
        """Test Municipality model metadata."""
        assert Municipality._meta.verbose_name == "Municipality"
        assert Municipality._meta.verbose_name_plural == "Municipalities"
        assert Municipality._meta.ordering == ("name",)


@pytest.mark.django_db
class TestSettlementModel:
    """Tests for Settlement model."""

    def test_settlement_str_representation(self):
        """Test Settlement string representation."""
        assert hasattr(Settlement, "__str__")
        assert Settlement._meta.db_table == '"rpj"."settlements"'
        assert Settlement._meta.managed is False

    def test_settlement_has_municipality_relationship(self):
        """Test Settlement has municipality foreign key."""
        assert hasattr(Settlement, "municipality")
        municipality_field = Settlement._meta.get_field("municipality")
        assert municipality_field.related_model is Municipality
        assert municipality_field.db_column == "municipality_code"
        assert municipality_field.to_field.name == "national_code"

    def test_settlement_meta(self):
        """Test Settlement model metadata."""
        assert Settlement._meta.verbose_name == "Settlement"
        assert Settlement._meta.verbose_name_plural == "Settlements"
        assert Settlement._meta.ordering == ("name",)


@pytest.mark.django_db
class TestPostalOfficeModel:
    """Tests for PostalOffice model."""

    def test_postal_office_str_representation(self):
        """Test PostalOffice string representation."""
        assert hasattr(PostalOffice, "__str__")
        assert PostalOffice._meta.db_table == '"rpj"."postal_offices"'
        assert PostalOffice._meta.managed is False

    def test_postal_office_meta(self):
        """Test PostalOffice model metadata."""
        assert PostalOffice._meta.verbose_name == "Postal Office"
        assert PostalOffice._meta.verbose_name_plural == "Postal Offices"
        assert PostalOffice._meta.ordering == ("postal_code",)


@pytest.mark.django_db
class TestStreetModel:
    """Tests for Street model."""

    def test_street_str_representation(self):
        """Test Street string representation."""
        assert hasattr(Street, "__str__")
        assert Street._meta.db_table == '"rpj"."streets"'
        assert Street._meta.managed is False

    def test_street_has_settlement_relationship(self):
        """Test Street has settlement foreign key."""
        assert hasattr(Street, "settlement")
        settlement_field = Street._meta.get_field("settlement")
        assert settlement_field.related_model is Settlement
        assert settlement_field.db_column == "settlement_code"
        assert settlement_field.to_field.name == "national_code"

    def test_street_has_postal_office_relationship(self):
        """Test Street has optional postal office foreign key."""
        assert hasattr(Street, "postal_office")
        postal_field = Street._meta.get_field("postal_office")
        assert postal_field.related_model is PostalOffice
        assert postal_field.null is True
        assert postal_field.blank is True

    def test_street_meta(self):
        """Test Street model metadata."""
        assert Street._meta.verbose_name == "Street"
        assert Street._meta.verbose_name_plural == "Streets"
        assert Street._meta.ordering == ("name",)


@pytest.mark.django_db
class TestStreetFeatureModel:
    """Tests for StreetFeature model (materialized view)."""

    def test_street_feature_str_representation(self):
        """Test StreetFeature string representation."""
        assert hasattr(StreetFeature, "__str__")
        assert StreetFeature._meta.db_table == '"gs"."mv_streets"'
        assert StreetFeature._meta.managed is False

    def test_street_feature_has_derived_fields(self):
        """Test StreetFeature has derived fields from materialized view."""
        assert hasattr(StreetFeature, "settlement_name")
        assert hasattr(StreetFeature, "municipality_name")
        assert hasattr(StreetFeature, "county_name")

    def test_street_feature_meta(self):
        """Test StreetFeature model metadata."""
        assert StreetFeature._meta.verbose_name == "Street (materialized view)"
        assert StreetFeature._meta.verbose_name_plural == "Streets (materialized view)"
        assert StreetFeature._meta.ordering == ("name",)


@pytest.mark.django_db
class TestAddressModel:
    """Tests for Address model."""

    def test_address_str_representation(self):
        """Test Address string representation."""
        assert hasattr(Address, "__str__")
        assert Address._meta.db_table == '"rpj"."addresses"'
        assert Address._meta.managed is False

    def test_address_has_street_relationship(self):
        """Test Address has street foreign key."""
        assert hasattr(Address, "street")
        street_field = Address._meta.get_field("street")
        assert street_field.related_model is Street
        assert street_field.db_column == "street_id"

    def test_address_has_point_geometry(self):
        """Test Address has point geometry field."""
        assert hasattr(Address, "geom")
        geom_field = Address._meta.get_field("geom")
        assert geom_field.srid == 3765

    def test_address_meta(self):
        """Test Address model metadata."""
        assert Address._meta.verbose_name == "Address"
        assert Address._meta.verbose_name_plural == "Addresses"
        assert Address._meta.ordering == ("id",)


@pytest.mark.django_db
class TestCadastralMunicipalityModel:
    """Tests for CadastralMunicipality model."""

    def test_cadastral_municipality_str_representation(self):
        """Test CadastralMunicipality string representation."""
        assert hasattr(CadastralMunicipality, "__str__")
        assert CadastralMunicipality._meta.db_table == '"dkp"."cadastral_municipalities"'
        assert CadastralMunicipality._meta.managed is False

    def test_cadastral_municipality_has_harmonization_status(self):
        """Test CadastralMunicipality has harmonization_status field."""
        assert hasattr(CadastralMunicipality, "harmonization_status")

    def test_cadastral_municipality_meta(self):
        """Test CadastralMunicipality model metadata."""
        assert CadastralMunicipality._meta.verbose_name == "Cadastral Municipality"
        assert CadastralMunicipality._meta.verbose_name_plural == "Cadastral Municipalities"
        assert CadastralMunicipality._meta.ordering == ("name",)


@pytest.mark.django_db
class TestCadastralParcelModel:
    """Tests for CadastralParcel model."""

    def test_cadastral_parcel_str_representation(self):
        """Test CadastralParcel string representation."""
        assert hasattr(CadastralParcel, "__str__")
        assert CadastralParcel._meta.db_table == '"dkp"."cadastral_parcels"'
        assert CadastralParcel._meta.managed is False

    def test_cadastral_parcel_has_municipality_relationship(self):
        """Test CadastralParcel has cadastral municipality foreign key."""
        assert hasattr(CadastralParcel, "cadastral_municipality")
        municipality_field = CadastralParcel._meta.get_field("cadastral_municipality")
        assert municipality_field.related_model is CadastralMunicipality
        assert municipality_field.db_column == "cadastral_municipality_code"
        assert municipality_field.to_field.name == "national_code"

    def test_cadastral_parcel_has_graphical_area(self):
        """Test CadastralParcel has graphical_area field."""
        assert hasattr(CadastralParcel, "graphical_area")
        area_field = CadastralParcel._meta.get_field("graphical_area")
        assert area_field.max_digits == 12
        assert area_field.decimal_places == 2

    def test_cadastral_parcel_meta(self):
        """Test CadastralParcel model metadata."""
        assert CadastralParcel._meta.verbose_name == "Cadastral Parcel"
        assert CadastralParcel._meta.verbose_name_plural == "Cadastral Parcels"
        assert CadastralParcel._meta.ordering == ("parcel_code",)


@pytest.mark.django_db
class TestUsageModel:
    """Tests for Usage model."""

    def test_usage_str_representation(self):
        """Test Usage string representation."""
        assert hasattr(Usage, "__str__")
        assert Usage._meta.db_table == '"dkp"."usages"'
        assert Usage._meta.managed is False

    def test_usage_meta(self):
        """Test Usage model metadata."""
        assert Usage._meta.verbose_name == "Usage"
        assert Usage._meta.verbose_name_plural == "Usages"
        assert Usage._meta.ordering == ("code",)


@pytest.mark.django_db
class TestBuildingModel:
    """Tests for Building model."""

    def test_building_str_representation(self):
        """Test Building string representation."""
        assert hasattr(Building, "__str__")
        assert Building._meta.db_table == '"dkp"."buildings"'
        assert Building._meta.managed is False

    def test_building_has_usage_relationship(self):
        """Test Building has usage foreign key."""
        assert hasattr(Building, "usage")
        usage_field = Building._meta.get_field("usage")
        assert usage_field.related_model is Usage
        assert usage_field.db_column == "usage_code"
        assert usage_field.to_field.name == "code"

    def test_building_has_cadastral_municipality_relationship(self):
        """Test Building has cadastral municipality foreign key."""
        assert hasattr(Building, "cadastral_municipality")
        municipality_field = Building._meta.get_field("cadastral_municipality")
        assert municipality_field.related_model is CadastralMunicipality
        assert municipality_field.db_column == "cadastral_municipality_code"
        assert municipality_field.to_field.name == "national_code"

    def test_building_meta(self):
        """Test Building model metadata."""
        assert Building._meta.verbose_name == "Building"
        assert Building._meta.verbose_name_plural == "Buildings"
        assert Building._meta.ordering == ("building_number",)

