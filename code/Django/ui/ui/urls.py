from django.urls import include, path
from django.conf.urls import url
from django.contrib import admin
from . import settings

urlpatterns = [
    path('', include('search.urls')),
    
]