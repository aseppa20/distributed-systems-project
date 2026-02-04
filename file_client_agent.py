import inotify.adapters, inotify.constants
import ftplib
import getpass
import sys

def send_file_to_cache(user: str, host: str, keyfile: str, file):
    
    ftplib.FTP_TLS(user=user, host=host, keyfile=keyfile)

# Check if files are up to date in followed folder with FS
def check_sync():
    pass

def main():
    user = getpass.getuser()

    follower = inotify.adapters.Inotify()

    follower.add_watch(f"/home/{user}")

if __name__ == "__main__":
    main()
else:
    print("Please don't use me as a library")