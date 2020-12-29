import hashlib
from Cryptodome.Cipher import AES
from base64 import b64encode, b64decode
from Cryptodome.Random import get_random_bytes


KEY = "The Knotty Chat1"
IV = get_random_bytes(16)


class CipherBlockChainingAES:
    def __init__(self):
        self.block_size = AES.block_size  # 16 bytes = 128 bits
        self.key = hashlib.sha256(KEY.encode()).digest()

        # Generate cipher
        self.cipher = AES.new(self.key, AES.MODE_ECB)

    @staticmethod
    def xor(b1, b2):
        return bytes(a ^ b for (a, b) in zip(b1, b2))

    def add_padding(self, plaintext):
        # Uses Public-Key Cryptography Standards #7
        data_blocks = []
        padding_size = (self.block_size - len(plaintext)) % self.block_size

        if padding_size == 0:
            padding_size = self.block_size

        padding_byte = chr(padding_size).encode()
        padding = (padding_byte * padding_size)
        data = plaintext.encode() + padding

        # Split the padded plaintext into blocks of 16 bytes
        for i in range(int(len(data) / self.block_size)):
            data_blocks.append(data[i * self.block_size:(i + 1) * self.block_size])

        return data_blocks

    @staticmethod
    def remove_padding(data_blocks):  # Function is flawed, use existing library instead
        data = bytearray(b"".join(data_blocks))
        padding_byte = data[-1:]
        padding_size = ord(padding_byte)

        for i in range(padding_size):
            if i == 0:
                continue

            if bytes(data[(-1 - i):-i]) != padding_byte:
                raise ValueError

        return data[:-padding_size]

    def encrypt(self, plaintext):
        cipher_blocks = []
        # Ensures that the plaintext size is a multiple of the buffer size (16 bytes)
        padded_plaintext = self.add_padding(plaintext)

        # Append IV as the first block and encrypts each subsequent block in the list
        for i, block in enumerate(padded_plaintext):
            if i == 0:
                cipher_blocks.append(IV)
                cipher_blocks.append(self.cipher.encrypt(self.xor(IV, block)))

            else:
                cipher_blocks.append(self.cipher.encrypt(self.xor(cipher_blocks[i], block)))

        return b64encode(b"".join(cipher_blocks)).decode()  # Decode back to string

    def decrypt(self, ciphertext):
        cipher_blocks = []
        data_blocks = []
        ciphertext = b64decode(ciphertext)

        # Split the cipher text into blocks of 16 bytes
        for i in range(int(len(ciphertext) / self.block_size)):
            cipher_blocks.append(ciphertext[i * self.block_size:(i + 1) * self.block_size])

        for i, block in enumerate(cipher_blocks):
            if i == 0:
                continue

            # Decrypt each block
            data_blocks.append(self.xor(self.cipher.decrypt(block), cipher_blocks[i - 1]))

        return self.remove_padding(data_blocks).decode("utf-8", "backslashreplace")

        # if plaintext:
        #     return plaintext.decode("utf-8", "backslashreplace")
        # else:
        #     return 0


# Test function

if __name__ == '__main__':
    AES_cipher = CipherBlockChainingAES()
    message = AES_cipher.encrypt("This is a secret that no one should know")
    print(f"Encrypted Message: {message}")
    ct = b64decode(message)

    text = AES_cipher.decrypt(message)
    print(f"Decrypted Plain Text Message: {text}")
