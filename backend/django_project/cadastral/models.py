"""
GeoDjango models that reflect the spatial tables defined in ``db/init``.

The database schema is provisioned via SQL scripts (outside of Django's
migration system), therefore every model below sets ``managed = False`` and
points ``db_table`` to the correct schema-qualified name.  Relationships rely
on the natural keys that exist in PostGIS (e.g. ``national_code``), so we
explicitly wire ``to_field``/``db_column`` to avoid surrogate keys.
"""
from django.contrib.gis.db import models


class TimestampedGeometryModel(models.Model):
    """
    Reusable mixin for read-only tables that expose an ``updated_at`` column.
    """

    updated_at = models.DateTimeField()

    class Meta:
        abstract = True
        managed = False


class County(TimestampedGeometryModel):
    id = models.IntegerField(primary_key=True)
    national_code = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    geom = models.MultiPolygonField(srid=3765)

    class Meta:
        managed = False
        db_table = '"rpj"."counties"'
        ordering = ("name",)
        verbose_name = "County"
        verbose_name_plural = "Counties"

    def __str__(self) -> str:
        return f"{self.name} ({self.national_code})"


class Municipality(TimestampedGeometryModel):
    id = models.IntegerField(primary_key=True)
    national_code = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    county = models.ForeignKey(
        County,
        to_field="national_code",
        db_column="county_code",
        related_name="municipalities",
        on_delete=models.DO_NOTHING,
    )
    geom = models.MultiPolygonField(srid=3765)

    class Meta:
        managed = False
        db_table = '"rpj"."municipalities"'
        ordering = ("name",)
        verbose_name = "Municipality"
        verbose_name_plural = "Municipalities"

    def __str__(self) -> str:
        return f"{self.name} ({self.national_code})"


class Settlement(TimestampedGeometryModel):
    id = models.IntegerField(primary_key=True)
    national_code = models.IntegerField(unique=True)
    municipality = models.ForeignKey(
        Municipality,
        to_field="national_code",
        db_column="municipality_code",
        related_name="settlements",
        on_delete=models.DO_NOTHING,
    )
    name = models.CharField(max_length=255)
    geom = models.MultiPolygonField(srid=3765)

    class Meta:
        managed = False
        db_table = '"rpj"."settlements"'
        ordering = ("name",)
        verbose_name = "Settlement"
        verbose_name_plural = "Settlements"

    def __str__(self) -> str:
        return f"{self.name} ({self.national_code})"


class PostalOffice(TimestampedGeometryModel):
    id = models.BigIntegerField(primary_key=True)
    postal_code = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = '"rpj"."postal_offices"'
        ordering = ("postal_code",)
        verbose_name = "Postal Office"
        verbose_name_plural = "Postal Offices"

    def __str__(self) -> str:
        return f"{self.postal_code} {self.name}"


class Street(TimestampedGeometryModel):
    id = models.BigIntegerField(primary_key=True)
    unique_identifier = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=255)
    settlement = models.ForeignKey(
        Settlement,
        to_field="national_code",
        db_column="settlement_code",
        related_name="streets",
        on_delete=models.DO_NOTHING,
    )
    postal_office = models.ForeignKey(
        PostalOffice,
        to_field="postal_code",
        db_column="postal_code",
        related_name="streets",
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
    )

    class Meta:
        managed = False
        db_table = '"rpj"."streets"'
        ordering = ("name",)
        verbose_name = "Street"
        verbose_name_plural = "Streets"

    def __str__(self) -> str:
        return self.name


class Address(TimestampedGeometryModel):
    id = models.BigIntegerField(primary_key=True)
    street = models.ForeignKey(
        Street,
        db_column="street_id",
        related_name="addresses",
        on_delete=models.DO_NOTHING,
    )
    house_number = models.CharField(max_length=10)
    geom = models.PointField(srid=3765)

    class Meta:
        managed = False
        db_table = '"rpj"."addresses"'
        ordering = ("id",)
        verbose_name = "Address"
        verbose_name_plural = "Addresses"

    def __str__(self) -> str:
        return f"{self.street.name} {self.house_number}"


class CadastralMunicipality(TimestampedGeometryModel):
    id = models.IntegerField(primary_key=True)
    national_code = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    harmonization_status = models.IntegerField()
    geom = models.MultiPolygonField(srid=3765)

    class Meta:
        managed = False
        db_table = '"dkp"."cadastral_municipalities"'
        ordering = ("name",)
        verbose_name = "Cadastral Municipality"
        verbose_name_plural = "Cadastral Municipalities"

    def __str__(self) -> str:
        return f"{self.name} ({self.national_code})"


class CadastralParcel(TimestampedGeometryModel):
    id = models.IntegerField(primary_key=True)
    parcel_code = models.CharField(max_length=20)
    cadastral_municipality = models.ForeignKey(
        CadastralMunicipality,
        to_field="national_code",
        db_column="cadastral_municipality_code",
        related_name="parcels",
        on_delete=models.DO_NOTHING,
    )
    graphical_area = models.DecimalField(max_digits=12, decimal_places=2)
    geom = models.MultiPolygonField(srid=3765)

    class Meta:
        managed = False
        db_table = '"dkp"."cadastral_parcels"'
        ordering = ("parcel_code",)
        verbose_name = "Cadastral Parcel"
        verbose_name_plural = "Cadastral Parcels"

    def __str__(self) -> str:
        return f"{self.cadastral_municipality.national_code}-{self.parcel_code}"


