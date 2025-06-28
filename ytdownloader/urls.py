from django.urls import path
from .views import youtube_downloader_view

urlpatterns = [
    path('', youtube_downloader_view, name='youtube_downloader'),
]


