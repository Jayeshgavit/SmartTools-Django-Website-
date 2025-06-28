import os
import uuid
from django.shortcuts import render
from django.http import FileResponse
from django.conf import settings
from .utils import compress_pdf

def pdf_compress_view(request):
    if request.method == 'POST' and request.FILES.get('pdf_file'):
        uploaded_pdf = request.FILES['pdf_file']
        if not uploaded_pdf.name.lower().endswith('.pdf'):
            return render(request, 'pdfcompressor/pdf_compressor.html', {
                'error': '❌ Please upload a valid PDF file.'
            })

        # Define paths
        temp_input_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
        output_dir = os.path.join(settings.MEDIA_ROOT, 'compressed')
        os.makedirs(temp_input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        # Save uploaded file
        temp_input_path = os.path.join(temp_input_dir, f"{uuid.uuid4()}_{uploaded_pdf.name}")
        with open(temp_input_path, 'wb+') as dest:
            for chunk in uploaded_pdf.chunks():
                dest.write(chunk)

        # Compress the PDF using utils
        output_path = os.path.join(output_dir, f"compressed_{os.path.basename(temp_input_path)}")
        success, error = compress_pdf(temp_input_path, output_path)

        if success:
            return FileResponse(open(output_path, 'rb'), as_attachment=True, filename=os.path.basename(output_path))
        else:
            return render(request, 'pdfcompressor/pdf_compressor.html', {
                'error': error
            })

    return render(request, 'pdfcompressor/pdf_compressor.html')
