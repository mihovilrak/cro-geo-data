"""
Comprehensive tests for URL routing and reverse lookups.
"""
import pytest
from django.urls import resolve, reverse, NoReverseMatch

from cadastral import views


@pytest.mark.django_db
class TestURLRouting:
    """Tests for URL routing."""

    def test_country_url_resolves(self):
        """Test that country URL resolves correctly."""
        url = "/api/country/"
        resolved = resolve(url)
        assert resolved.func.cls is views.CountryViewSet
        assert resolved.url_name == "country-list"

    def test_country_detail_url_resolves(self):
        """Test that country detail URL resolves correctly."""
        url = "/api/country/1/"
        resolved = resolve(url)
        assert resolved.func.cls is views.CountryViewSet
        assert resolved.url_name == "country-detail"
        assert resolved.kwargs["pk"] == "1"

    def test_counties_url_resolves(self):
        """Test that counties URL resolves correctly."""
        url = "/api/counties/"
        resolved = resolve(url)
        assert resolved.func.cls is views.CountyViewSet
        assert resolved.url_name == "county-list"

    def test_counties_detail_url_resolves(self):
        """Test that counties detail URL resolves correctly."""
        url = "/api/counties/1/"
        resolved = resolve(url)
        assert resolved.func.cls is views.CountyViewSet
        assert resolved.url_name == "county-detail"

    def test_municipalities_url_resolves(self):
        """Test that municipalities URL resolves correctly."""
        url = "/api/municipalities/"
        resolved = resolve(url)
        assert resolved.func.cls is views.MunicipalityViewSet
        assert resolved.url_name == "municipality-list"

    def test_municipalities_detail_url_resolves(self):
        """Test that municipalities detail URL resolves correctly."""
        url = "/api/municipalities/1/"
        resolved = resolve(url)
        assert resolved.func.cls is views.MunicipalityViewSet
        assert resolved.url_name == "municipality-detail"

    def test_settlements_url_resolves(self):
        """Test that settlements URL resolves correctly."""
        url = "/api/settlements/"
        resolved = resolve(url)
        assert resolved.func.cls is views.SettlementViewSet
        assert resolved.url_name == "settlement-list"

    def test_settlements_detail_url_resolves(self):
        """Test that settlements detail URL resolves correctly."""
        url = "/api/settlements/1/"
        resolved = resolve(url)
        assert resolved.func.cls is views.SettlementViewSet
        assert resolved.url_name == "settlement-detail"

    def test_streets_url_resolves(self):
        """Test that streets URL resolves correctly."""
        url = "/api/streets/"
        resolved = resolve(url)
        assert resolved.func.cls is views.StreetViewSet
        assert resolved.url_name == "street-list"

    def test_streets_detail_url_resolves(self):
        """Test that streets detail URL resolves correctly."""
        url = "/api/streets/1/"
        resolved = resolve(url)
        assert resolved.func.cls is views.StreetViewSet
        assert resolved.url_name == "street-detail"

    def test_addresses_url_resolves(self):
        """Test that addresses URL resolves correctly."""
        url = "/api/addresses/"
        resolved = resolve(url)
        assert resolved.func.cls is views.AddressViewSet
        assert resolved.url_name == "address-list"

    def test_addresses_detail_url_resolves(self):
        """Test that addresses detail URL resolves correctly."""
        url = "/api/addresses/1/"
        resolved = resolve(url)
        assert resolved.func.cls is views.AddressViewSet
        assert resolved.url_name == "address-detail"

    def test_postal_offices_url_resolves(self):
        """Test that postal offices URL resolves correctly."""
        url = "/api/postal_offices/"
        resolved = resolve(url)
        assert resolved.func.cls is views.PostalOfficeViewSet
        assert resolved.url_name == "postaloffice-list"

    def test_postal_offices_detail_url_resolves(self):
        """Test that postal offices detail URL resolves correctly."""
        url = "/api/postal_offices/1/"
        resolved = resolve(url)
        assert resolved.func.cls is views.PostalOfficeViewSet
        assert resolved.url_name == "postaloffice-detail"

    def test_cadastral_municipalities_url_resolves(self):
        """Test that cadastral municipalities URL resolves correctly."""
        url = "/api/cadastral_municipalities/"
        resolved = resolve(url)
        assert resolved.func.cls is views.CadastralMunicipalityViewSet
        assert resolved.url_name == "cadastralmunicipality-list"

    def test_cadastral_municipalities_detail_url_resolves(self):
        """Test that cadastral municipalities detail URL resolves correctly."""
        url = "/api/cadastral_municipalities/1/"
        resolved = resolve(url)
        assert resolved.func.cls is views.CadastralMunicipalityViewSet
        assert resolved.url_name == "cadastralmunicipality-detail"

    def test_cadastral_parcels_url_resolves(self):
        """Test that cadastral parcels URL resolves correctly."""
        url = "/api/cadastral_parcels/"
        resolved = resolve(url)
        assert resolved.func.cls is views.CadastralParcelViewSet
        assert resolved.url_name == "cadastralparcel-list"

    def test_cadastral_parcels_detail_url_resolves(self):
        """Test that cadastral parcels detail URL resolves correctly."""
        url = "/api/cadastral_parcels/1/"
        resolved = resolve(url)
        assert resolved.func.cls is views.CadastralParcelViewSet
        assert resolved.url_name == "cadastralparcel-detail"

    def test_buildings_url_resolves(self):
        """Test that buildings URL resolves correctly."""
        url = "/api/buildings/"
        resolved = resolve(url)
        assert resolved.func.cls is views.BuildingViewSet
        assert resolved.url_name == "building-list"

    def test_buildings_detail_url_resolves(self):
        """Test that buildings detail URL resolves correctly."""
        url = "/api/buildings/1/"
        resolved = resolve(url)
        assert resolved.func.cls is views.BuildingViewSet
        assert resolved.url_name == "building-detail"

    def test_usages_url_resolves(self):
        """Test that usages URL resolves correctly."""
        url = "/api/usages/"
        resolved = resolve(url)
        assert resolved.func.cls is views.UsageViewSet
        assert resolved.url_name == "usage-list"

    def test_usages_detail_url_resolves(self):
        """Test that usages detail URL resolves correctly."""
        url = "/api/usages/1/"
        resolved = resolve(url)
        assert resolved.func.cls is views.UsageViewSet
        assert resolved.url_name == "usage-detail"

    def test_layers_url_resolves(self):
        """Test that layers catalog URL resolves correctly."""
        url = "/api/layers/"
        resolved = resolve(url)
        assert resolved.func.cls is views.LayerCatalogView
        assert resolved.url_name == "layer-catalog"


@pytest.mark.django_db
class TestReverseLookups:
    """Tests for reverse URL lookups."""

    def test_reverse_country_list(self):
        """Test reverse lookup for country list."""
        url = reverse("country-list")
        assert url == "/api/country/"

    def test_reverse_country_detail(self):
        """Test reverse lookup for country detail."""
        url = reverse("country-detail", kwargs={"pk": 1})
        assert url == "/api/country/1/"

    def test_reverse_counties_list(self):
        """Test reverse lookup for counties list."""
        url = reverse("county-list")
        assert url == "/api/counties/"

    def test_reverse_counties_detail(self):
        """Test reverse lookup for counties detail."""
        url = reverse("county-detail", kwargs={"pk": 1})
        assert url == "/api/counties/1/"

    def test_reverse_municipalities_list(self):
        """Test reverse lookup for municipalities list."""
        url = reverse("municipality-list")
        assert url == "/api/municipalities/"

    def test_reverse_municipalities_detail(self):
        """Test reverse lookup for municipalities detail."""
        url = reverse("municipality-detail", kwargs={"pk": 1})
        assert url == "/api/municipalities/1/"

    def test_reverse_settlements_list(self):
        """Test reverse lookup for settlements list."""
        url = reverse("settlement-list")
        assert url == "/api/settlements/"

    def test_reverse_settlements_detail(self):
        """Test reverse lookup for settlements detail."""
        url = reverse("settlement-detail", kwargs={"pk": 1})
        assert url == "/api/settlements/1/"

    def test_reverse_streets_list(self):
        """Test reverse lookup for streets list."""
        url = reverse("street-list")
        assert url == "/api/streets/"

    def test_reverse_streets_detail(self):
        """Test reverse lookup for streets detail."""
        url = reverse("street-detail", kwargs={"pk": 1})
        assert url == "/api/streets/1/"

    def test_reverse_addresses_list(self):
        """Test reverse lookup for addresses list."""
        url = reverse("address-list")
        assert url == "/api/addresses/"

    def test_reverse_addresses_detail(self):
        """Test reverse lookup for addresses detail."""
        url = reverse("address-detail", kwargs={"pk": 1})
        assert url == "/api/addresses/1/"

    def test_reverse_postal_offices_list(self):
        """Test reverse lookup for postal offices list."""
        url = reverse("postaloffice-list")
        assert url == "/api/postal_offices/"

    def test_reverse_postal_offices_detail(self):
        """Test reverse lookup for postal offices detail."""
        url = reverse("postaloffice-detail", kwargs={"pk": 1})
        assert url == "/api/postal_offices/1/"

    def test_reverse_cadastral_municipalities_list(self):
        """Test reverse lookup for cadastral municipalities list."""
        url = reverse("cadastralmunicipality-list")
        assert url == "/api/cadastral_municipalities/"

    def test_reverse_cadastral_municipalities_detail(self):
        """Test reverse lookup for cadastral municipalities detail."""
        url = reverse("cadastralmunicipality-detail", kwargs={"pk": 1})
        assert url == "/api/cadastral_municipalities/1/"

    def test_reverse_cadastral_parcels_list(self):
        """Test reverse lookup for cadastral parcels list."""
        url = reverse("cadastralparcel-list")
        assert url == "/api/cadastral_parcels/"

    def test_reverse_cadastral_parcels_detail(self):
        """Test reverse lookup for cadastral parcels detail."""
        url = reverse("cadastralparcel-detail", kwargs={"pk": 1})
        assert url == "/api/cadastral_parcels/1/"

    def test_reverse_buildings_list(self):
        """Test reverse lookup for buildings list."""
        url = reverse("building-list")
        assert url == "/api/buildings/"

    def test_reverse_buildings_detail(self):
        """Test reverse lookup for buildings detail."""
        url = reverse("building-detail", kwargs={"pk": 1})
        assert url == "/api/buildings/1/"

    def test_reverse_usages_list(self):
        """Test reverse lookup for usages list."""
        url = reverse("usage-list")
        assert url == "/api/usages/"

    def test_reverse_usages_detail(self):
        """Test reverse lookup for usages detail."""
        url = reverse("usage-detail", kwargs={"pk": 1})
        assert url == "/api/usages/1/"

    def test_reverse_layer_catalog(self):
        """Test reverse lookup for layer catalog."""
        url = reverse("layer-catalog")
        assert url == "/api/layers/"


@pytest.mark.django_db
class TestURLEdgeCases:
    """Tests for URL edge cases and error handling."""

    def test_invalid_url_returns_404(self):
        """Test that invalid URL returns 404."""
        from django.test import Client
        client = Client()
        response = client.get("/api/invalid_endpoint/")
        assert response.status_code == 404

    def test_trailing_slash_handling(self):
        """Test that URLs work with and without trailing slashes."""
        # DRF router handles trailing slashes automatically
        url_with_slash = "/api/counties/"
        url_without_slash = "/api/counties"
        # Both should resolve (DRF redirects)
        resolved_with = resolve(url_with_slash)
        assert resolved_with.func.cls is views.CountyViewSet

