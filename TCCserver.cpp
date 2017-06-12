#include <iostream>
#include <sys/socket.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <netinet/in.h>


int main(int argc, char *argv[])
{	
	std::cout << "Hello World\n";
	int sockfd,newsockfd,portno;
	socklen_t clilen;
	
	char buffer[256];
	
	struct sockaddr_in serv_addr, cli_addr;
	int n;
	if(argc < 2) 
	{
		std::wcerr << "Error, no port provided\n";
		return 1;
	}

	sockfd = socket(AF_INET,SOCK_STREAM,0);
	if(sockfd < 0)
	{
		std::wcerr <<"ERROR opening socket";
		return 1;
	}
	bzero((char *) &serv_addr, sizeof(serv_addr));
	portno=atoi(argv[1]);
	serv_addr.sin_family = AF_INET;
	serv_addr.sin_addr.s_addr= INADDR_ANY;
	serv_addr.sin_port = htons(portno);
	
	if(bind(sockfd,(struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0)
	{
	std::wcerr <<"ERROR on binding";
	return 1;
	}
	listen(sockfd, 5);
	clilen = sizeof(cli_addr);
	newsockfd = accept(sockfd, (struct sockaddr *) &cli_addr, &clilen);
	if(newsockfd < 0)
	{
		std::wcerr << "ERROR on accept";
		return 1;
	}
	bzero(buffer, 256);
	n= read(newsockfd,buffer,255);
	if(n<0)
	{
		std::wcerr << "ERROR reading from socket";
		return 1;
	}
	printf("Here is the message: %s\n", buffer);
	n= write(newsockfd, "I got your message",18);
	if(n < 0)
	{
		std::wcerr << "ERROR writing to socket";
		return 1;
	}
	close(newsockfd);
	close(sockfd);
	return 0;
	
	
	
	
	
	
	
	
	
}
