/* filterslide object */

/* class fslide communicates with the filterslide controller over the serial
 * port */

#include <stdio.h>
#include <iostream>

#ifndef __GLOBALS__
#include "globals.h"
#endif

#include <stdio.h>   /* Standard input/output definitions */
#include <string.h>  /* String function definitions */
#include <iostream>
#include <unistd.h>  /* UNIX standard function definitions */
#include <fcntl.h>   /* File control definitions */
#include <sys/ioctl.h>   /* For reading serial buffer count directly */
#include <errno.h>   /* Error number definitions */
#include <termios.h> /* POSIX terminal control definitions */
#include <time.h>    /* for nanosleep and clock */
#include <sys/time.h>/* for gettimeofday() */
#include <stdlib.h>  /* for EXIT_FAILURE */



#include "fslide.h"

#define BAUDRATE 1200

using namespace std;

fslide::fslide(void)
{
   cout << "Setting up serial port" << endl;
   fflush(stdout);
   setup_port();
  
   
  
}

int fslide::setup_port()
{

   char errorstr[100];
   int i;	
	
   fd = open(FSLIDE_PORT, O_RDWR | O_NOCTTY | O_NDELAY | O_NONBLOCK); // jd added NONBLOCK
   if (fd == -1)
   {
		
      /* Could not open the port. */
      cout << "Error: Unable to open port " << FSLIDE_PORT 
	   << "\nMake sure username is /etc/groups for uucp, eg: uucp::14:uucp,mrouser \n\n";
      perror(errorstr);
      //return( SERIAL_ERR_OPEN_PT);
      //exit(EXIT_FAILURE);
   }
   else
   {
      //	fcntl(fd, F_SETFL, 0); /* set the port to block on no data */
      fcntl(fd, F_SETFL, FNDELAY);
	
      cout << "Port opened" << endl;

// configure port settings

      if(tcgetattr(fd, &port)<0) return(SERIAL_ERROR);

      cfsetispeed(&port, BAUDRATE);	// 1200
      cfsetospeed(&port, BAUDRATE);

      port.c_cflag &= ~CSIZE; /* Mask the character size bits */
      port.c_cflag |= CS8;    /* Select 8 data bits */

      /* set port to 8N1 */
      port.c_cflag &= ~PARENB;
      port.c_cflag &= ~CSTOPB;
      port.c_cflag &= ~CSIZE;
      port.c_cflag |= CS8;

      port.c_cflag |= (CLOCAL | CREAD);
      port.c_cflag &= ~CRTSCTS; /* this should turn off hdwr flow ctl */

      /* Check Parity, strip parity bits, map CR to NL */
      //port.c_iflag &= (INPCK | ISTRIP | ICRNL | IGNBRK ); 
      //port.c_iflag &= (IGNPAR); 
      port.c_iflag |= (IGNPAR | ICRNL); 

      port.c_oflag &= ~OPOST; /* Sets output to raw (unprocessed) */
      //port.c_oflag |=  OPOST; /* Sets output to PROCESSED */
      //port.c_oflag |=  NLDLY;
      //port.c_oflag |=  CRDLY;
      //port.c_oflag |=  VTDLY;
      port.c_oflag |= (NL0|CR0|VT0);
      //port.c_oflag &= ~OPOST; /* Sets output to raw (unprocessed) */

      port.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG); // we're in raw mode

      i=tcsetattr(fd, TCSANOW, &port);
      //printf("tcseattre RETURN val: %i\n", i);
      //get_port_info(fd);
      return(i);
   }



}

/* sends 'i' to the filterslide. Appearently this doesn't need to be done - ? */
void fslide::Initialize(void)
{
   write_serial("i"); // init the controller

}

/* 'm' is the move command, m2 goes to slide 2 */
void fslide::MoveToFilter(int n)
{

   string cmd;
   char tmp[4];
   sprintf(tmp,"m%d",n); 
   cmd = tmp;
   write_serial(cmd);


}

int fslide::ReportCurrentPosition(void)
{
   string out_string;
   string filterPos;
   write_serial("s");
   out_string.clear();
   read_serial(&out_string);
   cout << "out_string: " << out_string;
   if(out_string.length() > 0){
      filterPos = out_string.substr(0,1);
      cout << "filterPos: " << filterPos << endl;
   }
   




}

int fslide::write_serial(string in_string)
{
   // cout << "writing to serial: " << in_string << endl;
   //char tmp[MAXLINELEN]; 
   in_string = in_string + "\n";
   //cout << "Writing Cmd: " << in_string;
   bzero(buffer, MAXLINELEN);
   strncpy(buffer, in_string.c_str(), in_string.length() );
   bytes = strlen(buffer);
   bytes = write(fd, buffer, bytes);
   tcdrain(fd);

   if (bytes < 0)
   {
      perror("write_serial: returned error code");
      return(SERIAL_ERR_WRITE);
   }

   return(bytes);
}

ssize_t fslide::read_serial(string *out_string)
{
   bytes = 0;
  
   //char data[MAXLINELEN];
   bzero(buffer, MAXLINELEN);		// zero out buffer
   //sprintf(buffer, &in_string->c_str());

   bytes = read(fd, buffer, MAXLINELEN);	// read data
   *out_string = buffer;
  
   // cout << "Read from serial: " << *out_string << endl;
   //tcdrain(fd);
   return(bytes); // returns the number of bytes read
 

}





