# 🇭🇷 Croatia Cadastral & Administrative Web GIS

> ⚠️ **Note**: This project is a work in progress.

This repository contains a **full-stack** Web GIS application for **Croatia's cadastral and administrative** spatial data.

## 🧱 Tech Stack

- **Backend**: Python 3, Django 4, GeoDjango, Django REST Framework, Django Filters, Celery (optional)
- **Database**: PostgreSQL 15 + PostGIS 3.3
- **GeoServer**: OSGEO GeoServer 2.23.x
- **Frontend**: React 18 + TypeScript, OpenLayers 6, Tailwind CSS
- **Containerization**: Docker, Docker Compose, nginx (reverse proxy)
- **CI/CD & Version Control**: Git

## 🚀 Getting Started

### Prerequisites

- Docker 20.10+ & Docker Compose v2+
- (Optional) Local Python 3.11 + Node 18 installations for development without Docker

### Quick Start

1. **Clone or navigate to the project directory**

2. **Set up environment variables**

   Create `.env` files in `backend/` and `frontend/` directories (see examples below)

3. **Build & Run with Docker Compose**

   ```bash
   cd docker
   docker-compose up --build
   ```

4. **Access the application**

   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000/api/
   - **GeoServer**: http://localhost:8080/geoserver/
   - **Admin**: http://localhost:8000/admin/

### Environment Variables

#### `backend/.env`
```ini
SECRET_KEY=your_django_secret_key_here_change_in_production
DEBUG=True
DB_HOST=db
DB_PORT=5432
DB_NAME=gis
DB_USER=postgres
DB_PASSWORD=postgres
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

#### `frontend/.env`
```ini
REACT_APP_API_BASE_URL=http://localhost:8000/api
REACT_APP_GEOSERVER_URL=http://localhost:8080/geoserver
```

## 📁 Project Structure

```
cro-geo-data/
├── backend/                    # Django + GeoDjango backend
│   ├── django_project/         # Django project
│   ├── scripts/                # Scraping scripts (future)
│   └── requirements.txt
├── frontend/                   # React + TypeScript + OpenLayers
│   ├── src/
│   │   ├── components/         # UI components
│   │   ├── services/           # API clients
│   │   └── utils/              # Utilities
│   └── package.json
├── geoserver/                  # GeoServer configuration
│   └── data_dir/               # GeoServer data directory
├── docker/                     # Docker configuration
│   ├── nginx/                  # nginx config
│   └── docker-compose.yml
├── db/                         # Database init scripts
└── docs/                       # Documentation
```

## 📄 Documentation

See the `docs/` folder and `Instructions.md` for detailed documentation.

## 🛠️ Development

### Running Frontend Locally (without Docker)

```bash
cd frontend
npm install
npm start
```

### Running Backend Locally (without Docker)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## 📝 License

[Add your license here]

## 🤝 Contributing

[Add contribution guidelines here]

