from tkinter import *

global pic
global pop


def show_frame(frame):
    frame.tkraise()


def choice(option):
    pop.destroy()
    if option == "yes":
        my_label.config(text="You clicked yes!")

    elif option == "no":
        my_label.config(text="You clicked no!")


def popup():
    global pop
    pop = Toplevel(window)
    pop.title("My Popup")
    w = 250  # Width for the popup window
    h = 150  # Height for the popup window

    # Get screen width and height
    ws = window.winfo_screenwidth()  # Width of the screen
    hs = window.winfo_screenheight()  # Height of the screen

    # Calculate x and y coordinates for the popup window
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)

    # Set the popup window to open in the middle of the user's screen
    pop.geometry('%dx%d+%d+%d' % (w, h, x, y))
    pop.config(bg='green')

    # Picture (Optional)
    global pic
    pic = PhotoImage(file="../images/error2.png")

    pop_label = Label(pop, text="Would you like to proceed?", bg="green", fg="white", font=("helvetica", 12))
    pop_label.pack(pady=10)

    my_frame = Frame(pop, bg="green")
    my_frame.pack(pady=5)

    me_pic = Label(my_frame, image=pic, borderwidth=0)
    me_pic.grid(row=0, column=0, padx=10)

    # Button
    yes_btn = Button(my_frame, text="YES", command=lambda: choice("yes"), bg="orange")
    yes_btn.grid(row=0, column=1)

    no_btn = Button(my_frame, text="NO", command=lambda: choice("no"), bg="yellow")
    no_btn.grid(row=0, column=2)


window = Tk()
window.state('zoomed')

window.rowconfigure(0, weight=1)
window.columnconfigure(0, weight=1)

frame1 = Frame(window)
frame2 = Frame(window)
frame3 = Frame(window)

for f in (frame1, frame2, frame3):
    f.grid(row=0, column=0, sticky='nsew')

my_button = Button(window, text="Click for popup!", command=popup)
# my_button.pack(pady=50)
my_button.grid(row=1, column=0)
my_label = Label(window, text="")
# my_label.pack(pady=20)
my_label.grid(row=2, column=0)

# Frame1 code
frame1_title = Label(frame1, text='This is frame 1', bg='red')
frame1_title.pack(fill='x')

frame1_btn = Button(frame1, text='Enter', command=lambda: show_frame(frame2))
frame1_btn.pack()

# Frame2 code
frame2_title = Label(frame2, text='This is frame 2', bg='yellow')
frame2_title.pack(fill='x')

frame2_btn = Button(frame2, text='Enter', command=lambda: show_frame(frame3))
frame2_btn.pack()

# Frame3 code
frame3_title = Label(frame3, text='This is frame 3', bg='green')
frame3_title.pack(fill='x')

frame3_btn = Button(frame3, text='Enter', command=lambda: show_frame(frame1))
frame3_btn.pack()


if __name__ == '__main__':
    mainloop()
