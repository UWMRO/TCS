using namespace std;

#include <stdio.h>
#include "bct30.h"

int main(){
}

bct30::bct30(void)
{

}

bct30::~bct30()
{

}



/******* private commands *********/
int bct30::OpenController(void)
{

}


/******* public commands *********/


/* public get commands */

/*    Return the raw encoder count */
int bct30::getEncoderCnt(int AxisNumber, double *posit)
{
    printf("getEncoderCnt() called");
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
    printf("getPosition() called.");
}

void bct30::getVelocity(int AxisNumber, double *velocity)
{
    printf("getVelocity() called.");
}


short int bct30::getDigitalIO(int channel)
{
    printf("getDigitalIO() called.");
}

// return a human-readable string
void bct30::TranslateError(char *buff, int buff_len)
{
    printf("TranslateError called.");
}

short int bct30::GetError()
{
    printf("GetError called.");
}


/* public set commands */


int bct30::setZenith(void)
{
    printf("setZenith() called.");
}

int bct30::setEncoderToZero(int AxisNumber)
{
    printf("setEncoderToZero() called.");
}

/* set current encoder value to degrees off zenith */
void bct30::setPosition(int AxisNumber, double *degrees)
{
    printf("setPosition() called.");
}

/** Motion Commands **/
/* normal stop */
void bct30::stopSlew(int AxisNumber)
{
    printf("stopSlew() called.");
}

/* normal stop */
void bct30::stopSlew()
{
    printf("stopSlew() called.");
}

/* Estop - abrupt stop */
void bct30::estop(int AxisNumber)
{
    printf("estop() called.");
}

void bct30::estop(void)
{
    printf("estop() called.");
}


void bct30::enableAmp(int AxisNumber, bool state)
{
    printf("enableAmp() called.");
}



bool bct30::IsAtTarget(int AxisNumber)
{
   printf("IsAtTarget() called.");
}


bool bct30::IsStopped(int AxisNumber)
{
    printf("IsStopped() called.");
}


/* distance == encoder counts
   Positive encoder cnts Ra  == East
   Positive encdoer cnts Dec == South
*/
void bct30::MoveRelative(int AxisNumber, double distance)
{
    printf("MoveRelative() called.");
}


/* Jog 'distance' arcsecs. 20 enc cnts = 1 arcsec
   Used for the N,S,E,W jog buttons in the Qt interface. Return value used
   to determine when we're done, and un-gray jog buttons in Qt interface */

int bct30::Jog(int AxisNumber, double distance)
{
    printf("Jog() called.");
}


/* scope must be properly set to zenith of ra=0 dec=0 encoder counts,
   or all bets are off.
   degrees wrt zenith. Positive degrees = east
   Input is in degrees, we convert to encoder counts
*/
int bct30::moveTo(int AxisNumber, double *degrees)
{
    printf("moveTo() called.");
}


/* position is encoder counts */
// something is strange here. After a hand-paddle move, this function fails
// to work - do another hand-paddle move, it works ??

void bct30::MoveAbsolute(int AxisNumber, double position)
{
    printf("MoveAbsolute() called.");
}


/* track at standard sideral rate */
void bct30::track(void)
{
    printf("track() called.");
}


/* Track at non-sidereal rate. rate is arcsec/sec (or deg/hr) */
int bct30::track(int AxisNumber, double rate)
{
    printf("track() called.");
}

/* move degrees off zenith */
void bct30::moveRelativeDegrees(int AxisNumber, double *degrees)
{
    printf("moveRelativeDegrees() called.");
}

int bct30::checkHandPaddle()
{
    printf("checkHandPaddle() called.");
}

/* a safer, position-based jog */
/* depricated: regular jog seems fine now */
void bct30::checkHandPaddle2()
{
    printf("checkHandPaddle2() called.");
}

void bct30::GetFollowingError(int AxisNumber, double *error)
{
    printf("GetFollowingError() called.");
}

void bct30::Reset(int AxisNumber)
{
    printf("Reset() called.");
}

void bct30::getStatus(int AxisNumber, int *stat)
{
    printf("getStatus() called.");
}

void bct30::getMode(int AxisNumber, int *mode)
{
    printf("getMode() called.");
}

/*******************************
      initialize an axes
********************************/
int bct30::initAxis(int AxisNumber)
{
    printf("initAxis() called.");
}


