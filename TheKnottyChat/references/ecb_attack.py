import hashlib

from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
from Cryptodome.Util.Padding import pad, unpad
from base64 import b64encode, b64decode


KEY = b'This chat is bad'
ecb_cipher = AES.new(KEY, AES.MODE_ECB)
FORMAT = 'utf-8'
BLOCK_SIZE = 16


if __name__ == '__main__':
    print("Type 'exit' to quit")
    while True:
        plaintext = input("Please enter your plaintext: ")
        if plaintext == 'exit':
            break

        ciphertext = ecb_cipher.encrypt(pad(plaintext.encode(FORMAT), BLOCK_SIZE))
        print(pad(plaintext.encode(FORMAT), BLOCK_SIZE))
        print(f"Ciphertext: {ciphertext.hex()}")
