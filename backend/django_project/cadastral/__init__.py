"""
App init tweaks for optional dependencies.
"""
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView

if not hasattr(DjangoFilterBackend, "get_schema_operation_parameters"):
    def _schema_operation_parameters(self, view: APIView) -> list:
        return []

    DjangoFilterBackend.get_schema_operation_parameters = _schema_operation_parameters  # type: ignore[attr-defined]
