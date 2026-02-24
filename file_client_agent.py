import inotify.adapters, inotify.constants
import paramiko
import getpass
import time
import glob
import os

def send_file_to_cache(user: str, host: str, file):
    connection = paramiko.SSHClient()
    connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    connection.connect(host, 22, user, "1234")
    sftp = connection.open_sftp()
    try:
        sftp.put(file, file)
    except FileNotFoundError:
        # Temp files might be deleted before sent, so skipping any not found files
        pass
    finally:
        connection.close()

def send_cached_command(user, host, command):
    connection = paramiko.SSHClient()
    connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    connection.connect(host, 22, user, "1234")
    connection.exec_command(f"echo '{command}' >> /home/{user}/.cachedcommands")
    connection.exec_command(f"{command}")
    connection.close()

# Check if files are up to date in followed folder with FSs
def check_sync(user: str, host: str):
    connection = paramiko.SSHClient()
    connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    connection.connect(host, 22, user, "1234")
    sftp = connection.open_sftp()
    files = sftp.listdir()
    for file in files:
        if file[0] == ".":
            continue
        try:
            filestat = sftp.stat(file)
            lfile = os.stat(f"/home/{user}/{file}").st_mtime
            rfile = filestat.st_mtime
            if rfile == None:
                rfile = 0
            if lfile < rfile:
                sftp.get(file, f"/home/{user}/{file}")
            elif lfile.as_integer_ratio() == rfile.as_integer_ratio():
                continue
            else:
                send_file_to_cache(user, host, f"/home/{user}/{file}")
        except FileNotFoundError:
            sftp.get(file, f"/home/{user}/{file}")
        except IsADirectoryError:
            pass
    
    connection.close()
    

def main():
    user = getpass.getuser()
    host = "192.168.124.251"
    follow_folder = f"/home/{user}"
    check_sync(user, host)
    follower = inotify.adapters.Inotify()

    follower.add_watch(follow_folder)

    while True:
        for event in follower.event_gen(yield_nones=False):
            if event == None:
                continue
            (_, type_names, path, filename) = event

            if type_names == ["IN_CLOSE_WRITE"] or type_names == ["IN_CREATE"]:
                if filename[0] == ".":
                    continue
                send_file_to_cache(user, host, f"{path}/{filename}")
            elif type_names == ["IN_DELETE"]:
                send_cached_command(user, host, f"rm {path}/{filename}")
        
        time.sleep(1)

if __name__ == "__main__":
    main()
else:
    print("Please don't use me as a library")