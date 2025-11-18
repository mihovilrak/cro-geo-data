"""
Management command to publish all configured layers to GeoServer.

This command invokes the GeoServer REST API to (re)publish spatial layers
as defined in the project's publishing configuration. Intended for use after
database refresh or metadata changes. Used both in automation and for manual
GeoServer refresh from the backend container.

Usage:
    python manage.py publish_layers
"""

from typing import Any

from django.core.management.base import BaseCommand

from geoserver_integration.publisher import publish_layers

class Command(BaseCommand):
    """
    Django management command to (re)publish
    all configured spatial layers to GeoServer.

    This command calls the GeoServer REST API to ensure the latest database
    state is reflected in published map layers. It is typically used following
    a data refresh, schema migration, or style update—either as part of the
    automated ETL pipeline or for manual intervention.
    """
    help = "Publish all configured layers to GeoServer via the REST API."

    def handle(self, *args: Any, **options: Any) -> None:
        """
        Publishes all configured layers to GeoServer.

        Args:
            *args (Any): Variable length argument list.
            **options (Any): Arbitrary keyword arguments
                        passed from the management command.
        """
        publish_layers()
        self.stdout.write(self.style.SUCCESS("GeoServer layers published."))
