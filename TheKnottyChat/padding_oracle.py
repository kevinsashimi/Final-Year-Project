import time

from aes_cbc import CipherBlockChainingAES
from base64 import b64encode, b64decode


BLOCK_SIZE = 16


class PaddingOracle:
    def __init__(self, ciphertext):
        self.ciphertext = b64decode(ciphertext)
        self.decrypted_text = ''

        # Split ciphertext into blocks of  16 bytes each
        cipher_blocks = [self.ciphertext[i:i + BLOCK_SIZE] for i in range(0, len(self.ciphertext), BLOCK_SIZE)]
        print(f"Ciphertext after base64 decode: {cipher_blocks}")
        print(f"IV found: {cipher_blocks[0]}")

        current_block = len(cipher_blocks) - 1
        print(f"Total number of blocks in ciphertext: {current_block + 1}\n")
        print("Staring padding oracle attack...\n")
        print("Getting padding size from last block...")

        while current_block > 0:
            padding_length = self.get_padding(cipher_blocks, current_block)
            print(f"Padding length: {padding_length}")
            message_length = BLOCK_SIZE - padding_length
            print(f"Message length: {message_length}")

            # Get previous block to modify
            block_prime = bytearray(cipher_blocks[current_block - 1])

            while message_length > 0:
                print(f"Decrypting current block: {current_block}...")
                print(f"Message length to decrypt: {message_length}")
                # Start from the back (Index 15)
                byte_position = BLOCK_SIZE - 1
                print(f"Current byte position: {byte_position}")
                predicted_padding = (padding_length + 1)
                print(f"Setting predicted padding to: {predicted_padding}")

                while byte_position >= message_length:
                    block_prime[byte_position] = block_prime[byte_position] ^ padding_length ^ predicted_padding
                    byte_position -= 1

                for guessed_byte in range(256):
                    block_prime[byte_position] = guessed_byte
                    modified_block = b64encode(bytes(block_prime) + cipher_blocks[current_block]).decode()

                    try:
                        cipher.decrypt(modified_block)
                        print(f"Guessed byte: {guessed_byte}")
                        current_byte = cipher_blocks[current_block - 1][byte_position]
                        decrypted_byte = chr(predicted_padding ^ guessed_byte ^ current_byte)
                        print(f"Decrypted byte: {decrypted_byte}\n")
                        self.decrypted_text += decrypted_byte
                        break

                    except ValueError:
                        pass

                padding_length += 1
                message_length -= 1

            current_block -= 1

        self.decrypted_text = self.decrypted_text[::-1]

    @staticmethod
    def get_padding(cipher_blocks, current_block):
        byte_position = 0

        # If the current block is not the last block, then there is no padding
        if current_block < len(cipher_blocks) - 1:
            byte_position = BLOCK_SIZE

        else:  # Get padding from last block
            # Where block prime is the modified version of the previous block
            block_prime = bytearray(cipher_blocks[current_block - 1])
            print(f"Block prime: {block_prime}")

            for byte in block_prime:
                print(f"Byte: {byte}")
                print(f"BlockP Position: {block_prime[byte_position]}")
                # Modify the byte to check for padding error, byte - 1 to prevent value out of range if byte is 255
                block_prime[byte_position] = byte - 1 if block_prime[byte_position] == 255 else byte + 1

                modified_block = b64encode(bytes(block_prime) + cipher_blocks[current_block]).decode()

                try:
                    cipher.decrypt(modified_block)

                except ValueError:
                    print("Padding error detected!")
                    print("Padding size found!")
                    print(f"Padding size is: {BLOCK_SIZE - byte_position}\n")
                    break

                byte_position += 1

        return BLOCK_SIZE - byte_position  # Returns the padding length


if __name__ == '__main__':
    cipher = CipherBlockChainingAES()

    while True:
        print()
        print("1) Perform Padding Oracle Attack")
        print("0) Exit")
        print()
        choice = input("> ")

        if choice == '0':
            print("Exiting...")
            break

        elif choice == '1':
            ct = input("Enter ciphertext to decrypt: ")
            if not ct:
                print("Nothing was entered, returning...")
                continue

            start_time = time.perf_counter()
            try:
                oracle = PaddingOracle(ct)
                print(f"Decrypted text: {oracle.decrypted_text}")

            except Exception as e:
                print("\nDecryption failed")
                print(e)

            finally:
                print(f"Elapsed Time: {(time.perf_counter() - start_time):0.6f}s")

        else:
            print("Invalid choice, please choose either '1' or '0'")
