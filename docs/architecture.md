# System Architecture

## Overview

High-level diagram showing:
- Data ingestion pipeline (ATOM → Scripts → PostGIS) - **Future implementation**
- Backend (GeoDjango + DRF) → PostGIS
- GeoServer → PostGIS
- Frontend (React + OpenLayers) → GeoServer WMS/WFS & DRF API
- nginx as reverse proxy
- Celery for scheduled tasks - **Future implementation**

## Components

### 1. Data Ingestion (Future)
1. **fetch_atom_data.py** - ATOM feed scraper
2. **parse_and_load.py** - Data conversion and loading
3. **PostGIS** - Spatial database

### 2. Backend
1. **Django + GeoDjango** - Web framework with GIS support
2. **Models** - Database schema (to be implemented)
3. **DRF ViewSets & Serializers** - REST API endpoints
4. **Celery (Tasks)** - Background tasks (future)

### 3. GeoServer
1. **Workspace**: croatia
2. **Datastore**: PostGIS connection parameters
3. **Layers**: cadastral_cadastralparcel, cadastral_administrativeboundary, dof_ortho

### 4. Frontend
1. **React Components** - UI components
2. **OpenLayers Map** - Interactive map visualization
3. **LayerSwitcher, MetadataPopup, DownloadMenu** - Feature components

### 5. Deployment
1. **Docker Compose Services**
   - db, redis, backend, frontend, geoserver, nginx
2. **Volumes & Networking**
3. **Environment Variables**
4. **SSL/TLS** - Future enhancement

