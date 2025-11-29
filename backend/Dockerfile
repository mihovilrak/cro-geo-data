FROM python:3.15.0a1-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gdal-bin \
    libgdal-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && pip install --upgrade pip \
    && pip install -r requirements.txt --no-cache-dir \
    && mkdir -p /app/staticfiles /app/media

COPY . .
