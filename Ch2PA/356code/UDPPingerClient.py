import sys #import stuff I want/need
from socket import * #import stuff I want/need
import time #import stuff I want/need
import numpy as np #import stuff I want/need


clientSocket = socket(AF_INET,SOCK_DGRAM) #set up socket
clientSocket.settimeout(2) #set timer
udpHost = sys.argv[1] #grab the address I put in args
udpPort = int(sys.argv[2]) #grab the port number I put in args

PingData = [] #for the ping stats


for i in range(1,16): #set up the pings to number from 1 to 15
    try: #try to send a ping to server
        sendTime = time.time() #get send time 
        clientSocket.sendto(f"Ping {i} {sendTime}".encode(),(udpHost,udpPort)) #ping server
        clientSocket.recv(1024) #wait for server to respond
        recieveTime = time.time() #get recieve time if no exception raised
    except OSError as error: #if the socket times out this error will be raised
        print("Request timed out\n") #print the specified request thingy 
        continue #continue to next ping
    print("RTT=",float(recieveTime - sendTime)) #calculate and print RTT
    PingData += [float(recieveTime - sendTime)] #add RTT data to PingData

#get the data required
print("The RTT min: ",min(PingData)) #min
print("The RTT max: ",max(PingData)) #max
print("The RTT median: ",np.median(PingData)) #median
print("The RTT average: ",np.average(PingData)) #average
print(f"The RTT packet loss rate as percentage: {(len(PingData)/15)*100}%") #packet loss as a percentage

clientSocket.close()#close the socker


    
    


