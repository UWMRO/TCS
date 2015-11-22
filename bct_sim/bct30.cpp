using namespace std;

#include <stdio.h>
#include "bct30.h"

int main(){
}

bct30::bct30(void)
{
    printf("bct30 constructor called\n");
}

bct30::~bct30()
{
    printf("bct30 destructor called\n");
}



/******* private commands *********/
int bct30::OpenController(void)
{
    printf("OpenController(void) called\n");
}


/******* public commands *********/


/* public get commands */

/*    Return the raw encoder count */
int bct30::getEncoderCnt(int AxisNumber, double *posit)
{
    printf("getEncoderCnt(%d, posit_ref) called\n", AxisNumber);
}


/* calculate axis position in degrees Zero degrees is defined as zenith,
   and these are "raw" degrees from zenith

   N = positive, S = negative
   E = negative, W = positive

   NB: Looking west of zenith is +hr angle, so we'll
   also call that positive degreesOffZenith
*/
int bct30::getPosition(int AxisNumber, double *degrees)
{
    printf("getPosition(%d, degrees_ref) called\n", AxisNumber);
}

void bct30::getVelocity(int AxisNumber, double *velocity)
{
    printf("getVelocity(%d, velocity_ref) called\n", AxisNumber);
}


short int bct30::getDigitalIO(int channel)
{
    printf("getDigitalIO(%d) called\n", channel);
}

// return a human-readable string
void bct30::TranslateError(char *buff, int buff_len)
{
    printf("TranslateError(%s, %d) called\n", buff, buff_len);
}

short int bct30::GetError()
{
    printf("GetError() called\n");
}


/* public set commands */


int bct30::setZenith(void)
{
    printf("setZenith(void) called\n");
}

int bct30::setEncoderToZero(int AxisNumber)
{
    printf("setEncoderToZero(%d) called\n", AxisNumber);
}

/* set current encoder value to degrees off zenith */
void bct30::setPosition(int AxisNumber, double *degrees)
{
    printf("setPosition(%d, degrees_ref) called\n", AxisNumber);
}

/** Motion Commands **/
/* normal stop */
void bct30::stopSlew(int AxisNumber)
{
    printf("stopSlew(%d) called\n", AxisNumber);
}

/* normal stop */
void bct30::stopSlew()
{
    printf("stopSlew() called\n");
}

/* Estop - abrupt stop */
void bct30::estop(int AxisNumber)
{
    printf("estop(%d) called\n", AxisNumber);
}

void bct30::estop(void)
{
    printf("estop(void) called\n");
}


void bct30::enableAmp(int AxisNumber, bool state)
{
    printf("enableAmp(%d,", AxisNumber);
    if (state)
        printf(" True) called\n");
    else
        printf(" False) called\n");
}



bool bct30::IsAtTarget(int AxisNumber)
{
   printf("IsAtTarget() called\n");
}


bool bct30::IsStopped(int AxisNumber)
{
    printf("IsStopped(%d) called\n", AxisNumber);
}


/* distance == encoder counts
   Positive encoder cnts Ra  == East
   Positive encdoer cnts Dec == South
*/
void bct30::MoveRelative(int AxisNumber, double distance)
{
    printf("MoveRelative(%d, %f) called\n", AxisNumber, distance);
}


/* Jog 'distance' arcsecs. 20 enc cnts = 1 arcsec
   Used for the N,S,E,W jog buttons in the Qt interface. Return value used
   to determine when we're done, and un-gray jog buttons in Qt interface */

int bct30::Jog(int AxisNumber, double distance)
{
    printf("Jog(%d, %f) called\n", AxisNumber, distance);
}


/* scope must be properly set to zenith of ra=0 dec=0 encoder counts,
   or all bets are off.
   degrees wrt zenith. Positive degrees = east
   Input is in degrees, we convert to encoder counts
*/
int bct30::moveTo(int AxisNumber, double *degrees)
{
    printf("moveTo(%d, degrees_ref) called\n", AxisNumber);
}


/* position is encoder counts */
// something is strange here. After a hand-paddle move, this function fails
// to work - do another hand-paddle move, it works ??

void bct30::MoveAbsolute(int AxisNumber, double position)
{
    printf("MoveAbsolute(%d, %f) called\n", AxisNumber, position);
}


/* track at standard sideral rate */
void bct30::track(void)
{
    printf("track(void) called\n");
}


/* Track at non-sidereal rate. rate is arcsec/sec (or deg/hr) */
int bct30::track(int AxisNumber, double rate)
{
    printf("track(%d, %f) called\n", AxisNumber, rate);
}

/* move degrees off zenith */
void bct30::moveRelativeDegrees(int AxisNumber, double *degrees)
{
    printf("moveRelativeDegrees(%d, degrees_ref) called\n", AxisNumber);
}

int bct30::checkHandPaddle()
{
    printf("checkHandPaddle() called\n");
}

/* a safer, position-based jog */
/* depricated: regular jog seems fine now */
void bct30::checkHandPaddle2()
{
    printf("checkHandPaddle2() called\n");
}

void bct30::GetFollowingError(int AxisNumber, double *error)
{
    printf("GetFollowingError(%d, error_ref) called\n", AxisNumber);
}

void bct30::Reset(int AxisNumber)
{
    printf("Reset(%d) called\n", AxisNumber);
}

void bct30::getStatus(int AxisNumber, int *stat)
{
    printf("getStatus(%d, stat_ref) called\n", AxisNumber);
}

void bct30::getMode(int AxisNumber, int *mode)
{
    printf("getMode(%d, mode_ref) called\n", AxisNumber);
}

/*******************************
      initialize an axes
********************************/
int bct30::initAxis(int AxisNumber)
{
    printf("initAxis() called\n");
}


