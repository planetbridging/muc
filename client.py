import socket, threading, os
try:
   import queue
except ImportError:
   import Queue as queue
import time
from threading import Thread

from datetime import datetime
dateTimeObj = datetime.now()
#dateclean = "project_"+dateTimeObj.strftime().replace(" ","_").replace(":","-").replace(".","-")

timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S.%f)")
timestampStr = "project_"+timestampStr.replace(" ","_").replace(":","-").replace(".","-")
#print('Current Timestamp : ', timestampStr)
print(timestampStr)
dirName = 'ScanResults'

MaxTcpPorts = 65535
TcpClients = []
TcpComplete = []

class IncomingOutput(threading.Thread):
    def __init__(self,clientsocket, cip):
        threading.Thread.__init__(self)
        self.csocket = clientsocket
        self.clientIp = cip
        self.JobCount = 0
        print("Connected: " + cip + "\n")
        
    def GetClientIp(self):
        return self.clientIp
        
    def SendCmd(self,cmd):
        self.csocket.sendall(bytes(cmd))
        print("sent: " + cmd)
        
    def PrintIncoming(self):
        while True:
            try:
                data = data +  self.csocket.recv(1024)
                #print("before"+data+"after")
                return data.decode('utf-8')
            except:
                continue
                
    def SaveData(self,data):
        self.JobCount += 1
        savingto = dirName + "//" + timestampStr + "//client_" + self.clientIp.replace(".","_") + "_" + str(self.JobCount) + ".txt"
        f = open(savingto,'w+')
        f.write(data)
        f.close()
        TcpComplete.append(self.clientIp)
        print(str(len(TcpComplete)) + "/" + str(len(TcpClients)))
                
    def run(self):
        filter_response = ""
        while True:
            data = self.csocket.recv(2048)
            print(data)
            #in_data =  self.PrintIncoming()
            #print("before")
            d = data.decode('utf-8')
            if d.find('</nmaprun>') > 0:
                filter_response += d
                #print(filter_response)
                self.SaveData(filter_response)
                d = ""
            else:
                filter_response += d
            #print("after")


def StartClient(SERVER):
    try:
        #SERVER = input("Enter ip: ")
        #SERVER = "192.168.0.122"
        PORT = 8080
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((SERVER, PORT))
        #client.sendall(bytes("This is from Client",'UTF-8'))
        newthread = IncomingOutput(client,SERVER)
        newthread.start()
        TcpClients.append(newthread)
        
        #testcmd = "nmap -sP -oG - 192.168.0.0/24"
        #client.sendall(bytes(testcmd))
        #while True:
         #   command = raw_input("Shell: ")
            #print ("type of name", type(command)) 
            #client.sendall(bytes(command,'UTF-8'))
            #client.sendall(bytes(command))
        #client.close()
    except:
        pass
        
        #print("failed: " + SERVER)
    #return newthread
 
 
def ShowConnectedClients():
    for c in TcpClients:
        print(c.GetClientIp() + "\n")
        
def ShowCountClients():
    clientcount = len(TcpClients)
    print("ClientCount: " + str(clientcount) + "\n")
        
        
def ShowHelp():
    print("list - shows clients")
    print("quit - quits")

def TestCmd():
    cmd = "lstport nmap --open -T4 -sV --max-parallelism 100 -vvv -sS --min-rate 10000 -oX - 192.168.0.1"
    cmd = "lstport nmap --open -T4 -sV -vvv -sS -oX - 192.168.1.1"
    
def DivideAndConquer(cmd):
    TcpComplete = []
    clientcount = len(TcpClients)
    print("Muc count: " + str(clientcount))
    print("Work load: " + str(round(MaxTcpPorts/clientcount)))
    DivPorts = MaxTcpPorts
    DivCountedPorts = 1
    
    cmd = cmd.replace("lstport nmap","")
    cc_last = 0
    for c in TcpClients:
        cc_last += 1
        print(str(cc_last) + "/" + str(clientcount))
        
        startingport = 0
        endingport = 0
        
        if cc_last != clientcount:
            startingport = DivCountedPorts
            endingport = (DivPorts / clientcount) + startingport
        
        if cc_last == clientcount:
            startingport = DivCountedPorts
            endingport = MaxTcpPorts
            
        
        #print("port range: " + str(startingport) + "-" + str(endingport))
        newcmd = "nmap -p " + str(startingport) + "-" + str(endingport) + " " + cmd
        c.SendCmd(newcmd)
        DivCountedPorts += (DivPorts / clientcount) + 1
        #print(newcmd)
        
    
   # for c in range(0,clientcount - 1):
       # print(c)
      #  print(TcpClients[c].GetClientIp())
        #startingport = DivCountedPorts
        #endingport = (DivPorts / clientcount) + startingport
        #print("port range: " + str(startingport) + "-" + str(endingport))
        #newcmd = "nmap -p " + str(startingport) + "-" + str(endingport) + " " + cmd
        #print(newcmd)
        
        #TcpClients[c].SendCmd(newcmd)
        
        
        #DivCountedPorts += (DivPorts / clientcount) + 1
   # print("single")
  #  print(TcpClients[clientcount - 1].GetClientIp())
    #startingport = DivCountedPorts
    #endingport = MaxTcpPorts
    #newcmd = "nmap -p " + str(startingport) + "-" + str(endingport) + " " + cmd
    #print(newcmd)
    #TcpClients[clientcount -1].SendCmd(newcmd)
    #print("port range: " + str(startingport) + "-" + str(endingport))
    #DivCountedPorts += (DivPorts / clientcount) + 1
    
    
def SetupSaving(newdir):
    
    try:
        # Create target Directory
        os.mkdir(newdir)
        print("Directory " , newdir ,  " Created ") 
    except:
        pass
        #print("Directory " , dirName ,  " already exists")

def SetupFindingClients():
    localip = socket.gethostbyname(socket.gethostname())
    localip = "192.168.1.1"
    divip = localip.split(".")
    #print(divip)
        
    q = queue.Queue()
    #for i in range(5):
    for ip in range(1,256):
        tryip = divip[0] + "." + divip[1] + "." + divip[2] + "." + str(ip)
        t = Thread(target=StartClient, args=(tryip,))
        t.daemon = True
        t.start()

    #for item in range(5):
        #q.put(item)
    #    q.join()
    

def RemoteManagement(ipc):
    SelClient = ""
    ipc = ipc.replace("ipc ","")
    for c in TcpClients:
        if ipc == c.GetClientIp():
            SelClient = c
            break
    if SelClient != "":
        while True:
            command = raw_input("Shell@"+ipc+": ")
            
            if command == "back":
                break
            else:
                SelClient.SendCmd(command)


#ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
#ROOT_DIR = ROOT_DIR.replace("\\","//")

SetupSaving(dirName)
SetupSaving(dirName + "//" + timestampStr)
SetupFindingClients()

ShowCountClients()
while True:
    command = raw_input("Shell: ")
    if command == "quit":
        break
        
    if command == "list":
        ShowConnectedClients()
        
    if command == "count":
        ShowCountClients()
        
    if command.startswith("lstport"):
        DivideAndConquer(command)
    
    if command.startswith("ipc"):
        RemoteManagement(command)
    
print("bub bye now")