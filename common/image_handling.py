# Helper function to hash image content
import hashlib
import os

UPLOAD_FOLDER = './uploads'

def hash_image(image_content):
    return hashlib.sha256(image_content).hexdigest()

# Save image to the server and return its hash
def save_image(image_file, provided_hash=False):
    image_content = image_file.read()

    if provided_hash:
        image_hash = provided_hash
    else:
        image_hash = hash_image(image_content)

    image_path = os.path.join(UPLOAD_FOLDER, image_hash)

    if not os.path.exists(image_path):
        # Save the image if it doesn't exist yet
        with open(image_path, 'wb') as f:
            f.write(image_content)

    return image_hash
