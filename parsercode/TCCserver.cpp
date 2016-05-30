#include <iostream>
#include <stdio.h>
#include <sstream>
#include <stdlib.h>
#include <string.h>
#include <vector>
#include <algorithm>
#include <iterator>
#include <unistd.h>
//#include "home/mro/mcapi/mcapi-4.4.1/src/mcapi.h"
#include "mcapi.h"
#include "bct30.h"

#include <cstring> // Needed for memset 
#include <sys/socket.h>  // Needed for the socket functions
#include <netdb.h>  // Needed for the socket functions


bct30 pmc;

const char *parser(std::string input)
{	
	pmc.init();
	std::string s = input;
	std::string delimiter = " ";
	size_t n = std::count(s.begin(), s.end(), ' ')+1;
	std::string tokens[n];
	int begin=0;
	for(int i = 0;i < n; i++)
	{
		std::string token = s.substr(0,s.find(' '));
		tokens[i]=token;
		s=s.substr(s.find(' ')+1,s.length());
	}  

	if(tokens[0]=="slew")
	{
		std::cout << "slew " << tokens[1] << " "<< tokens[2] <<std::endl;
		/*
		double ra = ::atof(tokens[1].c_str());
		double dec = ::atof(tokens[2].c_str());
		pmc.moveTo(0,&ra);
		pmc.moveTo(1,&dec);
		
		int deg, hour, min;
   		double sec;
   		double target_degrees, current_degrees, temp_degrees;
   		double RAtarget_degrees, DECtarget_degrees; // the target, in degrees

   
   		double SDdeg;
  
   		bool ok;
   		//QString L;  		


   		// positive degrees == East
   		RAmove_2_deg = (tokens[1] - LST)*15.0; 
   		DECmove_2_deg = tokens[2] - mrolat;

		//   bct30::moveTo, degrees are decimal degrees
   		if(fabs(RAmove_2_deg) > (maxHourAngle*15.0))
   		{
      		info("Target RA out of range");
      		slewstate = IDLE;
      		return;
   		}
   		if(fabs(DECmove_2_deg) > maxZenith)
   		{
      		info("Target DEC out of range");
      		slewstate = IDLE;
      		return;
   		}

  
   		// if moveTo returns non-zero, something is wrong with the range
   		if(pmc.moveTo(RaAxis, &RAmove_2_deg)) 
   		{
      		halt();
      		slewstate = IDLE;
      		return;
   		}

   		else if(pmc.moveTo(DecAxis, &DECmove_2_deg))
   		{
      		halt();
      		slewstate = IDLE;
      		return;
   		}
   		else 
      		slewstate = PERFORMING;


		}
		*/
		return 0;
		
	}
	if(tokens[0] == "focus")
	{
		std::cout << "focus " << tokens[1] <<std::endl;
		return 0;
	}
	if(tokens[0] == "offset")
	{
		std::cout << "offset " << tokens[1] << " "<< tokens[2] << std::endl;
		return 0;
	}
	if(tokens[0] == "settrackingrate")
	{
		std::cout << "set tracking rate\n";
		return 0;
	}
	if(tokens[0] == "stop")
	{
		std::cout << "stop\n";
		pmc.stopSlew();
		//const char *nstop = "nstop 1";
		return 0;
	}
	if(tokens[0] == "toggletrack")
	{
		std::cout << "toggle the track\n";
		return 0;
	}
	if(tokens[0] == "halt")
	{
		std::cout << "halt\n";
		pmc.estop(1);
		pmc.estop(0);
		return 0;
	}
	if(tokens[0] == "trackingstatus")
	{
		std::cout << "tracking status\n";
		return 0;
	}
	
	
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

int main(int argc, char *argv[])
{
	std::string data;
	std::string spacer= " ";
	data.append(std::string(argv[1]));
	for(int i = 2;i < argc; i++)
	{
	data.append(spacer);
	data.append(std::string(argv[i]));
	}
	//std::cout << data;
	
	std::string input = data.c_str();
	//std::cout << input;
	parser(input);
	return 0;
}


