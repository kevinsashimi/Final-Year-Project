import hashlib
import time

from PIL import Image
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
from Cryptodome.Util.Padding import pad, unpad
from base64 import b64encode, b64decode


# Server key
KEY = "This chat is knotty!"

# Image demo key
KEY_DEMO = get_random_bytes(16)
cipher_demo = AES.new(KEY_DEMO, AES.MODE_ECB)

filename = "images/top_secret.png"
output_filename = "encrypted_image"
FORMAT = "utf-8"
IMG_FORMAT = "png"


class ElectronicCodeBookAES:
    def __init__(self):
        self.block_size = AES.block_size  # 16 bytes = 128 bits
        self.key = hashlib.sha256(KEY.encode(FORMAT)).digest()

    def encrypt(self, plaintext):
        # Generate AES ECB cipher
        cipher_ecb = AES.new(self.key, AES.MODE_ECB)
        return b64encode(cipher_ecb.encrypt(pad(plaintext.encode(FORMAT), self.block_size)))

    def decrypt(self, ciphertext):
        ciphertext = b64decode(ciphertext)
        try:
            cipher_ecb = AES.new(self.key, AES.MODE_ECB)

        except ValueError:
            return

        data = cipher_ecb.decrypt(ciphertext)

        try:
            return unpad(data, 16)

        except ValueError:
            # Error raised if padding does not match
            raise ValueError


# Maps the RGB
def rgb_conversion(data):
    r, g, b = tuple(map(lambda d: [data[i] for i in range(0, len(data)) if i % 3 == d], [0, 1, 2]))
    pixels = tuple(zip(r, g, b))
    return pixels


# Process the encrypted image file
def process_image(file):
    # Opens image and converts it to RGB format for PIL
    image_file = Image.open(file)
    data_bytes = image_file.convert("RGB").tobytes()
    original_size = len(data_bytes)

    # Encrypts the image
    print("Encrypting image data...")
    ciphertext = cipher_demo.encrypt(pad(data_bytes, AES.block_size))[:original_size]

    print("Mapping ciphertext to RGB...")
    data = rgb_conversion(ciphertext)

    # Create a new PIL Image object and save the old image data into the new image.
    print(f"Saving new image as: {output_filename}.{IMG_FORMAT}")
    encrypted_image = Image.new(image_file.mode, image_file.size)
    encrypted_image.putdata(data)

    # Save image
    encrypted_image.save(output_filename+"."+IMG_FORMAT)


if __name__ == '__main__':
    print("""
    ****************************************************************************
    *ADVANCED ENCRYPTION STANDARD: ELECTRONIC CODE BOOK MODE DEMO ON IMAGE FILE*
    ****************************************************************************
    """)
    print("Processing image file...")
    start_time = time.perf_counter()
    process_image(filename)
    print("AES ECB encryption to image file completed")
    print(f"\nElapsed Time: {(time.perf_counter() - start_time):0.6f}s")
