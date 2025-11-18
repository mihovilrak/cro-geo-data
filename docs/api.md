# REST API Endpoints

All endpoints live under `http://<host>/api/` and emit GeoJSON unless noted.
The OpenAPI document is published at `http://<host>/api/openapi.yaml`
and mirrored under version control in `docs/openapi.yaml`.

## Feature Services

### 1. `GET /parcels/`
Spatial features from `dkp.cadastral_parcels`.

**Query parameters**

| Name | Description |
| --- | --- |
| `parcel_id` | Exact parcel code (case-insensitive) |
| `cadastral_municipality_code` | Numeric cadastral municipality code |
| `cadastral_municipality` | Municipality label (substring match) |
| `updated_after`, `updated_before` | ISO8601 timestamps |
| `bbox` | `minX,minY,maxX,maxY` in EPSG:3857 |
| `limit`, `offset` | Pagination controls |

```bash
curl "$API_ROOT/parcels/?cadastral_municipality_code=326704&limit=5"
```

### 2. `GET /admin_boundaries/`
Read-only access to counties or municipalities. Defaults to municipalities;
set `admin_type=county` to switch.

**Query parameters**

| Name | Description |
| --- | --- |
| `admin_type` | `municipality` (default) or `county` |
| `national_code`, `name` | Filter by identifier or label |
| `county_code`, `county_name` | When querying municipalities |
| `bbox`, `limit`, `offset` | Spatial filter + pagination |

```bash
curl "$API_ROOT/admin_boundaries/?admin_type=county&name=Zagreb"
```

### 3. `GET /settlements/`
GeoJSON for `rpj.settlements` with related municipality/county names.

**Query parameters**

| Name | Description |
| --- | --- |
| `national_code`, `name` | Filter by code or label |
| `municipality_code`, `county_code` | Parent identifiers |
| `bbox`, `limit`, `offset` | Spatial filter + pagination |

```bash
curl "$API_ROOT/settlements/?municipality_code=2134&limit=1"
```

### 4. `GET /streets/`
Generalized street geometries from materialized view `gs.mv_streets`.

**Query parameters**

| Name | Description |
| --- | --- |
| `settlement_code` | Numeric settlement code |
| `settlement_name`, `municipality_name`, `name` | Substring matches |
| `bbox`, `limit`, `offset` | Spatial filter + pagination |

```bash
curl "$API_ROOT/streets/?settlement_code=326704&limit=10"
```

### 5. `GET /addresses/`
House/address points including street + administrative labels.

**Query parameters**

| Name | Description |
| --- | --- |
| `street_id` | Street identifier |
| `house_number` | Partial/complete house number |
| `settlement_code`, `municipality_code` | Parent identifiers |
| `bbox`, `limit`, `offset` | Spatial filter + pagination |

```bash
curl "$API_ROOT/addresses/?house_number=12"
```

### 6. `GET /layers/`
Returns the layer catalog consumed by the frontend layer switcher and
the ETL/GeoServer automation. Each item contains:

```json
{
  "id": "cadastral_parcels",
  "title": "Cadastral Parcels",
  "wms_name": "cadastral_parcels",
  "api_path": "/api/parcels/",
  "native_table": "gs.v_cadastral_parcels",
  "workspace": "cro-geo-data",
  "default": true
}
```

Use `wms_name` + `workspace` when building GeoServer WMS/WFS URLs, and
`api_path` for DRF calls. The frontend’s `LayerSwitcher` consumes this
endpoint (see `frontend/src/services/apiClient.ts`).

## Schema Reference

- Live schema: `GET /api/openapi.yaml`
- Version-controlled snapshot: `docs/openapi.yaml`

The document lists response schemas for each FeatureCollection along with
standard pagination fields (`count`, `next`, `previous`, `results`).

## ETL & GeoServer Automation

- Scheduled pipeline: `celery -A django_project beat` runs the
  `cadastral.tasks.run_full_ingest` task every Sunday at 02:00 (see
  `settings.CELERY_BEAT_SCHEDULE`).
- Manual run: `python manage.py run_ingest` (use `--skip-download`
  or `--skip-publish` during development).
- GeoServer publishing: `python manage.py publish_layers` or the Celery
  pipeline refresh both workspace + datastore based on `settings.LAYER_CATALOG`.


