/*

*/
#ifndef __FSLIDE__
#define __FSLIDE__


#include <termios.h> /* POSIX terminal control definitions */
#include <string>

#include "serial.h"

using namespace std;

class fslide {
public:

   fslide(void);
   ~fslide() {}
   void Initialize(void);
   void MoveToFilter(int n);   
   ssize_t read_serial(string *out_string); 
   int write_serial(string in_string);  
   int ReportCurrentPosition(void);


private:
   int setup_port();

   struct termios port;
   //termios port;
   int fd;
   ssize_t bytes;

   char in_buffer  [MAXLINELEN];  	// char array for input (response) strings
   char out_buffer [MAXLINELEN];  	// char array for command strings
   char buffer [MAXLINELEN];

protected:
   
   
};
#endif
