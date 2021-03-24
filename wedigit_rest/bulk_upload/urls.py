from bulk_upload import views
from django.urls import path
from django.conf.urls import include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'documents', views.DocumentModelViewSet, basename='document')

urlpatterns = [
    path('', include(router.urls)),
]
