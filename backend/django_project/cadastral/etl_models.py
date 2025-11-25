"""
Django models for ETL run tracking (read-only, backed by journal.etl_runs).
"""
from django.db import models

class ETLRun(models.Model):
    """
    Read-only model for journal.etl_runs table.
    Tracks ETL pipeline execution runs.
    """

    id = models.BigIntegerField(primary_key=True)
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20)
    error_message = models.TextField(null=True, blank=True)
    downloads_performed = models.BooleanField()
    geoserver_published = models.BooleanField()
    records_inserted = models.IntegerField(null=True, blank=True)
    records_deleted = models.IntegerField(null=True, blank=True)
    records_updated = models.IntegerField(null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = '"journal"."etl_runs"'
        ordering = ("-started_at",)
        verbose_name = "ETL Run"
        verbose_name_plural = "ETL Runs"

    def __str__(self) -> str:
        return f"ETL Run #{self.id} ({self.status}) - {self.started_at}"
