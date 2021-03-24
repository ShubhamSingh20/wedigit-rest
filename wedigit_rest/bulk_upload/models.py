from uuid import uuid4
from django.db import models
from helper.models import ModelStamps

# Create your models here.

class Document(ModelStamps):
    file = models.FileField(upload_to='documents/%Y/%m/%d/')
    slug = models.UUIDField(default=uuid4, editable=False)

    @property
    def cols(self):
        return Schema.objects.filter(document=self)

    @property
    def total_rows(self):
        return Schema.objects.filter(document=self).count()

    @property
    def total_cols(self):
        return DocumentEntries.objects.filter(schema__document=self).count()

    def __str__(self) -> str:
        return '%s' % self.file

class Schema(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    column_name = models.CharField(max_length=15)

class DocumentEntries(models.Model):
    schema = models.ForeignKey(Schema, on_delete=models.CASCADE)
    data = models.TextField()
