import sys
import platform


print(f"Platform: {sys.platform}")
print(f"Architecture: {platform.architecture()}")  # e.g. 64-bit

print(f"System: {platform.system()}")  # e.g. Windows, Linux, Darwin
print(f"Computer Network Name/Hostname: {platform.node()}")
print(f"System Release: {platform.release()}")
print(f"System Release Version: {platform.version()}")
print(f"Machine Type: {platform.machine()}")  # e.g. x86_64
print(f"Processor: {platform.processor()}")  # e.g. i386

architecture = platform.architecture()
uname = platform.uname()
print(f"Uname: {uname}")  # Returns System, Node, Release, Release Version, Machine, Processor in a tuple

print(f"\nHostname: {uname[1]}\n"
      f"Platform: {sys.platform}\n"
      f"Architecture: {architecture[0]}, {architecture[1]}\n"
      f"System: {uname[0]}\n"
      f"Release Version: {uname[3]}\n"
      f"Machine: {uname[4]}\n"
      f"Processor: {uname[5]}")

# Mac OS Platform
platform.mac_ver(release='', versioninfo=('', '', ''), machine='')

# Unix Platform
platform.libc_ver(executable=sys.executable, lib='', version='', chunksize=16384)
