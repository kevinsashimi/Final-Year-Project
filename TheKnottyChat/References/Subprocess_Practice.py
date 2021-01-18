import subprocess


# subprocess.call("ipconfig", shell=True)

# output = subprocess.check_output('dir', shell=True, universal_newlines=True)
# print(output)

# Sets the stdout and stderr to the sub process pipe
p1 = subprocess.run('dir', shell=True, capture_output=True)
print(p1.stdout.decode('utf-8'))

# Comes in as a string
p2 = subprocess.run('dir', shell=True, capture_output=True, text=True)
print(p2.stdout)

# Redirects the stdout and stderr into pipe
p3 = subprocess.run('dir', shell=True, stdout=subprocess.PIPE, text=True)
print(p3.stdout)

# Redirect output to a file
with open('output.txt', 'w') as f:
    p4 = subprocess.run('dir', shell=True, stdout=f, text=True)

# Redirect the output of p5 into the input of p6
# Note this is using windows commands
p5 = subprocess.run('type output.txt', shell=True, capture_output=True, text=True)
p6 = subprocess.run('findstr -i Subprocess_Practice.py', shell=True, capture_output=True, text=True, input=p5.stdout)
print(p6.stdout)
