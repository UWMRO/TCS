/* $Id: iomappings.h,v 1.1 2007/04/08 20:49:41 jdosher Exp $ */
/* 
   This file maps the channels on the PMC motion controller card to C/C++ variables
   ->Connector J1 on the PMC card: Servos, axis 1 & 2
   Connector J2 on the PMC card: Servos, axis 3 & 4
   Connector J3 on the PMC card: Steppers, axis 5 & 6
   ->Connector J4 on the PMC card: Steppers, axis 7 & 8

   Ra Servo: 1
   Dec Servo: 2
   Focus stepper: 
   
*/

// Servos
#define RaAxis		1
#define DecAxis		2
#define RaAmpEnable	49	// digital I/O channel 53
#define DecAmpEnable	53


// Steppers
#define FocusAxis	8
#define FocusAmpEnable	46	// PIN 20, J4

/* digital I/O */     //channel number
#define JogWest		1
#define JogEast		2
#define JogNorth	3
#define JogSouth	4
#define SetSlew		14 // the hand paddle set/slew switch 






