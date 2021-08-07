#include<stdio.h>
#include<string.h>	
#include<stdlib.h>	
#include<sys/socket.h>
#include<arpa/inet.h>	
#include<unistd.h>	
#include <stdbool.h>

#define PORT 8888

void sub_400e08(int );
void sub_400ce4(void *);
void sub_400e60(int*, int, int*);
bool sub_400cb4(int);
bool sub_400ca4(int);

int main(int argc , char *argv[])
{
	int socket_desc, bind_desc, client_sock , c , *new_sock;
	struct sockaddr_in server , client;
	int connected_clients = 0;	
	
	socket_desc = socket(AF_INET , SOCK_STREAM , 0);	
	if(!(sub_400cb4(socket_desc)))
		return -1;
	
	
	server.sin_family = AF_INET;
	server.sin_addr.s_addr = inet_addr("127.0.0.1");
	server.sin_port = htons( PORT );
	
	bind_desc = bind(socket_desc,(struct sockaddr *)&server , sizeof(server));
	if(!sub_400ca4(bind_desc))
		return -1;
	
	
	listen(socket_desc , 3);
	
	
	c = sizeof(struct sockaddr_in);
	while( (client_sock = accept(socket_desc, (struct sockaddr *)&client, (socklen_t*)&c)) )
	{
		sub_400e60(new_sock, client_sock, &connected_clients);
	}
	
	if (client_sock < 0)
	{
		perror("accept failed");
		return 1;
	}
	
	return 0;
}


bool sub_400ca4(int desc) {
	return (desc != -1);
}


bool sub_400cb4(int desc) {
	if(desc == -1) 
	{	
		printf("Could not create the socket");
		return false;
	}
	return true;
}

/*
 * This will handle connection for each client, it is invoked by the child process
 * */
void sub_400ce4(void *socket_desc)
{
	//Get the socket descriptor
	int sock = *(int*)socket_desc;
	int read_size;
	char *message , client_message[2000];
	
	//Send some messages to the client
	message = "New Connection handler!\n";
	write(sock , message , strlen(message));	
	
	//Receive a message from client
	while( (read_size = recv(sock , client_message , 1000 , 0)) > 0 )
	{
		write(sock , client_message , strlen(client_message));
	}
	
	if(read_size == 0)
	{
		puts("Client disconnected");
		fflush(stdout);
	}
	else if(read_size == -1)
	{
		perror("recv failed");
	}
		
	//Free the socket pointer
	free(socket_desc);
	
	return 0;
}


void sub_400e08(int conn)
{	
	int a = 2;
	int b = 123;
	int res = (a+b)/5;
       	res++;
	res -= conn;	
	if (conn == 3)
		printf("Success!!!\n");	
}


/*
 * Invoked for each incoming connection 
 */
void sub_400e60(int* new_sock, int client_sock, int* connected_clients) 
{
	pid_t pid;
		
	new_sock = malloc(1);
	*new_sock = client_sock;
	pid = fork();

	if(pid == -1) {
		perror("fork failed\n");
		return;
	}
	else if(pid > 0) {
		// parent
		*connected_clients += 1;	
		close(client_sock);
		sub_400e08(*connected_clients);
	}
	else {
		// child
		sub_400ce4((void*) new_sock);
	}
	puts("Handler assigned");

}
