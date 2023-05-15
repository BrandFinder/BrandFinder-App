from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve
from django.conf.urls.static import static
import os

from . import views

urlpatterns = [
    path("", views.index, name="index"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
