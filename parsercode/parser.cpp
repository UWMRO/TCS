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
#ifndef __BCT30__
#include "bct30.h"
#endif

//bct30 pmc;

int parser(std::string input)
{	
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


