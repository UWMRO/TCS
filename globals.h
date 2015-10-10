#define __GLOBALS__

#ifndef TRUE
#define TRUE 1
#endif
#ifndef FALSE
#define FALSE 0
#endif
#define HIGH 1
#define LOW 0

#define SLOW 0
#define FAST 1


/* 1 enc count equals 0.05 arcseconds of motion (degrees, not time)
   20 counts equals 1 arcsecond
   15 deg/hr == 15 arcsec/sec
   15 arcsec/sec * enc_cnts/.05arcsec = 300 enc_cnts/sec - Sidereal tracking
   1 degree = 3600 arcseconds ==> 20*3600 = 72,000 encoder counts per degree
*/

#define SLEW_VELOCITY 120000	// encoder cnts per second
#define SET_VELOCITY    3000

/* Unit conversions */
// jd
static double ARCSEC_PER_CNT = 0.05; // from old tcc code
//static int SIDEREAL_CNT_PER_SEC = 300; // 300 encoder cnts/sec at standard sidereal rate
static double SIDEREAL_RATE = 15.04108;

static double SIDEREAL_CNT_PER_SEC = SIDEREAL_RATE/ARCSEC_PER_CNT;



static double mrolong = 120.7233333333;

static float DEGPERRAD = 57.2957795131;
static float RADPERHR = 0.2617993987799;
static float mrolatinrads = 0.819452445986;
static float mrolat = 46.951166666667;

/* motion limits wrt zenith */
static double maxZenith = 80.0;		// degrees
static double maxDecAngle = 90.0;	// degrees
static double maxHourAngle = 8.0;	// hours

/* the remove/replace cover position (in encoder counts) */
static double RaCover = 0;
static double DecCover = 5115086;

/* 
   15 deg/hr == 15 arcsec/sec
   15 arcsec/sec * enc_cnts/.05arcsec = 300 enc_cnts/sec 

*/


#define DEC_CNTS_PER_REV  2000

#define DEG_PER_CNT 1.38888889e-5	// degrees per encoder count
#define HRS_PER_CNT 9.25925925e-7	// hours per encoder count
//#define SIDEREAL_RATE 18.20648	// encoder ticks per second at siderial
//#define SIDEREAL_RATE 36.20648	// encoder ticks per second at siderial

/* filter slide */
static double FSLIDE_INCREMENT = 4500;	// cnts for focus in/out
#define FSLIDE_PORT "/dev/ttyS0"
//#define MAXLINELEN	2000
#define BAUDRATE	1200
/* serial errors */
#define SERIAL_ERROR       -1 // General error for serial communications
#define SERIAL_ERR_OPEN_PT -5
#define SERIAL_ERR_WRITE   -6 // Failed to Write to Port

