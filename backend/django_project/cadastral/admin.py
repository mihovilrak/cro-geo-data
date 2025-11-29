"""
Admin configuration for the cadastral app models.

This module registers the cadastral models with the Django admin interface,
providing custom admin classes for geographic display and configuration.
"""

from django.contrib import admin

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
    Street,
    StreetFeature,
    Usage,
)

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    readonly_fields = ("id", "national_code", "name", "updated_at", "geom")
    list_display = ("name", "national_code", "updated_at")

@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    readonly_fields = ("id", "national_code", "name", "updated_at", "geom")
    list_display = ("name", "national_code", "updated_at")
    search_fields = ("name", "national_code")

@admin.register(Municipality)
class MunicipalityAdmin(admin.ModelAdmin):
    readonly_fields = (
        "id",
        "national_code",
        "name",
        "county",
        "updated_at",
        "geom"
    )
    list_display = ("name", "national_code", "county", "updated_at")
    list_filter = ("county",)
    search_fields = ("name", "national_code")

@admin.register(Settlement)
class SettlementAdmin(admin.ModelAdmin):
    readonly_fields = (
        "id",
        "national_code",
        "name",
        "municipality",
        "updated_at",
        "geom"
    )
    list_display = ("name", "national_code", "municipality", "updated_at")
    list_filter = ("municipality__county", "municipality")
    search_fields = ("name", "national_code")

@admin.register(PostalOffice)
class PostalOfficeAdmin(admin.ModelAdmin):
    readonly_fields = ("id", "postal_code", "name", "updated_at")
    list_display = ("postal_code", "name", "updated_at")
    search_fields = ("name", "postal_code")

@admin.register(Street)
class StreetAdmin(admin.ModelAdmin):
    readonly_fields = (
        "id",
        "unique_identifier",
        "name",
        "settlement",
        "postal_office",
        "updated_at"
    )
    list_display = (
        "name",
        "settlement",
        "postal_office",
        "updated_at"
    )
    list_filter = (
        "settlement__municipality__county",
        "settlement__municipality",
        "settlement"
    )
    search_fields = ("name",)

@admin.register(StreetFeature)
class StreetFeatureAdmin(admin.ModelAdmin):
    readonly_fields = (
        "id",
        "name",
        "unique_identifier",
        "settlement_code",
        "settlement_name",
        "municipality_name",
        "county_name",
        "geom"
    )
    list_display = (
        "name",
        "settlement_name",
        "municipality_name",
        "county_name"
    )
    list_filter = ("county_name", "municipality_name")
    search_fields = ("name", "settlement_name")

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    readonly_fields = (
        "id",
        "street",
        "house_number",
        "updated_at",
        "geom"
    )
    list_display = ("house_number", "street", "updated_at")
    list_filter = (
        "street__settlement__municipality__county",
        "street__settlement__municipality",
        "street__settlement"
    )
    search_fields = ("house_number", "street__name")

@admin.register(CadastralMunicipality)
class CadastralMunicipalityAdmin(admin.ModelAdmin):
    readonly_fields = (
        "id",
        "national_code",
        "name",
        "harmonization_status",
        "updated_at",
        "geom"
    )
    list_display = (
        "name",
        "national_code",
        "harmonization_status",
        "updated_at",
    )
    list_filter = ("harmonization_status",)
    search_fields = ("name", "national_code")

@admin.register(CadastralParcel)
class CadastralParcelAdmin(admin.ModelAdmin):
    readonly_fields = (
        "id",
        "parcel_code",
        "cadastral_municipality",
        "graphical_area",
        "updated_at",
        "geom",
    )
    list_display = (
        "parcel_code",
        "cadastral_municipality",
        "graphical_area",
        "updated_at",
    )
    list_filter = ("cadastral_municipality",)
    search_fields = ("parcel_code", "cadastral_municipality__name")

@admin.register(Usage)
class UsageAdmin(admin.ModelAdmin):
    readonly_fields = ("code", "name", "updated_at")
    list_display = ("code", "name", "updated_at")
    search_fields = ("name",)

@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    readonly_fields = (
        "id",
        "building_number",
        "usage",
        "cadastral_municipality",
        "updated_at",
        "geom",
    )
    list_display = (
        "building_number",
        "cadastral_municipality",
        "usage",
        "updated_at",
    )
    list_filter = ("cadastral_municipality", "usage")
    search_fields = (
        "building_number",
        "cadastral_municipality__name",
        "usage__name",
    )
