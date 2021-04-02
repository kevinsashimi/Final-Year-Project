from tkinter import *
# In tkinter, every object created is treated as a widget
from PIL import ImageTk, Image

# Root widget
root = Tk()
root.title("GUI Test")
root.iconbitmap("../images/cat_sashimi.ico")  # Add icon

my_img = ImageTk.PhotoImage(Image.open("../images/kids_playing.jpg"))
my_label = Label(image=my_img)
my_label.pack()

# Exit button
button_quit = Button(root, text="Exit Program", command=root.quit)
button_quit.pack()

# Create label widget (First step)
myLabel1 = Label(root, text="Hello World!")
myLabel2 = Label(root, text="Kevin!")

# Pack it onto the screen (Second step)
# myLabel.pack()

# Grid system
# myLabel1.grid(row=0, column=0)
# myLabel2.grid(row=1, column=5)

# Shortcut
# myLabel1 = Label(root, text="Hello World!").grid(row=0, column=0)

# Button widget
"""
state=DISABLED - Disables the button
command - Does something after a button is being pressed
fg - Foreground color (color codes accepted)
bg - Background color
borderwidth - Border width
"""


def my_click():
    # hello = "Hello " + entry.get()  # As a variable
    # click_me = Label(root, text=hello)
    # click_me = Label(root, text="Button clicked!")
    click_me = Label(root, text="Hello " + entry.get())
    click_me.pack()


myButton = Button(root,
                  text="Enter your name!",
                  padx=50, pady=50,
                  command=my_click,
                  fg="blue", bg="red")
myButton.pack()


# Input/entry widget
entry = Entry(root, width=50, bg="green", borderwidth=10)
entry.pack()
entry.insert(5, "Enter Your Name: ")  # Inserts a default text in the input box


# Main loop of the program
root.mainloop()  # Runs root
