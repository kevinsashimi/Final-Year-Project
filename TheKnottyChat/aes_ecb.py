from PIL import Image
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
from Cryptodome.Util.Padding import pad


key = get_random_bytes(16)
cipher = AES.new(key, AES.MODE_ECB)

filename = "top_secret.png"
output_filename = "encrypted_image"
FORMAT = "png"


# Maps the RGB
def rgb_conversion(data):
    r, g, b = tuple(map(lambda d: [data[i] for i in range(0, len(data)) if i % 3 == d], [0, 1, 2]))
    pixels = tuple(zip(r, g, b))
    return pixels


def process_image(file):
    # Opens image and converts it to RGB format for PIL
    image_file = Image.open(file)
    data_bytes = image_file.convert("RGB").tobytes()
    original_size = len(data_bytes)

    ciphertext = cipher.encrypt(pad(data_bytes, AES.block_size))[:original_size]

    data = rgb_conversion(ciphertext)

    # Create a new PIL Image object and save the old image data into the new image.
    encrypted_image = Image.new(image_file.mode, image_file.size)
    encrypted_image.putdata(data)

    # Save image
    encrypted_image.save(output_filename+"."+FORMAT)


if __name__ == '__main__':
    process_image(filename)
    print("\nImage file AES ECB encryption completed")
