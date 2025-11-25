"""
Serializers for ETL run tracking endpoints.
"""
from rest_framework import serializers

from .etl_models import ETLRun

class ETLRunSerializer(serializers.ModelSerializer):
    """
    Serializer for ETL run records.
    """
    class Meta:
        model = ETLRun
        fields = (
            "id",
            "started_at",
            "completed_at",
            "status",
            "error_message",
            "downloads_performed",
            "geoserver_published",
            "records_inserted",
            "records_deleted",
            "records_updated",
            "duration_seconds",
            "created_at",
        )
        read_only_fields = fields
