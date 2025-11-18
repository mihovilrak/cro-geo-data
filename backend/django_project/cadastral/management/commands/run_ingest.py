"""Management command to execute the full ingest pipeline.

This module provides a Django management command that triggers the entire ETL
workflow: downloading data sources, updating PostGIS tables, and publishing
layers to GeoServer as needed. Allows for selective skipping of download and
publish steps via command-line flags.
"""

from __future__ import annotations
from typing import Any, TYPE_CHECKING

from django.core.management.base import BaseCommand

from cadastral import tasks

if TYPE_CHECKING:
    import argparse

class Command(BaseCommand):
    """
    Django management command to run the full cadastral data ingest pipeline.

    This command triggers the ETL workflow including:
      - Downloading source datasets (with option to skip via --skip-download)
      - Refreshing PostGIS spatial tables
      - Republishing layers in GeoServer (with option to skip via --skip-publish)

    It is intended for manual invocation within the backend container or as an
    integration point for automation. The command-line flags allow selective
    re-execution of only the desired pipeline stages.
    """
    help = (
        "Run the full ingest pipeline once: download sources, refresh PostGIS,"
        " and republish GeoServer layers."
    )

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add command-line arguments for the ingest pipeline command.

        Adds options to control which steps of the ETL pipeline are executed,
        allowing selective skipping of the download and GeoServer publishing phases.

        Args:
            parser (argparse.ArgumentParser): The parser to 
                            which arguments should be added.
        """
        parser.add_argument(
            "--skip-download",
            action="store_true",
            help="Reuse already downloaded archives and skip network calls.",
        )
        parser.add_argument(
            "--skip-publish",
            action="store_true",
            help="Skip the GeoServer publication step.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """
        Executes the cadastral data ingest pipeline.

        This method coordinates the ETL workflow by
        invoking the pipeline tasks with options to
        selectively skip resource-intensive steps
        based on user-specified command-line flags.

        Args:
            *args (Any): Positional arguments passed by the
                        Django management framework (unused).
            **options (Any): Dictionary of keyword arguments
                            containing command-line options.
                - skip_download (bool): If True, skip dataset download steps.
                - skip_publish (bool): If True, skip GeoServer publication steps.
        """
        tasks.run_pipeline(
            perform_downloads=not options["skip_download"],
            publish_to_geoserver=not options["skip_publish"],
        )
        self.stdout.write(self.style.SUCCESS("Ingest pipeline completed."))
