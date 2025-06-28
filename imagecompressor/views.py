from django.shortcuts import render
from django.http import HttpResponse
from PIL import Image
import io

def image_compress_view(request):
    if request.method == 'POST' and request.FILES.get('image'):
        uploaded_image = request.FILES['image']
        compression_level = request.POST.get('level', 'medium')  # Default to medium

        image = Image.open(uploaded_image)

        # Convert to RGB if not JPEG compatible
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        # Choose quality based on user selection
        quality_map = {
            "low": 20,
            "medium": 50,
            "high": 85
        }
        quality = quality_map.get(compression_level, 50)

        # Always save as JPEG for best compression
        img_io = io.BytesIO()
        image.save(img_io, format='JPEG', quality=quality, optimize=True)
        img_io.seek(0)

        # Return compressed file
        response = HttpResponse(img_io, content_type='image/jpeg')
        response['Content-Disposition'] = f'attachment; filename="compressed_{uploaded_image.name.split(".")[0]}.jpg"'
        return response

    return render(request, 'imagecompressor/image_compress.html')
