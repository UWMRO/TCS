/* This is a C++ telnet server for the new TCC to connect to the drivers without SWIG.
   This version can only handle one client at a time and will shutdown once the connection is lost.
   The client should then turn on this server, wait a sec for the port to be opened 
   and then continue.
   Compile with g++ listener.cpp
*/

#include <iostream>
#include <cstring> // Needed for memset 
#include <sys/socket.h>  // Needed for the socket functions
#include <netdb.h>  // Needed for the socket functions
#include <stdlib.h>
//#include <stdio.h>
//#include <sys/socket.h>
#include <unistd.h>

#define PORT "5501"

void Listener(void);

int main(int argc, char *argv[]) {

  Listener();
  
}


void Listener(void) {
  /* To start a server we need to first create a socket.  This happens with first defining your address
     info (e.g. IPv4 vs IPv6 or TCP vs UDP).  Once the socket has been made there is a descriptor used
     for the other methods.  One then needs to bind the socket which is to essentially reserve the 
     port for use.  After the code listens on that now open and reserved port.  Data is then 
     explicitely accepted and waits to recieve bites.*/
  int status;
  struct addrinfo host_info; // The struct that getaddrinfo() fills up with data.
  struct addrinfo *host_info_list; // holds list of different connections should be of size one

  // Uses getaddrinfo to succinctly build the socket
  memset(&host_info, 0, sizeof(host_info)); // allocates memory for the list of host.  Server
                                            // should just be one.

  std::cout << "Setting up the structs..." << std::endl;

  host_info.ai_family = AF_INET; // Uses IPv4 address; TCC IP is 192.168.1.10
  host_info.ai_socktype = SOCK_STREAM; // Uses SOCK_STREAM to define TCP protocol.
  host_info.ai_flags = AI_PASSIVE;  // IP Wildcard

  // Fill linked list of host_info structs with ip adresses of localhost.  One
  status = getaddrinfo(NULL, "5501", &host_info, &host_info_list);

  if(status != 0) {
	std::cout << "getaddrinfo error" << gai_strerror(status) << std::endl;
   
  }
  
  std::cout << "Creating a socket..." << std::endl;
  int socketfd; // Socket descriptor; passed a lot to function
  socketfd = socket(host_info_list->ai_family, host_info_list->ai_socktype, host_info_list->ai_protocol);
  if(socketfd == -1) {
	std::cout << "socket error ";
  }
  std::cout << "Binding socket..." << std::endl;
  int yes = 1;
  status = setsockopt(socketfd, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(int));
  status = bind(socketfd, host_info_list->ai_addr, host_info_list->ai_addrlen);
  if(status == -1) {
	std::cout << "bind error" << std::endl;
  }

  std::cout << "Listen()ing for connections.." << std::endl;
  status = listen(socketfd, 5); // up to five connections (can't handle all of them yet)
  
  // Check if successfully listen on binded port
  if(status == -1) {
	std::cout << "listen error" << std::endl;
  }
  
  int new_fd;
  struct sockaddr_storage their_addr;
  socklen_t addr_size = sizeof(their_addr);
  new_fd = accept(socketfd, (struct sockaddr*) &their_addr, &addr_size);
  
  if(new_fd == -1) {
	std::cout << "listen error" << std::endl;
  }
  else {
	std::cout << "Connection accepted. Using new socketfd : " << new_fd << std::endl;
  }

  std::cout << "Waiting to recieve data..." << std::endl;


  while(1) {

	ssize_t bytes_received;
	char incoming_data_buffer[1000];
	bytes_received = recv(new_fd, incoming_data_buffer, 1000, 0);

	if(bytes_received == 0) {
	  std::cout << "host shut down." << std::endl;
	  break;
	}
	if(bytes_received == -1) {
	  std::cout << "receive error!" << std::endl;
	  break;
	}

	/* Place parser code here.  Return a string up and then send that string with send.*/
	
	const char *msg = "receive data";
	send(new_fd, msg, strlen(msg), 0);

	std::cout << bytes_received << " bytes recieved :" << std::endl;
	incoming_data_buffer[bytes_received] = '\0';
	std::cout << incoming_data_buffer << std::endl;
  } 
  // clean up
  close(new_fd);
  close(socketfd);
  

}
