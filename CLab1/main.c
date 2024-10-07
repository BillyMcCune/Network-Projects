// implement a simple echo server using the ANSI C socket API. An echo server can listen on a specific TCP port, and wait for a client to connect. After a TCP connection is established between the echo server and a client, the client can send arbitrary messages to the server and the server will echo back the same message to the client.
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <stdlib.h>

int server(uint16_t port);
int client(const char * addr, uint16_t port);

#define MAX_MSG_LENGTH (1300)
#define MAX_BACK_LOG (5)

int main(int argc, char ** argv)
{
	if (argc < 3 || (argv[1][0] == 'c' && argc < 4)) {
		printf("usage: myprog c <port> <address> or myprog s <port>\n");
		return 0;
	}

	uint32_t number = atoi(argv[2]);
	if (number < 1024 || number > 65535) {
		fprintf(stderr, "port number should be larger than 1023 and less than 65536\n");
		return 0;
	}

	uint16_t port = atoi(argv[2]);
	
	if (argv[1][0] == 'c') {
		return client(argv[3], port);
	} else if (argv[1][0] == 's') {
		return server(port);
	} else {
		fprintf(stderr, "unkonwn commend type %s\n", argv[1]);
		return 0;
	}
	return 0;
}

int client(const char * addr, uint16_t port)
{
	int sock;
	struct sockaddr_in server_addr;
	char msg[MAX_MSG_LENGTH], reply[MAX_MSG_LENGTH];

	if ((sock = socket(AF_INET, SOCK_STREAM/* use tcp */, 0)) < 0) {
		perror("Create socket error:");
		return 1;
	}

	printf("Socket created\n");
	server_addr.sin_addr.s_addr = inet_addr(addr);
	server_addr.sin_family = AF_INET;
	server_addr.sin_port = htons(port);

	if (connect(sock, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
		perror("Connect error:");
		return 1;
	}

	printf("Connected to server %s:%d\n", addr, port);
	printf("Enter message: \n");
	while (fgets(msg, MAX_MSG_LENGTH, stdin)) {
		if (send(sock, msg, strnlen(msg, MAX_MSG_LENGTH), 0) < 0) {
			perror("Send error:");
			return 1;
		}
		int recv_len = 0;
		if ((recv_len = recv(sock, reply, MAX_MSG_LENGTH, 0)) < 0) {
			perror("Recv error:");
			return 1;
		}
		if (recv_len == 0){
			printf("Server disconnected, client quit.\n");
			break;
		}
		reply[recv_len] = '\0';
		printf("Server reply:\n%s", reply);
		printf("Enter message: \n");
	}
	if (send(sock, "", 0, 0) < 0) {
		perror("Send error:");
		return 1;
	}
	return 0;
}

// Your server can listen on an arbitrary TCP port (from 1024 to 65535). Your server can wait for a client to connect. You can assume that only one client is served at a time. After connected to a client, your server can receive a message no longer than 512 bytes from the client, and echo back the same message, until the client closes the TCP connection. Your server needs to handle the EOF sent by client. The client will quit after sending the EOF to server. You can send EOF in shell by pressing Ctrl+D. After the previous client closes its TCP connection, your server could wait for another client to connect impliment simple echo server using the ANSI C socket API. An echo server can listen on a specific TCP port, and wait for a client to connect. After a TCP connection is established between the echo server and a client, the client can send arbitrary messages to the server and the server will echo back the same message to the client.
int server(uint16_t port)
{
    int ServerSock, connection, receivedMSG;
    int backlog = MAX_BACK_LOG; 
    char msg[MAX_MSG_LENGTH];
    struct sockaddr_in cliaddr, servaddr;
    socklen_t clilen;

    // Create socket
    if ((ServerSock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        perror("Create socket error:");
        return 1;
    }

	//set socket up
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
    servaddr.sin_port = htons(port);
    printf("Socket created\n");
	
	//bind 
    if (bind(ServerSock, (struct sockaddr *) &servaddr, sizeof(servaddr)) < 0) {
        perror("Binding error:");
        return 1;
    }

    if (listen(ServerSock, backlog) < 0) { //listen
        perror("Listen error:");
        return 1;
    }

    printf("Server is running on port %d\n", port); //print port

    while (1) {
        clilen = sizeof(cliaddr); 
        connection = accept(ServerSock, (struct sockaddr *) &cliaddr, &clilen);

        if (connection < 0) {
            perror("Accept error:");
            return 1;
        }

        printf("nice\n");
		//wait to recieve message
       while ((receivedMSG = recv(connection, msg, MAX_MSG_LENGTH, 0)) > 0) {

            if (send(connection, msg, receivedMSG, 0) < 0) {
                perror("Send error:");
                return 1;
            }

            if (receivedMSG == 0) {
                printf("client closed\n");
                break;
            }

            memset(msg, 0, sizeof(msg)); 
        }

        if (receivedMSG < 0) {
            perror("Recv error:");
            return 1;
        }

        close(connection); 
    }

    close(ServerSock); //close it up
    return 0;
}

