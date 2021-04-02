from tkinter import *
from PIL import ImageTk, Image


# key down function
def click():
    entered_text = entry_box.get()  # collects the text from the text box
    output.delete(0.0, END)
    output.insert(END, entered_text)


# Exit function
def close_window():
    window.destroy()
    exit()


# Main function
window = Tk()
window.title("My first GUI")
window.configure(background="black")
# window.geometry('400x200')


# Photo
my_img = ImageTk.PhotoImage(Image.open("../images/kids_playing.jpg"))
my_label = Label(image=my_img)
my_label.grid(row=1, column=0, sticky=W)
# photo1  PhotoImage(file="kids_playing.jpg")
# Label(window, image=photo1, bg="black").grid(row=0, column=0, sticky=W)


# Create Label
Label(window, text="Enter text here: ", fg='blue', bg='black', font='none 20 bold').grid(row=1, column=0, sticky=W)


# Create a text entry box
entry_box = Entry(window, width=20, bg="white")
entry_box.grid(row=2, column=0, sticky=W)


# Add a submit button
Button(window, text="SUBMIT", width=6, command=click).grid(row=3, column=0, sticky=W)


# Create another label
Label(window, text="\nOutput: ", bg='black', fg='white', font="none 12 bold").grid(row=4, column=0, sticky=W)

# Create a output text box
output = Text(window, width=75, height=6, wrap=WORD, background='white')
output.grid(row=5, column=0, columnspan=2, sticky=W)

# Exit Button
Button(window, text="Exit", width=14, command=close_window).grid(row=7, column=0, sticky=W)

window.mainloop()
