These instructions guide an AI Agent (or Senior Python/Web/GIS Developer) through building a full-stack Web GIS application that:

1. **Scrapes cadastral and administrative data for Croatia** from the Državna Geodetska Uprava (DGU) ATOM service on a **weekly** basis
2. **Stores** scraped data into a **PostgreSQL + PostGIS** database
3. **Publishes** spatial data via a **GeoDjango** backend, **GeoServer**, and a **React (TypeScript) + OpenLayers** frontend
4. Enables users to **switch layers**, view **metadata**, perform **GetFeatureInfo** queries, and **download** data in multiple formats (Shapefile, GeoPackage, GeoJSON, KML, DXF, etc.)
5. Is fully **containerized** with **Docker** (including **nginx** as reverse proxy)
6. Maintains a **Git** repository with a **`.gitignore`**, **README.md**, and **comprehensive documentation**
7. Adheres to **best coding practices** (linting, formatting, testing)
8. Uses **OSM** and the official **Digital Orthophoto of Croatia (DOF)** as background layers

---

## 📦 1. Project Structure

```bash
croatia-gis/                    # Repository root
├── backend/                    # Django + GeoDjango backend
│   ├── django_project/         # Django project root
│   │   ├── django_project/     # Django settings module
│   │   │   ├── settings.py
│   │   │   ├── urls.py
│   │   │   └── wsgi.py
│   │   ├── cadastral/          # Django app for cadastral & administrative data
│   │   │   ├── migrations/
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── tasks.py        # Celery tasks (optional)
│   │   │   └── admin.py
│   │   ├── geoserver_integration/  # Optional: scripts/REST calls to GeoServer
│   │   │   └── publish_layers.py
│   │   └── manage.py
│   ├── scripts/                # Standalone Python scripts for scraping
│   │   ├── fetch_atom_data.py
│   │   ├── parse_and_load.py
│   │   └── utils.py            # Utility functions (logging, config parsing)
│   └── requirements.txt
│
├── frontend/                   # React + TypeScript + OpenLayers frontend
│   ├── public/
│   │   ├── index.html
│   │   └── favicon.ico
│   ├── src/
│   │   ├── components/         # Reusable UI components (LayerSwitcher, MapCanvas, etc.)
│   │   │   ├── LayerSwitcher.tsx
│   │   │   ├── MetadataPopup.tsx
│   │   │   ├── DownloadMenu.tsx
│   │   │   └── Navbar.tsx
│   │   ├── pages/              # Route-based pages (Home, About, etc.)
│   │   ├── services/           # API client code (axios instances, TypeScript types)
│   │   ├── utils/              # Utility functions (date formatting, etc.)
│   │   ├── App.tsx
│   │   ├── index.tsx
│   │   └── react-app-env.d.ts
│   └── package.json
│
├── geoserver/                  # GeoServer container & configuration
│   ├── data_dir/               # GeoServer data directory (styles, workspaces, etc.)
│   └── docker-compose.geoserver.yml
│
├── docker/                     # Docker-related files
│   ├── nginx/                  # nginx configuration
│   │   └── default.conf
│   ├── docker-compose.yml
│   └── .env                    # Environment variables for all services
│
├── db/                         # Database initialization scripts
│   └── init.sql                # Creates PostGIS extension, schemas, initial users
│
├── docs/                       # Project documentation
│   ├── architecture.md         # High-level architecture diagrams & descriptions
│   ├── api.md                  # REST API endpoint specs
│   ├── geoserver.md            # GeoServer setup & layer publication guide
│   ├── data_model.md           # PostGIS schema & ERD
│   └── scraping.md             # Detailed guide: ATOM endpoints, parsing, error handling
│
├── .gitignore
├── README.md
└── Instructions.md             # ← You are here
```

---

## ✅ 2. Weekly Scraping from DGU ATOM Service

### 2.1. Overview

- **Objective**: Every week, fetch the latest cadastral and administrative datasets from DGU’s ATOM feeds, convert them to PostGIS-compatible format, and load them into our database.
- **Data Format**:
  - Most ATOM feeds link to **GML** or **ZIP** (containing Shapefiles).
  - Filenames often include dataset type (e.g., “katastar_gml_YYYYMMDD.zip” or “administrativne_granice_gml_YYYYMMDD.gml”).

### 2.2. Required Python Dependencies

In `backend/requirements.txt`, include at minimum:

```text
Django>=4.2
djangorestframework>=3.14
django-filter>=23.2
psycopg2-binary>=2.9
celery>=5.3
redis>=4.3          # If using Redis as Celery broker
requests>=2.29
lxml>=4.9
gdal>=3.7           # Note: match system GDAL version
python-dotenv>=1.0  # For `.env` support
```

> **Note**: Installing GDAL via `pip` can be problematic. On Docker images, install `gdal-bin` and `libgdal-dev` via apt, then set `GDAL_VERSION` env var before `pip install`.

### 2.3. `fetch_atom_data.py` (Skeleton)

Place in `backend/scripts/fetch_atom_data.py`. This script:

1. Reads ATOM feed URLs (from config or `.env`).
2. Sends HTTP GET to each ATOM URL.
3. Parses XML to extract `<entry>` items:
   - `<title>`: Dataset name/date
   - `<link rel="enclosure">`: URL to GML/ZIP
   - `<updated>`: Timestamp
4. Checks local **ETag/Last-Modified** or a local “history” table to avoid re-downloading unchanged files.
5. Downloads new files to a staging folder (e.g., `backend/data/weekly/`).
6. Unpacks ZIP if needed.
7. Delegates to `parse_and_load.py` for conversion + loading.

```python
# backend/scripts/fetch_atom_data.py
import os
import sys
import logging
import requests
import shutil
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load .env (contains ATOM_FEED_URLS, DB connection info, etc.)
load_dotenv(dotenv_path=Path(__file__).parents[2] / ".env")

ATOM_FEED_URLS = os.getenv("ATOM_FEED_URLS", "").split(",")
STAGING_DIR = Path(__file__).parents[2] / "backend" / "data" / "weekly"
HISTORY_FILE = Path(__file__).parents[2] / "backend" / "data" / "history.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_history():
    if not HISTORY_FILE.exists():
        return {}
    import json
    with open(HISTORY_FILE, "r") as f:
        return json.load(f)

def save_history(history):
    import json
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def parse_atom_feed(feed_url):
    logger.info(f"Fetching ATOM feed: {feed_url}")
    resp = requests.get(feed_url, timeout=60)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)
    namespace = {"atom": "http://www.w3.org/2005/Atom"}
    entries = root.findall("atom:entry", namespace)
    datasets = []
    for entry in entries:
        title = entry.find("atom:title", namespace).text
        updated = entry.find("atom:updated", namespace).text
        # Find <link rel="enclosure" href="...">
        for link in entry.findall("atom:link", namespace):
            if link.attrib.get("rel") == "enclosure":
                url = link.attrib["href"]
                datasets.append({"title": title, "updated": updated, "url": url})
                break
    return datasets

def download_dataset(url, dest_folder: Path):
    dest_folder.mkdir(parents=True, exist_ok=True)
    local_filename = dest_folder / url.split("/")[-1]
    logger.info(f"Downloading {url} → {local_filename}")
    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(local_filename, "wb") as f:
            shutil.copyfileobj(r.raw, f)
    return local_filename

def main():
    history = load_history()
    for feed_url in ATOM_FEED_URLS:
        try:
            datasets = parse_atom_feed(feed_url)
        except Exception as e:
            logger.error(f"Failed to parse ATOM feed {feed_url}: {e}")
            continue

        for ds in datasets:
            ds_key = ds["url"]
            ds_updated = ds["updated"]
            # If not seen before or updated changed:
            if ds_key not in history or history[ds_key] != ds_updated:
                try:
                    file_path = download_dataset(ds_key, STAGING_DIR)
                    # Delegate to parse_and_load script
                    os.system(f"python3 {Path(__file__).parent / 'parse_and_load.py'} {file_path}")
                    history[ds_key] = ds_updated
                except Exception as e:
                    logger.exception(f"Error processing {ds_key}: {e}")

    save_history(history)

if __name__ == "__main__":
    main()
```

> **Security Note**: When calling `os.system(…)`, ensure `PATH` and `PYTHONPATH` are correctly set, or use `subprocess.run([...], check=True)` for safer execution.

### 2.4. `parse_and_load.py` (Skeleton)

This script takes a downloaded file (GML or ZIP) and loads it into PostGIS using **GDAL/OGR** or `psycopg2` for metadata. Place in `backend/scripts/parse_and_load.py`.

```python
# backend/scripts/parse_and_load.py
import os
import sys
import logging
import tempfile
import subprocess
import zipfile
from pathlib import Path
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load DB connection from .env
load_dotenv(dotenv_path=Path(__file__).parents[2] / ".env")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "gis")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

def run_ogr2ogr(input_path: Path, layer_name: str):
    """
    Use ogr2ogr to import a GML/ESRI Shapefile into PostGIS.
    Example: ogr2ogr -f "PostgreSQL" PG:"host=db user=postgres password=… dbname=gis" \
             "/path/to/data.gml" -nln layer_name -nlt PROMOTE_TO_MULTI -overwrite
    """
    conn_str = f"PG:host={DB_HOST} port={DB_PORT} user={DB_USER} " \
               f"dbname={DB_NAME} password={DB_PASSWORD}"
    args = [
        "ogr2ogr",
        "-f", "PostgreSQL",
        conn_str,
        str(input_path),
        "-nln", layer_name,
        "-nlt", "PROMOTE_TO_MULTI",
        "-lco", "GEOMETRY_NAME=geom",
        "-lco", "FID=ogc_fid",
        "-overwrite"
    ]
    logger.info(f"Running ogr2ogr: {' '.join(args)}")
    subprocess.check_call(args)

def extract_zip(zip_path: Path, dest_dir: Path) -> list[Path]:
    extracted_files = []
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(dest_dir)
        for member in zf.namelist():
            extracted_files.append(dest_dir / member)
    return extracted_files

def main():
    if len(sys.argv) < 2:
        logger.error("Usage: python3 parse_and_load.py <path_to_file>")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    staging_dir = input_file.parent
    work_dir = staging_dir / "temp_extract"
    work_dir.mkdir(exist_ok=True)

    if input_file.suffix.lower() == ".zip":
        extracted = extract_zip(input_file, work_dir)
        # Find primary GML or Shapefile in extracted
        for f in extracted:
            if f.suffix.lower() in [".gml", ".shp"]:
                layer_name = f.stem.replace(".", "_")  # e.g., “administracija_20250601”
                run_ogr2ogr(f, layer_name)
    elif input_file.suffix.lower() == ".gml":
        layer_name = input_file.stem.replace(".", "_")
        run_ogr2ogr(input_file, layer_name)
    else:
        logger.warning(f"Unsupported file type: {input_file}")
    # Clean up temp
    import shutil
    shutil.rmtree(work_dir, ignore_errors=True)

if __name__ == "__main__":
    main()
```

> **Important**
> - Ensure the Docker container running this script has access to the `gdal-bin` binary.
> - Adapt `layer_name` logic to match your naming conventions (e.g., include date or dataset type).

### 2.5. Scheduling Weekly Execution

#### Option A: Linux `cron` (Simpler)

1. SSH into Docker host (or orchestrator VM).
2. Edit crontab (`crontab -e`) for the user that owns `.env` & project files.
3. Add entry (runs every Sunday at 2 AM):
   ```cron
   0 2 * * 0 cd /path/to/croatia-gis/backend/scripts && /usr/bin/python3 fetch_atom_data.py >> /path/to/croatia-gis/backend/logs/scrape.log 2>&1
   ```
4. Ensure the host’s environment variables (e.g., `.env`) are loaded inside `fetch_atom_data.py`.

#### Option B: **Celery Beat** (Inside Docker)

1. Add Celery config to `django_project/settings.py`:

   ```python
   CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
   CELERY_BEAT_SCHEDULE = {
       "weekly-scrape": {
           "task": "cadastral.tasks.fetch_and_load",
           "schedule": crontab(hour=2, minute=0, day_of_week=0),
       },
   }
   ```

2. Create a Celery task in `backend/django_project/cadastral/tasks.py`:

   ```python
   # cadastral/tasks.py
   from celery import shared_task
   import subprocess
   from pathlib import Path
   import logging

   logger = logging.getLogger(__name__)

   @shared_task
   def fetch_and_load():
       script_path = Path(__file__).parents[2] / "scripts" / "fetch_atom_data.py"
       try:
           subprocess.check_call(["python3", str(script_path)])
       except Exception as e:
           logger.exception(f"Weekly scrape failed: {e}")
   ```

3. Update `docker-compose.yml` to include a `celery` and `celery-beat` service (details in section 6).

---

## 🗄️ 3. PostgreSQL + PostGIS Database Setup

### 3.1. Dockerized PostGIS

Create `docker/docker-compose.yml` with:

```yaml
version: "3.9"
services:
  db:
    image: postgis/postgis:15-3.3
    container_name: croatia_gis_db
    restart: unless-stopped
    environment:
      - POSTGRES_DB=${DB_NAME}
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - ./db:/docker-entrypoint-initdb.d  # Runs init.sql on first start
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7
    container_name: croatia_gis_redis
    restart: unless-stopped
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

> The `db/init.sql` script will run on container startup.

### 3.2. `db/init.sql`

```sql
-- db/init.sql

-- Create PostGIS extension if not exists
CREATE EXTENSION IF NOT EXISTS postgis;
-- Example: Create a schema for cadastral data
CREATE SCHEMA IF NOT EXISTS cadastral AUTHORIZATION ${DB_USER};
-- Optional: create a role for read-only clients
-- CREATE ROLE gis_reader LOGIN PASSWORD 'strongpassword';
-- GRANT USAGE ON SCHEMA public, cadastral TO gis_reader;
```

> **Environment Variable Substitution**: Docker initializes `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` automatically, so you can `\c` into the DB from other services.

---

## 🌐 4. GeoDjango Backend (Django + GeoDjango + Django REST Framework)

### 4.1. Install Dependencies

In `backend/requirements.txt` (already shown), ensure:

```text
Django>=4.2
djangorestframework>=3.14
djangorestframework-gis>=0.19
django-filter>=23.2
psycopg2-binary>=2.9
celery>=5.3
redis>=4.3
GDAL>=3.7
django-cors-headers>=3.15
python-dotenv>=1.0
```

### 4.2. Project Initialization

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
django-admin startproject django_project .
python manage.py startapp cadastral
python manage.py migrate
```

#### 4.2.1. `.env` (Place in `backend/`)

```ini
# backend/.env

SECRET_KEY=your_django_secret_key_here
DEBUG=False

# Database
DB_HOST=db
DB_PORT=5432
DB_NAME=gis
DB_USER=postgres
DB_PASSWORD=strongpassword

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# CORS (allow frontend domain)
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

> **Note**: In production, set `DEBUG=False` and configure `ALLOWED_HOSTS` accordingly.

### 4.3. `django_project/settings.py` Configuration

1. **Add Installed Apps**:

   ```python
   INSTALLED_APPS = [
       "django.contrib.admin",
       "django.contrib.auth",
       "django.contrib.contenttypes",
       "django.contrib.sessions",
       "django.contrib.messages",
       "django.contrib.staticfiles",
       "django.contrib.gis",                # GeoDjango
       "rest_framework",
       "rest_framework_gis",                # GeoJSON Renderers, Filters
       "django_filters",
       "corsheaders",
       "cadastral",                         # Our app
   ]
   ```

2. **Middleware** (insert `CorsMiddleware` at top):

   ```python
   MIDDLEWARE = [
       "corsheaders.middleware.CorsMiddleware",
       "django.middleware.security.SecurityMiddleware",
       "django.contrib.sessions.middleware.SessionMiddleware",
       "django.middleware.common.CommonMiddleware",
       "django.middleware.csrf.CsrfViewMiddleware",
       "django.contrib.auth.middleware.AuthenticationMiddleware",
       "django.contrib.messages.middleware.MessageMiddleware",
       "django.middleware.clickjacking.XFrameOptionsMiddleware",
   ]
   ```

3. **Database Settings**:

   ```python
   import os
   from pathlib import Path

   BASE_DIR = Path(__file__).resolve().parent.parent

   # Load .env
   from dotenv import load_dotenv
   load_dotenv(os.path.join(BASE_DIR, ".env"))

   DATABASES = {
       "default": {
           "ENGINE": "django.contrib.gis.db.backends.postgis",
           "NAME": os.getenv("DB_NAME"),
           "USER": os.getenv("DB_USER"),
           "PASSWORD": os.getenv("DB_PASSWORD"),
           "HOST": os.getenv("DB_HOST", "localhost"),
           "PORT": os.getenv("DB_PORT", "5432"),
       }
   }
   ```

4. **REST Framework + GIS Settings**:

   ```python
   REST_FRAMEWORK = {
       "DEFAULT_PERMISSION_CLASSES": [
           "rest_framework.permissions.AllowAny",
       ],
       "DEFAULT_FILTER_BACKENDS": [
           "django_filters.rest_framework.DjangoFilterBackend"
       ],
       "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
       "PAGE_SIZE": 100,
   }
   ```

5. **Static & Media**:

   ```python
   STATIC_URL = "/static/"
   STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
   MEDIA_URL = "/media/"
   MEDIA_ROOT = os.path.join(BASE_DIR, "media")
   ```

6. **CORS**:

   ```python
   CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
   ```

### 4.4. Defining the Data Model (in `cadastral/models.py`)

Each ATOM dataset typically yields one or more layers. For demonstration, assume two core layers:

- `CadastralParcel`
- `AdministrativeBoundary`

```python
# cadastral/models.py
from django.contrib.gis.db import models

class CadastralParcel(models.Model):
    """
    Represents cadastral parcels in Croatia.
    Imported from weekly ATOM feeds (GML/Shapefile).
    """
    ogc_fid = models.BigIntegerField(primary_key=True)
    parcel_id = models.CharField(max_length=100, unique=True)  # e.g., “RH_PARCEL_123456789”
    cadastral_municipality = models.CharField(max_length=100)
    area_sqm = models.FloatField()
    geom = models.MultiPolygonField(srid=3765)  # Assume Croatian CRS (TMH / D48)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cadastral_cadastralparcel"
        verbose_name = "Cadastral Parcel"
        verbose_name_plural = "Cadastral Parcels"
        indexes = [
            models.Index(fields=["parcel_id"]),
            models.GinIndex(fields=["geom"]),
        ]

    def __str__(self):
        return f"{self.parcel_id}"

class AdministrativeBoundary(models.Model):
    """
    Represents administrative boundaries (municipalities/counties).
    """
    ogc_fid = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=100)  # e.g., “Grad Zagreb”
    admin_type = models.CharField(max_length=50)  # “Municipality”, “County”, etc.
    geom = models.MultiPolygonField(srid=3765)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cadastral_administrativeboundary"
        verbose_name = "Administrative Boundary"
        verbose_name_plural = "Administrative Boundaries"
        indexes = [
            models.Index(fields=["name"]),
            models.GinIndex(fields=["geom"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.admin_type})"
```

> **CRS Note**:
> - Croatia primarily uses **EPSG:3765** (D48 / Croatia). If the data is in **EPSG:4326**, convert during ingest. Adjust SRID accordingly.

### 4.5. Serializers (in `cadastral/serializers.py`)

```python
# cadastral/serializers.py
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import CadastralParcel, AdministrativeBoundary

class CadastralParcelSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = CadastralParcel
        geo_field = "geom"
        fields = (
            "ogc_fid",
            "parcel_id",
            "cadastral_municipality",
            "area_sqm",
            "updated_at",
        )

class AdministrativeBoundarySerializer(GeoFeatureModelSerializer):
    class Meta:
        model = AdministrativeBoundary
        geo_field = "geom"
        fields = (
            "ogc_fid",
            "name",
            "admin_type",
            "updated_at",
        )
```

> **Why GeoFeatureModelSerializer?**
> - Automatically formats responses as **GeoJSON FeatureCollections**.

### 4.6. Views & URLs (in `cadastral/views.py` and `cadastral/urls.py`)

#### 4.6.1. `views.py`

```python
# cadastral/views.py
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import CadastralParcel, AdministrativeBoundary
from .serializers import CadastralParcelSerializer, AdministrativeBoundarySerializer

class CadastralParcelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    /api/parcels/
    - GET: List / Retrieve cadastral parcels as GeoJSON
    - Filter by parcel_id, cadastral_municipality, bounding box, etc.
    """
    queryset = CadastralParcel.objects.all()
    serializer_class = CadastralParcelSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["parcel_id", "cadastral_municipality"]
    search_fields = ["parcel_id", "cadastral_municipality"]

class AdministrativeBoundaryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    /api/admin_boundaries/
    - GET: List / Retrieve administrative boundaries
    - Filter by name, admin_type, bounding box, etc.
    """
    queryset = AdministrativeBoundary.objects.all()
    serializer_class = AdministrativeBoundarySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["name", "admin_type"]
    search_fields = ["name"]
```

#### 4.6.2. `urls.py`

```python
# cadastral/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CadastralParcelViewSet, AdministrativeBoundaryViewSet

router = DefaultRouter()
router.register(r"parcels", CadastralParcelViewSet, basename="parcel")
router.register(r"admin_boundaries", AdministrativeBoundaryViewSet, basename="admboundary")

urlpatterns = [
    path("", include(router.urls)),
]
```

#### 4.6.3. Root URLs (`django_project/urls.py`)

```python
# django_project/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("cadastral.urls")),   # /api/parcels/, /api/admin_boundaries/
]
```

> **Tip**:
> - To implement **GetFeatureInfo** style behavior (point queries), you can add a custom DRF view that accepts `lat/lon` and returns features at that point within a tolerance. For example, use `geom__intersects=Point` filter. Alternatively, rely on **GeoServer** for GetFeatureInfo.

---

## 🌍 5. GeoServer Integration

### 5.1. Why GeoServer?

GeoServer provides:
- **WMS** and **WFS** endpoints for tiled rendering and feature queries
- Built-in **GetFeatureInfo** support
- **Download** in multiple formats out-of-the-box (Shapefile, GeoJSON, KML, DXF, GPKG, etc.) via WFS “outputFormat” parameter

### 5.2. Docker Compose for GeoServer

Create `geoserver/docker-compose.geoserver.yml`:

```yaml
version: "3.9"
services:
  geoserver:
    image: osgeo/geoserver:2.23.7
    container_name: croatia_gis_geoserver
    restart: unless-stopped
    ports:
      - "8080:8080"
    environment:
      - GEOSERVER_ADMIN_USER=${GEOSERVER_USER}
      - GEOSERVER_ADMIN_PASSWORD=${GEOSERVER_PASSWORD}
    volumes:
      - ./data_dir:/opt/geoserver/data_dir
```

> **Note**: Set `GEOSERVER_USER` and `GEOSERVER_PASSWORD` in your `docker/.env` file.

### 5.3. GeoServer `data_dir/` Structure (Minimal)

```
geoserver/
└── data_dir/
    ├── workspaces/
    │   └── croatia/
    │       ├── data/          # Shapefiles or directories to auto-publish
    │       └── styles/        # SLD/GeoServer CSS for styling layers
    ├── global.xml             # General config (auto-generated on first start)
    ├── security/              # Password files, roles, etc.
    └── ...                    # Other GeoServer config files
```

### 5.4. Auto-publishing via GeoServer REST API

Create a Python script `backend/django_project/geoserver_integration/publish_layers.py` to:

1. Connect to GeoServer’s REST endpoint (`http://geoserver:8080/geoserver/rest`).
2. Create a **Workspace** named `croatia` (if not exists).
3. Create a **Store** linking to the PostGIS database.
4. Publish each table (layer) from PostGIS into GeoServer:

   - Use `POST /rest/workspaces/croatia/datastores/…/featuretypes` requests with a minimal XML body.
   - Create default styles (optional): e.g., `polygon` style with no fill or transparent fill.

```python
# geoserver_integration/publish_layers.py
import os
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"))

GEOSERVER_URL = os.getenv("GEOSERVER_URL", "http://geoserver:8080/geoserver")
USER = os.getenv("GEOSERVER_USER", "admin")
PASSWORD = os.getenv("GEOSERVER_PASSWORD", "geoserver")

NAMESPACE = "croatia"  # Workspace
DATASTORE = "postgis_croatia"

def create_workspace():
    url = f"{GEOSERVER_URL}/rest/workspaces"
    headers = {"Content-Type": "text/xml"}
    body = f"<workspace><name>{NAMESPACE}</name></workspace>"
    resp = requests.post(url, auth=(USER, PASSWORD), headers=headers, data=body)
    if resp.status_code in (201, 202):
        print(f"Workspace '{NAMESPACE}' created.")
    elif resp.status_code == 401:
        raise Exception("Invalid GeoServer credentials.")
    else:
        print(f"Workspace creation returned: {resp.status_code} ({resp.text})")

def create_datastore():
    url = f"{GEOSERVER_URL}/rest/workspaces/{NAMESPACE}/datastores"
    headers = {"Content-Type": "text/xml"}
    body = f"""
    <dataStore>
        <name>{DATASTORE}</name>
        <connectionParameters>
            <host>{os.getenv("DB_HOST")}</host>
            <port>{os.getenv("DB_PORT")}</port>
            <database>{os.getenv("DB_NAME")}</database>
            <user>{os.getenv("DB_USER")}</user>
            <passwd>{os.getenv("DB_PASSWORD")}</passwd>
            <dbtype>postgis</dbtype>
            <namespace>{NAMESPACE}</namespace>
        </connectionParameters>
    </dataStore>
    """
    resp = requests.post(url, auth=(USER, PASSWORD), headers=headers, data=body)
    if resp.status_code in (201, 202):
        print(f"Datastore '{DATASTORE}' created.")
    else:
        print(f"Datastore creation returned: {resp.status_code} ({resp.text})")

def publish_layer(layer_name: str, default_style: str = "polygon"):
    url = f"{GEOSERVER_URL}/rest/workspaces/{NAMESPACE}/datastores/{DATASTORE}/featuretypes"
    headers = {"Content-Type": "text/xml"}
    body = f"""
    <featureType>
        <name>{layer_name}</name>
        <nativeName>{layer_name}</nativeName>
        <title>{layer_name.replace('_', ' ').title()}</title>
        <srs>EPSG:3765</srs>
        <nativeCRS>EPSG:3765</nativeCRS>
        <projectionPolicy>REPROJECT_TO_DECLARED</projectionPolicy>
        <enabled>true</enabled>
    </featureType>
    """
    resp = requests.post(url, auth=(USER, PASSWORD), headers=headers, data=body)
    if resp.status_code in (201, 202):
        print(f"Layer '{layer_name}' published.")
        # Optionally set default style:
        style_url = f"{GEOSERVER_URL}/rest/layers/{NAMESPACE}:{layer_name}"
        style_body = f"<layer><defaultStyle><name>{default_style}</name></defaultStyle></layer>"
        style_resp = requests.put(style_url, auth=(USER, PASSWORD), headers=headers, data=style_body)
        if style_resp.status_code not in (200, 201, 202, 204):
            print(f"Failed to set style for '{layer_name}': {style_resp.status_code}")
    else:
        print(f"Layer publication returned: {resp.status_code} ({resp.text})")

def main():
    create_workspace()
    create_datastore()
    # List tables in PostGIS schema 'public' or 'cadastral'
    # For example, if all tables are in schema 'public':
    from psycopg2 import connect, sql
    conn = connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    cur = conn.cursor()
    schema = "public"  # or 'cadastral'
    cur.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = %s AND table_type = 'BASE TABLE';
    """, (schema,))
    tables = [row[0] for row in cur.fetchall()]
    for tbl in tables:
        publish_layer(tbl)
    conn.close()

if __name__ == "__main__":
    main()
```

> **Run this script** once the PostGIS DB & GeoServer are up. You can integrate it into your **Docker entrypoint** or run manually via `docker exec`.

### 5.5. GeoServer REST vs. Manual UI

- **REST** is recommended for reproducibility and automation.
- If manually using the GeoServer UI:
  1. Log in at `http://<host>:8080/geoserver` (default credentials `admin/geoserver`).
  2. Create a workspace named `croatia`.
  3. Create a PostGIS store, filling in connection parameters.
  4. “Publish” each table as a layer.
  5. For each layer, configure:
     - **Coordinate Reference System**: `EPSG:3765`
     - **Bounding boxes**: Recalculate from data
     - **Default Style**: Assign a style (e.g., `polygon`). You can upload an SLD or use a built-in style.

---

## ⚛️ 6. React (TypeScript) Frontend + OpenLayers

### 6.1. Create React App (TypeScript)

```bash
cd frontend
npx create-react-app . --template typescript
npm install ol axios @types/ol react-router-dom @types/react-router-dom
npm install tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

#### 6.1.1. Configure Tailwind (`tailwind.config.js`)

```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}", "./public/index.html"],
  theme: {
    extend: {},
  },
  plugins: [],
};
```

#### 6.1.2. Include Tailwind in `src/index.css`

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Add custom styles below */
```

### 6.2. Frontend Environment Variables

Create a `.env` (in `frontend/`) with:

```ini
REACT_APP_API_BASE_URL=http://localhost:8000/api
REACT_APP_GEOSERVER_URL=http://localhost:8080/geoserver
```

> **Note**: React will only read variables prefixed with `REACT_APP_`.

### 6.3. Folder Structure

```
frontend/
└── src/
    ├── components/
    │   ├── LayerSwitcher.tsx
    │   ├── MetadataPopup.tsx
    │   ├── DownloadMenu.tsx
    │   └── Navbar.tsx
    ├── pages/
    │   ├── Home.tsx
    │   └── About.tsx
    ├── services/
    │   ├── apiClient.ts
    │   └── types.ts
    ├── utils/
    │   └── format.ts
    ├── App.tsx
    ├── index.tsx
    └── react-app-env.d.ts
```

### 6.4. Core Map Component (`MapCanvas.tsx`)

```tsx
// src/components/MapCanvas.tsx
import React, { useEffect, useRef, useState } from "react";
import "ol/ol.css";
import { Map, View } from "ol";
import { Tile as TileLayer, Vector as VectorLayer } from "ol/layer";
import { OSM, TileWMS, Vector as VectorSource } from "ol/source";
import { GeoJSON } from "ol/format";
import { Style, Fill, Stroke } from "ol/style";
import { fromLonLat } from "ol/proj";
import { defaults as defaultControls, ScaleLine } from "ol/control";
import axios from "axios";
import { get } from "ol/proj";
import { toStringHDMS } from "ol/coordinate";

interface MapCanvasProps {
  selectedLayers: string[];       // e.g., ["cadastral_cadastralparcel", "cadastral_administrativeboundary"]
  onFeatureClick: (properties: any) => void;
}

const MapCanvas: React.FC<MapCanvasProps> = ({
  selectedLayers,
  onFeatureClick,
}) => {
  const mapRef = useRef<HTMLDivElement | null>(null);
  const [mapObject, setMapObject] = useState<Map>();

  // Base layers: OSM + DOF
  const osmLayer = new TileLayer({
    source: new OSM(),
    visible: true,
    title: "OpenStreetMap",
  });

  const dofLayer = new TileLayer({
    source: new TileWMS({
      url: process.env.REACT_APP_GEOSERVER_URL + "/wms",
      params: {
        LAYERS: "croatia:dof_ortho",   // assume this is configured in GeoServer
        FORMAT: "image/png",
        TRANSPARENT: true,
      },
      serverType: "geoserver",
      crossOrigin: "anonymous",
    }),
    visible: false,
    title: "Croatia DOF",
  });

  // Dynamically add vector WMS layers based on selectedLayers
  const wmsLayers = selectedLayers.map((layerName) => {
    return new TileLayer({
      source: new TileWMS({
        url: process.env.REACT_APP_GEOSERVER_URL + "/wms",
        params: {
          LAYERS: `croatia:${layerName}`,
          FORMAT: "image/png",
          TRANSPARENT: true,
        },
        serverType: "geoserver",
        crossOrigin: "anonymous",
      }),
      visible: true,
      title: layerName,
    });
  });

  useEffect(() => {
    if (!mapObject && mapRef.current) {
      const initialMap = new Map({
        target: mapRef.current,
        controls: defaultControls().extend([new ScaleLine()]),
        view: new View({
          center: fromLonLat([16.0, 45.0]), // Rough center of Croatia
          zoom: 7,
          projection: "EPSG:3857",
        }),
        layers: [osmLayer, dofLayer, ...wmsLayers],
      });

      // Click handling for GetFeatureInfo
      initialMap.on("singleclick", async (evt) => {
        const viewResolution = initialMap.getView().getResolution();
        const coordinate = evt.coordinate;
        const hdms = toStringHDMS(get(coordinate, "EPSG:3857")); // For popup
        // Build GetFeatureInfo URL for first selected layer (for simplicity)
        if (selectedLayers.length > 0) {
          const layerName = selectedLayers[0];
          const url = (
            wmsLayers[0].getSource() as TileWMS
          ).getFeatureInfoUrl(
            coordinate,
            viewResolution!,
            "EPSG:3857",
            { INFO_FORMAT: "application/json", QUERY_LAYERS: `croatia:${layerName}` }
          );
          if (url) {
            try {
              const resp = await axios.get(url);
              if (resp.data && resp.data.features.length > 0) {
                onFeatureClick(resp.data.features[0].properties);
              }
            } catch (error) {
              console.error("GetFeatureInfo error:", error);
            }
          }
        }
      });

      setMapObject(initialMap);
    }

    // When selectedLayers changes, update map layers
    if (mapObject) {
      // Remove existing WMS layers (indexes 2+)
      mapObject.getLayers().getArray().slice(2).forEach((lyr) => {
        mapObject.removeLayer(lyr as TileLayer);
      });
      // Add new ones
      wmsLayers.forEach((lyr) => {
        mapObject.addLayer(lyr);
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mapRef, selectedLayers]);

  return <div ref={mapRef} className="w-full h-full" />;
};

export default MapCanvas;
```

> **Explanation**:
> - **`osmLayer`**: OpenStreetMap via OSM source (XYZ) as default background.
> - **`dofLayer`**: Croatian orthophoto WMS from GeoServer. Toggle visibility via UI.
> - **`wmsLayers`**: vector layers published in GeoServer (e.g., `cadastral_cadastralparcel`, `cadastral_administrativeboundary`).
> - **GetFeatureInfo**: On map click, build WMS GetFeatureInfo URL for the top-most layer, fetch attributes, and pass to callback.

### 6.5. LayerSwitcher Component

Allow users to toggle layer visibility (both base & vector).

```tsx
// src/components/LayerSwitcher.tsx
import React from "react";

interface LayerSwitcherProps {
  availableLayers: { id: string; title: string }[];
  selectedLayers: string[];
  toggleLayer: (layerId: string) => void;
  toggleBase: (base: "OSM" | "DOF") => void;
  activeBase: "OSM" | "DOF";
}

const LayerSwitcher: React.FC<LayerSwitcherProps> = ({
  availableLayers,
  selectedLayers,
  toggleLayer,
  toggleBase,
  activeBase,
}) => {
  return (
    <div className="bg-white p-2 rounded shadow mb-2">
      <h3 className="font-semibold mb-1">Background Layer</h3>
      <div className="flex items-center mb-2">
        <label className="mr-2">
          <input
            type="radio"
            checked={activeBase === "OSM"}
            onChange={() => toggleBase("OSM")}
          />{" "}
          OSM
        </label>
        <label className="ml-4">
          <input
            type="radio"
            checked={activeBase === "DOF"}
            onChange={() => toggleBase("DOF")}
          />{" "}
          DOF
        </label>
      </div>
      <h3 className="font-semibold mb-1">Layers</h3>
      {availableLayers.map((layer) => (
        <div key={layer.id}>
          <label>
            <input
              type="checkbox"
              checked={selectedLayers.includes(layer.id)}
              onChange={() => toggleLayer(layer.id)}
            />{" "}
            {layer.title}
          </label>
        </div>
      ))}
    </div>
  );
};

export default LayerSwitcher;
```

> **Props**:
> - `availableLayers`: Array of `{ id: string; title: string }` (e.g., `[{ id: "cadastral_cadastralparcel", title: "Parcels" }, {...}]`).
> - `selectedLayers`: Controlled checkbox state.
> - `toggleLayer`: Callback when user checks/unchecks a layer.

### 6.6. MetadataPopup & DownloadMenu Components

#### 6.6.1. `MetadataPopup.tsx`

Displays feature properties (from GetFeatureInfo) in a small popup/dialog.

```tsx
// src/components/MetadataPopup.tsx
import React from "react";

interface MetadataPopupProps {
  properties: Record<string, any> | null;
  onClose: () => void;
}

const MetadataPopup: React.FC<MetadataPopupProps> = ({ properties, onClose }) => {
  if (!properties) return null;
  return (
    <div className="fixed top-1/4 left-1/2 transform -translate-x-1/2 bg-white p-4 rounded shadow-lg z-50 w-80">
      <div className="flex justify-between items-center mb-2">
        <h3 className="font-semibold">Feature Metadata</h3>
        <button className="text-gray-600" onClick={onClose}>
          ✕
        </button>
      </div>
      <div className="text-sm overflow-y-auto max-h-64">
        {Object.entries(properties).map(([key, value]) => (
          <div key={key} className="mb-1 flex">
            <span className="font-medium w-32">{key}</span>:{" "}
            <span className="ml-1">{String(value)}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MetadataPopup;
```

#### 6.6.2. `DownloadMenu.tsx`

Offers download links (via **GeoServer WFS** or **Django API**) for the active layer or bounding box.

```tsx
// src/components/DownloadMenu.tsx
import React, { useState } from "react";

interface DownloadMenuProps {
  activeLayer: string;  // e.g. "cadastral_cadastralparcel"
  bbox?: [number, number, number, number]; // [minX, minY, maxX, maxY] in EPSG:3857
}

const DownloadMenu: React.FC<DownloadMenuProps> = ({ activeLayer, bbox }) => {
  const [format, setFormat] = useState<string>("application/json");

  // Map user-friendly labels to GeoServer WFS outputFormat params
  const formatOptions = [
    { label: "GeoJSON", value: "application/json" },
    { label: "Shapefile (zip)", value: "shape-zip" },
    { label: "KML", value: "KML" },
    { label: "DXF", value: "application/dxf" },
    { label: "GPKG", value: "application/geopackage+sqlite3" },
    { label: "CSV", value: "text/csv" },
  ];

  const buildWfsUrl = () => {
    const base = `${process.env.REACT_APP_GEOSERVER_URL}/wfs`;
    const params = new URLSearchParams({
      service: "WFS",
      version: "1.1.0",
      request: "GetFeature",
      typeName: `croatia:${activeLayer}`,
      outputFormat: format,
    });
    if (bbox) {
      params.append("bbox", bbox.join(",") + ",EPSG:3857");
    }
    return `${base}?${params.toString()}`;
  };

  return (
    <div className="bg-white p-2 rounded shadow mt-2">
      <h4 className="font-semibold mb-1">Download "{activeLayer}"</h4>
      <div className="flex items-center">
        <select
          className="border p-1 mr-2"
          value={format}
          onChange={(e) => setFormat(e.target.value)}
        >
          {formatOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        <a
          href={buildWfsUrl()}
          target="_blank"
          rel="noreferrer"
          className="bg-blue-500 text-white px-3 py-1 rounded"
        >
          Download
        </a>
      </div>
    </div>
  );
};

export default DownloadMenu;
```

> **Notes**:
> - If you prefer to generate downloads via Django (e.g., filter by attribute), build a DRF view that streams a file.
> - WFS “shape-zip” automatically packages Shapefile components into a ZIP.

### 6.7. Main App Logic (`App.tsx`)

Combine components, manage state, and render UI.

```tsx
// src/App.tsx
import React, { useState, useEffect } from "react";
import MapCanvas from "./components/MapCanvas";
import LayerSwitcher from "./components/LayerSwitcher";
import MetadataPopup from "./components/MetadataPopup";
import DownloadMenu from "./components/DownloadMenu";
import axios from "axios";
import { getBBox } from "./utils/format";

const App: React.FC = () => {
  const [availableLayers, setAvailableLayers] = useState<
    { id: string; title: string }[]
  >([]);
  const [selectedLayers, setSelectedLayers] = useState<string[]>([]);
  const [activeBase, setActiveBase] = useState<"OSM" | "DOF">("OSM");
  const [featureProps, setFeatureProps] = useState<any | null>(null);
  const [currentLayer, setCurrentLayer] = useState<string>("");

  useEffect(() => {
    // Fetch list of layers from GeoServer REST API or hardcode
    // Example: hardcoded for now
    setAvailableLayers([
      { id: "cadastral_cadastralparcel", title: "Parcels" },
      { id: "cadastral_administrativeboundary", title: "Admin Boundaries" },
    ]);
  }, []);

  const toggleLayer = (layerId: string) => {
    setFeatureProps(null);
    if (selectedLayers.includes(layerId)) {
      setSelectedLayers(selectedLayers.filter((l) => l !== layerId));
      if (currentLayer === layerId) setCurrentLayer("");
    } else {
      setSelectedLayers([...selectedLayers, layerId]);
      setCurrentLayer(layerId);
    }
  };

  const toggleBase = (base: "OSM" | "DOF") => {
    setActiveBase(base);
  };

  const handleFeatureClick = (props: any) => {
    setFeatureProps(props);
  };

  // Optional: compute current map extent → pass as bbox to DownloadMenu
  const [bbox, setBbox] = useState<[number, number, number, number]>();

  // Skipping implementation of capturing bbox, but can use mapObject.getView().calculateExtent()

  return (
    <div className="h-screen flex flex-col">
      <nav className="bg-gray-800 text-white p-4 flex items-center">
        <h1 className="text-xl font-bold mr-auto">Croatia Cadastral GIS</h1>
        {/* Additional nav items */}
      </nav>
      <div className="flex flex-1">
        <aside className="w-64 border-r p-2">
          <LayerSwitcher
            availableLayers={availableLayers}
            selectedLayers={selectedLayers}
            toggleLayer={toggleLayer}
            toggleBase={toggleBase}
            activeBase={activeBase}
          />
          {featureProps && (
            <MetadataPopup
              properties={featureProps}
              onClose={() => setFeatureProps(null)}
            />
          )}
          {currentLayer && (
            <DownloadMenu activeLayer={currentLayer} bbox={bbox} />
          )}
        </aside>
        <main className="flex-1">
          <MapCanvas
            selectedLayers={selectedLayers}
            onFeatureClick={handleFeatureClick}
          />
        </main>
      </div>
    </div>
  );
};

export default App;
```

> **Key Points**:
> - **`availableLayers`**: Ideally fetched from GeoServer’s REST (list all layers in workspace `croatia`). You can create a `/api/layers/` endpoint in Django that proxies to GeoServer.
> - **`toggleLayer`** and **`toggleBase`** manage visible layers.
> - **`DownloadMenu`** only appears for the “currently active” vector layer.
> - **`bbox`**: You can listen to `map.on("moveend", ...)` to update bounding box state.

### 6.8. TypeScript Types (`services/types.ts`)

Define common data types (e.g., Feature properties, layer descriptors).

```ts
// src/services/types.ts

export interface LayerDescriptor {
  id: string;          // “cadastral_cadastralparcel”
  title: string;       // “Parcels”
  workspace?: string;  // “croatia” (optional)
  srid?: number;       // 3765 (optional)
}

export interface ParcelProperties {
  ogc_fid: number;
  parcel_id: string;
  cadastral_municipality: string;
  area_sqm: number;
  updated_at: string; // ISO Date
}

export interface BoundaryProperties {
  ogc_fid: number;
  name: string;
  admin_type: string;
  updated_at: string;
}
```

### 6.9. API Client (Optional: Proxy to Django)

If you prefer to fetch layers (metadata) via Django, create `services/apiClient.ts`:

```ts
// src/services/apiClient.ts
import axios from "axios";

const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export async function fetchParcels(
  bbox?: [number, number, number, number],
  filters?: Record<string, string>
) {
  const params: any = {};
  if (bbox) {
    // Convert EPSG:3857 bbox to WGS84 or backend’s expected CRS
    params.bbox = bbox.join(",");
  }
  if (filters) {
    Object.assign(params, filters);
  }
  const resp = await apiClient.get("/parcels/", { params });
  return resp.data;
}

export async function fetchAdminBoundaries() {
  const resp = await apiClient.get("/admin_boundaries/");
  return resp.data;
}
```

> **Tip**:
> - Use `fetchAdminBoundaries()` on page load to build **LayerSwitcher** items dynamically.

---

## 🐳 7. Docker & Nginx Deployment

### 7.1. `docker/docker-compose.yml`

```yaml
version: "3.9"
services:
  db:
    image: postgis/postgis:15-3.3
    container_name: croatia_gis_db
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - "../db:/docker-entrypoint-initdb.d"
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    container_name: croatia_gis_redis
    restart: unless-stopped

  backend:
    build:
      context: ../backend
      dockerfile: Dockerfile
    container_name: croatia_gis_backend
    restart: unless-stopped
    env_file:
      - ../backend/.env
    volumes:
      - "../backend:/app"
    depends_on:
      - db
      - redis
    command: >
      sh -c "python manage.py migrate &&
             python manage.py collectstatic --noinput &&
             gunicorn django_project.wsgi:application
               --bind 0.0.0.0:8000
               --workers 3"

  frontend:
    build:
      context: ../frontend
      dockerfile: Dockerfile
    container_name: croatia_gis_frontend
    restart: unless-stopped
    env_file:
      - ../frontend/.env
    volumes:
      - "../frontend:/usr/src/app"
    command: sh -c "npm install && npm run build && npm run serve"
    ports:
      - "3000:3000"
    depends_on:
      - backend
      - geoserver

  geoserver:
    image: osgeo/geoserver:2.23.7
    container_name: croatia_gis_geoserver
    restart: unless-stopped
    env_file:
      - ../docker/.env
    volumes:
      - "../geoserver/data_dir:/opt/geoserver/data_dir"
    ports:
      - "8080:8080"
    depends_on:
      - db

  nginx:
    image: nginx:1.23-alpine
    container_name: croatia_gis_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - "../docker/nginx/default.conf:/etc/nginx/conf.d/default.conf:ro"
      - "../frontend/build:/usr/share/nginx/html"
    depends_on:
      - backend
      - frontend
      - geoserver

volumes:
  postgres_data:
```

> **Service Details**:
> - **db**: PostGIS database
> - **redis**: Celery broker/result backend (optional)
> - **backend**: Django+GeoDjango served by **Gunicorn**
> - **frontend**: React build served by `serve` (or you can let Nginx serve static files directly)
> - **geoserver**: OSGEO GeoServer container
> - **nginx**: Reverse proxy & HTTPS termination (optional)

### 7.2. Dockerfiles

#### 7.2.1. `backend/Dockerfile`

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gdal-bin \
    libgdal-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
# If GDAL version mismatch, set:
# ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
# ENV C_INCLUDE_PATH=/usr/include/gdal

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project files
COPY . .

# Create static and media folders
RUN mkdir -p /app/staticfiles /app/media
```

> **Note**: Adjust GDAL headers includes if needed (e.g., set `C_INCLUDE_PATH`).

#### 7.2.2. `frontend/Dockerfile`

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine

WORKDIR /usr/src/app

# Copy package definition
COPY package.json package-lock.json ./

RUN npm ci

# Copy the rest of the source code
COPY . .

# Build React app
RUN npm run build

# Install a simple static file server (serve)
RUN npm install -g serve

CMD ["serve", "-s", "build", "-l", "3000"]
```

### 7.3. Nginx Configuration (`docker/nginx/default.conf`)

```nginx
# docker/nginx/default.conf
server {
    listen 80;
    server_name _;

    # Redirect HTTP to HTTPS (optional)
    # return 301 https://$host$request_uri;

    # Serve frontend static files
    location / {
        root /usr/share/nginx/html;
        try_files $uri /index.html;
    }

    # Proxy API requests to Django backend
    location /api/ {
        proxy_pass http://backend:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Proxy GeoServer UI & OGC endpoints
    location /geoserver/ {
        proxy_pass http://geoserver:8080/geoserver/;
        proxy_set_header Host $host;
    }

    # Proxy static/media if served by Django (rare in production)
    location /static/ {
        alias /app/staticfiles/;
    }
    location /media/ {
        alias /app/media/;
    }
}
```

> **HTTPS**: To enable HTTPS, mount your certs and add an SSL server block with `ssl_certificate` and `ssl_certificate_key`.

---

## 🔗 8. Git Repository & `.gitignore`

### 8.1. Initialize Git

```bash
cd croatia-gis
git init
```

### 8.2. `.gitignore` (at root)

```text
# Python / Django
/backend/venv/
/backend/__pycache__/
/backend/*.pyc
/backend/staticfiles/
/backend/media/

# Node / React
/frontend/node_modules/
/frontend/build/
/frontend/.env.local

# PostgreSQL data & logs (persisted by Docker)
/db/
docker/postgres_data/

# GeoServer data (if you don’t want to track data_dir contents)
/geoserver/data_dir/logs/
*.log

# Docker Compose environment
/docker/.env

# IDE files
.vscode/
.idea/
*.swp
```

> **Tip**: If you want to keep certain GeoServer configs under version control, selectively add them under `geoserver/data_dir/workspaces/croatia/styles/`, etc.

---

## 📖 9. README.md (Template)

Create `README.md` at repo root:

```markdown
# 🇭🇷 Croatia Cadastral & Administrative Web GIS

This repository contains a **full-stack** Web GIS application for **Croatia’s cadastral and administrative** spatial data. It automates:

1. Weekly scraping from Državna Geodetska Uprava ATOM feeds
2. Importing into a **PostgreSQL + PostGIS** database
3. Publishing via **GeoDjango**, **GeoServer**, and **React + OpenLayers**
4. Serving to end-users with **layer switching**, **GetFeatureInfo**, **metadata**, and **download** in multiple formats

---

## 🧱 Tech Stack

- **Backend**: Python 3, Django 4, GeoDjango, Django REST Framework, Django Filters, Celery (optional)
- **Database**: PostgreSQL 15 + PostGIS 3.3
- **GeoServer**: OSGEO GeoServer 2.23.x
- **Frontend**: React 18 + TypeScript, OpenLayers 6, Tailwind CSS
- **Containerization**: Docker, Docker Compose, nginx (reverse proxy)
- **CI/CD & Version Control**: Git

---

## 🚀 Getting Started

### Prerequisites

- Docker 20.10+ & Docker Compose v2+
- (Optional) Local Python 3.11 + Node 18 installations for development without Docker

### Clone Repo

```bash
git clone https://github.com/your-org/croatia-gis.git
cd croatia-gis
```

### Environment Variables

Copy `.env.example` to `.env` in both `backend/` and `frontend/` directories, then update:

```bash
# backend/.env
SECRET_KEY=your_django_secret_key
DEBUG=True
DB_HOST=db
DB_NAME=gis
DB_USER=postgres
DB_PASSWORD=strongpassword
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
CORS_ALLOWED_ORIGINS=http://localhost:3000

# frontend/.env
REACT_APP_API_BASE_URL=http://localhost:8000/api
REACT_APP_GEOSERVER_URL=http://localhost:8080
```

### Build & Run (Docker Compose)

```bash
cd docker
docker-compose up --build -d
```

- **PostGIS** initializes and runs migrations (via Django entrypoint).
- **GeoServer** initializes with empty data dir—you may run `publish_layers.py` to auto-publish tables.
- **React** app builds and is served on port **3000**.
- **nginx** listens on port **80** (8000+ for internal).

### Access URLs

- **Frontend**: http://localhost
- **Backend API**: http://localhost/api/
- **GeoServer**: http://localhost/geoserver/ (UI + OGC endpoints)
- **Admin**: http://localhost/admin/ (Django admin—create superuser via `docker exec -it croatia_gis_backend python manage.py createsuperuser`)

---

## 📄 Documentation

See the `docs/` folder:

- **architecture.md**: System architecture diagrams & component descriptions
- **api.md**: REST API specs (endpoints, query parameters, response schemas)
- **geoserver.md**: GeoServer configuration & layer publication guide
- **data_model.md**: PostGIS schema, spatial indexes, ERD
- **scraping.md**: ATOM feed details, parsing logic, error handling, retry strategy

---

## 🛠️ Development & Best Practices

1. **Coding Style**
   - **Python**:
     - Follow **PEP 8**.
     - Use **Black** for formatting: `black .`
     - Lint with **flake8**: `flake8 .`
   - **TypeScript**:
     - Use **ESLint** + **Prettier**.
     - Run `npm run lint` before commit.

2. **Testing**
   - **Backend**:
     - Use **pytest** + **pytest-django**.
     - Write tests for: models (geometry validity), serializers, views (status codes, GeoJSON format).
   - **Frontend**:
     - Use **React Testing Library** + **Jest**.
     - Test: Map rendering, layer toggling, GetFeatureInfo behavior (mock WMS responses).

3. **Continuous Integration**
   - Integrate **GitHub Actions** (or GitLab CI) to run lint, formatting, and tests on each PR.

4. **Security**
   - Store secrets in environment variables (`.env` files not committed).
   - Use `HTTPS` in production; configure **nginx** with valid TLS certs (Let’s Encrypt).
   - Restrict CORS to trusted domains.
   - Regularly update Docker images to patch vulnerabilities.

5. **Logging & Monitoring**
   - **Django**: Configure `LOGGING` in `settings.py` to output to files/STDOUT.
   - **GeoServer**: Tail logs under `geoserver/data_dir/logs/`.
   - **Docker**: Use `docker logs` and consider integrating with ELK stack for production.

---

## 📝 10. Documentation Outline (`docs/`)

### 10.1. `architecture.md`

```markdown
# System Architecture

## Overview
High-level diagram showing:
- Data ingestion pipeline (ATOM → Scripts → PostGIS)
- Backend (GeoDjango + DRF) → PostGIS
- GeoServer → PostGIS
- Frontend (React + OpenLayers) → GeoServer WMS/WFS & DRF API
- nginx as reverse proxy
- Celery for scheduled tasks

## Components

### 1. Data Ingestion
1. **fetch_atom_data.py**
2. **parse_and_load.py**
3. **PostGIS**

### 2. Backend
1. **Django + GeoDjango**
2. **Models**
3. **DRF ViewSets & Serializers**
4. **Celery (Tasks)**

### 3. GeoServer
1. **Workspace**: croatia
2. **Datastore**: PostGIS connection parameters
3. **Layers**: cadastral_cadastralparcel, cadastral_administrativeboundary, dof_ortho

### 4. Frontend
1. **React Components**
2. **OpenLayers Map**
3. **LayerSwitcher, MetadataPopup, DownloadMenu**

### 5. Deployment
1. **Docker Compose Services**
   - db, redis, backend, frontend, geoserver, nginx
2. **Volumes & Networking**
3. **Environment Variables**
4. **SSL/TLS**
```

### 10.2. `api.md`

```markdown
# REST API Endpoints

## Base URL
`http://<host>/api/`

## Endpoints

### 1. GET `/parcels/`
Returns a **GeoJSON FeatureCollection** of cadastral parcels.

#### Query Parameters
- `parcel_id`: Filter by exact parcel ID (string)
- `cadastral_municipality`: Filter by municipality name (string)
- `bbox`: Comma-separated bounding box in EPSG:4326 (minLon,minLat,maxLon,maxLat)
- `limit`, `offset`: Pagination

#### Response (200 OK)
```jsonc
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": { "type": "MultiPolygon", "coordinates": [ ... ] },
      "properties": {
        "ogc_fid": 12345,
        "parcel_id": "RH_PARCEL_000123",
        "cadastral_municipality": "Zagreb",
        "area_sqm": 250.5,
        "updated_at": "2025-06-01T02:00:00Z"
      }
    },
    ...
  ],
  "count": 1500,
  "next": "http://.../parcels/?offset=100&limit=100",
  "previous": null
}
```

### 2. GET `/parcels/{pk}/`
Retrieve a single parcel.

#### URL Parameters
- `pk`: Primary key (ogc_fid)

#### Response (200 OK)
Same as single-feature GeoJSON Feature.

### 3. GET `/admin_boundaries/`
Returns administrative boundaries.

#### Query Parameters
- `name`: Filter by name substring
- `admin_type`: Filter by “Municipality” / “County”
- `limit`, `offset`

#### Response (200 OK)
```jsonc
{
  "type": "FeatureCollection",
  "features": [ ... ],
  "count": 51,
  "next": null,
  "previous": null
}
```

### 4. GET `/admin_boundaries/{pk}/`
Retrieve a single boundary.

### 5. GET `/layers/` (Optional)
List all published layers from GeoServer (proxy).
```

### 10.3. `geoserver.md`

```markdown
# GeoServer Setup & Layer Publication

## 1. Installing GeoServer (Docker)
- Uses `osgeo/geoserver:2.23.7` Docker image
- Mount `data_dir/` for persistent config

## 2. Data Directory Structure
```
data_dir/
├── workspaces/
│   └── croatia/
│       ├── data/      ← (unused for PostGIS; for files)
│       └── styles/    ← SLD files
└── ...
```

## 3. Creating Workspace & Datastore
### 3.1. Using REST API
- POST `/rest/workspaces`
- POST `/rest/workspaces/croatia/datastores`
- Body: see `publish_layers.py`

### 3.2. Manual UI
1. Login at `/geoserver` (`admin/geoserver`)
2. Workspaces → Add new workspace: `croatia`
3. Stores → PostGIS → Fill connection (host, port, db, user, pass)

## 4. Publishing Layers
- Workspace: `croatia`
- Datastore: `postgis_croatia`

### 4.1. Layer Settings
- Name: `<table_name>` (e.g., `cadastral_cadastralparcel`)
- Title: Human-readable (auto-generated)
- CRS: `EPSG:3765`
- Bounding Boxes: “Compute from data”
- Style: Use default or custom SLD

### 4.2. Download Formats
GeoServer WFS supports output formats:
- `application/json` (GeoJSON)
- `shape-zip` (Shapefile zipped)
- `KML`
- `application/geopackage+sqlite3`
- `application/dxf`
- `text/csv`
- etc.
```

### 10.4. `data_model.md`

```markdown
# PostGIS Data Model

## Schemas
- `public` (default)
  - **Tables loaded from ATOM**:
    - `cadastral_cadastralparcel`
    - `cadastral_administrativeboundary`
    - (Any additional datasets)
- `cadastral` (optional)

## Table: `cadastral_cadastralparcel`
| Column                   | Type                     | Notes                                  |
|--------------------------|--------------------------|----------------------------------------|
| ogc_fid                  | integer (PRIMARY KEY)    | OGR-generated unique ID                |
| parcel_id                | varchar(100)             | Unique parcel identifier               |
| cadastral_municipality   | varchar(100)             | Municipality name                      |
| area_sqm                 | double precision         | Area in square meters                  |
| geom                     | MULTIPOLYGON, SRID=3765  | Spatial geometry (MultiPolygon)        |
| updated_at               | timestamp with time zone | Last update timestamp (Django-managed) |

- **Indexes**:
  - `CREATE INDEX idx_parcel_geom ON cadastral_cadastralparcel USING GIST (geom);`
  - `CREATE INDEX idx_parcel_id ON cadastral_cadastralparcel (parcel_id);`

## Table: `cadastral_administrativeboundary`
| Column | Type                       | Notes                            |
|--------|----------------------------|----------------------------------|
| ogc_fid | integer (PRIMARY KEY)     | OGR-generated                     |
| name    | varchar(100)              | Boundary name                     |
| admin_type | varchar(50)            | “Municipality” / “County”         |
| geom    | MULTIPOLYGON, SRID=3765   | Spatial geometry (MultiPolygon)   |
| updated_at | timestamp with time zone | Last update (Django-managed)     |

- **Indexes**:
  - `CREATE INDEX idx_adm_geom ON cadastral_administrativeboundary USING GIST (geom);`
  - `CREATE INDEX idx_adm_name ON cadastral_administrativeboundary (name);`

## CRS & Transformations
- **Source Data**: If original GML/Shapefile is in **EPSG:4326** or **EPSG:3857**, use `-t_srs EPSG:3765` in `ogr2ogr` to reproject.
- **Database**: Store geometries in **EPSG:3765** (TMH / D48).
- **Frontend**: Reproject on-fly to **EPSG:3857** using OpenLayers.

## Data Volume Considerations
- Cadastral parcels: ~1.5 million features
- Administrative boundaries: ~5 000 features
- Plan to create spatial indexes for all geometry columns.

## Foreign Keys & Relationships
- If additional tables (e.g., land use, ownership), define proper **FK** relationships.
- Use **`SERIAL`** or **`BIGSERIAL`** for surrogate IDs if needed.

## Versioning & History
- Consider using **audit triggers** (e.g., `trigger_update_timestamp()`) if you need to track changes.
```

### 10.5. `scraping.md`

```markdown
# Data Scraping & Loading Guide

## 1. ATOM Feeds

### 1.1. Feed URLs
- **Cadastral Parcels**: `https://dgu.gov.hr/atom/kadastrovi/katastar_parcela.xml`
- **Administrative Boundaries**: `https://dgu.gov.hr/atom/administrativne_granice.xml`
- (Replace with actual URLs; these are illustrative.)

### 1.2. XML Structure

```xml
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Katastar Parcela</title>
  <updated>2025-06-01T00:00:00Z</updated>
  <entry>
    <title>Parcel Data 2025-06-01</title>
    <updated>2025-06-01T00:00:00Z</updated>
    <link rel="enclosure" href="https://dgu.gov.hr/data/kat_parcela_20250601.gml" type="application/gml+xml"/>
    <id>...</id>
    <summary>...</summary>
  </entry>
  ...
</feed>
```

### 1.3. Parsing Logic

1. **Namespace**: ATOM uses `xmlns="http://www.w3.org/2005/Atom"`.
2. **Elements**:
   - `<entry>`: One dataset release
   - `<entry><updated>`: Timestamp (UTC)
   - `<entry><link rel="enclosure" href="…" />`: Download URL
3. **Deduplication**:
   - Use `ETag` or `Last-Modified` from HTTP headers.
   - Maintain a **`history.json`** mapping `{ "url": "last_updated" }`.
   - Only download if `updated` differs from stored value.

### 1.4. Download & Conversion

#### 1.4.1. Supported Formats
- **GML**: Directly importable via `ogr2ogr`.
- **ZIP**: Usually contains ESRI Shapefiles. Unzip, locate `.shp` and import via `ogr2ogr`.
- **SHP**: If zipped or standalone.

#### 1.4.2. Conversion to PostGIS

- **ogr2ogr** command (example):

  ```bash
  ogr2ogr \
    -f "PostgreSQL" \
    PG:"host=db user=postgres dbname=gis password=strongpassword" \
    "/path/to/data.gml" \
    -nln cadastral_cadastralparcel \
    -nlt PROMOTE_TO_MULTI \
    -t_srs EPSG:3765 \
    -lco GEOMETRY_NAME=geom \
    -lco FID=ogc_fid \
    -overwrite
  ```

- **Options**:
  - `-f "PostgreSQL"`: Target format
  - `PG:"..."`: Connection string
  - `-nln`: New layer name (schema_table)
  - `-nlt PROMOTE_TO_MULTI`: Ensure MultiPolygon geometry
  - `-t_srs EPSG:3765`: Reproject to Croatian CRS
  - `-lco GEOMETRY_NAME=geom`: Column name for geometry
  - `-lco FID=ogc_fid`: Column name for feature ID
  - `-overwrite`: Drop existing table & re-create

### 1.5. Error Handling & Logging

- **HTTP Errors**:
  - Retry 3× with exponential backoff on 5xx.
  - If 4xx, log & skip.
- **GDAL Errors**:
  - Capture stderr from `ogr2ogr`.
  - If `t_srs` fails (e.g., missing CRS), inspect source file’s CRS.
- **Partial Downloads**:
  - Download to a temp file (`.part`) then rename on success.
- **History Persistence**:
  - On successful load, update `history.json`.
  - Use atomic file write to avoid corruption: write to `history_tmp.json`, then `mv`.

### 1.6. Scheduling

- If using **Celery Beat**:
  1. Start **Redis**: `docker-compose up -d redis`
  2. Start **Celery Worker**:
     ```bash
     docker exec -it croatia_gis_backend celery -A django_project worker -l info
     ```
  3. Start **Celery Beat**:
     ```bash
     docker exec -it croatia_gis_backend celery -A django_project beat -l info
     ```
- If using **cron**:
  - Use `crontab -e` on host.
  - Example entry:
    ```cron
    0 3 * * 0 docker exec croatia_gis_backend python /app/scripts/fetch_atom_data.py >> /app/logs/scrape.log 2>&1
    ```

---

## 🧹 11. Code Quality & Best Practices

### 11.1. Python (Backend)

- **Formatting**:
  ```bash
  pip install black flake8 isort
  black .
  isort .
  flake8 .
  ```
- **Type Checking** (optional): Use **mypy**.
  ```bash
  pip install mypy
  mypy .
  ```
- **Tests**:
  - Place tests under `cadastral/tests/`.
  - Use fixtures for PostGIS geometry.
  - Example test (pytest):

    ```python
    # cadastral/tests/test_models.py
    import pytest
    from django.contrib.gis.geos import MultiPolygon, Polygon
    from cadastral.models import CadastralParcel

    @pytest.mark.django_db
    def test_create_parcel():
        poly = MultiPolygon(Polygon(((0, 0), (1, 0), (1, 1), (0, 1), (0, 0))))
        p = CadastralParcel.objects.create(
            parcel_id="TEST_001",
            cadastral_municipality="Test",
            area_sqm=100.0,
            geom=poly,
        )
        assert p.parcel_id == "TEST_001"
        assert p.geom.area == 1.0  # In degrees, but basic test
    ```

### 11.2. TypeScript (Frontend)

- **Install ESLint & Prettier**:

  ```bash
  npm install --save-dev eslint eslint-plugin-react eslint-plugin-react-hooks @typescript-eslint/parser @typescript-eslint/eslint-plugin prettier eslint-config-prettier eslint-plugin-prettier
  ```

- **`.eslintrc.js`**:

  ```js
  module.exports = {
    parser: "@typescript-eslint/parser",
    extends: [
      "react-app",
      "plugin:@typescript-eslint/recommended",
      "plugin:prettier/recommended",
    ],
    plugins: ["@typescript-eslint", "react", "prettier"],
    rules: {
      "prettier/prettier": "error",
      "@typescript-eslint/no-unused-vars": ["warn"],
      "react/react-in-jsx-scope": "off",
    },
    settings: {
      react: {
        version: "detect",
      },
    },
  };
  ```

- **`.prettierrc`**:

  ```jsonc
  {
    "semi": true,
    "singleQuote": true,
    "jsxSingleQuote": false,
    "printWidth": 80,
    "trailingComma": "all",
    "tabWidth": 2
  }
  ```

- **Scripts in `package.json`**:

  ```jsonc
  {
    ...
    "scripts": {
      "start": "react-scripts start",
      "build": "react-scripts build",
      "test": "react-scripts test",
      "lint": "eslint 'src/**/*.{ts,tsx}'",
      "format": "prettier --write 'src/**/*.{ts,tsx,js,jsx,css,md}'"
    }
  }
  ```

- **Testing**:

  ```bash
  npm install --save-dev @testing-library/react @testing-library/jest-dom jest-environment-jsdom
  ```

  - Create tests under `src/__tests__/`.
  - Example:

    ```tsx
    // src/__tests__/LayerSwitcher.test.tsx
    import React from "react";
    import { render, screen, fireEvent } from "@testing-library/react";
    import LayerSwitcher from "../components/LayerSwitcher";

    describe("LayerSwitcher", () => {
      const layers = [
        { id: "a", title: "Layer A" },
        { id: "b", title: "Layer B" },
      ];
      test("renders and toggles correctly", () => {
        const toggleLayer = jest.fn();
        const toggleBase = jest.fn();
        render(
          <LayerSwitcher
            availableLayers={layers}
            selectedLayers={["a"]}
            toggleLayer={toggleLayer}
            toggleBase={toggleBase}
            activeBase={"OSM"}
          />
        );
        // Check checkboxes
        const checkboxA = screen.getByLabelText("Layer A") as HTMLInputElement;
        expect(checkboxA.checked).toBe(true);
        fireEvent.click(checkboxA);
        expect(toggleLayer).toHaveBeenCalledWith("a");
      });
    });
    ```

---

## 🏁 12. Final Checklist

Before merging to **main** (or deploying to production), ensure:

- [ ] **Scraper scripts** tested locally (download & ingest test files)
- [ ] **PostGIS** database built with correct schemas & indexes
- [ ] **GeoServer** workspace, datastore, and layers published correctly
- [ ] **GeoDjango** API endpoints returning valid GeoJSON
- [ ] **React** UI renders map, toggles layers, shows metadata, and downloads work
- [ ] **Docker Compose** up & services communicate (networking, env vars)
- [ ] **nginx** reverse proxy routes requests correctly (HTTP & HTTPS)
- [ ] **README.md** up-to-date with run instructions
- [ ] **Documentation** in `docs/` covers architecture, API, data model, scraping
- [ ] **Testing**: All unit tests (backend & frontend) pass in CI
- [ ] **Linting & Formatting**: No lint errors, code formatted with Black & Prettier

---

## 🧠 Tips & Considerations for the AI Agent

1. **Monitoring Feed Changes**:
   - Use HTTP ETag/Last-Modified to detect truly new/changed feeds.
   - If feed structure changes (element names), update XML parsing logic.

2. **Handling Large Datasets**:
   - Cadastral parcels may be millions of polygons—consider batch ingest or streaming via `ogr2ogr` with `-segments` and `-clip`.
   - Use **COPY** or **`ogr2ogr -append`** instead of full table overwrite if incremental updates are possible.

3. **Spatial Indexing & Performance**:
   - After each ingest, run `CREATE INDEX <idx_name> ON <table> USING GIST (geom);`.
   - VACUUM ANALYZE tables periodically.

4. **GeoServer Caching**:
   - Enable **GeoWebCache** for WMS/WFS tile caching.
   - Configure caching parameters (`gridsets`, `diskQuota`, etc.) to speed up repeated map views.

5. **CRS Transformations**:
   - If source GML uses EPSG:3765 but `ogr2ogr` misinterprets, supply a user-provided CRS file.
   - Ensure `proj4` definition for EPSG:3765 is available in container.

6. **Production Deployment**:
   - Use a managed PostGIS (e.g., AWS RDS) for high availability.
   - Run GeoServer behind a load balancer if expecting high traffic.
   - Use a CI/CD pipeline (GitHub Actions) to build Docker images on push, run tests, then push to container registry.

7. **Security & Permissions**:
   - Use database users with minimal privileges (e.g., separate “writer” for ingest, “reader” for GeoServer).
   - Use GeoServer security to restrict publishing privileges; allow “read-only” for WFS.
   - Enforce HTTPS and HSTS in nginx.

8. **Scaling & Caching**:
   - For WFS downloads of large layers, consider pre-generating GeoPackages and storing them on object storage (e.g., S3).
   - Use CDN for serving static assets (React build).

9. **Backup & Recovery**:
   - Schedule regular PostGIS backups (`pg_dump`).
   - Export GeoServer `data_dir` settings and styles periodically.

10. **Future Extensions**:
    - Add **user authentication** (e.g., JWT via DRF).
    - Allow users to **draw custom polygons** and query intersecting parcels.
    - Integrate additional layers: Land Cover, Hydrography, etc.
    - Provide **vector tile** support (TileJSON) for improved performance.

---

You now have a **detailed blueprint**—from **data ingestion** to **backend**, **GeoServer**, **frontend**, **Docker**, **nginx**, **documentation**, and **best practices**.

Proceed to implement each component step by step, iteratively test locally, and then stage for a production-like environment. Good luck!