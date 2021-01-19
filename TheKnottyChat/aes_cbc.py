import hashlib

from Cryptodome.Random import get_random_bytes
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
from base64 import b64encode, b64decode


# Key can be of any size, does not necessarily have to be 16 bytes long
KEY = "This chat is knotty!"
FORMAT = "utf-8"


class CipherBlockChainingAES:
    def __init__(self):
        self.block_size = AES.block_size  # 16 bytes = 128 bits
        self.key = hashlib.sha256(KEY.encode(FORMAT)).digest()

    def encrypt(self, plaintext):
        # Generate Initialization Vector
        iv = get_random_bytes(16)

        # Generate cipher
        cipher = AES.new(self.key, AES.MODE_CBC, iv)

        # Padding uses Public-Key Cryptography Standards #7
        return b64encode(iv + cipher.encrypt(pad(plaintext.encode(FORMAT), self.block_size)))

    def decrypt(self, ciphertext):
        ciphertext = b64decode(ciphertext)
        iv = ciphertext[:self.block_size]
        try:
            cipher = AES.new(self.key, AES.MODE_CBC, iv)

        except ValueError:
            return

        data = cipher.decrypt(ciphertext[self.block_size:])

        try:
            return unpad(data, 16)

        except ValueError:
            # Error raised if padding does not match
            raise ValueError


# Test function
if __name__ == '__main__':
    aes_cipher = CipherBlockChainingAES()
    message = "This is a secret that no one should know about"
    encrypted_message = aes_cipher.encrypt(message)
    print(f"Ciphertext: {encrypted_message}")
    decrypted_message = aes_cipher.decrypt(encrypted_message)
    print(f"Deciphered message: {decrypted_message}")
