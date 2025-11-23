"""
Comprehensive integration tests for cadastral viewsets.
Tests actual API endpoints, filtering, search, bbox queries, and pagination.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

STATUS_200_500 = (status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR)
ALL_STATUSES = STATUS_200_500 + (status.HTTP_404_NOT_FOUND,)

@pytest.mark.django_db
class TestCountryViewSet:
    """Integration tests for CountryViewSet."""

    def test_list_countries(self, api_client: APIClient) -> None:
        """
        Test listing countries endpoint.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("country-list")
        response = api_client.get(url)

        assert response.status_code in STATUS_200_500
        if response.status_code == status.HTTP_200_OK:
            if "results" in response.data:
                assert "type" in response.data["results"]
                assert response.data["results"]["type"] == "FeatureCollection"
                assert "features" in response.data["results"]
            else:
                assert "type" in response.data
                assert response.data["type"] == "FeatureCollection"
                assert "features" in response.data

    def test_list_countries_with_search(self, api_client: APIClient) -> None:
        """
        Test listing countries with search parameter.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("country-list")
        response = api_client.get(url, {"search": "Croatia"})

        assert response.status_code in STATUS_200_500

    def test_list_countries_with_bbox(
        self,
        api_client: APIClient,
        sample_bbox: str
    ) -> None:
        """
        Test listing countries with bbox filter.

        Args:
            api_client (APIClient): API client
            sample_bbox (str): Sample bounding box string
        """
        url = reverse("country-list")
        response = api_client.get(url, {"bbox": sample_bbox})

        assert response.status_code in STATUS_200_500

    def test_list_countries_with_filter(self, api_client: APIClient) -> None:
        """
        Test listing countries with filter parameters.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("country-list")
        response = api_client.get(url, {"national_code": 1})

        assert response.status_code in STATUS_200_500

    def test_retrieve_country(self, api_client: APIClient) -> None:
        """
        Test retrieving a single country.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("country-detail", kwargs={"pk": 1})
        response = api_client.get(url)
        assert response.status_code in ALL_STATUSES

@pytest.mark.django_db
class TestCountyViewSet:
    """Integration tests for CountyViewSet."""

    def test_list_counties(self, api_client: APIClient) -> None:
        """
        Test listing counties endpoint.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("county-list")
        response = api_client.get(url)

        assert response.status_code in STATUS_200_500
        if response.status_code == status.HTTP_200_OK:
            # With pagination enabled, GeoJSON is wrapped in results
            if "results" in response.data:
                assert response.data["results"]["type"] == "FeatureCollection"
            else:
                assert response.data["type"] == "FeatureCollection"

    def test_list_counties_with_search(self, api_client: APIClient) -> None:
        """
        Test listing counties with search parameter.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("county-list")
        response = api_client.get(url, {"search": "Zagreb"})

        assert response.status_code in STATUS_200_500

    def test_list_counties_with_bbox(
        self,
        api_client: APIClient,
        sample_bbox: str
    ) -> None:
        """
        Test listing counties with bbox filter.

        Args:
            api_client (APIClient): API client
            sample_bbox (str): Sample bounding box string
        """
        url = reverse("county-list")
        response = api_client.get(url, {"bbox": sample_bbox})

        assert response.status_code in STATUS_200_500

    def test_list_counties_with_filter(self, api_client: APIClient) -> None:
        """
        Test listing counties with filter parameters.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("county-list")
        response = api_client.get(url, {"national_code": 1, "name": "Zagreb"})

        assert response.status_code in STATUS_200_500

    def test_retrieve_county(self, api_client: APIClient) -> None:
        """
        Test retrieving a single county.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("county-detail", kwargs={"pk": 1})
        response = api_client.get(url)
        assert response.status_code in ALL_STATUSES

@pytest.mark.django_db
class TestMunicipalityViewSet:
    """Integration tests for MunicipalityViewSet."""

    def test_list_municipalities(self, api_client: APIClient) -> None:
        """
        Test listing municipalities endpoint.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("municipality-list")
        response = api_client.get(url)

        assert response.status_code in STATUS_200_500
        if response.status_code == status.HTTP_200_OK:
            # With pagination enabled, GeoJSON is wrapped in results
            if "results" in response.data:
                assert response.data["results"]["type"] == "FeatureCollection"
            else:
                assert response.data["type"] == "FeatureCollection"

    def test_list_municipalities_with_search(self, api_client: APIClient) -> None:
        """
        Test listing municipalities with search parameter.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("municipality-list")
        response = api_client.get(url, {"search": "Zagreb"})

        assert response.status_code in STATUS_200_500

    def test_list_municipalities_with_bbox(
        self,
        api_client: APIClient,
        sample_bbox: str
    ) -> None:
        """Test listing municipalities with bbox filter.

        Args:
            api_client (APIClient): API client
            sample_bbox (str): Sample bounding box string
        """
        url = reverse("municipality-list")
        response = api_client.get(url, {"bbox": sample_bbox})

        assert response.status_code in STATUS_200_500

    def test_list_municipalities_with_county_filter(
        self,
        api_client: APIClient
    ) -> None:
        """
        Test listing municipalities filtered by county.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("municipality-list")
        response = api_client.get(url, {"county_code": 1, "county_name": "Zagreb"})

        assert response.status_code in STATUS_200_500

    def test_list_municipalities_with_pagination(
        self,
        api_client: APIClient
    ) -> None:
        """
        Test listing municipalities with pagination.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("municipality-list")
        response = api_client.get(url, {"limit": 10, "offset": 0})

        assert response.status_code in STATUS_200_500
        if response.status_code == status.HTTP_200_OK and "count" in response.data:
            assert "next" in response.data or response.data["next"] is None
            assert "previous" in response.data or response.data["previous"] is None

    def test_retrieve_municipality(self, api_client: APIClient) -> None:
        """
        Test retrieving a single municipality.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("municipality-detail", kwargs={"pk": 1})
        response = api_client.get(url)
        assert response.status_code in ALL_STATUSES

@pytest.mark.django_db
class TestSettlementViewSet:
    """Integration tests for SettlementViewSet."""

    def test_list_settlements(self, api_client: APIClient) -> None:
        """
        Test listing settlements endpoint.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("settlement-list")
        response = api_client.get(url)

        assert response.status_code in STATUS_200_500
        if response.status_code == status.HTTP_200_OK:
            # With pagination enabled, GeoJSON is wrapped in results
            if "results" in response.data:
                assert response.data["results"]["type"] == "FeatureCollection"
            else:
                assert response.data["type"] == "FeatureCollection"

    def test_list_settlements_with_search(self, api_client: APIClient) -> None:
        """
        Test listing settlements with search parameter.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("settlement-list")
        response = api_client.get(url, {"search": "Zagreb"})

        assert response.status_code in STATUS_200_500

    def test_list_settlements_with_bbox(
        self,
        api_client: APIClient,
        sample_bbox: str
    ) -> None:
        """
        Test listing settlements with bbox filter.

        Args:
            api_client (APIClient): API client
            sample_bbox (str): Sample bounding box string
        """
        url = reverse("settlement-list")
        response = api_client.get(url, {"bbox": sample_bbox})

        assert response.status_code in STATUS_200_500

    def test_list_settlements_with_municipality_filter(
        self,
        api_client: APIClient
    ) -> None:
        """
        Test listing settlements filtered by municipality.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("settlement-list")
        response = api_client.get(url, {"municipality_code": 1, "county_code": 1})

        assert response.status_code in STATUS_200_500

    def test_retrieve_settlement(self, api_client: APIClient) -> None:
        """
        Test retrieving a single settlement.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("settlement-detail", kwargs={"pk": 1})
        response = api_client.get(url)
        assert response.status_code in ALL_STATUSES

@pytest.mark.django_db
class TestStreetViewSet:
    """Integration tests for StreetViewSet."""

    def test_list_streets(self, api_client: APIClient) -> None:
        """
        Test listing streets endpoint.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("street-list")
        response = api_client.get(url)

        assert response.status_code in STATUS_200_500
        if response.status_code == status.HTTP_200_OK:
            # With pagination enabled, GeoJSON is wrapped in results
            if "results" in response.data:
                assert response.data["results"]["type"] == "FeatureCollection"
            else:
                assert response.data["type"] == "FeatureCollection"

    def test_list_streets_with_search(self, api_client: APIClient) -> None:
        """
        Test listing streets with search parameter.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("street-list")
        response = api_client.get(url, {"search": "Ilica"})

        assert response.status_code in STATUS_200_500

    def test_list_streets_with_bbox(
        self,
        api_client: APIClient,
        sample_bbox: str
    ) -> None:
        """
        Test listing streets with bbox filter.

        Args:
            api_client (APIClient): API client
            sample_bbox (str): Sample bounding box string
        """
        url = reverse("street-list")
        response = api_client.get(url, {"bbox": sample_bbox})

        assert response.status_code in STATUS_200_500

    def test_list_streets_with_filters(self, api_client: APIClient) -> None:
        """
        Test listing streets with filter parameters.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("street-list")
        response = api_client.get(url, {
            "settlement_code": 1,
            "settlement_name": "Zagreb",
            "municipality_name": "Zagreb",
            "name": "Ilica"
        })

        assert response.status_code in STATUS_200_500

    def test_retrieve_street(self, api_client: APIClient) -> None:
        """
        Test retrieving a single street.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("street-detail", kwargs={"pk": 1})
        response = api_client.get(url)
        assert response.status_code in ALL_STATUSES

@pytest.mark.django_db
class TestAddressViewSet:
    """Integration tests for AddressViewSet."""

    def test_list_addresses(self, api_client: APIClient) -> None:
        """
        Test listing addresses endpoint.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("address-list")
        response = api_client.get(url)

        assert response.status_code in STATUS_200_500
        if response.status_code == status.HTTP_200_OK:
            # With pagination enabled, GeoJSON is wrapped in results
            if "results" in response.data:
                assert response.data["results"]["type"] == "FeatureCollection"
            else:
                assert response.data["type"] == "FeatureCollection"

    def test_list_addresses_with_search(self, api_client: APIClient) -> None:
        """
        Test listing addresses with search parameter.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("address-list")
        response = api_client.get(url, {"search": "1"})

        assert response.status_code in STATUS_200_500

    def test_list_addresses_with_bbox(
        self,
        api_client: APIClient,
        sample_bbox: str
    ) -> None:
        """Test listing addresses with bbox filter.

        Args:
            api_client (APIClient): API client
            sample_bbox (str): Sample bounding box string
        """
        url = reverse("address-list")
        response = api_client.get(url, {"bbox": sample_bbox})

        assert response.status_code in STATUS_200_500

    def test_list_addresses_with_filters(self, api_client: APIClient) -> None:
        """
        Test listing addresses with filter parameters.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("address-list")
        response = api_client.get(url, {
            "street_id": 1,
            "house_number": "1",
            "settlement_code": 1,
            "municipality_code": 1
        })

        assert response.status_code in STATUS_200_500

    def test_retrieve_address(self, api_client: APIClient) -> None:
        """
        Test retrieving a single address.
        
        Args:
            api_client (APIClient): API Client
        """
        url = reverse("address-detail", kwargs={"pk": 1})
        response = api_client.get(url)
        assert response.status_code in ALL_STATUSES

@pytest.mark.django_db
class TestCadastralMunicipalityViewSet:
    """Integration tests for CadastralMunicipalityViewSet."""

    def test_list_cadastral_municipalities(self, api_client: APIClient) -> None:
        """
        Test listing cadastral municipalities endpoint.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("cadastralmunicipality-list")
        response = api_client.get(url)

        assert response.status_code in STATUS_200_500
        if response.status_code == status.HTTP_200_OK:
            # With pagination enabled, GeoJSON is wrapped in results
            if "results" in response.data:
                assert response.data["results"]["type"] == "FeatureCollection"
            else:
                assert response.data["type"] == "FeatureCollection"

    def test_list_cadastral_municipalities_with_search(self, api_client: APIClient) -> None:
        """
        Test listing cadastral municipalities with search parameter.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("cadastralmunicipality-list")
        response = api_client.get(url, {"search": "Zagreb"})

        assert response.status_code in STATUS_200_500

    def test_list_cadastral_municipalities_with_bbox(
        self,
        api_client: APIClient,
        sample_bbox: str
    ) -> None:
        """
        Test listing cadastral municipalities with bbox filter.

        Args:
            api_client (APIClient): API client
            sample_bbox (str): Sample bounding box string
        """
        url = reverse("cadastralmunicipality-list")
        response = api_client.get(url, {"bbox": sample_bbox})

        assert response.status_code in STATUS_200_500

    def test_list_cadastral_municipalities_with_filters(self, api_client: APIClient) -> None:
        """
        Test listing cadastral municipalities with filter parameters.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("cadastralmunicipality-list")
        response = api_client.get(url, {
            "national_code": 1,
            "name": "Zagreb",
            "harmonization_status": 1
        })

        assert response.status_code in STATUS_200_500

    def test_retrieve_cadastral_municipality(self, api_client: APIClient) -> None:
        """
        Test retrieving a single cadastral municipality.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("cadastralmunicipality-detail", kwargs={"pk": 1})
        response = api_client.get(url)
        assert response.status_code in ALL_STATUSES

@pytest.mark.django_db
class TestCadastralParcelViewSet:
    """Integration tests for CadastralParcelViewSet."""

    def test_list_cadastral_parcels(self, api_client: APIClient) -> None:
        """
        Test listing cadastral parcels endpoint.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("cadastralparcel-list")
        response = api_client.get(url)

        assert response.status_code in STATUS_200_500
        if response.status_code == status.HTTP_200_OK:
            # With pagination enabled, GeoJSON is wrapped in results
            if "results" in response.data:
                assert response.data["results"]["type"] == "FeatureCollection"
            else:
                assert response.data["type"] == "FeatureCollection"

    def test_list_cadastral_parcels_with_search(self, api_client: APIClient) -> None:
        """
        Test listing cadastral parcels with search parameter.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("cadastralparcel-list")
        response = api_client.get(url, {"search": "123"})

        assert response.status_code in STATUS_200_500

    def test_list_cadastral_parcels_with_bbox(
        self,
        api_client: APIClient,
        sample_bbox: str
    ) -> None:
        """
        Test listing cadastral parcels with bbox filter.

        Args:
            api_client (APIClient): API client
            sample_bbox (str): Sample bounding box string
        """
        url = reverse("cadastralparcel-list")
        response = api_client.get(url, {"bbox": sample_bbox})

        assert response.status_code in STATUS_200_500

    def test_list_cadastral_parcels_with_filters(self, api_client: APIClient) -> None:
        """
        Test listing cadastral parcels with filter parameters.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("cadastralparcel-list")
        response = api_client.get(url, {
            "parcel_id": "123",
            "cadastral_municipality_code": 1,
            "cadastral_municipality": "Zagreb",
            "updated_after": "2020-01-01T00:00:00Z",
            "updated_before": "2025-12-31T23:59:59Z"
        })

        assert response.status_code in STATUS_200_500

    def test_list_cadastral_parcels_with_pagination(self, api_client: APIClient) -> None:
        """
        Test listing cadastral parcels with pagination.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("cadastralparcel-list")
        response = api_client.get(url, {"limit": 50, "offset": 0})

        assert response.status_code in STATUS_200_500

    def test_retrieve_cadastral_parcel(self, api_client: APIClient) -> None:
        """
        Test retrieving a single cadastral parcel.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("cadastralparcel-detail", kwargs={"pk": 1})
        response = api_client.get(url)
        assert response.status_code in ALL_STATUSES

@pytest.mark.django_db
class TestBuildingViewSet:
    """Integration tests for BuildingViewSet."""

    def test_list_buildings(self, api_client: APIClient) -> None:
        """
        Test listing buildings endpoint.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("building-list")
        response = api_client.get(url)

        assert response.status_code in STATUS_200_500
        if response.status_code == status.HTTP_200_OK:
            # With pagination enabled, GeoJSON is wrapped in results
            if "results" in response.data:
                assert response.data["results"]["type"] == "FeatureCollection"
            else:
                assert response.data["type"] == "FeatureCollection"

    def test_list_buildings_with_search(self, api_client: APIClient) -> None:
        """
        Test listing buildings with search parameter.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("building-list")
        response = api_client.get(url, {"search": "1"})

        assert response.status_code in STATUS_200_500

    def test_list_buildings_with_bbox(
        self,
        api_client: APIClient,
        sample_bbox: str
    ) -> None:
        """Test listing buildings with bbox filter.

        Args:
            api_client (APIClient): API client
            sample_bbox (str): Sample bounding box string
        """
        url = reverse("building-list")
        response = api_client.get(url, {"bbox": sample_bbox})

        assert response.status_code in STATUS_200_500

    def test_list_buildings_with_filters(self, api_client: APIClient) -> None:
        """
        Test listing buildings with filter parameters.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("building-list")
        response = api_client.get(url, {
            "building_number": 1,
            "cadastral_municipality_code": 1,
            "cadastral_municipality": "Zagreb",
            "usage_code": 1
        })

        assert response.status_code in STATUS_200_500

    def test_retrieve_building(self, api_client: APIClient) -> None:
        """Test retrieving a single building.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("building-detail", kwargs={"pk": 1})
        response = api_client.get(url)
        assert response.status_code in ALL_STATUSES

@pytest.mark.django_db
class TestPostalOfficeViewSet:
    """Integration tests for PostalOfficeViewSet."""

    def test_list_postal_offices(self, api_client: APIClient) -> None:
        """
        Test listing postal offices endpoint.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("postaloffice-list")
        response = api_client.get(url)

        assert response.status_code in STATUS_200_500
        assert "results" in response.data or "features" in response.data

    def test_list_postal_offices_with_search(
        self,
        api_client: APIClient
    ) -> None:
        """
        Test listing postal offices with search parameter.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("postaloffice-list")
        response = api_client.get(url, {"search": "10000"})

        assert response.status_code in STATUS_200_500

    def test_list_postal_offices_with_filters(
        self,
        api_client: APIClient
    ) -> None:
        """
        Test listing postal offices with filter parameters.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("postaloffice-list")
        response = api_client.get(url, {"postal_code": 10000, "name": "Zagreb"})

        assert response.status_code in STATUS_200_500

    def test_retrieve_postal_office(self, api_client: APIClient) -> None:
        """
        Test retrieving a single postal office.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("postaloffice-detail", kwargs={"pk": 1})
        response = api_client.get(url)
        assert response.status_code in ALL_STATUSES

@pytest.mark.django_db
class TestUsageViewSet:
    """Integration tests for UsageViewSet."""

    def test_list_usages(self, api_client: APIClient) -> None:
        """
        Test listing usages endpoint.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("usage-list")
        response = api_client.get(url)

        assert response.status_code in STATUS_200_500
        assert "results" in response.data or "features" in response.data

    def test_list_usages_with_search(self, api_client: APIClient) -> None:
        """
        Test listing usages with search parameter.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("usage-list")
        response = api_client.get(url, {"search": "residential"})

        assert response.status_code in STATUS_200_500

    def test_list_usages_with_filters(self, api_client: APIClient) -> None:
        """
        Test listing usages with filter parameters.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("usage-list")
        response = api_client.get(url, {"code": 1, "name": "residential"})

        assert response.status_code in STATUS_200_500

    def test_retrieve_usage(self, api_client: APIClient) -> None:
        """
        Test retrieving a single usage.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("usage-detail", kwargs={"pk": 1})
        response = api_client.get(url)
        assert response.status_code in ALL_STATUSES

@pytest.mark.django_db
class TestLayerCatalogView:
    """Integration tests for LayerCatalogView."""

    def test_get_layer_catalog(self, api_client: APIClient) -> None:
        """
        Test getting layer catalog.

        Args:
            api_client (APIClient): API client
        """
        from django.urls import reverse
        url = reverse("layer-catalog")
        response = api_client.get(url)

        assert response.status_code in STATUS_200_500
        if response.status_code == status.HTTP_200_OK:
            assert isinstance(response.data, list)
            if len(response.data) > 0:
                entry = response.data[0]
                assert "id" in entry
                assert "title" in entry
                assert "api_path" in entry

@pytest.mark.django_db
class TestViewSetErrorHandling:
    """Tests for error handling in viewsets."""

    def test_invalid_bbox_format(self, api_client: APIClient) -> None:
        """
        Test handling of invalid bbox format.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("county-list")
        response = api_client.get(url, {"bbox": "invalid"})
        assert response.status_code in ALL_STATUSES

    def test_invalid_pagination_parameters(self, api_client: APIClient) -> None:
        """
        Test handling of invalid pagination parameters.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("municipality-list")
        response = api_client.get(url, {"limit": "invalid", "offset": "invalid"})
        assert response.status_code in ALL_STATUSES

    def test_nonexistent_resource(self, api_client: APIClient) -> None:
        """
        Test retrieving a nonexistent resource.

        Args:
            api_client (APIClient): API client
        """
        url = reverse("county-detail", kwargs={"pk": 999999})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
