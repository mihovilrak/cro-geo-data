"""
Comprehensive integration tests for cadastral viewsets.
Tests actual API endpoints, filtering, search, bbox queries, and pagination.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

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
class TestCountryViewSet:
    """Integration tests for CountryViewSet."""

    def test_list_countries(self, api_client: APIClient):
        """Test listing countries endpoint."""
        url = reverse("country-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert "type" in response.data
        assert response.data["type"] == "FeatureCollection"
        assert "features" in response.data

    def test_list_countries_with_search(self, api_client: APIClient):
        """Test listing countries with search parameter."""
        url = reverse("country-list")
        response = api_client.get(url, {"search": "Croatia"})
        assert response.status_code == status.HTTP_200_OK

    def test_list_countries_with_bbox(self, api_client: APIClient, sample_bbox: str):
        """Test listing countries with bbox filter."""
        url = reverse("country-list")
        response = api_client.get(url, {"bbox": sample_bbox})
        assert response.status_code == status.HTTP_200_OK

    def test_list_countries_with_filter(self, api_client: APIClient):
        """Test listing countries with filter parameters."""
        url = reverse("country-list")
        response = api_client.get(url, {"national_code": 1})
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_country(self, api_client: APIClient):
        """Test retrieving a single country."""
        url = reverse("country-detail", kwargs={"pk": 1})
        response = api_client.get(url)
        # May return 404 if no data, but should not return 500
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestCountyViewSet:
    """Integration tests for CountyViewSet."""

    def test_list_counties(self, api_client: APIClient):
        """Test listing counties endpoint."""
        url = reverse("county-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["type"] == "FeatureCollection"

    def test_list_counties_with_search(self, api_client: APIClient):
        """Test listing counties with search parameter."""
        url = reverse("county-list")
        response = api_client.get(url, {"search": "Zagreb"})
        assert response.status_code == status.HTTP_200_OK

    def test_list_counties_with_bbox(self, api_client: APIClient, sample_bbox: str):
        """Test listing counties with bbox filter."""
        url = reverse("county-list")
        response = api_client.get(url, {"bbox": sample_bbox})
        assert response.status_code == status.HTTP_200_OK

    def test_list_counties_with_filter(self, api_client: APIClient):
        """Test listing counties with filter parameters."""
        url = reverse("county-list")
        response = api_client.get(url, {"national_code": 1, "name": "Zagreb"})
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_county(self, api_client: APIClient):
        """Test retrieving a single county."""
        url = reverse("county-detail", kwargs={"pk": 1})
        response = api_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestMunicipalityViewSet:
    """Integration tests for MunicipalityViewSet."""

    def test_list_municipalities(self, api_client: APIClient):
        """Test listing municipalities endpoint."""
        url = reverse("municipality-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["type"] == "FeatureCollection"

    def test_list_municipalities_with_search(self, api_client: APIClient):
        """Test listing municipalities with search parameter."""
        url = reverse("municipality-list")
        response = api_client.get(url, {"search": "Zagreb"})
        assert response.status_code == status.HTTP_200_OK

    def test_list_municipalities_with_bbox(self, api_client: APIClient, sample_bbox: str):
        """Test listing municipalities with bbox filter."""
        url = reverse("municipality-list")
        response = api_client.get(url, {"bbox": sample_bbox})
        assert response.status_code == status.HTTP_200_OK

    def test_list_municipalities_with_county_filter(self, api_client: APIClient):
        """Test listing municipalities filtered by county."""
        url = reverse("municipality-list")
        response = api_client.get(url, {"county_code": 1, "county_name": "Zagreb"})
        assert response.status_code == status.HTTP_200_OK

    def test_list_municipalities_with_pagination(self, api_client: APIClient):
        """Test listing municipalities with pagination."""
        url = reverse("municipality-list")
        response = api_client.get(url, {"limit": 10, "offset": 0})
        assert response.status_code == status.HTTP_200_OK
        # Check pagination keys if data exists
        if "count" in response.data:
            assert "next" in response.data or response.data["next"] is None
            assert "previous" in response.data or response.data["previous"] is None

    def test_retrieve_municipality(self, api_client: APIClient):
        """Test retrieving a single municipality."""
        url = reverse("municipality-detail", kwargs={"pk": 1})
        response = api_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestSettlementViewSet:
    """Integration tests for SettlementViewSet."""

    def test_list_settlements(self, api_client: APIClient):
        """Test listing settlements endpoint."""
        url = reverse("settlement-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["type"] == "FeatureCollection"

    def test_list_settlements_with_search(self, api_client: APIClient):
        """Test listing settlements with search parameter."""
        url = reverse("settlement-list")
        response = api_client.get(url, {"search": "Zagreb"})
        assert response.status_code == status.HTTP_200_OK

    def test_list_settlements_with_bbox(self, api_client: APIClient, sample_bbox: str):
        """Test listing settlements with bbox filter."""
        url = reverse("settlement-list")
        response = api_client.get(url, {"bbox": sample_bbox})
        assert response.status_code == status.HTTP_200_OK

    def test_list_settlements_with_municipality_filter(self, api_client: APIClient):
        """Test listing settlements filtered by municipality."""
        url = reverse("settlement-list")
        response = api_client.get(url, {"municipality_code": 1, "county_code": 1})
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_settlement(self, api_client: APIClient):
        """Test retrieving a single settlement."""
        url = reverse("settlement-detail", kwargs={"pk": 1})
        response = api_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestStreetViewSet:
    """Integration tests for StreetViewSet."""

    def test_list_streets(self, api_client: APIClient):
        """Test listing streets endpoint."""
        url = reverse("street-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["type"] == "FeatureCollection"

    def test_list_streets_with_search(self, api_client: APIClient):
        """Test listing streets with search parameter."""
        url = reverse("street-list")
        response = api_client.get(url, {"search": "Ilica"})
        assert response.status_code == status.HTTP_200_OK

    def test_list_streets_with_bbox(self, api_client: APIClient, sample_bbox: str):
        """Test listing streets with bbox filter."""
        url = reverse("street-list")
        response = api_client.get(url, {"bbox": sample_bbox})
        assert response.status_code == status.HTTP_200_OK

    def test_list_streets_with_filters(self, api_client: APIClient):
        """Test listing streets with filter parameters."""
        url = reverse("street-list")
        response = api_client.get(url, {
            "settlement_code": 1,
            "settlement_name": "Zagreb",
            "municipality_name": "Zagreb",
            "name": "Ilica"
        })
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_street(self, api_client: APIClient):
        """Test retrieving a single street."""
        url = reverse("street-detail", kwargs={"pk": 1})
        response = api_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestAddressViewSet:
    """Integration tests for AddressViewSet."""

    def test_list_addresses(self, api_client: APIClient):
        """Test listing addresses endpoint."""
        url = reverse("address-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["type"] == "FeatureCollection"

    def test_list_addresses_with_search(self, api_client: APIClient):
        """Test listing addresses with search parameter."""
        url = reverse("address-list")
        response = api_client.get(url, {"search": "1"})
        assert response.status_code == status.HTTP_200_OK

    def test_list_addresses_with_bbox(self, api_client: APIClient, sample_bbox: str):
        """Test listing addresses with bbox filter."""
        url = reverse("address-list")
        response = api_client.get(url, {"bbox": sample_bbox})
        assert response.status_code == status.HTTP_200_OK

    def test_list_addresses_with_filters(self, api_client: APIClient):
        """Test listing addresses with filter parameters."""
        url = reverse("address-list")
        response = api_client.get(url, {
            "street_id": 1,
            "house_number": "1",
            "settlement_code": 1,
            "municipality_code": 1
        })
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_address(self, api_client: APIClient):
        """Test retrieving a single address."""
        url = reverse("address-detail", kwargs={"pk": 1})
        response = api_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestCadastralMunicipalityViewSet:
    """Integration tests for CadastralMunicipalityViewSet."""

    def test_list_cadastral_municipalities(self, api_client: APIClient):
        """Test listing cadastral municipalities endpoint."""
        url = reverse("cadastralmunicipality-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["type"] == "FeatureCollection"

    def test_list_cadastral_municipalities_with_search(self, api_client: APIClient):
        """Test listing cadastral municipalities with search parameter."""
        url = reverse("cadastralmunicipality-list")
        response = api_client.get(url, {"search": "Zagreb"})
        assert response.status_code == status.HTTP_200_OK

    def test_list_cadastral_municipalities_with_bbox(self, api_client: APIClient, sample_bbox: str):
        """Test listing cadastral municipalities with bbox filter."""
        url = reverse("cadastralmunicipality-list")
        response = api_client.get(url, {"bbox": sample_bbox})
        assert response.status_code == status.HTTP_200_OK

    def test_list_cadastral_municipalities_with_filters(self, api_client: APIClient):
        """Test listing cadastral municipalities with filter parameters."""
        url = reverse("cadastralmunicipality-list")
        response = api_client.get(url, {
            "national_code": 1,
            "name": "Zagreb",
            "harmonization_status": 1
        })
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_cadastral_municipality(self, api_client: APIClient):
        """Test retrieving a single cadastral municipality."""
        url = reverse("cadastralmunicipality-detail", kwargs={"pk": 1})
        response = api_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestCadastralParcelViewSet:
    """Integration tests for CadastralParcelViewSet."""

    def test_list_cadastral_parcels(self, api_client: APIClient):
        """Test listing cadastral parcels endpoint."""
        url = reverse("cadastralparcel-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["type"] == "FeatureCollection"

    def test_list_cadastral_parcels_with_search(self, api_client: APIClient):
        """Test listing cadastral parcels with search parameter."""
        url = reverse("cadastralparcel-list")
        response = api_client.get(url, {"search": "123"})
        assert response.status_code == status.HTTP_200_OK

    def test_list_cadastral_parcels_with_bbox(self, api_client: APIClient, sample_bbox: str):
        """Test listing cadastral parcels with bbox filter."""
        url = reverse("cadastralparcel-list")
        response = api_client.get(url, {"bbox": sample_bbox})
        assert response.status_code == status.HTTP_200_OK

    def test_list_cadastral_parcels_with_filters(self, api_client: APIClient):
        """Test listing cadastral parcels with filter parameters."""
        url = reverse("cadastralparcel-list")
        response = api_client.get(url, {
            "parcel_id": "123",
            "cadastral_municipality_code": 1,
            "cadastral_municipality": "Zagreb",
            "updated_after": "2020-01-01T00:00:00Z",
            "updated_before": "2025-12-31T23:59:59Z"
        })
        assert response.status_code == status.HTTP_200_OK

    def test_list_cadastral_parcels_with_pagination(self, api_client: APIClient):
        """Test listing cadastral parcels with pagination."""
        url = reverse("cadastralparcel-list")
        response = api_client.get(url, {"limit": 50, "offset": 0})
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_cadastral_parcel(self, api_client: APIClient):
        """Test retrieving a single cadastral parcel."""
        url = reverse("cadastralparcel-detail", kwargs={"pk": 1})
        response = api_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestBuildingViewSet:
    """Integration tests for BuildingViewSet."""

    def test_list_buildings(self, api_client: APIClient):
        """Test listing buildings endpoint."""
        url = reverse("building-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["type"] == "FeatureCollection"

    def test_list_buildings_with_search(self, api_client: APIClient):
        """Test listing buildings with search parameter."""
        url = reverse("building-list")
        response = api_client.get(url, {"search": "1"})
        assert response.status_code == status.HTTP_200_OK

    def test_list_buildings_with_bbox(self, api_client: APIClient, sample_bbox: str):
        """Test listing buildings with bbox filter."""
        url = reverse("building-list")
        response = api_client.get(url, {"bbox": sample_bbox})
        assert response.status_code == status.HTTP_200_OK

    def test_list_buildings_with_filters(self, api_client: APIClient):
        """Test listing buildings with filter parameters."""
        url = reverse("building-list")
        response = api_client.get(url, {
            "building_number": 1,
            "cadastral_municipality_code": 1,
            "cadastral_municipality": "Zagreb",
            "usage_code": 1
        })
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_building(self, api_client: APIClient):
        """Test retrieving a single building."""
        url = reverse("building-detail", kwargs={"pk": 1})
        response = api_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestPostalOfficeViewSet:
    """Integration tests for PostalOfficeViewSet."""

    def test_list_postal_offices(self, api_client: APIClient):
        """Test listing postal offices endpoint."""
        url = reverse("postaloffice-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        # Postal offices don't have geometry, so response format may differ
        assert "results" in response.data or "features" in response.data

    def test_list_postal_offices_with_search(self, api_client: APIClient):
        """Test listing postal offices with search parameter."""
        url = reverse("postaloffice-list")
        response = api_client.get(url, {"search": "10000"})
        assert response.status_code == status.HTTP_200_OK

    def test_list_postal_offices_with_filters(self, api_client: APIClient):
        """Test listing postal offices with filter parameters."""
        url = reverse("postaloffice-list")
        response = api_client.get(url, {"postal_code": 10000, "name": "Zagreb"})
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_postal_office(self, api_client: APIClient):
        """Test retrieving a single postal office."""
        url = reverse("postaloffice-detail", kwargs={"pk": 1})
        response = api_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestUsageViewSet:
    """Integration tests for UsageViewSet."""

    def test_list_usages(self, api_client: APIClient):
        """Test listing usages endpoint."""
        url = reverse("usage-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data or "features" in response.data

    def test_list_usages_with_search(self, api_client: APIClient):
        """Test listing usages with search parameter."""
        url = reverse("usage-list")
        response = api_client.get(url, {"search": "residential"})
        assert response.status_code == status.HTTP_200_OK

    def test_list_usages_with_filters(self, api_client: APIClient):
        """Test listing usages with filter parameters."""
        url = reverse("usage-list")
        response = api_client.get(url, {"code": 1, "name": "residential"})
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_usage(self, api_client: APIClient):
        """Test retrieving a single usage."""
        url = reverse("usage-detail", kwargs={"pk": 1})
        response = api_client.get(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestLayerCatalogView:
    """Integration tests for LayerCatalogView."""

    def test_get_layer_catalog(self, api_client: APIClient):
        """Test getting layer catalog."""
        from django.urls import reverse
        url = reverse("layer-catalog")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        # Check that catalog entries have required fields
        if len(response.data) > 0:
            entry = response.data[0]
            assert "id" in entry
            assert "title" in entry
            assert "api_path" in entry


@pytest.mark.django_db
class TestViewSetErrorHandling:
    """Tests for error handling in viewsets."""

    def test_invalid_bbox_format(self, api_client: APIClient):
        """Test handling of invalid bbox format."""
        url = reverse("county-list")
        response = api_client.get(url, {"bbox": "invalid"})
        # Should handle gracefully, either return 400 or ignore invalid bbox
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
        ]

    def test_invalid_pagination_parameters(self, api_client: APIClient):
        """Test handling of invalid pagination parameters."""
        url = reverse("municipality-list")
        response = api_client.get(url, {"limit": "invalid", "offset": "invalid"})
        # Should handle gracefully
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
        ]

    def test_nonexistent_resource(self, api_client: APIClient):
        """Test retrieving a nonexistent resource."""
        url = reverse("county-detail", kwargs={"pk": 999999})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

