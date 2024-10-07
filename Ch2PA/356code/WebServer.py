#import socket module
from socket import *
import sys # In order to terminate the program
serverSocket = socket(AF_INET, SOCK_STREAM)

serverSocket.bind(('0.0.0.0', 80)) #I bind the server to port 80 and allow it to accept any address
serverSocket.listen(5) # I set it to listen to 5 which sets up the number of connections I can have backlogged before I refuse the connection

while True:
#Establish the connection
    print('Ready to serve...')
    connectionSocket, addr = serverSocket.accept() #use the accept method which will output the connect socket object and the address that is connecting
    try:
        message = connectionSocket.recv(1024)  #the server will receive the message from the client through a TCP message with at 1024 byte buffer
        filename = message.split()[1][1:] 
        f = open(filename,'r')
        outputdata = f.read() # the file once opened will be read
        #Send one HTTP header line into socket

        connectionSocket.send('HTTP/1.1 200 OK\r\n'.encode())
        connectionSocket.send('Content-Type: text/html\r\n\r\n'.encode()) #im sending a 200 ok and the type of content
        #Send the content of the requested file to the client
        for i in range(0, len(outputdata)):
            connectionSocket.send(outputdata[i].encode())

        connectionSocket.send("\r\n".encode())
        connectionSocket.close()
    except IOError:
        #Send response message for file not found
        #Fill in start
        connectionSocket.send('HTTP/1.1 404 Not Found\r\n'.encode())
        connectionSocket.send('Content-Type: text/html\r\n\r\n'.encode())
        connectionSocket.send('<html><head></head><body><h1>404 Not Found</h1></body></html>'.encode()) #I first send the error header and then I send a nice 404 message to the server to be displayed to the client

        connectionSocket.close() #closing the socket

serverSocket.close()
sys.exit()#Terminate the program after sending the corresponding data