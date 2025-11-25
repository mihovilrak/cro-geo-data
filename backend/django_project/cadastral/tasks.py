"""
Celery tasks orchestrating the ETL pipeline and GeoServer automation.
"""
from __future__ import annotations
from pathlib import Path

from celery import shared_task
from django.db import connection

from cadastral.etl_journaling import track_etl_run
from geoserver_integration.publisher import publish_layers
from scripts.dkp_downloader import DKPDownloader
from scripts import extractor, rpj_downloader

from logger import logger

@shared_task
def run_full_ingest() -> None:
    """
    Entry point scheduled via Celery Beat: download datasets, refresh tables,
    and notify GeoServer so endpoints remain in sync.
    """
    run_pipeline()

def run_pipeline(
    *,
    perform_downloads: bool = True,
    publish_to_geoserver: bool = True,
) -> None:
    """
    Shared orchestrator used by Celery tasks and the ``run_ingest`` management
    command. Allows selective skipping of downloads or GeoServer publication for
    faster local iterations.

    Args:
        perform_downloads (bool): Whether to perform downloads.
        publish_to_geoserver (bool): Whether to publish to GeoServer.
    """
    logger.info(
        "Starting ingest pipeline (downloads=%s, publish=%s)",
        perform_downloads,
        publish_to_geoserver,
    )

    with track_etl_run(
        downloads_performed=perform_downloads,
        geoserver_published=publish_to_geoserver,
    ) as tracker:
        if perform_downloads:
            download_and_extract_sources()
        else:
            logger.info("Skipping download/extraction step")

        apply_database_refresh()

        if publish_to_geoserver:
            logger.info("Publishing layers to GeoServer")
            try:
                publish_layers()
                tracker.update_geoserver_status(True)
            except Exception as e:
                logger.exception("GeoServer publishing failed: %s", e)
                tracker.update_geoserver_status(False)
        else:
            logger.info("Skipping GeoServer publication step")

    logger.info("Pipeline complete")

def download_and_extract_sources(max_concurrent_downloads: int = 5) -> None:
    """
    Downloads and extracts required data sources for the ETL pipeline.

    Downloads the latest DKP archives using multiple concurrent downloads and
    extracts their contents. Also downloads AU (Administrative Units) and AD
    (Addresses) datasets, which handle extraction internally.

    Args:
        max_concurrent_downloads (int): Maximum number of concurrent downloads
            for DKP archives. Defaults to 5.
    """
    downloader = DKPDownloader()
    downloaded_paths = downloader.download(max_concurrent_downloads)
    for zip_path in downloaded_paths:
        logger.info("Extracting DKP archive %s", Path(zip_path).name)
        extractor.extract_dkp(zip_path)

    logger.info("Downloading AU dataset")
    rpj_downloader.download_au()
    logger.info("Downloading AD dataset")
    rpj_downloader.download_ad()

def apply_database_refresh() -> None:
    """
    Execute the PostGIS merge routine that moves data from staging tables
    into the production schemas + refreshes materialized views.
    """
    logger.info("Applying staging.update_tables()")
    with connection.cursor() as cursor:
        cursor.execute("SELECT staging.update_tables();")
