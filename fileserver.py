from subprocess import call
import time
import os
try:
    import paramiko
except ImportError:
    call('sudo apt-get -y install python3-paramiko', shell = True)
    import paramiko
import getpass


#############
#######
#VARIABLES
#######
############
fileserver = getpass.getuser()
homepath = "/home/" + fileserver + "/backups/"
shortpath = "/home/" + fileserver
userList  = []
blackList = []
blackListreference = {}
blackListIP = []
timeToReset = int(30) 
#TO IMPROVE TESTING AND READING TERMINAL
basicWait = int(3)

##########################
#######
###CHANGE THEEEEEEEEEEEEEEEEEEEEEEEEESE FOR THE CURRENT NETWORK ENVIRONMENT
#######
##########################

#FOR CACHE USER
username  = ""
passkey = ""
#NEXT ONE WILL BE IP
cache = ""
#ADD USERNAME FOR THE USER TO BE BLOCKED IN DEMO
blackListUser = ''




##########
######
#FUNCTIONS
#####
#########


def initializeUser(user: str) -> None:
        path = homepath
        call('mkdir -p ' + path + user + '/trash', shell = True)

def listIntoFile()-> None:
        cdCommand  =  'cd ' + shortpath + '; '
        createPersistentFile = 'touch userListForOperations.txt ; '
        call(cdCommand + createPersistentFile, shell = True )
        with open(shortpath + '/'  + 'userListForOperations.txt', 'w+') as f:
                for items in userList:
                        f.write('%s\n' %items)

def ReadFileIntoList():
        with open(shortpath + '/'  + 'userListForOperations.txt', 'r') as f:
                for line in f.readlines():
                    user = line.strip()
                    if user not in userList:
                        userList.append(user)

def installer() -> None:
        install  = 'sudo apt-get -y install '
        call(install +'pip;  ' + install + 'python3-paramiko; '+ install + 'git; ' + install + 'sshpass; ', shell = True)

def  connectCache(host : str, user : str):
        connection = paramiko.SSHClient()
        connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        connection.connect(host, 22, user, passkey)
        sftp = connection.open_sftp()
        userList.clear()
        userList.extend(sftp.listdir('/home/'))
        listIntoFile()
        connection.close()


def initializeBlacklist() -> None:
        if not os.path.exists('/home/wazuh/blacklist'):
            return
        with open('/home/wazuh/blacklist', 'r') as f:
            for line in f.readlines():
                ip = line.strip()
                if ip not in blackListIP:
                    blackListIP.append(ip)
        if  blackListUser not in blackList:
            blackList.append(blackListUser)


def getCachedCommands(user: str) -> None:
        remoteFile = username + '@' + cache + ':/home/' + user + '/.cachedCommands'
        localDestination = homepath + user + '/'
        initializeUser(user)
        ##########
        ###
        #DONT USE SSH PASS FOR REAL APPLICATION SET UP KEY-BASED AUTH
        ###
        #########
        rSyncCommand = 'sshpass -p ' + passkey + ' rsync -avz -e ssh '  + remoteFile + ' ' + localDestination
        call(rSyncCommand, shell = True)


def flushCachedCommandsRemote(user: str) -> None:
        remoteFile = '/home/' + user + '/.cachedCommands'
        print("deleting on remote: " + remoteFile)
        connection = paramiko.SSHClient()
        connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        connection.connect(cache, 22, username, passkey)
        stdin, stdout, stderr = connection.exec_command('rm -f ' + remoteFile)
        stdout.channel.recv_exit_status()
        connection.close()


def runCachedCommands(user: str) -> None:
        commandList = []
        os.chdir(homepath + user)
        cachedFile = homepath + user + '/.cachedCommands'
        if not os.path.exists(cachedFile):
            return
        with open(cachedFile, 'r') as f:
            for line in f.readlines():
                commandList.append(line.strip())
        for command in commandList:
            if 'rm *' in command:
                    continue
            call(command, shell = True)
        commandList.clear()


def flushCachedCommandsLocal(user: str) -> None:
        localFile = homepath + user + '/.cachedCommands'
        print("deleting: " + localFile)
        call('rm -f ' + localFile, shell = True)




def syncDir(user: str) -> None:
        remoteDirectory = username + '@' + cache + ':/home/' + user + '/'
        localDirectory = homepath + user + '/'
        initializeUser(user)
        ##########
        ###
        #DONT USE SSH PASS FOR REAL APPLICATION SET UP KEY-BASED AUTH
        ###
        #########
        rSyncCommand = 'sshpass -p ' + passkey + ' rsync -avz -e ssh ' + remoteDirectory + ' ' + localDirectory
        call(rSyncCommand, shell = True)


 




def syncFiles()-> None:
  initializeBlacklist()
  for user in userList:
    #maybe will be used later.
    userPath = '/home/' + user
    if user in blackList:
        continue
    print("running getCachedCommands for " + user)
    getCachedCommands(user)
    time.sleep(basicWait)
    print("flushCachedCommandsRemote for " + user)
    flushCachedCommandsRemote(user)
    time.sleep(basicWait)
    print("runCachedCommands for " + user)
    runCachedCommands(user)
    time.sleep(basicWait)
    print("flushCachedCommandsLocal for " + user)
    flushCachedCommandsLocal(user)
    time.sleep(basicWait)
    print("syncDir for " + user)
    syncDir(user)
    time.sleep(basicWait)
    print("im done with this -> " + user)


################
###########
###MAIN
##########
################


def main() -> None:
    while True:
        connectCache(cache, fileserver)
        print(userList)
        syncFiles()
        print("ready to sleep")
        time.sleep(timeToReset)
        
        
        
        
###############
########
##FINALIZATION
########
###############

if __name__ == "__main__":
    installer()
    main()
else: 
    pass
    
    
    
   




