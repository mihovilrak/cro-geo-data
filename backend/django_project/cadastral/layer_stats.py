"""
Layer statistics endpoint implementation.

Provides metadata about each layer including:
- Total feature count
- Last updated timestamp
- Data freshness indicators
"""

from datetime import datetime
from typing import Any

from django.db.models import Max
from django.utils import timezone
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Address,
    Building,
    CadastralMunicipality,
    CadastralParcel,
    County,
    Municipality,
    Settlement,
    StreetFeature,
)

LAYER_STATS_MODEL_MAP: dict[str, Any] = {
    "cadastral_parcels": CadastralParcel,
    "cadastral_municipalities": CadastralMunicipality,
    "counties": County,
    "municipalities": Municipality,
    "settlements": Settlement,
    "streets": StreetFeature,
    "addresses": Address,
    "buildings": Building,
}

class LayerStatsView(APIView):
    """
    Endpoint to retrieve statistics for all layers in the catalog.

    Returns counts and last updated timestamps for each layer,
    enabling the frontend to display data freshness indicators.
    """
    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        """
        Return statistics for all layers in the catalog.

        Response format:
        {
            "layers": {
                "cadastral_parcels": {
                    "count": 1234567,
                    "last_updated": "2025-01-15T10:30:00Z",
                    "freshness_days": 5
                },
                ...
            }
        }
        """
        stats: dict[str, dict[str, Any]] = {}

        for layer_id, model in LAYER_STATS_MODEL_MAP.items():
            try:
                count = model.objects.count()

                if hasattr(model, "updated_at"):
                    last_updated_result = model.objects.aggregate(
                        max_updated=Max("updated_at")
                    )
                    last_updated = last_updated_result.get("max_updated")
                else:
                    last_updated = None

                freshness_days: int | None = None
                if last_updated:
                    if isinstance(last_updated, datetime):
                        if last_updated.tzinfo is None:
                            from datetime import timezone as tz
                            last_updated = last_updated.replace(tzinfo=tz.utc)
                        now = timezone.now()
                        delta = now - last_updated
                        freshness_days = delta.days

                stats[layer_id] = {
                    "count": count,
                    "last_updated": (
                        last_updated.isoformat() if last_updated else None
                    ),
                    "freshness_days": freshness_days,
                }
            except Exception as e:
                stats[layer_id] = {
                    "count": None,
                    "last_updated": None,
                    "freshness_days": None,
                    "error": str(e),
                }

        return Response({"layers": stats})
