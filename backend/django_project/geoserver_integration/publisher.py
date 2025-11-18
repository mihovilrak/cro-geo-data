"""
Minimal GeoServer REST client used by the ETL pipeline to (re)publish layers.
"""
from __future__ import annotations

import logging
from typing import Any, TYPE_CHECKING

import httpx
from django.conf import settings
from django.db import connection

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

logger = logging.getLogger(__name__)

class GeoServerPublisher:
    """
    Minimal GeoServer REST client used by the ETL pipeline to (re)publish layers.
    """
    def __init__(self) -> None:
        """
        Initializes the GeoServer publisher.
        """
        self.base_url = settings.GEOSERVER_URL.rstrip("/")
        self.workspace = settings.GEOSERVER_WORKSPACE
        self.datastore = settings.GEOSERVER_DATASTORE
        self._client = httpx.Client(
            base_url=self.base_url,
            auth=(settings.GEOSERVER_USER, settings.GEOSERVER_PASSWORD),
            timeout=60.0,
        )

    def publish_catalog(self, catalog: Sequence[Mapping[str, Any]]) -> None:
        """
        Publishes the layer catalog to GeoServer.

        Args:
            catalog (Sequence[Mapping[str, Any]]): The layer catalog to publish.
        """
        self._ensure_workspace()
        self._ensure_datastore()
        for layer in catalog:
            try:
                self._publish_layer(layer)
            except httpx.HTTPError as exc:
                logger.exception("GeoServer publish failed for %s: %s", layer["id"], exc)

    def _ensure_workspace(self) -> None:
        """
        Ensures the GeoServer workspace exists.
        """
        resp = self._client.get(f"/rest/workspaces/{self.workspace}.json")
        if resp.status_code == 200:
            return
        payload = {"workspace": {"name": self.workspace}}
        logger.info("Creating GeoServer workspace %s", self.workspace)
        self._client.post("/rest/workspaces", json=payload)

    def _ensure_datastore(self) -> None:
        """
        Ensures the GeoServer datastore exists.
        """
        resp = self._client.get(
            f"/rest/workspaces/{self.workspace}/datastores/{self.datastore}.json"
        )
        if resp.status_code == 200:
            return

        payload = {
            "dataStore": {
                "name": self.datastore,
                "connectionParameters": {
                    "host": settings.DATABASES["default"]["HOST"],
                    "port": settings.DATABASES["default"]["PORT"],
                    "database": settings.DATABASES["default"]["NAME"],
                    "user": settings.DATABASES["default"]["USER"],
                    "passwd": settings.DATABASES["default"]["PASSWORD"],
                    "dbtype": "postgis",
                    "schema": "public",
                },
            }
        }
        logger.info(
            "Creating GeoServer datastore %s in workspace %s",
            self.datastore,
            self.workspace,
        )
        self._client.post(
            f"/rest/workspaces/{self.workspace}/datastores",
            json=payload,
        )

    def _publish_layer(self, layer: Mapping[str, Any]) -> None:
        """
        Publishes a layer to GeoServer.

        Args:
            layer (Mapping[str, Any]): The layer to publish.
        """
        bbox = self._compute_bbox(layer["native_table"])
        payload = {
            "featureType": {
                "name": layer["wms_name"],
                "nativeName": layer["native_table"],
                "title": layer["title"],
                "srs": "EPSG:3765",
                "nativeCRS": "EPSG:3765",
                "projectionPolicy": "REPROJECT_TO_DECLARED",
                "enabled": True,
                "nativeBoundingBox": bbox,
                "latLonBoundingBox": {
                    "minx": 13.0,
                    "maxx": 20.0,
                    "miny": 42.0,
                    "maxy": 47.0,
                    "crs": "EPSG:4326",
                },
            }
        }
        url = (
            f"/rest/workspaces/{self.workspace}/datastores/"
            f"{self.datastore}/featuretypes"
        )
        create_resp = self._client.post(url, json=payload)
        if create_resp.status_code == 201:
            logger.info("Published GeoServer layer %s", layer["wms_name"])
            return
        if create_resp.status_code == 409:
            self._client.put(f"{url}/{layer['wms_name']}", json=payload)
            logger.info("Updated GeoServer layer %s", layer["wms_name"])
            return
        create_resp.raise_for_status()

    def _compute_bbox(self, table_name: str) -> dict[str, float]:
        """
        Computes the bounding box of a layer.

        Args:
            table_name (str): The name of the table to compute the bounding box of.

        Returns:
            dict[str, float]: The bounding box of the layer.
        """
        schema, table = table_name.split(".", 1)
        qualified = f'"{schema}"."{table}"'
        sql = f"""
            SELECT
                ST_XMin(extent),
                ST_YMin(extent),
                ST_XMax(extent),
                ST_YMax(extent)
            FROM (
                SELECT ST_Extent(geom) AS extent FROM {qualified}
            ) AS sub;
        """
        with connection.cursor() as cursor:
            cursor.execute(sql)
            row = cursor.fetchone()
        if not row:
            return {
                "minx": 0.0,
                "miny": 0.0,
                "maxx": 0.0,
                "maxy": 0.0,
                "crs": "EPSG:3765",
            }
        minx, miny, maxx, maxy = row
        return {
            "minx": float(minx or 0.0),
            "miny": float(miny or 0.0),
            "maxx": float(maxx or 0.0),
            "maxy": float(maxy or 0.0),
            "crs": "EPSG:3765",
        }

def publish_layers() -> None:
    """
    Convenience helper used by Celery tasks.
    """
    publisher = GeoServerPublisher()
    publisher.publish_catalog(settings.LAYER_CATALOG)
