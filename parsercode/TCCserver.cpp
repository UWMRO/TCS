#include <iostream>
#include <fstream>
#include <math.h>
#include <stdio.h>
#include <sstream>
#include <stdlib.h>
#include <string.h>
#include <vector>
#include <algorithm>
#include <iterator>
#include <chrono>
#include <thread>
#include <unistd.h>
#include "mcapi.h"
#include "iomappings.h"
#ifndef __BCT30__
#include "bct30.h"
#endif

#include <cstring> // Needed for memset 
#include <sys/socket.h>  // Needed for the socket functions
#include <netdb.h>  // Needed for the socket functions


bct30 pmc;

double pastRApos=0.0;
double pastDECpos=0.0;

double RaRate=0.0;
double DecRate=0.0;

bool tracking=false;
//bool resumetracking=false;

void paddletimer()
{
	while ( 1 )
	{
		int x;
		x=300;
		std::this_thread::sleep_for(std::chrono::milliseconds(x));
		int isSlew = pmc.checkHandPaddle();	// has side-effect of setting 
		if (isSlew == 0 && tracking) 
			{
			pmc.track(RaAxis, RaRate);
			}	
	}
}

const char *parser(std::string input)
{	
	//std::cout << "reached parser" << std::endl;
	
	//std::cout << "through parser" << std::endl;
	std::string s = input;
	double RArate,Decrate;
	//test print
	//std::cout << "line 27: " << s << std::endl;

	std::string delimiter = " ";
	size_t n = std::count(s.begin(), s.end(), ' ')+1;
	std::string tokens[n];
	int begin=0;
	for(int i = 0;i < n; i++)
	{
		std::string token = s.substr(0,s.find(' '));
		//std::cout << "loop " << i << ": " << token << std::endl;
		tokens[i]=token;
		s=s.substr(s.find(' ')+1,s.length());
	}  

	if(tokens[0]=="slew")
	{
		std::cout << "slew " << tokens[1] << " "<< tokens[2] << " "<< tokens[3] <<std::endl;
		
		double RAtarget_degrees = ::atof(tokens[1].c_str());
		double DECtarget_degrees = ::atof(tokens[2].c_str());
		double LST = ::atof(tokens[3].c_str());
		double RAtarget_hrs, RAmove_2_deg, DECmove_2_deg;
		double RAvel, DECvel;
		
		RAtarget_hrs = RAtarget_degrees/15.0;
		
		RAmove_2_deg = (RAtarget_hrs - LST)*15.0; 
   		DECmove_2_deg = DECtarget_degrees - 46.951166666667; //mrolat
		const char *slew = "slew 1";
		if(fabs(RAmove_2_deg) > (8.0*15.0)) //maxHourAngle
   		{
      		const char *out= "Target RA exceeds max Hour Angle";
      		return out;
   		}
   		if(fabs(DECmove_2_deg) > 80.0) //maxZenith
   		{
      		const char *out= "Target DEC out of range";
      		return out;
   		}
   		pmc.getVelocity(RaAxis,&RAvel);
   		std::cout << RAvel <<std::endl;
		pmc.moveTo(RaAxis, &RAmove_2_deg);
		pmc.moveTo(DecAxis, &DECmove_2_deg);
		pmc.getVelocity(RaAxis,&RAvel);
		//std::cout << RAvel <<std::endl;
		return slew;
		
	}
	if(tokens[0] == "velmeasure")
	{
		double curRApos, curDECpos; // axis velocity
		
		pmc.getPosition(RaAxis, &curRApos); //ra in degrees
		pmc.getPosition(DecAxis, &curDECpos); //dec in degrees
		std::cout << curRApos << ' ' << curDECpos << std::endl;
		if(fabs(curRApos-pastRApos) < 0.0001 && fabs(curDECpos-pastDECpos) < 0.0001)
		{
			const char *out="velmeasure 1";
			return out;
		}
		else
		{
			pastDECpos = curDECpos;
			pastRApos = curRApos;
			const char *out="velmeasure 0";
			return out;
		}
		//std::ostringstream RAvelstr;
		//std::ostringstream DECvelstr;
		//RAvelstr << RAvel;
		//DECvelstr << DECvel;
		//std::string RAstr = RAvelstr.str();
		//std::string DECstr = DECvelstr.str();
		//return RAstr.c_str();
		//return key,RAstr.c_str(),DECstr.c_str();
	}
	if(tokens[0]=="status")
	{
		double ira_deg, idec_deg;
		
		//std::cout << "status begin" <<std::endl;
		pmc.getPosition(RaAxis, &ira_deg);	// for calculating the offsets
   		pmc.getPosition(DecAxis, &idec_deg);  //RA and DEC in degrees off zenith
   		//std::cout << ira_deg <<std::endl;
   		//std::cout << idec_deg <<std::endl;
   		double ira_hrs;
   		double LST_hrs = ::atof(tokens[3].c_str());
   		ira_hrs=ira_deg/15.0;
   		std::ostringstream RAstr;
		std::ostringstream DECstr;
		RAstr << LST_hrs-ira_hrs; //current RA in hours
		DECstr << 46.951166666667-idec_deg; //current DEC in degrees
   		std::string curRAstr = RAstr.str();
   		std::string curDECstr = DECstr.str();
   		std::string data=tokens[1]+" "+curRAstr+" "+curDECstr+" "+tokens[2]+" "+tokens[3];
   		std::ofstream log(tokens[4], std::ios_base::app | std::ios_base::out);
   		//myfile.open (tokens[4]);
   		log << data+"\n";
  		log.close();
  		const char *out = "File Written";
  		return out;
	}
	if(tokens[0] == "focus")
	{
		double focus_inc = ::atof(tokens[1].c_str());
		pmc.MoveRelative(FocusAxis, focus_inc);
		const char *focus = "focusing";
		return focus;
	}
	//std::cout << "offset incoming" << std::endl;
	if(tokens[0] == "offset")
	{
		const char *offset;
		std::cout << "offset " << tokens[1] << " "<< tokens[2] << tokens[3] << tokens[4] << std::endl;
		double inc = ::atof(tokens[2].c_str());
		double RATR= ::atof(tokens[4].c_str());
		pmc.stopSlew();
		if(tokens[1]=="N")
		{
			pmc.Jog(DecAxis,inc);
			offset = "offset N";
		}
		if(tokens[1]=="S")
		{
			pmc.Jog(DecAxis,-inc);
			offset = "offset S";
		}
		if(tokens[1]=="E")
		{
			pmc.Jog(RaAxis,inc);
			offset = "offset E";
		}
		if(tokens[1]=="W")
		{
			pmc.Jog(RaAxis,-inc);
			offset = "offset W";
		}
		if(tokens[3]=="True")
		{
			pmc.track(RaAxis, RATR);
		}
		return offset;
	}
	if(tokens[0] == "stop")
	{
		pmc.stopSlew();
		const char *nstop = "stop slew";
		return nstop;
	}
	if(tokens[0] == "track")
	{
		std::cout << "toggling tracking\n";
		if(tokens[1] == "on")
		{
			tracking = true;
			RaRate = ::atof(tokens[2].c_str());
			DecRate = ::atof(tokens[3].c_str());
		 	if((RaRate > 25) || (RaRate < -10))
		 	{
      			const char *out= "Ra rate must be between -10 and 25 deg/hr.";
      			return out;
   			}
      		if((DecRate > 25) || (RaRate < -10)) 
	 		{
      			const char *out= "Dec rate must be between -10 and 25 deg/hr.";
      			
      			return out;
   			}
   			pmc.stopSlew();
			pmc.track(RaAxis, RaRate);
	 		//pmc.track(DecAxis, DecRate);
	 		//pmc.track();
	 		const char *out= "Tracking Enabled";
      		return out;
		}
		if(tokens[1] == "off")
		{
			tracking = false;
			pmc.stopSlew();
			const char *out= "Tracking Disabled";
      		return out;
		}
		const char *out= "Invalid Command";
      	return out;
	}
	if(tokens[0] == "halt")
	{
		const char *out= "Emergency Stop";
		pmc.estop(RaAxis);
		pmc.estop(DecAxis);
		return out;
	}
	if(tokens[0] == "trackingstatus")
	{
		std::cout << "tracking status\n";
		return 0;
	}
	if(tokens[0] == "coverpos")
	{
	static double RaCover = 0;
    static double DecCover = 5115086;
    
	pmc.stopSlew();	// stop any motion. 
	pmc.MoveAbsolute(RaAxis, RaCover);	// see globals.h for Ra/DecCover values
    pmc.MoveAbsolute(DecAxis, DecCover);
    const char *out = "Slewed to Cover Position";
	return out;
	}
	if(tokens[0] == "park")
	{
	pmc.MoveAbsolute(RaAxis, 0.0);
    pmc.MoveAbsolute(DecAxis, 0.0);
    const char *out = "Parked Telescope";
	return out;
	}
	if(tokens[0] == "zenith")
	{
	pmc.setZenith();	// reset encoders to zeros
	const char *out = "Telescope at Zenith";
	return out;
	}
	if(tokens[0] == "point")
	{
	double ira_deg, idec_deg;	// initial values
    double ra_deg, dec_deg;	//encoder positions in decimal degrees
    double LST = ::atof(tokens[3].c_str());
    double RA = ::atof(tokens[1].c_str());
    
    pmc.getPosition(RaAxis, &ira_deg);	// for calculating the offsets
    pmc.getPosition(DecAxis, &idec_deg); //
    
    ra_deg = RA - (LST*15.0);
   	//ra_deg = -ra_deg; //pmc.setPosition input fix
   	
   	dec_deg = 46.951166666667 - LST;
   	
   	pmc.setPosition(RaAxis, &ra_deg);
    pmc.setPosition(DecAxis, &dec_deg);
    
    const char *out= "Pointing set";
    return out;
	}
	return "Invalid Command";
	
	
	
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
	
	//std::cout << bytes_received << " bytes recieved" << std::endl;
	incoming_data_buffer[bytes_received] = '\0';
	
	std::string input = (std::string) incoming_data_buffer;
	//std::cout << "reached " <<input << std::endl;
	//std::cout << "reached line 229" << std::endl;
	const char* results = parser((std::string) incoming_data_buffer);
	//std::cout << "reached line 231" << std::endl;
	//std::cout << "results are: " << results << std::endl;
	//const char *msg = "receive data";
	std::cout << results << std::endl;
	//send(new_fd, results, strlen(results), 0);

	
	//incoming_data_buffer[bytes_received] = '\0';
	//std::cout << incoming_data_buffer << std::endl;
  } 
  // clean up
  close(new_fd);
  close(socketfd);
  

}

int main(int argc, char *argv[])
{
	pmc.init();
	std::thread t1(paddletimer);
	Listener();
	t1.join();
	/*
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
	*/
	return 0;
}


