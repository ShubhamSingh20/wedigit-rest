from typing import Dict, List
from django.db.models.query import QuerySet
from rest_framework import serializers
from bulk_upload.models import Document
from django.forms.models import model_to_dict
from django.core.validators import FileExtensionValidator
import pandas as pd

DocumentSchema = Dict

user_t = lambda user :  model_to_dict(user, fields=['email', 'first_name', 'last_name']) \
    if user is not None else {}

# create serializers here. 

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
            'total_cols': cols.count(),
            'total_rows': instance.total_rows,
            'created_at': instance.created_at,
            'created_by': user_t(instance.created_by),
            'columns': cols.values_list('column_name', flat=True),
        }

    def get_csv_data(self, filepath) -> List[DocumentSchema]:
        return [pd.read_csv(filepath, squeeze=True).T.to_dict()]

    def get_excel_data(self, filepath) -> List[DocumentSchema]:
        sheets_df = pd.read_excel(
            filepath, sheet_name=None, 
            squeeze=True, index=False
        )

        data = []

        for sheet_name in sheets_df:
            df = sheets_df[sheet_name]
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            data.append(sheets_df[sheet_name].T.to_dict())

        return data

    def create(self, validated_data):
        document : Document = super().create(validated_data)
        ext = document.file.name.split('.')[-1]

        if ext == 'csv':
            data = self.get_csv_data(document.file.path)

        if ext == 'xlsx':
            data = self.get_excel_data(document.file.path)

        return document

