"""
URL configuration for django_project project.
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework.renderers import JSONOpenAPIRenderer, OpenAPIRenderer
from rest_framework.schemas import get_schema_view

schema_view = get_schema_view(
    title="Croatia Geo API",
    description="Spatial datasets exposed via GeoDjango + DRF.",
    version="1.0.0",
    public=True,
    renderer_classes=[OpenAPIRenderer, JSONOpenAPIRenderer],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("cadastral.urls")),
    path("api/openapi.yaml", schema_view, name="openapi-schema"),
]
