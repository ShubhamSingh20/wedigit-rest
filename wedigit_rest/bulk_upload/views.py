from bulk_upload.models import Document
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAuthenticated
from bulk_upload.serializers import DetailDocumentSerializer, DocumentUploadSerializer
from rest_framework.viewsets import GenericViewSet
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.mixins import (ListModelMixin, DestroyModelMixin, CreateModelMixin, RetrieveModelMixin)

# Create your views here.
class DocumentModelViewSet(CreateModelMixin, 
                            RetrieveModelMixin, 
                            ListModelMixin, 
                            DestroyModelMixin, 
                            GenericViewSet):

    lookup_field = 'slug'
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_serializer_class(self):

        if self.action in ['retrieve']:
            return DetailDocumentSerializer
        
        return DocumentUploadSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        return Document.objects.filter(created_by=self.request.user).order_by('-created_at')
