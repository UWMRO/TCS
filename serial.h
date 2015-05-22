/* this file contains header information specific to serial.c */



#ifndef _SERIAL_H_
#define _SERIAL_H_


#define MAXLINELEN 	1024
//#define RFID_PORT	"/dev/ttyS0"
//#define MOTOR_PORT	"/dev/ttyS1" //1
//#define BAUDRATE B38400
#define INIT_BAUDRATE  B19200 // Used for opening port and initialization
//#define INIT_BAUDRATE  B38400
#define FAST_BAUDRATE  B38400 // After init, sets and runs at this rate.
//#define WAIT_ECHO        0.01 // Maximum wait time forcommand echo (in sec)
//#define WAIT_RESPONSE     0.5 // Maximum wait time for command response (in sec)
#define WAIT_ECHO          25 // Maximum wait time for servo command echo (in msec)
#define WAIT_RESPONSE      80 // Maximum wait time for servo command response (in msec)
#define WAIT_PEND       10000 // Maxumum wait time for "pending" a serial servo response
#define WAIT_RFID        7000 // Maximum wait time for RFID serial response <ETX>
#define ASCII_ETX        0x03 // End of Text byte, used by RFID to signal end of comm. 
#define SERIAL_OK           0 // General Success Flag for serial Communications
#define SERIAL_ERROR       -1 // General error for serial communications 
#define SERIAL_ERR_ECHO    -2 // Indicates no command echo received
#define SERIAL_ERR_RESP    -3 // Expected response to command not reveived (timeout)
#define SERIAL_ERR_PEND    -4 // Pending response outlasted the WAIT_PEND time
#define SERIAL_ERR_OPEN_PT -5 // Failed to Open port
#define SERIAL_ERR_WRITE   -6 // Failed to Write to Port
#define SERIAL_CHKSUM_ERR  -7 // RFID serial Checksum Failed
#ifndef TRUE
#define TRUE                1
#endif
#ifndef FALSE
#define FALSE               0
#endif


// Flush buffers, Write command to given address, check for command echo and concatenate any
// response into *answer.  *answer may have numerous CR or NL characters (consider a single command 
// that draws multiple responses)  
// IMPORTANT: Make sure the string buffer pointed to by *answer is large enough to handle the data 
// AND        *** You porbably want to empty "answer" before calling this fxn, it adds, not overwrites ***
// Returns:   SERIAL_OK upons succes, or SERIAL_ERR_ECHO if no echo, or SERIAL_ERR_RESP if no response.
int do_command_no_response(int fd, char *command);                              // Ecpects no answer (only checks for echo)
int do_command_w_response(int fd, char *command, char *answer);                 // expects only one answer (CR or NL) and echo
int do_command_w_response(int fd, char *command, char *answer, int answer_num); // expects answer_num answers (CR's or NL's) and echo
// This does the same thing as do_command_w_response, but it waits much longer (WAIT_PEND ms)
// Returns SERIAL_OK upon success, SERIAL_ERR_ECHO if no echo, or SERIAL_ERR_PEND if no response at all or in time.
int do_command_pend_response(int fd, char *command, char *answer, int answer_num); // expects answer_num answers (CR's or NL's) and echo

int do_command_nochk(int fd, char *command, char *answer); // obsolete
int do_command_rfid_no_checksum(int fd, char * command, char * response); //Sends command, returns 
int get_line(int fd, char *line);
int open_port(char *port);
int close_port(int fd);
int read_serial_old(int fd, char *string);
int read_serial(int fd, char *string);
int read_serial2(int fd, char *string); // Assumes Null terminator for all incoming data
                                        // Only if Null Term ('\r' '\n') reached and read
                                        // does this fxn return; if this fails, timeouts w/ error; converts '\r' to '\n'

// Reads in num_bytes from fd(serial file pointer).  Returns SERIAL_OK on success
// Retruns SERIAL_ERR on Faiure.
int read_n_serial(int fd, char *string, int num_bytes);
int check_for_response(int fd, char *expected_str, char * input_str);
int setup_port(int fd);
int write_serial(int fd, char *string);
int init_servos(int fd, char motor0, char motor1, char motor2); 
int serial_fast_baudrate(int fd);
// strips string of 1st space if there, returns number of spaces removed or -1 on failure
int str_strip_1st_space(char *string);
int str_CR_to_NL(char *string);  // Converts any CR (\r) characters to NL (\n)
/***********************************************************************
 * setup the serial port with the faster baud rate and stuff we want to have.
 ***********************************************************************/
int setup_port_fast(int fd);

int get_port_info(int fd);

void print_non_ascii(char * str);

#endif /* _SERIAL_H_ */
