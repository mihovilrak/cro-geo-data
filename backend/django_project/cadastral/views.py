from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import action

# Placeholder views - will be implemented when models are ready
class CadastralParcelViewSet(viewsets.ViewSet):
    """
    Placeholder viewset for cadastral parcels.
    Will be implemented when models are ready.
    """
    def list(self, request: Request) -> Response:
        return Response({
            "message": "Cadastral parcels endpoint - models not yet implemented",
            "features": []
        })

class AdministrativeBoundaryViewSet(viewsets.ViewSet):
    """
    Placeholder viewset for administrative boundaries.
    Will be implemented when models are ready.
    """
    def list(self, request: Request) -> Response:
        return Response({
            "message": "Administrative boundaries endpoint - models not yet implemented",
            "features": []
        })

