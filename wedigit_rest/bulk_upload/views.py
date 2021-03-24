from rest_framework.request import Request
from rest_framework.response import Response
from bulk_upload.models import Document, DocumentEntries
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import action
from bulk_upload.serializers import DetailDocumentSerializer, DocumentUploadSerializer
from rest_framework.viewsets import GenericViewSet
from rest_framework.exceptions import ValidationError
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

    @action(detail=True, methods=['post'])
    def new_entry(self, request, slug):
        document = self.get_object()
        cols = document.cols

        if not any(set(cols.values_list('column_name', flat=True)).intersection(set(request.data.keys()))):
            raise ValidationError({'error': ['all the fields are required']})

        row, data = document.total_rows + 1, []

        for col in cols:
            data.append(DocumentEntries(
                schema=col, row_no=row, 
                data=request.data.get(col.column_name)
            ))
        

        DocumentEntries.objects.bulk_create(data)

        return Response(
            data=DetailDocumentSerializer(instance=document).data, 
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['patch'])
    def update_entry(self, request, slug, row_no=None):
        document = self.get_object()
        cols = document.cols

        if not any(set(cols.values_list('column_name', flat=True)).intersection(set(request.data.keys()))):
            raise ValidationError({'error': ['all the fields are required']})

        DocumentEntries.objects.filter(row_no=row_no, schema__in=document.cols).delete()

        data = []

        for col in cols:
            data.append(DocumentEntries(
                schema=col, row_no=row_no, 
                data=request.data.get(col.column_name)
            ))

        DocumentEntries.objects.bulk_create(data)

        return Response(
            data=DetailDocumentSerializer(instance=document).data, 
            status=status.status.HTTP_200_OK
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
