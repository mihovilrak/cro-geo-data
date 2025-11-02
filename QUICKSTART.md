# 🚀 Quick Start Guide

This guide will help you get the Croatia GIS application running quickly.

## Prerequisites

- **Docker** 20.10+ and **Docker Compose** v2+
- At least 4GB of RAM available for Docker

## Step 1: Set Up Environment Variables

### Backend
Create `backend/.env` file (copy from `.env.example` if needed):
```bash
cp backend/.env.example backend/.env
```

Then edit `backend/.env` and set:
- `SECRET_KEY` - A random Django secret key (generate one or use a secure random string)
- Other values can remain as defaults for development

### Frontend
Create `frontend/.env` file (copy from `.env.example` if needed):
```bash
cp frontend/.env.example frontend/.env
```

The default values should work for local development.

## Step 2: Build and Start Services

Navigate to the `docker` directory and start all services:

```bash
cd docker
docker-compose up --build
```

This will:
- Build Docker images for backend and frontend
- Start PostgreSQL + PostGIS database
- Start Redis
- Start Django backend
- Start React frontend (development server)
- Start GeoServer
- Start nginx (reverse proxy)

**Note**: The first build may take several minutes as it downloads images and installs dependencies.

## Step 3: Access the Application

Once all containers are running, you can access:

- **Frontend (Development)**: http://localhost:3000
- **Backend API**: http://localhost:8000/api/
- **Django Admin**: http://localhost:8000/admin/ (create superuser first)
- **GeoServer**: http://localhost:8080/geoserver/ (admin/geoserver)

## Step 4: Create Django Superuser (Optional)

To access the Django admin panel:

```bash
docker exec -it croatia_gis_backend python django_project/manage.py createsuperuser
```

Follow the prompts to create an admin user.

## Running in Background

To run services in detached mode:

```bash
cd docker
docker-compose up -d
```

View logs:
```bash
docker-compose logs -f
```

Stop services:
```bash
docker-compose down
```

## Troubleshooting

### Port Already in Use
If you get port conflicts, edit `docker/docker-compose.yml` and change the port mappings (e.g., `"8001:8000"` instead of `"8000:8000"`).

### Frontend Not Loading
1. Check if the frontend container is running: `docker ps`
2. Check frontend logs: `docker logs croatia_gis_frontend`
3. Ensure `frontend/.env` file exists with correct values

### Backend Errors
1. Check backend logs: `docker logs croatia_gis_backend`
2. Ensure `backend/.env` file exists
3. Try restarting: `docker-compose restart backend`

### Database Connection Issues
1. Wait for database to be healthy (check `docker-compose ps`)
2. Ensure database environment variables in `docker-compose.yml` match your `.env` files

## Development Mode

### Running Frontend Locally (without Docker)

If you prefer to run the frontend locally for faster development:

```bash
cd frontend
npm install
npm start
```

The frontend will run on http://localhost:3000 and will connect to the backend running in Docker.

### Running Backend Locally (without Docker)

For local backend development:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd django_project
python manage.py migrate
python manage.py runserver
```

**Note**: Make sure PostgreSQL is running (via Docker) and update `backend/.env` with `DB_HOST=localhost` if needed.

## Next Steps

- Implement database models (see `Instructions.md` section 4.4)
- Set up scraping scripts (see `Instructions.md` section 2)
- Configure GeoServer layers (see `docs/geoserver.md`)
- Add authentication and user management
- Deploy to production server

For detailed documentation, see:
- `README.md` - Main project documentation
- `Instructions.md` - Complete implementation guide
- `docs/` - Additional documentation

