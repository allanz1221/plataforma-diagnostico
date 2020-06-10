import base64
import io

from PIL import Image


def convert_to_base64(request_file):
    image = Image.open(request_file)
    blob = io.BytesIO()
    image.save(blob, 'JPEG')
    contents = blob.getvalue()
    contents_base64 = base64.b64encode(contents)
    blob.close()
    image_data = 'data:image/webp;base64,' + contents_base64.decode('utf-8')
    return image_data
