import io

from PIL import Image
import requests


def load_image_from_url(url):
    try:
        # Send a GET request to fetch the image
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        # Load the image into Pillow
        image = Image.open(io.BytesIO(response.content))

        # Check if image format is supported
        if image.format not in ['JPEG', 'PNG']:
            raise ValueError(f"Unsupported image format: {image.format}")

        return image
    except requests.exceptions.RequestException as e:
        print(f"Error fetching image: {e}")
    except Exception as e:
        print(f"Error loading image: {e}")

    try:
        return Image.open(url)
    except:
        pass
    return None



url_images = ["https://www.youcubed.org/wp-content/uploads/2017/03/block-tower.jpg", "./block-tower.jpg"]
images = []
for url in url_images:
    images.append(
        load_image_from_url(url)#Image.open(requests.get(url).raw)
    )