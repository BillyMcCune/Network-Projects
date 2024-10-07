import sys #import stuff I want/need
from socket import * #import stuff I want/need
import time #import stuff I want/need
import numpy as np #import stuff I want/need


clientSocket = socket(AF_INET,SOCK_DGRAM) #set up socket
clientSocket.settimeout(2) #set timer
udpHost = sys.argv[1] #grab the address I put in args
udpPort = int(sys.argv[2]) #grab the port number I put in args

for i in range(1,16): #set up the pings to number from 1 to 15
    try: #try to send a ping to server
        sendTime = time.time() #get send time 
        clientSocket.sendto(f"Ping {i} {sendTime}".encode(),(udpHost,udpPort)) #ping server
    except OSError as error: #if the socket times out this error will be raised
        print("Request timed out\n") #print the specified request thingy 
        continue #continue to next ping
  

clientSocket.close()#close the socker