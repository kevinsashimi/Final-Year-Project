import threading
import socket
import netifaces
import os
import time
import tkc_database as db

from aes_ecb import ElectronicCodeBookAES
from aes_cbc import CipherBlockChainingAES
from random import randint, seed
from prettytable import PrettyTable


HEADER_LENGTH = 32
FORMAT = "utf-8"
"""
An empty string in SERVER_IP allows the server to listen
to requests coming from other computers on the network
"""
# Default Settings
SERVER_IP = ''  # Server to listen on all interfaces
SERVER_PORT = 5000
SERVER_SHELL_PORT = 5050
seed(123)
encryption_type = 'aes'
auto_chat = False
encryption = True

# Generate AES ciphers
cipher_ecb = ElectronicCodeBookAES()
cipher_cbc = CipherBlockChainingAES()


class Server(threading.Thread):
    # Initialize server
    def __init__(self, host, port, shell_port):
        super().__init__()
        self.host = host
        self.port = port
        self.shell_port = shell_port
        self.connection_list = []  # Contains client connections currently connected to the server
        self.shell_connection_list = []
        self.chatroom_list = []  # Contains active clients logged into the chatroom

    def run(self):  # Runs server code automatically upon new instance
        print(f"{current_time()} [SERVER]: Initializing Server...")
        default_interface = netifaces.ifaddresses(netifaces.gateways()['default'][netifaces.AF_INET][1])
        default_ipv4 = default_interface[netifaces.AF_INET][0]['addr']

        # Creates an admin account by default
        username_list = [user.username for user in db.session.query(db.Table).all()]
        if not username_list:
            print(f"{current_time()} [SERVER]: Database is empty!")

        if 'admin' not in username_list or username_list is None:
            print(f"{current_time()} [SERVER]: Setting up database...")
            new_account = db.Table(userid=0, username='admin', password=db.hash_password('root'))
            db.session.add(new_account)
            db.session.commit()

        # Resets all account status to offline
        account_data = db.session.query(db.Table).all()
        for account in account_data:
            account.status = False
            db.session.commit()

        server_socket = create_socket(self.host, self.port)
        shell_socket = create_socket(self.host, self.shell_port)
        server_socket.listen()
        shell_socket.listen()
        time.sleep(0.5)
        print(f"{current_time()} [SERVER]: Server startup successful")
        print(f"{current_time()} [SERVER]: Server is listening on {default_ipv4} at port {self.port}")

        while True:
            # Accepts new incoming connections
            client_socket, client_address = server_socket.accept()
            client_shell_socket, client_shell_address = shell_socket.accept()
            print(f"{current_time()} [SERVER]: Incoming connection from {client_socket.getpeername()}")

            # Creates a new thread for each new connection
            client_thread = Client(client_socket, client_address, self, client_shell_socket)
            client_thread.start()
            print(f"{current_time()} [SERVER]: New client thread started for {client_socket.getpeername()}")

            # Adds thread to the list of active connections
            self.connection_list.append(client_socket)
            self.shell_connection_list.append(client_shell_socket)

    """
    Both send_message and receive_message functions takes in the following parameters:
        client_socket: The connected socket used to sent/receive data
        message: The message being sent/receive in plain text form
    """
    @staticmethod
    def send_message(client_socket, message):
        # For server to send message to individual client
        message_data = cipher_cbc.encrypt(message)
        message_header = f"{len(message_data):<{HEADER_LENGTH}}".encode(FORMAT)
        client_socket.send(message_header + message_data)

    @staticmethod
    def receive_message(client_socket):
        # For server to receive message from individual client
        try:
            message_header = client_socket.recv(HEADER_LENGTH)
            if not len(message_header):
                return False

            message_length = int(message_header.decode(FORMAT))
            message_data = cipher_cbc.decrypt(client_socket.recv(message_length))

            """
            Returns a dictionary
                msg_header: Not used in this case but stored as additional information about the msg_data
                msg_data: Contains the message in bytes
            """
            return {'msg_header': message_length, 'msg_data': message_data.decode(FORMAT)}

        except WindowsError:
            # Client disconnected
            return False

    def broadcast_message(self, sender_socket, message):
        # Sends the sender's message to all active connected clients, except the sender
        for connection in self.chatroom_list:
            if connection != sender_socket:
                self.send_message(connection, message)

        # Acknowledge sender that message was received
        self.send_message(sender_socket, "200")

    def remove_connection(self, client_socket, client_shell_socket):
        try:
            self.connection_list.remove(client_socket)
            self.shell_connection_list.remove(client_shell_socket)

        except ValueError:
            print(f"{current_time()} [SERVER]: Connection not found")


class Client(threading.Thread):
    # Creates an instance of this class when a new thread is created
    def __init__(self, client_socket, client_address, server_socket, client_shell_socket):
        super().__init__()
        self.client_socket = client_socket
        self.client_address = client_address
        self.server_socket = server_socket
        self.client_shell_socket = client_shell_socket
        self.client_username = ''
        self.uid = ''

        # Generates an 8 number UID for the client
        for _ in range(8):
            self.uid = self.uid + str(randint(0, 9))
        print(f"{current_time()} [SERVER]: Generated UID {self.uid} issued to {self.client_socket.getpeername()}")
        server.send_message(self.client_socket, self.uid)

    def run(self):  # Runs connected client socket code automatically upon new instance
        while True:
            try:
                message_packet = self.server_socket.receive_message(self.client_socket)
                print(f"{current_time()} [{self.client_socket.getpeername()}]"
                      f"@MainMenuPage> {message_packet['msg_data']}")
                if message_packet:
                    choice = message_packet['msg_data']

                    if choice == 'login':
                        self.login_handler()

                    elif choice == 'create':
                        self.create_account(self.client_socket)

                    elif choice == 'close':
                        print(f"{current_time()} [SERVER]: {self.client_socket.getpeername()}"
                              f" has disconnected from the server![0]")
                        server.remove_connection(self.client_socket, self.client_shell_socket)
                        break

                else:  # Server shuts down
                    Server.lock = False
                    print(f"{current_time()} [SERVER]: {self.client_socket.getpeername()}"
                          f" will be automatically disconnected from the server...[1]")
                    self.set_status(self.client_username, False)
                    self.client_username = ''
                    server.remove_connection(self.client_socket, self.client_shell_socket)
                    break

            except TypeError:
                # Client disconnected from server
                print(f"{current_time()} [SERVER]: {self.client_socket.getpeername()}"
                      f" has unexpectedly disconnected from the server[2]")
                self.set_status(self.client_username, False)
                self.client_username = ''
                server.remove_connection(self.client_socket, self.client_shell_socket)
                break

    @staticmethod
    def verify_user(client_socket, input_username, input_password):
        # Note that the input username and password passed are in plaintext
        username_list = [user.username for user in db.session.query(db.Table).all()]

        # Verify username
        if input_username in username_list:
            stored_hash = [user.password
                           for user in db.session.query(db.Table).filter(db.Table.username == input_username).all()][0]

            # Verify password
            if db.verify_password(stored_hash, input_password):
                # Check if account is not currently in use
                client_info = db.session.query(db.Table).get(input_username)

                if not client_info.status:
                    if input_username == 'admin':
                        server.send_message(client_socket, '201')

                    else:
                        server.send_message(client_socket, '200')
                        server.send_message(client_socket, input_username)

                    return True

                else:
                    server.send_message(client_socket, '403')
                    return False

            else:
                # Wrong password entered
                server.send_message(client_socket, '401')
                return False

        else:
            # Username not found
            server.send_message(client_socket, '401')
            return False

    def login_handler(self):
        while True:
            variable = server.receive_message(self.client_socket)
            if variable['msg_data'] == "back":
                print(f"{current_time()} [SERVER]: {self.client_socket.getpeername()} quit login page")
                break

            username_data = server.receive_message(self.client_socket)  # Returns a dictionary or False
            password_data = server.receive_message(self.client_socket)

            print(f"{current_time()} [{self.client_socket.getpeername()}]"
                  f"@LoginPage> {username_data['msg_data']}")
            print(f"{current_time()} [{self.client_socket.getpeername()}]"
                  f"@LoginPage> {len(password_data['msg_data']) * '*'}")

            if username_data is False:  # If client disconnected
                continue

            if self.verify_user(self.client_socket,
                                username_data['msg_data'].lower(),
                                password_data['msg_data']):
                self.client_username = username_data['msg_data'].lower()

                # Sets the verified user's status as online
                self.set_status(self.client_username, True)

                if self.client_username == 'admin':
                    print(f"{current_time()} [SERVER]: {self.client_socket.getpeername()}"
                          f" has logged into <Administrator> account")
                    server.send_message(self.client_socket, f"[SERVER]: Administrator account login successful!\n"
                                                            f"[SERVER]: Welcome, Admin")

                    # Start Administrator account
                    self.admin()

                else:
                    server.chatroom_list.append(self.client_socket)
                    print(f"{current_time()} [SERVER]: Account {self.client_username}"
                          f" connected from {self.client_socket.getpeername()} has logged in")
                    server.send_message(self.client_socket, f"[SERVER]: Login successful!\n"
                                                            f"[SERVER]: Welcome, {self.client_username}!\n")
                    server.broadcast_message(self.client_socket, f"[SERVER]: {self.client_username} is online!")

                    # Starts the chatroom
                    self.chatroom()

                break

    @staticmethod
    def create_account(client_socket):
        while True:
            variable = server.receive_message(client_socket)
            if variable['msg_data'] == "back":
                print(f"{current_time()} [SERVER]: {client_socket.getpeername()} quit account creation")
                break

            input_username = server.receive_message(client_socket)
            input_password = server.receive_message(client_socket)

            print(f"{current_time()} [{client_socket.getpeername()}]"
                  f"@AccountCreationPage> {input_username['msg_data']}")
            print(f"{current_time()} [{client_socket.getpeername()}]"
                  f"@AccountCreationPage> {len(input_password['msg_data']) * '*'}")

            new_username = input_username['msg_data'].lower()

            username_list = [user.username for user in db.session.query(db.Table).all()]
            if new_username not in username_list:
                server.send_message(client_socket, '200')

                print(f"{current_time()} [{client_socket.getpeername()}]"
                      f"@AccountCreationPage> {len(input_password['msg_data']) * '*'}")
                new_password = db.hash_password(input_password['msg_data'])
                new_account = db.Table(username=new_username, password=new_password)
                db.session.add(new_account)
                db.session.commit()
                print(f"{current_time()} [SERVER]: {client_socket.getpeername()} created new account: {new_username}")
                print(f"{current_time()} [SERVER] New account successfully created")
                break

            else:
                server.send_message(client_socket, '401')

    def chatroom(self):
        global auto_chat
        global encryption
        while True:
            try:
                if auto_chat:
                    server.send_message(self.client_socket, '202')

                else:
                    server.send_message(self.client_socket, '203')

                message_packet = self.server_socket.receive_message(self.client_socket)
                if message_packet:
                    message = message_packet['msg_data']

                    if message == 'logout':
                        if self.client_username == 'admin':
                            server.chatroom_list.remove(self.client_socket)
                            server.send_message(self.client_socket, "200")

                        else:
                            print(f"{current_time()} [SERVER]: Account {self.client_username}"
                                  f" connected from {self.client_socket.getpeername()} has logged off")
                            server.broadcast_message(self.client_socket, f"[SERVER]: {self.client_username}"
                                                                         f" is offline!\n")

                            # Sets the verified user's status as offline and clear username
                            self.set_status(self.client_username, False)
                            server.chatroom_list.remove(self.client_socket)
                            self.client_username = ''
                        break

                    if encryption:
                        print(cipher_cbc.encrypt(message).decode(FORMAT))

                    else:
                        print(f"{current_time()} [{self.client_socket.getpeername()}]"
                              f"@Chatroom> {message}")

                    # Broadcast to all other clients
                    self.server_socket.broadcast_message(self.client_socket, message)

                else:
                    print(f"{current_time()} [SERVER]: Account {self.client_username}"
                          f" connected from {self.client_socket.getpeername()} has disconnected from the chatroom")
                    if self.client_username != 'admin':
                        server.broadcast_message(self.client_socket, f"{self.client_username}"
                                                                     f" has disconnected from the chatroom\n")

            except WindowsError:
                # Client disconnected from chatroom
                self.set_status(self.client_username, False)
                server.chatroom_list.remove(self.client_socket)
                self.client_username = ''
                break

    @staticmethod
    def set_status(client_username, status):
        try:
            if client_username:
                client_info = db.session.query(db.Table).get(client_username)
                client_info.status = status
                db.session.commit()

            else:
                print(f"{current_time()} [SERVER]: Username undefined, nothing was changed")

        except AttributeError:
            print(f"{current_time()} [SERVER]: Account is no longer in use or removed[5]")

    def list_accounts(self):
        account_table = PrettyTable()
        account_table.field_names = ["ID", "Username", "Status"]
        account_list = [accounts for accounts in db.session.query(db.Table).all()]
        for account in account_list:
            status = 'Online' if account.status else 'Offline'
            account_table.add_row([account.userid, account.username, status])

        server.send_message(self.client_socket, str(account_table))

    def delete_account(self):
        while True:
            variable = server.receive_message(self.client_socket)
            if variable['msg_data'] == "back":
                print(f"{current_time()} [SERVER]: {self.client_socket.getpeername()} quit account deletion")
                break

            input_username = server.receive_message(self.client_socket)
            print(f"{current_time()} [{self.client_socket.getpeername()}]"
                  f"<ADMIN>@AccountDeletionPage> {input_username['msg_data']}")
            del_username = input_username['msg_data'].lower()

            username_list = [user.username for user in db.session.query(db.Table).all()]
            if del_username in username_list:
                server.send_message(self.client_socket, '200')
                db.session.query(db.Table).filter(db.Table.username == del_username).delete()
                db.session.commit()
                print(f"{current_time()} [SERVER]: Account {del_username} has been removed successfully")
                break

            else:
                server.send_message(self.client_socket, '404')

    def admin(self):
        global auto_chat
        while True:
            try:
                message_packet = self.server_socket.receive_message(self.client_socket)
                if message_packet:
                    print(f"{current_time()} [{self.client_socket.getpeername()}]"
                          f"@AdminMenuPage> {message_packet['msg_data']}")
                    choice = message_packet['msg_data']
                    if choice == 'list':
                        self.list_accounts()

                    elif choice == 'create':
                        self.create_account(self.client_socket)

                    elif choice == 'delete':
                        self.delete_account()

                    elif choice == 'chat':
                        server.chatroom_list.append(self.client_socket)
                        self.chatroom()

                    elif choice == 'toggle':
                        self.server_socket.broadcast_message(self.client_socket, '202')
                        if auto_chat:
                            auto_chat = False
                            server.send_message(self.client_socket, "Automatic chatting disabled!")
                            print(f"{current_time()} [SERVER]: Automatic chatting disabled!")

                        else:
                            auto_chat = True
                            server.send_message(self.client_socket, "Automatic chatting enabled!")
                            print(f"{current_time()} [SERVER]: Automatic chatting enabled!")

                    elif choice == 'logout':
                        print(f"{current_time()} [SERVER]: {self.client_socket.getpeername()}"
                              f" has logged off from <Administrator> account")
                        self.set_status(self.client_username, False)
                        break

                else:  # Client as admin disconnected
                    print(f"{current_time()} [SERVER]: {self.client_socket.getpeername()}"
                          f" has logged off from <Administrator> account unexpectedly[3]")
                    self.set_status(self.client_username, False)
                    self.client_username = ''
                    server.remove_connection(self.client_socket, self.client_shell_socket)
                    break

            except Exception as e:
                print(f"{current_time()} [SERVER]: General error: ", str(e))
                print(f"{current_time()} [SERVER]: {self.client_socket.getpeername()}"
                      f" has logged off from <Administrator> account unexpectedly[4]")
                self.set_status(self.client_username, False)
                self.client_username = ''

                server.remove_connection(self.client_socket, self.client_shell_socket)
                break


def get_target(cmd):
    cmd = cmd.replace("select ", "")
    if not cmd:
        return None

    try:
        target = server.shell_connection_list[int(cmd)]

    except IndexError:
        print("Connection not found or no longer connected to the server, please try another one\n")
        return None

    except ValueError:
        print("Invalid input field after 'select' command (Numeric character expected)")
        print("Please try again or type the 'list' command to refer to the list of available connections available\n")
        return None

    print(f"You are now connected to {target.getpeername()}\n")
    return target


def execute_commands(target):
    while True:
        try:
            current_directory = server.receive_message(target)
            command = input(f"{target.getpeername()} {current_directory['msg_data']}> ")
            if not command:  # Empty string
                continue

            server.send_message(target, command)
            if command == 'exit':
                print(f"Disconnecting from {target.getpeername()}, returning to shell...\n")
                break

            if command[:2] == 'cd':
                continue

            output = server.receive_message(target)
            print(output['msg_data'])

        except TypeError:
            print(f"{target.getpeername()} has disconnected, returning to shell...\n")
            break


def turtle():
    global encryption
    while True:
        cmd = input("turtle> ")
        if not cmd:
            continue

        if cmd == 'exit':
            print("Quitting turtle...\n")
            break

        elif cmd == 'list':
            connection_table = PrettyTable()
            connection_table.field_names = ["No.", "IP Address", "Port"]
            for i, connection in enumerate(server.shell_connection_list):
                connection_table.add_row([i, connection.getpeername()[0], connection.getpeername()[1]])

            print(f"\n{connection_table}\n")

        elif cmd[:6] == 'select':
            target = get_target(cmd)

            if target is not None:
                execute_commands(target)

        elif cmd[:3] == 'aes':
            cmd = cmd.replace("aes ", "")
            if cmd == 'on':
                print("AES Encryption for messages in chatroom are now on")
                encryption = True

            elif cmd == 'off':
                encryption = False
                print("AES Encryption for messages in chatroom are now off")

            else:
                print("Invalid input field after 'aes' command ('on' or 'off' switch expected)")
                print("Please try again")

        else:
            print("Command not recognized")


def server_shell(server_session):
    start_time = time.perf_counter()
    while True:
        cmd = input()
        if cmd == 'shutdown':
            print(f"{current_time()} [SERVER]: Closing all connections...")

            for connection in server_session.connection_list:
                server.send_message(connection, '503')

            time.sleep(0.5)
            stop_time = time.perf_counter() - start_time
            print(f"{current_time()} [SERVER]: Total server uptime: {format_time(stop_time)}")
            print(f"{current_time()} [SERVER]: Server shutting down...")

            os._exit(0)

        elif cmd == 'wipe':
            confirmation = input("<WARNING> Are you sure you want to wipe"
                                 " all account records in database? (y/n): ").lower()

            if confirmation == 'y':
                print(f"{current_time()} [SERVER]: Wiping all account records in database...")
                db.session.query(db.Table).delete()
                db.session.commit()
                time.sleep(0.5)
                print(f"{current_time()} [SERVER]: Database wipe completed, please restart the server")

            elif confirmation == 'n':
                print("Nothing was done")

            else:
                print("Unrecognized command, nothing was done")

        elif cmd == 'turtle':
            turtle()

        else:
            print(f"{current_time()} [SERVER]: Unrecognized command, please try again...")
            # print("[SERVER]: Type -h for a list of commands")  # To be implemented in the future


def create_socket(host, port):
    address = (host, port)
    new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    new_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    new_socket.bind(address)
    return new_socket


def current_time():
    t = time.localtime()
    return time.strftime("%H:%M:%S", t)


def format_time(t):
    if t >= 59 * 60:
        hours = int(t / 60 / 60)
        minutes = int((t - (hours * 60 * 60)) / 60)
        seconds = t - ((hours * 60 * 60) + (minutes * 60))
        return f"{hours}hr {minutes}min {seconds:0.2f}s"

    elif t >= 60:
        minutes = int(t / 60)
        seconds = t - (minutes * 60)
        return f"{minutes}min {seconds:0.2f}s"

    else:
        return f"{t:0.2f}s"


if __name__ == '__main__':
    # Start up the server
    server = Server(SERVER_IP, SERVER_PORT, SERVER_SHELL_PORT)
    server.start()

    server_shell = threading.Thread(target=server_shell, args=(server,))
    server_shell.start()
    print(f"{current_time()} [SERVER]: Server shell started")
