import random #import stuff I want/need
from socket import * #import stuff I want/need
import time #import stuff I want/need


serverSocket = socket(AF_INET, SOCK_DGRAM) #set up serverSocket
prevtime = 0 #inizialize prevtime variable 
prevcount = 0 #inizialize prevcount variable 
totalPacketsLost = 0 #inizialize totalPacketsLost variable 

serverSocket.bind(('0.0.0.0', 12000))  #bind socket to localhost and port 12000

while True:
    try:
        print("Waiting for a packet...") #basic statement to confirm status of server
        serverSocket.settimeout(5) #setting timeout 
        message, address = serverSocket.recvfrom(1024) #waiting... 
        message = message.decode().split(" ") #gotta get that message data
        sendTime = float(message[-1])  #get packet time
        currentpacket = int(message[-2])
        if currentpacket - prevcount != 1:
            for i in range(1,currentpacket-prevcount): #for loop in case multiple packets lost in a row
                print(f"Missing Packet {str(prevcount+i)}") # if missing packet print message saying the one that is missing
            totalPacketsLost += currentpacket - prevcount-1 # calc total packets lost
        prevcount = currentpacket
        timeDiff = max(0, sendTime - prevtime) #get packet time diff
        message[-1] = "time diff: " + str(timeDiff) #put diff in
        response = " ".join(message) #construct response
        prevtime = sendTime  #assign prevTime to new value
        print(response)
    except OSError as error: #No packet for 5 seconds error handling
        print("Application closed probably") #message 
        print(f"total number of packets lost = {totalPacketsLost}") #calc and print total packets lost
        serverSocket.close()   #close socket
        break # get out of while true 

