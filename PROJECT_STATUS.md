# 📊 Project Status

## ✅ Completed / Ready Components

### Frontend (React + TypeScript + OpenLayers)
- React + Vite-style TypeScript app with Tailwind, routing scaffold, and environment-variable driven URLs is in place (`frontend/src`).
- Core map UX is implemented: `MapCanvas` talks to GeoServer WMS, supports base-layer toggling (OSM vs DOF), vector layer overlays, and GetFeatureInfo → `MetadataPopup`.
- Layer management, download menu, navbar and supporting utilities/types are finished and covered by RTL/Jest tests (`src/App.test.tsx`, `src/components/__tests__`, mocks for OpenLayers).
- Frontend Dockerfile + dev server wiring works (`frontend/Dockerfile`, `package.json` scripts).

### Backend Data Tooling
- Django/GeoDjango skeleton with DRF, CORS, Celery/Redis plumbing and Docker entrypoint exists (`backend/django_project`).
- Rich ingestion toolchain delivered under `backend/scripts/`: async DKP downloader, AU/AD downloader, and `extractor.py` orchestrating ogr2ogr with SQL templates. Behaviour is documented in `backend/scripts/README.md`.
- Script suite is unit-tested (`backend/tests/` covers extractor + downloaders) and uses shared logging (`backend/logger.py`).

### GeoDjango API Layer
- `cadastral/models.py` now mirrors the primary PostGIS tables (`rpj.counties/municipalities/settlements`, `dkp.cadastral_parcels`, etc.) with schema-qualified `managed=False` models plus relationship wiring.
- DRF viewsets power `/api/parcels/` and `/api/admin_boundaries/`, exposing GeoJSON with bbox, attribute filters, and search via `rest_framework_gis`.
- Serializers emit derived metadata (e.g., parent county names) and PostGIS connectivity defaults to the env-driven PostGIS DSN with an opt-in SQLite fallback for local dev.
- FilterSets (`cadastral/filters.py`) capture friendly query params like `parcel_id`, `cadastral_municipality`, and `admin_type`.

### Database Bootstrap (PostgreSQL + PostGIS)
- `db/init/` contains comprehensive DDL: schema creation (`dkp`, `rpj`, `staging`, `gs`, `journal`), lookup tables, union tables, materialized views, helper functions (e.g. `gs.get_native_bbox`, `journal` updaters) and data-mart views ready for GeoServer publishing.
- Function pipeline for staging→production sync is authored (`401-412_FUNC_*.sql`, `410_FUNC_update_tables.sql` etc.).

### GeoServer Automation Assets
- `geoserver/data_dir` placeholder plus `geoserver/scripts/init.sh` automate workspace/datastore creation, feature-type publishing, bbox injection via SQL helper functions, and upload of SLD styles (`geoserver/scripts/json/*.json`, `geoserver/scripts/sld/*.sld`).

### Containerization & Ops
- Root `docker-compose.yml` spins up PostGIS, Redis, GeoDjango (Gunicorn), React dev server, GeoServer and nginx with health checks, inter-service deps, shared volumes, and env passthrough.
- Backend/Frontend Dockerfiles install GDAL/OGR, build assets, and run appropriate commands.
- nginx reverse proxy bridges `/api` and `/geoserver`, serves built frontend, and exposes 80/443.

### Documentation & Guides
- `Instructions.md`, `README.md`, `QUICKSTART.md`, `docs/architecture.md`, `docs/api.md`, and the scripts README fully describe goals, stack, and ingestion flow.
- `.gitignore`, VS Code settings, and env templates are already curated.

## 🚧 Partially Implemented / Needs Integration
- **GeoDjango coverage gaps**: Parcels + counties/municipalities are live, but settlements/streets/addresses still need serializers, endpoints, and tests; spatial caching/pagination tuning is pending.
- **ETL orchestration**: Download/extract scripts operate, but there is no scheduler (Celery Beat/cron) nor glue code to move staged tables into the normalized schemas using the SQL functions.
- **GeoServer linkage**: REST payloads/SLDs are ready, yet the Docker stack does not invoke `geoserver/scripts/init.sh` automatically, and no .env wiring feeds DB credentials to that script.
- **Frontend ↔ API**: UI currently hardcodes available layers and only talks to GeoServer WMS; it is not wired to Django endpoints for metadata or layer catalogs.
- **Testing/CI**: Frontend has Jest coverage and backend scripts have pytest, but there are no tests for Django views/models, nor automated CI workflow.

## ⏳ Pending Implementation (Priority Order)
1. **Broaden GeoDjango API surface**: add serializers/viewsets for settlements, streets, and addresses (leveraging `gs` views), plus pagination/bbox tuning for large feature classes.
2. **Document and harden API contracts**: update `docs/api.md`, add OpenAPI schema, and cover viewsets with pytest + DRF test client cases.
3. **Integrate ETL pipeline**: add coordinator (Celery task or management command) that chains downloaders, extractor, and SQL refresh functions; persist run metadata/journaling.
4. **Automate GeoServer publishing**: hook `geoserver/scripts/init.sh` (or a Python REST client) into container startup with correct env vars so new tables auto-publish with styles.
5. **Frontend data plumbing**: replace hardcoded layer lists with API/GeoServer discovery, surface feature metadata from DRF, and align download links with authenticated GeoServer endpoints.
6. **Authentication & roles**: per roadmap, add Django auth/JWT plus nginx/GeoServer security configuration.
7. **CI/CD & QA**: introduce GitHub Actions (lint, pytest, frontend tests), add coverage for Django code, and document acceptance tests.
8. **Production hardening**: TLS cert automation, secrets management, logging/monitoring stack, and performance tuning for large datasets.

## 🎯 Next Steps
1. Extend the API to additional layers (settlements, addresses, cadastral municipalities) and mirror those changes in the frontend layer catalog.
2. Update `docs/api.md` and generate automated schema docs that reflect the live `/api/parcels` & `/api/admin_boundaries` capabilities (bbox, filtering, search).
3. Implement a management command or Celery Beat task that runs the downloader/extractor pipeline on a schedule and pushes staged data into live schemas via the provided SQL functions.
4. Integrate the GeoServer init script (or equivalent Python automation) into the docker lifecycle so published layers remain in sync with refreshed tables.
5. Connect the frontend to live layer metadata (via Django or GeoServer REST), and surface API-driven GetFeatureInfo data instead of placeholders.
6. Add CI automation plus backend API tests covering permissions, pagination, and geometry serialization.

## 🔍 What Works Right Now
1. **Frontend UI**: `npm start` (or `docker-compose up frontend`) renders the Croatia map, layer switcher, metadata/download components, and passes RTL tests without hitting live data.
2. **Backend GeoJSON endpoints**: `/api/parcels/` and `/api/admin_boundaries/` now query PostGIS, supporting bbox + attribute filters via DRF/GeoDjango.
3. **Data tooling**: `backend/scripts/dkp_downloader.py`, `rpj_downloader.py`, and `extractor.py` can already download OSS/INSPIRE data into `backend/data/downloads/` and load staging tables via ogr2ogr when `DB_STRING` is configured.
4. **Database bootstrap**: Starting `docker-compose` provisions PostGIS with all schemas, tables, views, and helper functions from `db/init/`.
5. **GeoServer access**: The container boots with default credentials and can be manually configured through the UI using the provided SLDs/json payloads.

## 📝 Notes
- Keep `backend/.env` and `frontend/.env` aligned with the docker-compose defaults; GDAL/OGR must be available for the extractor to run.
- Before exposing data publicly, wire authentication + HTTPS (nginx already maps 80/443).
- The ingestion SQL scripts expect staging tables (`staging.u_*`); ensure the Python ETL writes there before invoking the merge/update functions.