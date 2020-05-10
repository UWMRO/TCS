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


