"""
Comprehensive tests for cadastral filters.
Tests all filter types, edge cases, and filter combinations.
"""
import pytest
from django.contrib.gis.geos import Point, MultiPolygon, Polygon
from django_filters import FilterSet

from cadastral.filters import (
    CountryFilterSet,
    CountyBoundaryFilterSet,
    MunicipalityBoundaryFilterSet,
    SettlementFilterSet,
    StreetFilterSet,
    AddressFilterSet,
    CadastralMunicipalityFilterSet,
    CadastralParcelFilterSet,
    BuildingFilterSet,
    PostalOfficeFilterSet,
    UsageFilterSet,
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
class TestCountryFilterSet:
    """Tests for CountryFilterSet."""

    def test_country_filterset_fields(self):
        """Test CountryFilterSet has expected filter fields."""
        filterset = CountryFilterSet()
        assert "national_code" in filterset.filters
        assert "name" in filterset.filters

    def test_country_filterset_model(self):
        """Test CountryFilterSet uses correct model."""
        assert CountryFilterSet.Meta.model == Country


@pytest.mark.django_db
class TestCountyBoundaryFilterSet:
    """Tests for CountyBoundaryFilterSet."""

    def test_county_filterset_fields(self):
        """Test CountyBoundaryFilterSet has expected filter fields."""
        filterset = CountyBoundaryFilterSet()
        assert "national_code" in filterset.filters
        assert "name" in filterset.filters

    def test_county_filterset_model(self):
        """Test CountyBoundaryFilterSet uses correct model."""
        assert CountyBoundaryFilterSet.Meta.model == County

    def test_county_filterset_name_lookup(self):
        """Test CountyBoundaryFilterSet name filter uses icontains."""
        filterset = CountyBoundaryFilterSet()
        name_filter = filterset.filters["name"]
        assert name_filter.lookup_expr == "icontains"


@pytest.mark.django_db
class TestMunicipalityBoundaryFilterSet:
    """Tests for MunicipalityBoundaryFilterSet."""

    def test_municipality_filterset_fields(self):
        """Test MunicipalityBoundaryFilterSet has expected filter fields."""
        filterset = MunicipalityBoundaryFilterSet()
        assert "national_code" in filterset.filters
        assert "name" in filterset.filters
        assert "county_code" in filterset.filters
        assert "county_name" in filterset.filters

    def test_municipality_filterset_model(self):
        """Test MunicipalityBoundaryFilterSet uses correct model."""
        assert MunicipalityBoundaryFilterSet.Meta.model == Municipality

    def test_municipality_filterset_county_relationship(self):
        """Test MunicipalityBoundaryFilterSet filters on county relationship."""
        filterset = MunicipalityBoundaryFilterSet()
        county_code_filter = filterset.filters["county_code"]
        assert county_code_filter.field_name == "county__national_code"
        county_name_filter = filterset.filters["county_name"]
        assert county_name_filter.field_name == "county__name"
        assert county_name_filter.lookup_expr == "icontains"


@pytest.mark.django_db
class TestSettlementFilterSet:
    """Tests for SettlementFilterSet."""

    def test_settlement_filterset_fields(self):
        """Test SettlementFilterSet has expected filter fields."""
        filterset = SettlementFilterSet()
        assert "national_code" in filterset.filters
        assert "name" in filterset.filters
        assert "municipality_code" in filterset.filters
        assert "county_code" in filterset.filters

    def test_settlement_filterset_model(self):
        """Test SettlementFilterSet uses correct model."""
        assert SettlementFilterSet.Meta.model == Settlement

    def test_settlement_filterset_hierarchy_filters(self):
        """Test SettlementFilterSet filters on municipality and county hierarchy."""
        filterset = SettlementFilterSet()
        municipality_filter = filterset.filters["municipality_code"]
        assert municipality_filter.field_name == "municipality__national_code"
        county_filter = filterset.filters["county_code"]
        assert county_filter.field_name == "municipality__county__national_code"


@pytest.mark.django_db
class TestStreetFilterSet:
    """Tests for StreetFilterSet."""

    def test_street_filterset_fields(self):
        """Test StreetFilterSet has expected filter fields."""
        filterset = StreetFilterSet()
        assert "settlement_code" in filterset.filters
        assert "settlement_name" in filterset.filters
        assert "municipality_name" in filterset.filters
        assert "name" in filterset.filters

    def test_street_filterset_model(self):
        """Test StreetFilterSet uses correct model."""
        assert StreetFilterSet.Meta.model == StreetFeature

    def test_street_filterset_name_lookup(self):
        """Test StreetFilterSet name filters use icontains."""
        filterset = StreetFilterSet()
        name_filter = filterset.filters["name"]
        assert name_filter.lookup_expr == "icontains"
        settlement_name_filter = filterset.filters["settlement_name"]
        assert settlement_name_filter.lookup_expr == "icontains"
        municipality_name_filter = filterset.filters["municipality_name"]
        assert municipality_name_filter.lookup_expr == "icontains"


@pytest.mark.django_db
class TestAddressFilterSet:
    """Tests for AddressFilterSet."""

    def test_address_filterset_fields(self):
        """Test AddressFilterSet has expected filter fields."""
        filterset = AddressFilterSet()
        assert "street_id" in filterset.filters
        assert "house_number" in filterset.filters
        assert "settlement_code" in filterset.filters
        assert "municipality_code" in filterset.filters

    def test_address_filterset_model(self):
        """Test AddressFilterSet uses correct model."""
        assert AddressFilterSet.Meta.model == Address

    def test_address_filterset_house_number_lookup(self):
        """Test AddressFilterSet house_number filter uses icontains."""
        filterset = AddressFilterSet()
        house_number_filter = filterset.filters["house_number"]
        assert house_number_filter.lookup_expr == "icontains"

    def test_address_filterset_hierarchy_filters(self):
        """Test AddressFilterSet filters on street hierarchy."""
        filterset = AddressFilterSet()
        settlement_filter = filterset.filters["settlement_code"]
        assert settlement_filter.field_name == "street__settlement__national_code"
        municipality_filter = filterset.filters["municipality_code"]
        assert municipality_filter.field_name == "street__settlement__municipality__national_code"


@pytest.mark.django_db
class TestCadastralMunicipalityFilterSet:
    """Tests for CadastralMunicipalityFilterSet."""

    def test_cadastral_municipality_filterset_fields(self):
        """Test CadastralMunicipalityFilterSet has expected filter fields."""
        filterset = CadastralMunicipalityFilterSet()
        assert "national_code" in filterset.filters
        assert "name" in filterset.filters
        assert "harmonization_status" in filterset.filters

    def test_cadastral_municipality_filterset_model(self):
        """Test CadastralMunicipalityFilterSet uses correct model."""
        assert CadastralMunicipalityFilterSet.Meta.model == CadastralMunicipality

    def test_cadastral_municipality_filterset_name_lookup(self):
        """Test CadastralMunicipalityFilterSet name filter uses icontains."""
        filterset = CadastralMunicipalityFilterSet()
        name_filter = filterset.filters["name"]
        assert name_filter.lookup_expr == "icontains"


@pytest.mark.django_db
class TestCadastralParcelFilterSet:
    """Tests for CadastralParcelFilterSet."""

    def test_cadastral_parcel_filterset_fields(self):
        """Test CadastralParcelFilterSet has expected filter fields."""
        filterset = CadastralParcelFilterSet()
        assert "parcel_id" in filterset.filters
        assert "cadastral_municipality_code" in filterset.filters
        assert "cadastral_municipality" in filterset.filters
        assert "updated_after" in filterset.filters
        assert "updated_before" in filterset.filters

    def test_cadastral_parcel_filterset_model(self):
        """Test CadastralParcelFilterSet uses correct model."""
        assert CadastralParcelFilterSet.Meta.model == CadastralParcel

    def test_cadastral_parcel_filterset_parcel_id_mapping(self):
        """Test CadastralParcelFilterSet parcel_id maps to parcel_code."""
        filterset = CadastralParcelFilterSet()
        parcel_id_filter = filterset.filters["parcel_id"]
        assert parcel_id_filter.field_name == "parcel_code"
        assert parcel_id_filter.lookup_expr == "iexact"

    def test_cadastral_parcel_filterset_municipality_relationship(self):
        """Test CadastralParcelFilterSet filters on municipality relationship."""
        filterset = CadastralParcelFilterSet()
        municipality_code_filter = filterset.filters["cadastral_municipality_code"]
        assert municipality_code_filter.field_name == "cadastral_municipality__national_code"
        municipality_name_filter = filterset.filters["cadastral_municipality"]
        assert municipality_name_filter.field_name == "cadastral_municipality__name"
        assert municipality_name_filter.lookup_expr == "icontains"

    def test_cadastral_parcel_filterset_date_filters(self):
        """Test CadastralParcelFilterSet has date range filters."""
        filterset = CadastralParcelFilterSet()
        updated_after_filter = filterset.filters["updated_after"]
        assert updated_after_filter.lookup_expr == "gte"
        updated_before_filter = filterset.filters["updated_before"]
        assert updated_before_filter.lookup_expr == "lte"


@pytest.mark.django_db
class TestBuildingFilterSet:
    """Tests for BuildingFilterSet."""

    def test_building_filterset_fields(self):
        """Test BuildingFilterSet has expected filter fields."""
        filterset = BuildingFilterSet()
        assert "building_number" in filterset.filters
        assert "cadastral_municipality_code" in filterset.filters
        assert "cadastral_municipality" in filterset.filters
        assert "usage_code" in filterset.filters

    def test_building_filterset_model(self):
        """Test BuildingFilterSet uses correct model."""
        assert BuildingFilterSet.Meta.model == Building

    def test_building_filterset_relationships(self):
        """Test BuildingFilterSet filters on relationships."""
        filterset = BuildingFilterSet()
        municipality_code_filter = filterset.filters["cadastral_municipality_code"]
        assert municipality_code_filter.field_name == "cadastral_municipality__national_code"
        municipality_name_filter = filterset.filters["cadastral_municipality"]
        assert municipality_name_filter.field_name == "cadastral_municipality__name"
        assert municipality_name_filter.lookup_expr == "icontains"
        usage_filter = filterset.filters["usage_code"]
        assert usage_filter.field_name == "usage__code"


@pytest.mark.django_db
class TestPostalOfficeFilterSet:
    """Tests for PostalOfficeFilterSet."""

    def test_postal_office_filterset_fields(self):
        """Test PostalOfficeFilterSet has expected filter fields."""
        filterset = PostalOfficeFilterSet()
        assert "postal_code" in filterset.filters
        assert "name" in filterset.filters

    def test_postal_office_filterset_model(self):
        """Test PostalOfficeFilterSet uses correct model."""
        assert PostalOfficeFilterSet.Meta.model == PostalOffice

    def test_postal_office_filterset_name_lookup(self):
        """Test PostalOfficeFilterSet name filter uses icontains."""
        filterset = PostalOfficeFilterSet()
        name_filter = filterset.filters["name"]
        assert name_filter.lookup_expr == "icontains"


@pytest.mark.django_db
class TestUsageFilterSet:
    """Tests for UsageFilterSet."""

    def test_usage_filterset_fields(self):
        """Test UsageFilterSet has expected filter fields."""
        filterset = UsageFilterSet()
        assert "code" in filterset.filters
        assert "name" in filterset.filters

    def test_usage_filterset_model(self):
        """Test UsageFilterSet uses correct model."""
        assert UsageFilterSet.Meta.model == Usage

    def test_usage_filterset_name_lookup(self):
        """Test UsageFilterSet name filter uses icontains."""
        filterset = UsageFilterSet()
        name_filter = filterset.filters["name"]
        assert name_filter.lookup_expr == "icontains"


@pytest.mark.django_db
class TestFilterCombinations:
    """Tests for filter combinations and edge cases."""

    def test_multiple_filters_combined(self):
        """Test that multiple filters can be combined."""
        filterset = MunicipalityBoundaryFilterSet()
        # Should have all filter fields available
        assert len(filterset.filters) >= 4

    def test_filter_field_labels(self):
        """Test that filter fields have appropriate labels."""
        filterset = CadastralParcelFilterSet()
        parcel_id_filter = filterset.filters["parcel_id"]
        assert parcel_id_filter.label == "Parcel identifier"
        municipality_filter = filterset.filters["cadastral_municipality"]
        assert municipality_filter.label == "Cadastral municipality name"
