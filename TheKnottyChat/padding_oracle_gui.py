import time

from tkinter import *
from aes_cbc import CipherBlockChainingAES
from base64 import b64encode, b64decode


# GUI Code
########################################################################################################################
"""
Command to convert python file to executable:
pyinstaller --onefile --icon=hacker.ico padding_oracle_gui.py --noconsol

Extract the executable file from the dist folder
The dist, build, .idea folders and .spec file may be removed thereafter
"""


def submit():
    entered_text = entry_box.get()  # collects the text from the text box
    pt_output.delete(1.0, END)
    output_dt.delete(1.0, END)
    # Decryption here
    if not entered_text:
        pt_output.insert(END, "Nothing was entered, try again...")

    else:
        str_time = time.perf_counter()
        try:
            pad_oracle = PaddingOracle(entered_text)
            pt = pad_oracle.decrypted_text
            if pt:
                pt_output.insert(END, pt)

            else:
                pt_output.insert(END, "Decryption error")

        except Exception as err:
            pt_output.insert(END, "Decryption failed")
            pt_output.insert(END, f"\nError: {err}")

        finally:
            pt_output.insert(END, f"\n\nElapsed Time: {(time.perf_counter() - str_time):0.6f}s")


def clear():
    entry_box.delete(0, END)
    pt_output.delete(1.0, END)
    output_dt.delete(1.0, END)


def close_window():
    main_window.destroy()
    exit()


# Window Properties
main_window = Tk()
main_window.title("Padding Oracle Demo")

w = 1000  # Width for the program window
h = 1000  # Height for the program window
# Get screen width and height
ws = main_window.winfo_screenwidth()  # Width of the screen
hs = main_window.winfo_screenheight()  # Height of the screen
# Calculate x and y coordinates for the main_window
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)
# Set the popup window to open in the middle of the user's screen
main_window.geometry('%dx%d+%d+%d' % (w, h, x, y))

main_window.configure(background='light grey')
main_window.resizable(width=False, height=True)
# Add icon
main_window.iconbitmap("C:/Users/User/PycharmProjects/TheKnottyChat/images/hacker.ico")

# Title
title = Label(main_window, text="Padding Oracle Attack",
              bg='light grey',
              font="none, 60 bold")
title.pack(padx=50, pady=50)

# Input
prompt = Label(main_window, text="Enter ciphertext to decrypt",
               bg='light grey',
               font='arial 20')
prompt.pack()

entry_box = Entry(main_window, width=50,
                  borderwidth=5,
                  bg="white",
                  font="arial 20")
entry_box.pack()

frame_top = Frame(main_window, bg="light grey")
frame_top.pack(pady=(0, 20))

# Submit button
submit_btn = Button(frame_top,
                    text="Submit",
                    width=6,
                    font="arial 20 bold",
                    command=submit)
submit_btn.pack(side=LEFT)

# Clear button
clear_btn = Button(frame_top,
                   text="Clear",
                   width=6,
                   font="arial 20 bold",
                   command=clear)
clear_btn.pack(side=LEFT, padx=5)

# Close button
close_btn = Button(frame_top,
                   text="Close",
                   width=6,
                   font="arial 20 bold",
                   command=close_window)
close_btn.pack(side=LEFT)

# Plaintext Output
frame_pt = LabelFrame(main_window, text="Recovered Plaintext", font="arial 20 bold")
frame_pt.pack(pady=(0, 20))
pt_output = Text(frame_pt, width=50,
                 height=5,
                 borderwidth=5,
                 bg="white",
                 font=('Arial', 20),
                 wrap=WORD)
pt_output.pack()

# Output Details
frame_od = LabelFrame(main_window, text="Output Details", font="arial 20 bold")
frame_od.pack(pady=(0, 20))
output_dt = Text(frame_od, width=50,
                 height=11,
                 borderwidth=5,
                 bg="white",
                 font=('Arial', 20),
                 wrap=WORD)
output_dt.pack(side=LEFT, fill=Y)

# Scrollbar
scrollbar = Scrollbar(frame_od, command=output_dt.yview)
scrollbar.pack(side=RIGHT, fill=Y)
output_dt.configure(yscrollcommand=scrollbar.set)
scrollbar.config(command=output_dt.yview)


# Main Code
########################################################################################################################
BLOCK_SIZE = 16


class PaddingOracle:
    def __init__(self, ciphertext):
        self.ciphertext = b64decode(ciphertext)
        self.decrypted_text = ''

        # Split ciphertext into blocks of  16 bytes each
        cipher_blocks = [self.ciphertext[i:i + BLOCK_SIZE] for i in range(0, len(self.ciphertext), BLOCK_SIZE)]
        output_dt.insert(END, f"Ciphertext after base64 decode: {cipher_blocks}")
        output_dt.insert(END, f"\n\nIV found: {cipher_blocks[0]}")

        current_block = len(cipher_blocks) - 1
        output_dt.insert(END, f"\nTotal number of blocks in ciphertext: {current_block + 1}\n")
        output_dt.insert(END, "\nStaring padding oracle attack...\n")
        output_dt.insert(END, "\nGetting padding size from last block...")

        while current_block > 0:
            padding_length = self.get_padding(cipher_blocks, current_block)
            output_dt.insert(END, f"\nPadding length: {padding_length}")
            message_length = BLOCK_SIZE - padding_length
            output_dt.insert(END, f"\nMessage length: {message_length}")

            # Get previous block to modify
            block_prime = bytearray(cipher_blocks[current_block - 1])

            while message_length > 0:
                output_dt.insert(END, f"\nDecrypting current block: {current_block}...")
                output_dt.insert(END, f"\nMessage length to decrypt: {message_length}")
                # Start from the back (Index 15)
                byte_position = BLOCK_SIZE - 1
                output_dt.insert(END, f"\nCurrent byte position: {byte_position}")
                predicted_padding = (padding_length + 1)
                output_dt.insert(END, f"\nSetting predicted padding to: {predicted_padding}")

                while byte_position >= message_length:
                    block_prime[byte_position] = block_prime[byte_position] ^ padding_length ^ predicted_padding
                    byte_position -= 1

                for guessed_byte in range(256):
                    block_prime[byte_position] = guessed_byte
                    modified_block = b64encode(bytes(block_prime) + cipher_blocks[current_block]).decode()

                    try:
                        cipher.decrypt(modified_block)
                        output_dt.insert(END, f"\nGuessed byte: {guessed_byte}")
                        current_byte = cipher_blocks[current_block - 1][byte_position]
                        decrypted_byte = chr(predicted_padding ^ guessed_byte ^ current_byte)
                        output_dt.insert(END, f"\nDecrypted byte: {decrypted_byte}")
                        output_dt.insert(END, f"\n{48 * '-'}\n")
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
            output_dt.insert(END, f"\nBlock prime: {block_prime}")

            for byte in block_prime:
                output_dt.insert(END, f"\nByte: {byte}")
                output_dt.insert(END, f"\nBlockP Position: {block_prime[byte_position]}")
                # Modify the byte to check for padding error, byte - 1 to prevent value out of range if byte is 255
                block_prime[byte_position] = byte - 1 if block_prime[byte_position] == 255 else byte + 1

                modified_block = b64encode(bytes(block_prime) + cipher_blocks[current_block]).decode()

                try:
                    cipher.decrypt(modified_block)

                except ValueError:
                    output_dt.insert(END, "\nPadding error detected!")
                    output_dt.insert(END, "\nPadding size found!")
                    output_dt.insert(END, f"\nPadding size is: {BLOCK_SIZE - byte_position}\n")
                    break

                byte_position += 1

        return BLOCK_SIZE - byte_position  # Returns the padding length


if __name__ == '__main__':
    cipher = CipherBlockChainingAES()
    # Start GUI main loop
    main_window.mainloop()
