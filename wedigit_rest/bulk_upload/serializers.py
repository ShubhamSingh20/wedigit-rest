from typing import Dict, List
from django.db.models.query import QuerySet
from rest_framework import serializers
from bulk_upload.models import Document, DocumentEntries
from django.forms.models import model_to_dict
from django.core.validators import FileExtensionValidator
from bulk_upload.models import Schema
import pandas as pd

user_t = lambda user :  model_to_dict(user, fields=['email', 'first_name', 'last_name']) \
    if user is not None else {}

# create serializers here. 

class DetailDocumentSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='slug')
    class Meta:
        model = Document
        fields = ['id']

    def to_representation(self, instance : Document) -> Dict:
        entries, rows = DocumentEntries.objects.filter(document=instance), []
        rows = [ {en.id: en.row_data.split('$#$')} for en in entries]

        return {
            'id': instance.slug,
            'columns': instance.cols.values_list('column_name', flat=True),
            'created_at': instance.created_at,
            'created_by': user_t(instance.created_by),
            'rows': rows,
        }

class DocumentUploadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='slug')
    file = serializers.FileField(validators=[
        FileExtensionValidator(allowed_extensions=['csv', 'xlsx'])
    ])

    class Meta:
        model = Document
        fields = [
            'id', 'file', 
            'created_at', 'created_by'
        ]
        read_only_fields = ['created_by']
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }

    def to_representation(self, instance : Document) -> Dict:
        cols : QuerySet = instance.cols

        return {
            'id': instance.slug,
            'total_cols': cols.count(),
            'total_rows': instance.total_rows,
            'columns': cols.values_list('column_name', flat=True),
            'created_at': instance.created_at,
            'created_by': user_t(instance.created_by),
        }

    def get_csv_data(self, filepath) -> List[Dict]:
        df = pd.read_csv(filepath, squeeze=True)
        
        return [{
            'cols': list(df.columns),
            'data': df.T.to_dict()
        }]

    def get_excel_data(self, filepath) -> List[Dict]:
        sheets_df = pd.read_excel(
            filepath, sheet_name=None, 
            squeeze=True,
        )

        data = []

        for sheet_name in sheets_df:
            df = sheets_df[sheet_name]
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')] # remove unnamed columns
            data.append({
                'cols': list(df.columns),
                'data': df.to_dict()
            })
        
        return data

    def create(self, validated_data):
        document : Document = super().create(validated_data)
        ext = document.file.name.split('.')[-1]

        file_content = self.get_csv_data(document.file.path) if ext == 'csv' \
            else self.get_excel_data(document.file.path)

        # file_content contains a list of all the columns & all the 
        # data in dict format for every sheet

        for sheet in file_content:
            # keep track of all the columns created so far
            columns, entries = dict(), sheet.get('data')
            document_entries = [] # create objects for document entries for bulk insertion

            for row in entries.values():
                row_data = []
                for col, value in row.items():
                    if col not in columns:
                        # add the created schema object to columns
                        columns[col] = Schema.objects.create(document=document, column_name=col)
                    row_data.append(str(value))

                document_entries.append(DocumentEntries(document=document, row_data='$#$'.join(row_data)))

            DocumentEntries.objects.bulk_create(document_entries)

        return document
