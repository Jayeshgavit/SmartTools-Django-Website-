
import os
import uuid
from django.shortcuts import render
from django.http import FileResponse
from .utils import compress_pdf
from django.core.files.storage import default_storage

def pdf_compress_view(request):
    context = {}

    if request.method == 'POST':
        pdf = request.FILES.get('pdf_file')
        level = request.POST.get('compression_level')

        if not pdf:
            context['error'] = "Please upload a PDF file."
            return render(request, 'pdfcompressor/pdf_compressor.html', context)

        # Save uploaded file temporarily
        original_name = f"{uuid.uuid4()}_{pdf.name}"
        original_path = os.path.join('media/temp', original_name)
        default_storage.save(original_path, pdf)

        # Set compressed file path
        compressed_name = f"compressed_{original_name}"
        compressed_path = os.path.join('media/compressed', compressed_name)
        os.makedirs(os.path.dirname(compressed_path), exist_ok=True)

        # Compress PDF
        success, error = compress_pdf(original_path, compressed_path, level)

        # Delete uploaded file after compression
        if os.path.exists(original_path):
            os.remove(original_path)

        if not success:
            context['error'] = f"❌ Compression failed: {error}"
            return render(request, 'pdfcompressor/pdf_compressor.html', context)

        # Serve and cleanup after
        response = FileResponse(open(compressed_path, 'rb'), as_attachment=True, filename=f"compressed_{pdf.name}")

        def cleanup_file(file_path):
            def callback():
                if os.path.exists(file_path):
                    os.remove(file_path)
            return callback

        # Monkey-patch close to cleanup
        original_close = response.close

        def custom_close():
            original_close()
            cleanup_file(compressed_path)()

        response.close = custom_close

        return response

    return render(request, 'pdfcompressor/pdf_compressor.html', context)



from django.urls import path
from . import views

urlpatterns = [
    path('', views.pdf_compress_view, name='pdf_compress'),
]



urils.py

# import subprocess
# import os
# import uuid

# def compress_pdf(input_path, output_path, level="ebook"):
#     quality_map = {
#         "low": "/screen",
#         "medium": "/ebook",
#         "high": "/printer"
#     }
#     gs_quality = quality_map.get(level, "/ebook")

#     try:
#         cmd = [
#             "gswin64c",  # or "gs" if on Linux/macOS
#             "-sDEVICE=pdfwrite",
#             "-dCompatibilityLevel=1.4",
#             f"-dPDFSETTINGS={gs_quality}",
#             "-dNOPAUSE",
#             "-dQUIET",
#             "-dBATCH",
#             f"-sOutputFile={output_path}",
#             input_path
#         ]

#         subprocess.run(cmd, check=True)
#         return True, None
#     except Exception as e:
#         return False, str(e)


import subprocess
import os

def compress_pdf(input_path, output_path, level="medium"):
    quality_map = {
        "low": "/screen",
        "medium": "/ebook",
        "high": "/printer"
    }
    gs_quality = quality_map.get(level, "/ebook")

    try:
        cmd = [
            "gswin64c",  # use "gs" on Linux/macOS
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            f"-dPDFSETTINGS={gs_quality}",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            f"-sOutputFile={output_path}",
            input_path
        ]

        subprocess.run(cmd, check=True)

        # Optional: Compare file sizes
        original_size = os.path.getsize(input_path)
        compressed_size = os.path.getsize(output_path)

        print(f"Original: {original_size} bytes, Compressed: {compressed_size} bytes")

        return True, None
    except Exception as e:
        return False, str(e)




{% extends 'base.html' %}
{% load static %}

{% block content %}
<link rel="stylesheet" href="{% static 'pdfcompressor/pdfcompressor.css' %}">

<!-- 💠 Main Layout Wrapper -->
<section class="compressor-wrapper">

  <!-- ⬅️ Left Ad -->
  <div class="ad-slot left-ad">
    <p>Ad Left</p>
  </div>

  <!-- 🔧 PDF Compressor Main Box -->
  <div class="compressor-section">
    <div class="compressor-container">

      <h2>📄 Compress Your PDF</h2>

      <!-- 🚀 Upload Form -->
      <form method="post" enctype="multipart/form-data" id="pdfForm" target="hiddenIframe">
        {% csrf_token %}

        <div class="file-upload-group">
          <input type="file" name="pdf_file" accept=".pdf" required class="upload-input" id="pdfInput">
          <button type="button" id="clearBtn" class="clear-btn" style="display: none;">❌</button>
        </div>

        <label for="compression_level" class="compress-label">Choose Compression Level:</label>
        <select name="compression_level" id="compression_level" required class="compression-select">
          <option value="low">🔻 Low Quality (High Compression)</option>
          <option value="medium">⚖️ Medium Quality</option>
          <option value="high">🔺 High Quality (Low Compression)</option>
        </select>

        <button type="submit" class="compress-btn">Compress PDF</button>

        <!-- ⏳ Loader -->
        <div id="loadingSpinner" class="loading-spinner" style="display: none;">
          <div class="spinner"></div>
          <p>Compressing your PDF, please wait...</p>
        </div>
      </form>

      <!-- 🔽 Hidden Iframe for Download -->
      <iframe name="hiddenIframe" style="display:none;"></iframe>

      <!-- ℹ️ Tool Instructions -->
      <div class="tool-info">
        <h3>📘 How to Use:</h3>
        <ol>
          <li>Select your PDF file (Max size: 10MB)</li>
          <li>Choose your preferred compression level</li>
          <li>Click "Compress PDF" to download the optimized file</li>
          <li>You can cancel and upload another file if needed</li>
        </ol>
      </div>

    </div>
  </div>

  <!-- ➡️ Right Ad -->
  <div class="ad-slot right-ad">
    <p>Ad Right</p>
  </div>

</section>

<!-- 🔻 Full-width Bottom Ad Slot -->
<div class="bottom-banner-ad">
  <p>Place for Adsense or promotional banner</p>
</div>

<!-- ✅ JavaScript Logic -->
<script>
  const form = document.getElementById('pdfForm');
  const spinner = document.getElementById('loadingSpinner');
  const input = document.getElementById('pdfInput');
  const clearBtn = document.getElementById('clearBtn');

  // 📂 Show clear button when file is selected
  input.addEventListener('change', () => {
    if (input.files.length > 0) {
      clearBtn.style.display = 'inline-block';
    }
  });

  // ❌ Clear file input manually
  clearBtn.addEventListener('click', () => {
    input.value = '';
    clearBtn.style.display = 'none';
  });

  // 🚀 On form submit: show spinner & auto-clear after 3s
  form.addEventListener('submit', () => {
    spinner.style.display = 'block';

    setTimeout(() => {
      spinner.style.display = 'none';
      input.value = '';
      clearBtn.style.display = 'none';
    }, 3000); // ⏳ Adjust delay as needed
  });

  // 🔄 On page refresh or unload: reset inputs and hide spinner
  window.addEventListener('beforeunload', () => {
    spinner.style.display = 'none';
    input.value = '';
    clearBtn.style.display = 'none';
  });
</script>

{% endblock %}
