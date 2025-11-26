"""
GetFeatureInfo proxy endpoint implementation.

Provides a DRF endpoint that queries PostGIS directly for features
at a given point, returning enriched metadata with parent relationships.
"""

from typing import Any, Optional

from django.contrib.gis.geos import Point
from django.conf import settings
from rest_framework import status
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
)
from .serializers import (
    AddressSerializer,
    BuildingSerializer,
    CadastralMunicipalitySerializer,
    CadastralParcelSerializer,
    CountySerializer,
    MunicipalitySerializer,
    SettlementSerializer,
)

LAYER_MODEL_MAP = {
    "cadastral_parcels": {
        "model": CadastralParcel,
        "serializer": CadastralParcelSerializer,
        "geom_field": "geom",
        "tolerance_meters": 10.0,
    },
    "cadastral_municipalities": {
        "model": CadastralMunicipality,
        "serializer": CadastralMunicipalitySerializer,
        "geom_field": "geom",
        "tolerance_meters": 50.0,
    },
    "counties": {
        "model": County,
        "serializer": CountySerializer,
        "geom_field": "geom",
        "tolerance_meters": 100.0,
    },
    "municipalities": {
        "model": Municipality,
        "serializer": MunicipalitySerializer,
        "geom_field": "geom",
        "tolerance_meters": 50.0,
    },
    "settlements": {
        "model": Settlement,
        "serializer": SettlementSerializer,
        "geom_field": "geom",
        "tolerance_meters": 25.0,
    },
    "buildings": {
        "model": Building,
        "serializer": BuildingSerializer,
        "geom_field": "geom",
        "tolerance_meters": 10.0,
    },
    "addresses": {
        "model": Address,
        "serializer": AddressSerializer,
        "geom_field": "geom",
        "tolerance_meters": 5.0,
    },
}

class GetFeatureInfoView(APIView):
    """
    GetFeatureInfo proxy endpoint.

    Accepts lat/lon coordinates and optional layer name, queries PostGIS
    directly for intersecting features, and returns enriched metadata.

    Query parameters:
        - lat: Latitude in WGS84 (EPSG:4326)
        - lon: Longitude in WGS84 (EPSG:4326)
        - layer: Optional layer ID (e.g., "cadastral_parcels")
        - tolerance: Optional tolerance in meters (default: layer-specific)
        - srid: Optional source SRID (default: 4326)

    Returns GeoJSON FeatureCollection with enriched properties.
    """

    def get(self, request: Request) -> Response:
        """
        Handle GET requests for feature info at a point.
        """
        try:
            lat = float(request.query_params.get("lat"))
            lon = float(request.query_params.get("lon"))
        except (TypeError, ValueError):
            return Response(
                {"error": "Missing or invalid lat/lon parameters"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        layer_id = request.query_params.get("layer")
        tolerance = request.query_params.get("tolerance")
        source_srid = int(request.query_params.get("srid", 4326))

        point_wgs84 = Point(lon, lat, srid=source_srid)
        point_croatia = point_wgs84.transform(3765, clone=True)

        if layer_id:
            layers_to_query = [layer_id] if layer_id in LAYER_MODEL_MAP else []
        else:
            layers_to_query = list(LAYER_MODEL_MAP.keys())

        if not layers_to_query:
            return Response(
                {"error": f"Unknown layer: {layer_id}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        all_features = []

        for lid in layers_to_query:
            layer_config = LAYER_MODEL_MAP[lid]
            model = layer_config["model"]
            serializer_class = layer_config["serializer"]
            geom_field = layer_config["geom_field"]
            default_tolerance = layer_config["tolerance_meters"]

            tol = float(tolerance) if tolerance else default_tolerance

            query_point = point_croatia
            query_geom = query_point.buffer(tol)

            queryset = model.objects.filter(**{f"{geom_field}__intersects": query_geom})

            limit = 1 if lid != "addresses" else 5
            queryset = queryset[:limit]

            for obj in queryset:
                serializer = serializer_class(obj)
                feature_data = serializer.data

                if isinstance(feature_data, dict):
                    if "properties" in feature_data:
                        feature_data["properties"]["_layer"] = lid
                        feature_data["properties"]["_layer_title"] = self._get_layer_title(lid)
                    else:
                        feature_data["_layer"] = lid
                        feature_data["_layer_title"] = self._get_layer_title(lid)

                all_features.append(feature_data)

        return Response({
            "type": "FeatureCollection",
            "features": all_features,
            "query": {
                "lat": lat,
                "lon": lon,
                "layer": layer_id,
                "tolerance": tolerance or "default",
            },
        })

    def _get_layer_title(self, layer_id: str) -> str:
        """Get human-readable layer title from catalog."""
        for layer in settings.LAYER_CATALOG:
            if layer.get("id") == layer_id:
                return layer.get("title", layer_id)
        return layer_id
