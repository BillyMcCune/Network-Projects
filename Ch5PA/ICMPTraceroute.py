from socket import *
import os
import sys
import struct
import time
import select

ICMP_ECHO_REQUEST = 8
MAX_HOPS = 30
TIMEOUT = 2.0
TRIES = 2

# The packet that we shall send to each router along the path is the ICMP echo
# request packet, which is exactly what we had used in the ICMP ping exercise.
# We shall use the same packet that we built in the Ping exercise
def checksum(string):
# In this function we make the checksum of our packet
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0
    while count < countTo:
        thisVal = string[count + 1] * 256 + string[count]
        csum = csum + thisVal
        csum = csum & 0xffffffff
        count = count + 2
    if countTo < len(string):
        csum = csum + ord(string[len(string) - 1])
        csum = csum & 0xffffffff
    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


def build_packet():
# In the sendOnePing() method of the ICMP Ping exercise ,firstly the header of our
# packet to be sent was made, secondly the checksum was appended to the header and
# then finally the complete packet was sent to the destination.
# Make the header in a similar way to the ping exercise.
# Append checksum to the header.
# Don’t send the packet yet, just return the final packet in this function.
    #Fill in start
    #Explain each line
    ID = 0 #give an ID
    myChecksum = 0 #initialize checksum
    header = struct.pack("bbHHh",ICMP_ECHO_REQUEST,0,myChecksum,ID,1) #create dummy header before real checksum
    data = struct.pack("d", time.time()) #put time in data just cause
    myChecksum = checksum(header + data) #do checksum 

    if sys.platform == 'darwin': #checks if the platform is darwin
        myChecksum = htons(myChecksum) & 0xffff #convert 16-bit integers from host to network byte order
    else:
        myChecksum = htons(myChecksum) #if it isnt darwin this run this

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1) #make actual header 
    #Fill in end
    packet = header + data
    return packet


def get_route(hostname):
    timeLeft = TIMEOUT
    for ttl in range(1, MAX_HOPS):
        for tries in range(TRIES):
            destAddr = gethostbyname(hostname)
            # Fill in start
            # Make a raw socket named mySocket
            # Explain each line
            icmp = getprotobyname("icmp") #the proto parameter used to create a icmp socket
            mySocket = socket(AF_INET, SOCK_RAW, icmp) #the socket 
            # Fill in end
            mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', ttl))
            mySocket.settimeout(TIMEOUT)
            try:
                d = build_packet()
                mySocket.sendto(d, (hostname, 0))
                t = time.time()
                startedSelect = time.time()
                whatReady = select.select([mySocket], [], [], timeLeft)
                howLongInSelect = (time.time() - startedSelect)
                if whatReady[0] == []: # Timeout
                    print(" * * * Request timed out.")
                recvPacket, addr = mySocket.recvfrom(1024)
                timeReceived = time.time()
                timeLeft = max(0, timeLeft - howLongInSelect)
                if timeLeft <= 0:
                    print(" * * * Request timed out.")
            except timeout:
                continue
            else:
                # Fill in start
                # Fetch the icmp type from the IP packet
                icmpHeader = recvPacket[20:28]
                ICMPType, Code, myChecksum, myID, sequence = struct.unpack("bbHHh",
                icmpHeader)
                #Fill in end
                if ICMPType == 11:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 +bytes])[0]
                    print(" %d rtt=%.0f ms %s" % (ttl,(timeReceived - t) * 1000,addr[0]))
                elif ICMPType == 3:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    print(" %d rtt=%.0f ms %s" % (ttl,(timeReceived - t) * 1000,addr[0]))
                elif ICMPType == 0:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    print(" %d rtt=%.0f ms %s" % (ttl, (timeReceived - timeSent) * 1000,addr[0]))
                    return
                else:
                    print("error")
                    break
            finally:
                mySocket.close()

print("--------------------------------------------")
print ("umass.edu")
get_route("umass.edu")
print("--------------------------------------------")
print ("alibaba.com")
get_route("alibaba.com")
print("--------------------------------------------")
print ("bbc.com")
get_route("bbc.com")
print("--------------------------------------------")
print ("unimelb.edu.au")
get_route("unimelb.edu.au")
print("--------------------------------------------")
print ("pretoriazoo.org")
get_route("pretoriazoo.org")