from bulk_upload.models import Document
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAuthenticated
from bulk_upload.serializers import DocumentUploadSerializer
from rest_framework.viewsets import GenericViewSet
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.mixins import (ListModelMixin, DestroyModelMixin, CreateModelMixin, RetrieveModelMixin)

# Create your views here.
class DocumentModelViewSet(CreateModelMixin, 
                            RetrieveModelMixin, 
                            ListModelMixin, 
                            DestroyModelMixin, 
                            GenericViewSet):

    permission_classes = [IsAuthenticated]
    serializer_class = DocumentUploadSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        return Document.objects.filter(created_by=self.request.user)
