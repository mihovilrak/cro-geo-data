"""
Utilities for tracking ETL pipeline runs in the journal schema.
"""
from __future__ import annotations
from collections.abc import Iterator
from contextlib import contextmanager

from django.db import connection

from logger import logger

class ETLRunTracker:
    """
    Tracks ETL pipeline runs in the journal.etl_runs table.
    """

    def __init__(self) -> None:
        """Initialize the tracker."""
        self.run_id: int | None = None

    def start_run(
        self,
        *,
        downloads_performed: bool = False,
        geoserver_published: bool = False,
    ) -> int:
        """
        Start a new ETL run and return the run ID.

        Args:
            downloads_performed: Whether downloads will be performed.
            geoserver_published: Whether GeoServer publishing will be performed.

        Returns:
            The run ID.
        """
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO journal.etl_runs
                    (started_at, status, downloads_performed, geoserver_published)
                VALUES
                    (CURRENT_TIMESTAMP, 'running', %s, %s)
                RETURNING id;
                """,
                [downloads_performed, geoserver_published],
            )
            self.run_id = cursor.fetchone()[0]
            logger.info("Started ETL run #%d", self.run_id)
            return self.run_id

    def complete_run(
        self,
        *,
        success: bool = True,
        error_message: str | None = None,
        records_inserted: int | None = None,
        records_deleted: int | None = None,
        records_updated: int | None = None,
    ) -> None:
        """
        Mark an ETL run as completed.

        Args:
            success: Whether the run succeeded.
            error_message: Error message if the run failed.
            records_inserted: Total number of records inserted across all tables.
            records_deleted: Total number of records deleted across all tables.
            records_updated: Total number of records updated across all tables.
        """
        if self.run_id is None:
            logger.warning("Attempted to complete run but no run_id set")
            return

        status = "completed" if success else "failed"
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE journal.etl_runs
                SET
                    completed_at = CURRENT_TIMESTAMP,
                    status = %s,
                    error_message = %s,
                    records_inserted = %s,
                    records_deleted = %s,
                    records_updated = %s,
                    duration_seconds = EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - started_at))::INTEGER
                WHERE id = %s;
                """,
                [
                    status,
                    error_message,
                    records_inserted,
                    records_deleted,
                    records_updated,
                    self.run_id,
                ],
            )
            logger.info(
                "Completed ETL run #%d with status: %s",
                self.run_id,
                status,
            )

    def update_geoserver_status(self, published: bool) -> None:
        """
        Update the GeoServer published status for the current run.

        Args:
            published: Whether GeoServer publishing was performed.
        """
        if self.run_id is None:
            return

        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE journal.etl_runs
                SET geoserver_published = %s
                WHERE id = %s;
                """,
                [published, self.run_id],
            )

    def get_journal_summary(self) -> dict[str, int]:
        """
        Get summary statistics from journal tables for the most recent update.

        Returns:
            Dictionary with 'inserted', 'deleted', 'updated' totals.
        """
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    COALESCE(SUM(inserted), 0) AS total_inserted,
                    COALESCE(SUM(deleted), 0) AS total_deleted,
                    COALESCE(SUM(updated), 0) AS total_updated
                FROM journal.v_journals
                WHERE created_at >= (
                    SELECT MAX(created_at) - INTERVAL '1 hour'
                    FROM journal.v_journals
                );
                """
            )
            row = cursor.fetchone()
            return {
                "inserted": int(row[0]) if row[0] else 0,
                "deleted": int(row[1]) if row[1] else 0,
                "updated": int(row[2]) if row[2] else 0,
            }

@contextmanager
def track_etl_run(
    downloads_performed: bool = False,
    geoserver_published: bool = False,
) -> Iterator[ETLRunTracker]:
    """
    Context manager for tracking an ETL run.

    Usage:
        with track_etl_run(downloads_performed=True) as tracker:
            # Run ETL pipeline
            pass
        # Run is automatically marked as completed on exit
    """
    tracker = ETLRunTracker()
    run_id = tracker.start_run(
        downloads_performed=downloads_performed,
        geoserver_published=geoserver_published,
    )
    success = True
    error_message = None

    try:
        yield tracker
    except Exception as e:
        success = False
        error_message = str(e)
        logger.exception("ETL run #%d failed", run_id)
        raise
    finally:
        try:
            summary = tracker.get_journal_summary()
            tracker.complete_run(
                success=success,
                records_inserted=summary["inserted"],
                records_deleted=summary["deleted"],
                records_updated=summary["updated"],
                error_message=error_message,
            )
        except Exception as e:
            logger.exception(
                "Failed to complete ETL run tracking for run #%d: %s",
                run_id,
                e,
            )