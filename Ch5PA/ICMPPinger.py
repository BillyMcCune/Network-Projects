from socket import *
import os
import sys
import struct
import time
import select
ICMP_ECHO_REQUEST = 8


def checksum(string):
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


def receiveOnePing(mySocket, ID, timeout, destAddr):
    timeLeft = timeout
    while 1:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []: # Timeout
            return "Request timed out."
        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)
        # Fill in start
        #to receive the structure ICMP_ECHO_REPLY and fetch the information you need, such as checksum, sequence number, time to live (TTL), etc. Study the “sendOnePing” method before trying to complete the “receiveOnePing” method.
        # Fetch the ICMP header from the IP packet

        IPHead = struct.unpack("!BBHHHBBH4s4s",recPacket[:20]) #get head of IP
        TLLRecv = IPHead[5] #get TLL
        ICMPHead = struct.unpack("bbHHh",recPacket[20:28]) #unpack head

        # Your program can only detect timeouts in receiving ICMP echo responses. Modify the Pinger
        # program to parse the ICMP response error codes and display the corresponding error results to the
        # user. Examples of ICMP message types are listed in Fig. 1. All messages shown in Fig. 1 are ICMP
        # response error codes except echo reply (to ping). For simplicity, you only need to identify
        # “Destination Network Unreachable”, “Destination Host Unreachable”, and “Destination Protocol
        # Unreachable”, and output other messages as “Other Errors”. 

        typeRecv = ICMPHead[0] #the first item is the type
        codeRecv = ICMPHead[1] #get code
        if typeRecv == 0 and codeRecv == 0: #check if chill
            typeRecv = 0 #do nothing 
        elif typeRecv == 3 and codeRecv == 0: #check if network is unreachable
            print("Destinaton network unreachable") #print message
            return "packet lost"
        elif typeRecv == 3 and codeRecv == 1: #check if destination host unreachable
            print("Destination Host Unreachable") #print message
            return "packet lost"
        elif typeRecv == 3 and codeRecv == 2: #check if protocol unreachable
            print("Destination protocol unreachable") #print message
            return "packet lost"
        else:
            print("Other Errors") #print other errors
            return "packet lost"

        checksumRecv = ICMPHead[2] #the second item is the checksum call checksum method to return true
        IDRecv = ICMPHead[3] #get sequence num
        sequenceNumRecv = ICMPHead[4] #get TTL on packet
        if ID == IDRecv:
        #     print(f"This is the address {addr}")
        #     print(f"This was the destination address {destAddr}")
        #     print(f"This is the ICMP type {typeRecv}")
        #     print(f"This is the codeRecv {codeRecv}")
        #     print(f"This is the ICMP checksum {checksumRecv}")
        #     print(f"This is the ICMP ID {IDRecv}")
        #     print(f"This is the ICMP sequenceNum {sequenceNumRecv}")
        #     print(f"This is the ICMP TLL {TLLRecv}")
            return timeReceived - startedSelect 

        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return "Request timed out."


def sendOnePing(mySocket, destAddr, ID):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    myChecksum = 0
    # Make a dummy header with a 0 checksum
    # struct -- Interpret strings as packed binary data
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("d", time.time())
    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)


    # Get the right checksum, and put in the header
    if sys.platform == 'darwin':
        # Convert 16-bit integers from host to network byte order
        myChecksum = htons(myChecksum) & 0xffff
    else:
        myChecksum = htons(myChecksum)


    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data


    mySocket.sendto(packet, (destAddr, 1)) # AF_INET address must be tuple, not str
    # Both LISTS and TUPLES consist of a number of objects
    # which can be referenced by their position number within the object.


def doOnePing(destAddr, timeout):
    icmp = getprotobyname("icmp")
    # SOCK_RAW is a powerful socket type. For more details: http://sockraw.org/papers/sock_raw


    mySocket = socket(AF_INET, SOCK_RAW, icmp)


    myID = os.getpid() & 0xFFFF # Return the current process i
    sendOnePing(mySocket, destAddr, myID)
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)


    mySocket.close()
    return delay


def ping(host, timeout=1):
    # timeout=1 means: If one second goes by without a reply from the server,
    # the client assumes that either the client's ping or the server's pong is lost
    avgRTT = 0 #initialize value
    minRTT = 1000000 #initialize value
    maxRTT = 0 #initialize value
    hitPingNum = 0 #initialize value
    genPingNum = 0 #initialize value
    numMissed = 0 #initialize value
    dest = gethostbyname(host) 
    print("Pinging " + dest + " using Python:")
    print("")
    # Send ping requests to a server separated by approximately one second
    while 1:
        delay = doOnePing(dest, timeout) #get delay
        genPingNum += 1 #iterate general ping num

        if type(delay) == float or type(delay) == int: #check if delay is valid
            hitPingNum += 1 #iterate hit ping num for each ping that hits
            if hitPingNum == 1:
                avgRTT = delay  #RTT is the delay *2
            else:
                avgRTT = ((avgRTT * (hitPingNum - 1)) + delay) / hitPingNum  #run avg calculation

            minRTT = min(minRTT, delay) #max calculation
            maxRTT = max(maxRTT, delay) #min calculation
        else:
            numMissed += 1 
        if type(delay) == float or type(delay) == int: #if error isn't thrown print stats
            print(f"The RTT for this ping message was: {delay}") #print RTT
            print(f"The RTT for this packet was:")
            print(f"The AvgRTT is: {avgRTT}.") #print AvgRTT
            print(f"The MinRTT is: {minRTT}.") #print minRTT
            print(f"The MaxRRT is: {maxRTT}.") #print maxRTT
        print(f"The Packet Loss Percentage is: {((numMissed / genPingNum) * 100):.2f}%") #print packet loss percentage
        time.sleep(1) #eepy so it sends one ping every second

ping("umass.edu")
print("--------------------------------------------")
# ping("alibaba.com")
# print("--------------------------------------------")
# ping("bbc.com")
# print("--------------------------------------------")
# ping("unimelb.edu.au")
# print("--------------------------------------------")
# ping("pretoriazoo.org")