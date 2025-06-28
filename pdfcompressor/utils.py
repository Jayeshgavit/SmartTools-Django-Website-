import fitz  # PyMuPDF
import tempfile
from PIL import Image
import os

def compress_pdf(input_path, output_path):
    try:
        doc = fitz.open(input_path)
        doc.set_metadata({})  # Strip metadata

        for page_index in range(len(doc)):
            image_list = doc[page_index].get_images(full=True)
            for img in image_list:
                xref = img[0]

                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                ext = base_image["ext"]

                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp_img:
                    tmp_img.write(image_bytes)
                    tmp_img_path = tmp_img.name

                # Resize the image
                with Image.open(tmp_img_path) as pil_img:
                    width, height = pil_img.size
                    new_size = (int(width * 0.4), int(height * 0.4))  # Reduce dimensions
                    pil_img = pil_img.convert("RGB")
                    pil_img_resized = pil_img.resize(new_size, Image.LANCZOS)

                    compressed_path = tmp_img_path.replace(f".{ext}", "_compressed.jpg")
                    pil_img_resized.save(compressed_path, "JPEG", quality=30, optimize=True)

                # Replace image (safe zone: insert on rect, remove xref)
                page_rect = doc[page_index].rect
                doc[page_index].insert_image(page_rect, filename=compressed_path)
                doc[page_index].delete_image(xref)

                os.remove(tmp_img_path)
                os.remove(compressed_path)

        doc.save(output_path, garbage=4, deflate=True, clean=True)
        doc.close()

        return True, None

    except Exception as e:
        return False, f"❌ Compression failed: {str(e)}"
