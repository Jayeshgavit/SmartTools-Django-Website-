# from django.urls import path
# from .views import pdf_compress_view

# urlpatterns = [
#     path('', pdf_compress_view, name='pdf_compress'),
# ]

from django.conf import settings
from django.conf.urls.static import static

# pdfcompressor/urls.py

from django.urls import path
from .views import pdf_compress_view

urlpatterns = [
    path('', pdf_compress_view, name='pdf_compress'),  # ✅ Name is important!
]
