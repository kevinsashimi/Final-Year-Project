from tkinter import *

root = Tk()
root.title("Calculator")

entry = Entry(root, width=35, borderwidth=5)
entry.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

global first_num
global math


def button_click(number):
    # entry.delete(0, END)  # Clear entry box
    current = entry.get()
    entry.delete(0, END)
    entry.insert(0, str(current) + str(number))


def button_addition():
    num1 = entry.get()
    global first_num
    global math
    math = "addition"
    first_num = int(num1)
    entry.delete(0, END)


def button_subtraction():
    num1 = entry.get()
    global first_num
    global math
    math = "subtraction"
    first_num = int(num1)
    entry.delete(0, END)


def button_multiplication():
    num1 = entry.get()
    global first_num
    global math
    math = "multiplication"
    first_num = int(num1)
    entry.delete(0, END)


def button_division():
    num1 = entry.get()
    global first_num
    global math
    math = "division"
    first_num = int(num1)
    entry.delete(0, END)


def button_equal():
    num2 = entry.get()
    entry.delete(0, END)
    if math == "addition":
        entry.insert(0, first_num + int(num2))
    elif math == "subtraction":
        entry.insert(0, first_num - int(num2))
    elif math == "multiplication":
        entry.insert(0, first_num * int(num2))
    elif math == "division":
        entry.insert(0, first_num / int(num2))


def button_clear():
    entry.delete(0, END)


# Define buttons
button_0 = Button(root, text='0', padx=40, pady=20, command=lambda: button_click(0))
button_1 = Button(root, text='1', padx=40, pady=20, command=lambda: button_click(1))
button_2 = Button(root, text='2', padx=40, pady=20, command=lambda: button_click(2))
button_3 = Button(root, text='3', padx=40, pady=20, command=lambda: button_click(3))
button_4 = Button(root, text='4', padx=40, pady=20, command=lambda: button_click(4))
button_5 = Button(root, text='5', padx=40, pady=20, command=lambda: button_click(5))
button_6 = Button(root, text='6', padx=40, pady=20, command=lambda: button_click(6))
button_7 = Button(root, text='7', padx=40, pady=20, command=lambda: button_click(7))
button_8 = Button(root, text='8', padx=40, pady=20, command=lambda: button_click(8))
button_9 = Button(root, text='9', padx=40, pady=20, command=lambda: button_click(9))
button_add = Button(root, text="+", padx=39, pady=20, command=button_addition)
button_subtract = Button(root, text="-", padx=41, pady=20, command=button_subtraction)
button_multiply = Button(root, text="*", padx=40, pady=20, command=button_multiplication)
button_divide = Button(root, text="/", padx=41, pady=20, command=button_division)
button_equal = Button(root, text="=", padx=91, pady=20, command=button_equal)
button_clear = Button(root, text="Clear", padx=79, pady=20, command=button_clear)

# Put buttons ont he screen
button_0.grid(row=4, column=0)
button_1.grid(row=3, column=0)
button_2.grid(row=3, column=1)
button_3.grid(row=3, column=2)
button_4.grid(row=2, column=0)
button_5.grid(row=2, column=1)
button_6.grid(row=2, column=2)
button_7.grid(row=1, column=0)
button_8.grid(row=1, column=1)
button_9.grid(row=1, column=2)
button_add.grid(row=5, column=0)
button_subtract.grid(row=6, column=0)
button_multiply.grid(row=6, column=1)
button_divide.grid(row=6, column=2)
button_equal.grid(row=5, column=1, columnspan=2)
button_clear.grid(row=4, column=1, columnspan=2)

root.mainloop()


