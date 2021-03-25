from rest_framework.request import Request
from rest_framework.response import Response
from bulk_upload.models import Document, DocumentEntries
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import action
from bulk_upload.serializers import DetailDocumentSerializer, DocumentUploadSerializer
from rest_framework.viewsets import GenericViewSet
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.mixins import (ListModelMixin, DestroyModelMixin, CreateModelMixin, RetrieveModelMixin)

# Create your views here.
class DocumentModelViewSet(CreateModelMixin, 
                            RetrieveModelMixin, 
                            ListModelMixin, 
                            DestroyModelMixin, 
                            GenericViewSet):

    pagination_class = None
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

    @action(detail=True, methods=['post'])
    def new_entry(self, request, slug):
        document = self.get_object()
        cols, data = document.cols, []

        for col in cols:
            if  not (value := request.data.get(col.column_name, False)):
                raise ValidationError({'error': ['all the fields are required']})
            data.append(str(value))

        DocumentEntries.objects.create('#$#'.join(data))

        return Response(
            data=DetailDocumentSerializer(instance=document).data, 
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['put'])
    def update_entry(self, request, slug):
        document = self.get_object()
        row_no = request.query_params.get('row_no', None)
        
        try:
            entry = DocumentEntries.objects.get(document=document, id=row_no)
        except DocumentEntries.DoesNotExist:
            raise NotFound

        cols, data = document.cols, []

        for col in cols:
            if  not (value := request.data.get(col.column_name, False)):
                raise ValidationError({'error': ['all the fields are required']})
            data.append(str(value))

        entry.row_data = '#$#'.join(entry)
        entry.save()

        return Response(
            data=DetailDocumentSerializer(instance=document).data, 
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['delete'])
    def delete_entry(self, request : Request, slug):
        document = self.get_object()
        
        if row_no := request.query_params.get('row_no', None):
            DocumentEntries.objects.filter(id=row_no, document=document).delete()

        return Response(
            data=DetailDocumentSerializer(instance=document).data, 
            status=status.HTTP_200_OK
        )
