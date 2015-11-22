

#ifndef __BCT30__
#define __BCT30__

#include <iostream>
#include "mcapi.h"
#include "indiapi.h"

//#define Ra 1	// PMC board axis n assigned to <name> servo
//#define Dec 2
//#definse Focus 3

using namespace std;

typedef enum  {STOP, NORTH, SOUTH, EAST, WEST} SlewDir;

class bct30 {
public:
	
	bct30(void);	// default constructor
	//~bct30() {}	// destructor
	~bct30();

	bool manualSlewing;	// we're currently slewing if TRUE
	
/** setup **/
	int OpenController(void);
	int init(void);
/** set commands **/
	int setZenith(void);	// call once the scope has been manually set to zenith
	void Reset(int AxisNumber);
	void setPosition(int AxisNumber, double *degrees);

/** Motion Commands **/
	int checkHandPaddle();
	void checkHandPaddle2();
	void stopSlew(int AxisNumber);
	void stopSlew();		// all axes
	void estop(int AxisNumber);
	void estop();			// all axes
	void enableAmp(int AxisNumber, bool state);	// enable axis amp
	int Jog(int AxisNumber, double distance);
	int moveTo(int AxisNumber, double *degrees);
	void track(void); // track RA axis at standard sidereal rate
	int track(int AxisNumber, double rate);
	void moveRelativeDegrees(int AxisNumber, double *degrees);

// debug only
	void MoveRelative(int AxisNumber, double distance);	// encoder level (debug)
	void MoveAbsolute(int AxisNumber, double distance);	// encoder level (debug)

/** Reporting commands **/
	int getEncoderCnt(int AxisNumber, double *posit);	// double because MC uses double
	int getPosition(int AxisNumber, double *degrees);	// degrees from zenith
	void getVelocity(int AxisNumber, double *velocity);
	short int getDigitalIO(int channel);
	void TranslateError(char *buff, int buff_len);
	short int GetError();
	bool IsAtTarget(int AxisNumber);
	bool IsStopped(int AxisNumber);
	void GetFollowingError(int AxisNumber, double *error);
	void reportLimitSwitches(void);
	void getStatus(int AxisNumber, DWORD *stat);
	void getMode(int AxisNumber, int *mode);	// 0-vel, 1-position
   
private:

	double RAtarget_cnt; // for IsAtTarget
	double DECtarget_cnt;
	int fuckit;

	HCTRLR hCtlr;	// PMC controller handle
	bool ZenithIsSet;	// must = TRUE for setObjectRA/DEC and Slew() to return success
	double posit;	// raw encoder count
	SlewDir RaSlewDirection;
	SlewDir DecSlewDirection;
	int mode;	// position, velocity mode
	MCPARAM Param;	// axis parameters
	MCSCALE MSscale;	// scale motion params to real-world values
	MCMOTIONEX pMotion;	// motion configuration structure
	MCFILTEREX pFilter;	// pid filter params
	WORD pMode;		// digital io channel settings
	MCJOG pJog;
	double position;	// axis raw encoder count 
	double target_position; // target encoder count
	double distance;	// encoder counts
	int ret;		// return values
	MCSTATUSEX        NewStatus;
	int initAxis(int AxisNumber);


/* set commands */
	int setEncoderToZero(int AxisNumber);

/* conversion commands */



};
#endif
