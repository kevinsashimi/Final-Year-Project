from PIL import Image
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
from Cryptodome.Util.Padding import pad


IMG_FILE = "images/top_secret.png"
# IMG_FILE = "images/linux_penguin.png"
filename_encrypted_ecb = "top_secret_encrypted_ecb"
filename_encrypted_cbc = "top_secret_encrypted_cbc"

KEY = get_random_bytes(16)
FORMAT = "png"
BLOCK_SIZE = 16


# AES encrypted plaintext space is an integer multiple of 16, which cannot be divided evenly, so it needs to be filled
# In the corresponding ascii, "\x00" means 0x00, the specific value is NULL, b means that it is expressed in bytes


# Map the image data to RGB
def trans_format_rgb(data):
    # tuple: Immutable, ensure that data is not lost
    red, green, blue = tuple(map(lambda e: [data[i] for i in range(0, len(data)) if i % 3 == e], [0, 1, 2]))
    pixels = tuple(zip(red, green, blue))
    return pixels


def encrypt_image_ecb(filename):
    # Open the picture and convert it to RGB image
    image_original = Image.open(filename)
    # Convert image data into pixel value bytes
    value_vector = image_original.convert("RGB").tobytes()

    img_length = len(value_vector)

    # Map the pixel value of the filled and encrypted data
    value_encrypt = trans_format_rgb(aes_ecb_encrypt(KEY, pad(value_vector, BLOCK_SIZE))[:img_length])

    # Create a new object, store the corresponding value
    image_encrypted = Image.new(image_original.mode, image_original.size)
    image_encrypted.putdata(value_encrypt)

    # Save the object as an image in the corresponding format
    image_encrypted.save(filename_encrypted_ecb + "." + FORMAT, FORMAT)


def encrypt_image_cbc(filename):
    # Open the bmp picture and convert it to RGB image
    image_original = Image.open(filename)
    value_vector = image_original.convert("RGB").tobytes()

    # Convert image data to pixel value bytes
    img_length = len(value_vector)

    # Perform pixel value mapping on the filled and encrypted data
    value_encrypt = trans_format_rgb(aes_cbc_encrypt(KEY, pad(value_vector, BLOCK_SIZE))[:img_length])

    # Create a new object, store the corresponding value
    image_encrypted = Image.new(image_original.mode, image_original.size)
    image_encrypted.putdata(value_encrypt)

    # Save the object as an image in the corresponding format
    image_encrypted.save(filename_encrypted_cbc + "." + FORMAT, FORMAT)


# CBC encryption
def aes_cbc_encrypt(key, data, mode=AES.MODE_CBC):
    # IV is a random value
    iv = get_random_bytes(16)
    aes = AES.new(key, mode, iv)
    new_data = aes.encrypt(data)
    return new_data


# ECB encryption
def aes_ecb_encrypt(key, data, mode=AES.MODE_ECB):
    # The default mode is ECB encryption
    aes = AES.new(key, mode)
    new_data = aes.encrypt(data)
    return new_data


if __name__ == '__main__':
    encrypt_image_cbc(IMG_FILE)
    encrypt_image_ecb(IMG_FILE)
