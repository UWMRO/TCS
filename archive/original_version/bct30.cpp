// $Id: bct30.cpp,v 1.3 2007/05/15 23:21:16 jdosher Exp $

/*
  This file is the driver for the PMC I/O card. The MRO INDI server calls
  functions in this object to communicate with the physical hardware of the
  scope.

  This driver is written to interface with the PMC MultiFlex PCI 1440
  Controller in the TCC.

*/



#include <stdio.h>
#include <iostream>
#include <signal.h>
#include <stdlib.h>
#include <math.h>

#include "mcapi.h"

#ifndef INDI_DEVAPI_H
#include "indicom.h"
#endif

#ifndef __GLOBALS__
#include "globals.h"
#endif

#include "iomappings.h"
#ifndef __BCT30__
#include "bct30.h"
#endif

using namespace std;

bct30::bct30(void)
{
   OpenController();

   RAtarget_cnt = 0; // for IsAtTarget
   DECtarget_cnt = 0;
   


}

bct30::~bct30()
{
   MCStop(hCtlr, MC_ALL_AXES);
   MCReset(hCtlr, MC_ALL_AXES);
   MCClose(hCtlr);			// close handle to motion card
   // cout << "\n EXITING \n";
}



/******* private commands *********/
int bct30::OpenController(void)
{

   if ((hCtlr = MCOpen(0, MC_OPEN_BINARY, "")) > 0) 
   {
      
#if 0
      cout << "\nhCtlr = " << hCtlr << endl;	
      //  Obtain the current configuration from the controller
      MCGetConfiguration(hCtlr, &Param);
      std::cout << "There are " << Param.NumberAxes << " axes installed" << std::endl << std::endl;
      
      //
      //  Display position info
      //
      for (short int i = 1; i <= Param.NumberAxes; i++) 
      {
	 //double posit;
	 MCGetPositionEx(hCtlr, i, &posit);
	 std::cout << "  Axis " << i << " Position = " << posit << std::endl;
      }
#endif

      return 0;
   }
   else
   {
      char buffer[256];
      MCTranslateErrorEx(hCtlr, buffer, sizeof(buffer));
      std::cout << "Error attempting to open controler: " << buffer << std::endl; 

   }
   return -1;

}


int bct30::init(void)
{
   //MCReset(hCtlr, MC_ALL_AXES); // reset ALL axes
   if(initAxis(RaAxis) < 0) return -1;
   if(initAxis(DecAxis) < 0) return -1;
   if(initAxis(FocusAxis) < 0) return -1;
   
// configure digital I/O
// per-axis I/O configured in initAxis()
   MCConfigureDigitalIO(hCtlr, SetSlew, MC_DIO_INPUT|MC_DIO_LOW);
   MCConfigureDigitalIO(hCtlr, JogNorth, MC_DIO_INPUT|MC_DIO_LOW);
   MCConfigureDigitalIO(hCtlr, JogSouth, MC_DIO_INPUT|MC_DIO_LOW);
   MCConfigureDigitalIO(hCtlr, JogEast, MC_DIO_INPUT|MC_DIO_LOW);
   MCConfigureDigitalIO(hCtlr, JogWest, MC_DIO_INPUT|MC_DIO_LOW);
      
 
   // cout << "done running init()\n";
   return 0;
}


/******* public commands *********/


/* public get commands */

/*    Return the raw encoder count */
int bct30::getEncoderCnt(int AxisNumber, double *posit)
{
   return MCGetPositionEx(hCtlr, AxisNumber, posit);	
   // 0 if okay, MCERROR_XXX if error
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
   double pos;
      
   
   getEncoderCnt(AxisNumber, &pos);
   
   
   switch(AxisNumber)
   {
   case (RaAxis):
      *degrees = -(pos * DEG_PER_CNT);//encoders count "wrong"
      break;
   case (DecAxis):
      *degrees = pos * DEG_PER_CNT;
   }
   
   if(this->ZenithIsSet == FALSE) return -1; // encoders are not set to 0 = zenith
   return 0;
}

void bct30::getVelocity(int AxisNumber, double *velocity)
{
   MCGetVelocityActual(hCtlr, AxisNumber, velocity);
}


short int bct30::getDigitalIO(int channel)
{
   return(MCGetDigitalIO(hCtlr, channel));
}

// return a human-readable string
void bct30::TranslateError(char *buff, int buff_len)
{

   MCTranslateErrorEx(GetError(), buff, buff_len);

}

short int bct30::GetError()
{
   int err;
   err =  MCGetError(hCtlr);
   if(err == MCERR_NOERROR)
      return err;
   else
      cout << "Error = " << err;
   return err;
}


/* public set commands */


int bct30::setZenith(void)
{

   if(setEncoderToZero(DecAxis) != 0) return -1;
   if(setEncoderToZero(RaAxis) != 0) return -1;;
   this->ZenithIsSet = TRUE;
   
   return 0;

}

int bct30::setEncoderToZero(int AxisNumber)
{
   MCSetPosition(hCtlr, AxisNumber, 0);
   return 0;
}

/* set current encoder value to degrees off zenith */
void bct30::setPosition(int AxisNumber, double *degrees)
{
   distance = *degrees/DEG_PER_CNT; // distance == encoder 
   MCSetPosition(hCtlr, AxisNumber, distance);

}

/** Motion Commands **/
/* normal stop */
void bct30::stopSlew(int AxisNumber)
{
   MCStop(hCtlr, AxisNumber);
   //while(!MCIsStopped(hCtlr, AxisNumber,0)){};


}

/* normal stop */
void bct30::stopSlew()
{
   MCStop(hCtlr, MC_ALL_AXES);
   //MCStop(hCtlr, RaAxis);
   //MCStop(hCtlr, DecAxis);
   
  
}

/* Estop - abrupt stop */
void bct30::estop(int AxisNumber)
{
   MCAbort(hCtlr, AxisNumber);
   enableAmp(RaAxis, FALSE);
   enableAmp(DecAxis, FALSE);
   enableAmp(FocusAxis, FALSE);
 
   MCReset(hCtlr, AxisNumber);
}

void bct30::estop(void)
{
   MCAbort(hCtlr, MC_ALL_AXES);
   enableAmp(RaAxis, FALSE);
   enableAmp(DecAxis, FALSE);
   enableAmp(FocusAxis, FALSE);
  
   MCReset(hCtlr, MC_ALL_AXES);	// make sure all axes get 0V outputs
}


void bct30::enableAmp(int AxisNumber, bool state)
{
   switch(AxisNumber)
   {

   case RaAxis:
      MCEnableDigitalIO(hCtlr, RaAmpEnable, state);     
      break;

   case DecAxis:
      MCEnableDigitalIO(hCtlr, DecAmpEnable, state);
      break;

   case FocusAxis:
      MCEnableDigitalIO(hCtlr, FocusAmpEnable, state);
      break;

   }

}



bool bct30::IsAtTarget(int AxisNumber)
{
// last arg is timeout (double seconds)
// stupid mcapi doesn't work   
//  return MCIsAtTarget(hCtlr, AxisNumber, 0);
// returns TRUE or FALSE
   
   double window = 300; // 300 = 1 second
   double posit;

   switch(AxisNumber)
   {
   case(RaAxis):
      
      getEncoderCnt(AxisNumber, &posit);
#if 0
      cout << "\n IsAtTarget() \n";
      cout << "RAtarget_cnt " << RAtarget_cnt 
	   << ", position " << posit 

#endif
      if(fabs(RAtarget_cnt - posit) < window)
	 return TRUE;
      else 
	 return FALSE;
      break;

   case(DecAxis):
      getEncoderCnt(AxisNumber, &posit);
      if(fabs(DECtarget_cnt - posit) < window)
	 return TRUE;
      else 
	 return FALSE;
      break;
   }

}


bool bct30::IsStopped(int AxisNumber)
{
   return MCIsStopped(hCtlr, AxisNumber, 0);

}


/* distance == encoder counts
   Positive encoder cnts Ra  == East
   Positive encdoer cnts Dec == South
*/
void bct30::MoveRelative(int AxisNumber, double distance)
{
   //while( !MCIsStopped(hCtlr, AxisNumber, 0) ){}; // spin until prior move is done

// reset to normal velocity, but not for focus axis
   if(AxisNumber == RaAxis || AxisNumber == DecAxis)
   { 
      //cout << "Using SLEW_VELOCITY for MoveRelative\n";
      MCSetVelocity(hCtlr, AxisNumber, SLEW_VELOCITY);
   }
   if (mode != MC_MODE_POSITION)
      MCSetOperatingMode(hCtlr, AxisNumber, 0, MC_MODE_POSITION);
   
   MCMoveRelative(hCtlr, AxisNumber, distance);
}
	 

/* Jog 'distance' arcsecs. 20 enc cnts = 1 arcsec
   Used for the N,S,E,W jog buttons in the Qt interface. Return value used
   to determine when we're done, and un-gray jog buttons in Qt interface */

int bct30::Jog(int AxisNumber, double distance)
{

   

   if (mode != MC_MODE_POSITION)
      MCSetOperatingMode(hCtlr, AxisNumber, 0, MC_MODE_POSITION);

   MCSetVelocity(hCtlr, AxisNumber, SLEW_VELOCITY); 

   switch (AxisNumber)
   {
    
   case RaAxis:
      
      MCMoveRelative(hCtlr, AxisNumber, 15.0*distance/(ARCSEC_PER_CNT));
      break;
   case DecAxis:
      MCMoveRelative(hCtlr, AxisNumber, -distance/(ARCSEC_PER_CNT));
      break;

   }
 


// setTracking should take care of this for us
   // back to velocity mode
   //if (mode != MC_MODE_VELOCITY)
   //   MCSetOperatingMode(hCtlr, AxisNumber, 0, MC_MODE_VELOCITY);

}

 
/* scope must be properly set to zenith of ra=0 dec=0 encoder counts,
   or all bets are off.
   degrees wrt zenith. Positive degrees = east
   Input is in degrees, we convert to encoder counts
*/
int bct30::moveTo(int AxisNumber, double *degrees)
{


// do sanity check on *degrees
   double position = *degrees/DEG_PER_CNT;
   MCGetOperatingMode(hCtlr, AxisNumber, &mode);
   if (mode != MC_MODE_POSITION)
      MCSetOperatingMode(hCtlr, AxisNumber, 0, MC_MODE_POSITION);
   MCSetVelocity(hCtlr, AxisNumber, SLEW_VELOCITY);

   switch (AxisNumber)
   {

   case RaAxis:
      //cout << "Ra: " << *degrees << endl;
      if(fabs(position) > (maxHourAngle*15.0)/DEG_PER_CNT ) return -1;
      MCMoveAbsolute(hCtlr, AxisNumber, position);
      RAtarget_cnt = position; // for IsAtTarget
      cout << "target position quals "<< position << endl;
      cout << "\n moveTo() \n";
      cout << "RAtarget_cnt " << RAtarget_cnt << endl;
      break;
   case DecAxis:
      //cout << "Dec: " << *degrees << endl;
      if(fabs(position) > (maxZenith/DEG_PER_CNT) ) return -2;
      MCMoveAbsolute(hCtlr, AxisNumber, -position);
      DECtarget_cnt = -position; // for IsAtTarget
      break;
   default:
      return -3; // invalid axis
   }
   return 0;
}


/* position is encoder counts */
// something is strange here. After a hand-paddle move, this function fails
// to work - do another hand-paddle move, it works ??

void bct30::MoveAbsolute(int AxisNumber, double position)
{

   MCGetOperatingMode(hCtlr, AxisNumber, &mode);
   if (mode != MC_MODE_POSITION){
      MCSetOperatingMode(hCtlr, AxisNumber, 0, MC_MODE_POSITION);
      cout << "changing to position mode\n";
   }
   MCSetVelocity(hCtlr, AxisNumber, SLEW_VELOCITY);
   MCMoveAbsolute(hCtlr, AxisNumber, position);
}


/* track at standard sideral rate */
void bct30::track(void)
{
   double pVelocity;
   //cout << "sidereal rate: " << SIDEREAL_CNT_PER_SEC << endl; 
   MCGetVelocityActual(hCtlr, RaAxis, &pVelocity);
   /* make sure we've slowed down first */
   while( fabs(pVelocity) > SIDEREAL_CNT_PER_SEC*5 )
   {
      std::cout << "Velocity = " << pVelocity <<std::endl;
      MCStop(hCtlr, MC_ALL_AXES);
      MCGetVelocityActual(hCtlr, RaAxis, &pVelocity);
   }

   MCSetOperatingMode(hCtlr, RaAxis, 0, MC_MODE_VELOCITY);
   MCDirection(hCtlr, RaAxis, MC_DIR_NEGATIVE);
   MCSetVelocity(hCtlr, RaAxis, SIDEREAL_CNT_PER_SEC);
   MCGoEx(hCtlr, RaAxis, 0.0);
}


/* Track at non-sidereal rate. rate is arcsec/sec (or deg/hr) */
int bct30::track(int AxisNumber, double rate)
{
   
   double pVelocity, enc_rate;
   enc_rate = rate/ARCSEC_PER_CNT;

 

   MCGetVelocityActual(hCtlr, RaAxis, &pVelocity);
   /* make sure we're moving at or near zero first */
   while( fabs(pVelocity) > SIDEREAL_CNT_PER_SEC*30.0 )
   {
      std::cout << "Velocity = " << pVelocity <<std::endl;
      MCStop(hCtlr, MC_ALL_AXES);
      MCGetVelocityActual(hCtlr, AxisNumber, &pVelocity);
   }

   MCSetOperatingMode(hCtlr, AxisNumber, 0, MC_MODE_VELOCITY);
   MCDirection(hCtlr, AxisNumber, MC_DIR_NEGATIVE);
   MCSetVelocity(hCtlr, AxisNumber, enc_rate);
   MCGoEx(hCtlr, AxisNumber, 0.0);
   cout << "Axis " << AxisNumber << " sidereal rate (cnt/sec): " << enc_rate << endl; 
   
}

/* move degrees off zenith */
void bct30::moveRelativeDegrees(int AxisNumber, double *degrees)
{
// sanity check *degrees
 
   MCSetVelocity(hCtlr, AxisNumber, SLEW_VELOCITY);
   if (mode != MC_MODE_POSITION)
      MCSetOperatingMode(hCtlr, AxisNumber, 0, MC_MODE_POSITION);
   
   distance = *degrees/DEG_PER_CNT; // distance == encoder cnts to move
   MCMoveRelative(hCtlr, AxisNumber, distance);


}

int bct30::checkHandPaddle()
{
#if 1
// check state of set/slew switch
// Make sure we only override default velocity value if a button is pushed
   // Ra
   if(getDigitalIO(JogWest) || getDigitalIO(JogEast) ){
      if(getDigitalIO(SetSlew) == 0){
	 //cout << "Set\n";
	 MCSetVelocity(hCtlr, RaAxis, SLEW_VELOCITY);
      } else{
	 //cout << "Slew\n";
	 MCSetVelocity(hCtlr, RaAxis, SET_VELOCITY);
	
      }
   }

// dec
   if(getDigitalIO(JogNorth) || getDigitalIO(JogSouth) ){
      if(getDigitalIO(SetSlew) == 0){
	 //cout << "Set\n";
	 MCSetVelocity(hCtlr, DecAxis, SLEW_VELOCITY);
      } else{
	 //cout << "Slew\n";
	 MCSetVelocity(hCtlr, DecAxis, SET_VELOCITY);
      }
   }


#endif

   /* Ra */
   if(getDigitalIO(JogWest) && RaSlewDirection != WEST)
   {
      //cout << "JogWest\n";
      MCGetOperatingMode(hCtlr, RaAxis, &mode);
      if (mode != MC_MODE_VELOCITY){
	 MCSetOperatingMode(hCtlr, RaAxis, 0, MC_MODE_VELOCITY);
	 cout << "setting conrol to velocity mode\n";
      }
      MCDirection(hCtlr, RaAxis, MC_DIR_NEGATIVE);
    
      RaSlewDirection = WEST;
      MCGoEx(hCtlr, RaAxis, 0.0);
   }
   if(getDigitalIO(JogEast) && RaSlewDirection != EAST)
   {
      //cout << "JogEast\n";
      MCGetOperatingMode(hCtlr, RaAxis, &mode);
      if (mode != MC_MODE_VELOCITY)
	 MCSetOperatingMode(hCtlr, RaAxis, 0, MC_MODE_VELOCITY);
      
      MCDirection(hCtlr, RaAxis, MC_DIR_POSITIVE);
     
      RaSlewDirection = EAST;
      MCGoEx(hCtlr, RaAxis, 0.0);
									       
   }
        
/* Dec */
   if(getDigitalIO(JogNorth) && DecSlewDirection !=NORTH)
   {
      //cout << "JogNorth \n";
      MCGetOperatingMode(hCtlr, DecAxis, &mode);
      if (mode != MC_MODE_VELOCITY)
	 MCSetOperatingMode(hCtlr, DecAxis, 0, MC_MODE_VELOCITY);
      
      MCDirection(hCtlr, DecAxis, MC_DIR_NEGATIVE); 
     
      DecSlewDirection = NORTH;
      MCGoEx(hCtlr, DecAxis, 0.0); // do a move (when in vel mode)
   }
   if(getDigitalIO(JogSouth) && DecSlewDirection !=SOUTH)
   {
      //cout << "JogSouth \n";
      MCGetOperatingMode(hCtlr, DecAxis, &mode);
      if (mode != MC_MODE_VELOCITY)
	 MCSetOperatingMode(hCtlr, DecAxis, 0, MC_MODE_VELOCITY);
      
      MCDirection(hCtlr, DecAxis, MC_DIR_POSITIVE); 
    
      DecSlewDirection = SOUTH;
      MCGoEx(hCtlr, DecAxis, 0.0);
   }


   /* Now, if we were slewing, see if any buttons have been
      let up and we need to stop slewing */

   if( (RaSlewDirection == WEST) && (!getDigitalIO(JogWest)) )
   { 
      //cout << "stop jog WEST \n";
      stopSlew(RaAxis);
      RaSlewDirection = STOP;
   }
   if( (RaSlewDirection == EAST) && (!getDigitalIO(JogEast)) )
   {
      //cout << "stop jog EAST \n";
      stopSlew(RaAxis);
      RaSlewDirection = STOP;
   }
   if( (DecSlewDirection == NORTH) && (!getDigitalIO(JogNorth)) )
   {
      //cout << "stop jog NORTH \n";
      stopSlew(DecAxis);
      DecSlewDirection = STOP;
   }	 
   if( (DecSlewDirection == SOUTH) && (!getDigitalIO(JogSouth)) )
   {
      //cout << "stop jog SOUTH \n";
      stopSlew(DecAxis);
      DecSlewDirection = STOP;
   }


/* return 0 if not slewing, 1 if slewing */

   if(RaSlewDirection == STOP && DecSlewDirection == STOP)
   {
      
      return 0;
   }
   else return 1;

}

/* a safer, position-based jog */
/* depricated: regular jog seems fine now */
void bct30::checkHandPaddle2()
{

//#define FAST_JOG 500000	// encoder ticks
   static int FAST_JOG = 500000;
  
/* Ra */
   if(getDigitalIO(JogWest) )
   {
      //cout << "JogWest\n";
      getEncoderCnt(RaAxis, &position);
      MoveRelative(RaAxis, position-FAST_JOG);
      //RaSlewDirection = WEST;

   }
   if(getDigitalIO(JogEast) )
   {
      //cout << "JogEast\n";
      getEncoderCnt(RaAxis, &position);
      MoveRelative(RaAxis, position+FAST_JOG);
      //RaSlewDirection = EAST;
    									       
   }

/* Dec */
   if(getDigitalIO(JogWest) )
   {
      cout << "JogWest\n";
      getEncoderCnt(DecAxis, &position);
      //MoveRelative(DecAxis, position-FAST_JOG);
      //RaSlewDirection = WEST;

   }
   if(getDigitalIO(JogEast) )
   {
      cout << "JogEast\n";
      getEncoderCnt(DecAxis, &position);    
      //MoveRelative(DecAxis, position+FAST_JOG);
      //RaSlewDirection = EAST;
    									       
   }




}

void bct30::GetFollowingError(int AxisNumber, double *error)
{
   MCGetFollowingError(hCtlr, AxisNumber, error);
}

void bct30::Reset(int AxisNumber)
{
   MCReset(hCtlr, AxisNumber);
   MCEnableAxis(hCtlr, AxisNumber, TRUE);
}

void bct30::getStatus(int AxisNumber, int *stat)
{

// read out status 
   MCGetStatusEx(hCtlr, AxisNumber, &NewStatus);
   for (int i = 0; i < 9; i++)
   {
      MCDecodeStatusEx(hCtlr, &NewStatus, stat[i]);
       
   }



}

void bct30::getMode(int AxisNumber, int *mode)
{

   MCGetOperatingMode(hCtlr, AxisNumber, mode);

}

/******************************* 
      initialize an axes 
********************************/
int bct30::initAxis(int AxisNumber)
{
   //MCReset(hCtlr, AxisNumber);
   int mode;
   MCGetOperatingMode(hCtlr, AxisNumber, &mode);
   if (mode != MC_MODE_POSITION)
      MCSetOperatingMode(hCtlr, AxisNumber, 0, MC_MODE_POSITION); // no return value
   // start out in position mode by default

   pMotion.cbSize = sizeof(pMotion);
   pFilter.cbSize = sizeof(pFilter);

// trying Zeigler-Nichols method of gain determination
   float P = .0008;
   float Pc = 1; // Hz
   float I = 0.5 * Pc;
   float D = Pc/8.0;

   switch (AxisNumber)
   {

   case RaAxis: 
        
      MCEnableAxis(hCtlr, AxisNumber, FALSE); // see page 62 of mcapiref.pdf
      
      MCGetMotionConfigEx(6, AxisNumber, &pMotion);
      
      pMotion.Acceleration = 70000;
      pMotion.Deceleration = pMotion.Acceleration;
      pMotion.Velocity =     SLEW_VELOCITY; 
      pMotion.Torque = 3.5; // max volts out  
      //pMotion.MinVelocity = 0;
      MCSetMotionConfigEx(hCtlr, AxisNumber, &pMotion);

   
      MCSetServoOutputPhase(hCtlr, AxisNumber, MC_PHASE_REV); // no return val

#if 1
// setup MCFILTEREX struct
// PID gains
/*
  some audible noise during sidereal
  P 0.012
  I 0.000001
  D 0.4

  seems to work pretty well. Dec is a little jittery though
  0.010
  0.000001
  0.25
*/

      MCGetFilterConfigEx(hCtlr, AxisNumber, &pFilter);
      pFilter.Gain =		0.010;	
      pFilter.IntegralGain =	0.000001;
      pFilter.DerivativeGain =	0.25;
      
      pFilter.DerSamplePeriod = .000250;
      pFilter.FollowingError = 2500;
      // pFilter.IntegralOption = MC_INT_ZERO; // normal and zero
      pFilter.IntegrationLimit = 1000;
      //pFilter.UpdateRate = MC_RATE_HIGH;

      MCSetFilterConfigEx(hCtlr, AxisNumber, &pFilter);
      MCSetProfile(hCtlr, AxisNumber, MC_PROF_SCURVE);	// gentler motion
#endif


// configure limit switch for RightAscention Axis (RaAxis = 1)
      MCSetLimits(hCtlr,AxisNumber, 
		  MC_LIMIT_BOTH,
		  0,0.0,0.0);
      MCConfigureDigitalIO(hCtlr, 18, MC_DIO_INPUT|MC_DIO_LOW); // limit+ 
      MCConfigureDigitalIO(hCtlr, 19, MC_DIO_INPUT|MC_DIO_LOW); // limit-


// reverse logic on amp enable/inhibit digital IO      
      MCConfigureDigitalIO(hCtlr, RaAmpEnable, MC_DIO_OUTPUT|MC_DIO_LOW); 
     
      MCEnableAxis(hCtlr, AxisNumber, TRUE);

      break;
   
   case DecAxis:

      MCSetServoOutputPhase(hCtlr, AxisNumber, MC_PHASE_REV);
// use same values as Ra Axis for now

//      MCGetMotionConfigEx(hCtlr, AxisNumber, &pMotion); // get motion config params
      pMotion.Acceleration = pMotion.Acceleration - 10000;
      pMotion.Deceleration = pMotion.Acceleration;
      pMotion.Velocity =     SLEW_VELOCITY; 
      //    pMotion.Torque = 1; // max volts out  
      //pMotion.MinVelocity = 0;
      //pMotion.HardLimitMode = MC_LIMIT_LOW|MC_LIMIT_SMOOTH;

      MCSetMotionConfigEx(hCtlr, AxisNumber, &pMotion);

// setup MCFILTEREX struct
// use same values as Ra axis for now

      //MCGetFilterConfigEx(hCtlr, AxisNumber, &pFilter);
      pFilter.Gain =		0.005;		// "working" gain .0009;	// P
      pFilter.IntegralGain =	0.000001;	// "working" gain 0.00013;	// I
      pFilter.DerivativeGain =	0.25;	// D 0.007;
      pFilter.DerSamplePeriod = .000250;

      pFilter.FollowingError = 2500;
      
      MCSetFilterConfigEx(hCtlr, AxisNumber, &pFilter);


// reverse logic on amp enable/inhibit digital IO      
      MCConfigureDigitalIO(hCtlr, DecAmpEnable, MC_DIO_OUTPUT|MC_DIO_LOW); 
  

// configure limit switchs for Dec
      MCSetLimits(hCtlr,AxisNumber, 
		  MC_LIMIT_BOTH,
		  0,0.0,0.0);
      MCConfigureDigitalIO(hCtlr, 22, MC_DIO_INPUT|MC_DIO_LOW); // limit+ 
      MCConfigureDigitalIO(hCtlr, 23, MC_DIO_INPUT|MC_DIO_LOW); // limit-

      MCEnableAxis(hCtlr, AxisNumber, TRUE);
      break;

  
   case FocusAxis:
   
      MCEnableAxis(hCtlr, AxisNumber, FALSE); // see page 62 of mcapiref.pdf
      MCGetMotionConfigEx(hCtlr, AxisNumber, &pMotion);

// write motion config params
/* old card had "sv26, si10, sa3" */
      MCEnableAxis(hCtlr, AxisNumber, FALSE);
      pMotion.Acceleration = 500; // default = 10000
      pMotion.Deceleration = pMotion.Acceleration;
      pMotion.Velocity = 770.0; // default = 10000
      pMotion.MinVelocity = 400; // default = 1000
      pMotion.StepSize = MC_STEP_FULL;
      //pMotion.Current = MC_CURRENT_HALF;
      MCSetMotionConfigEx(hCtlr, AxisNumber, &pMotion);
      //MCSetProfile(hCtlr, AxisNumber, MC_PROF_TRAPEZOID );
     
      MCSetModuleInputMode(hCtlr, AxisNumber, MC_IM_OPENLOOP); // configure stepper
      MCSetModuleOutputMode(hCtlr, AxisNumber,  MC_OM_PULSE_DIR); // set to pulse/dir mode 
      
// configure limit switchs for Focus stepper (axis 7)
      MCConfigureDigitalIO(hCtlr, FocusAmpEnable, MC_DIO_OUTPUT|MC_DIO_HIGH);
      MCEnableDigitalIO(hCtlr, FocusAmpEnable, TRUE);
       
      MCSetLimits(hCtlr,AxisNumber, 
		  MC_LIMIT_BOTH,
		  0,0.0,0.0);
      MCConfigureDigitalIO(hCtlr, 30, MC_DIO_INPUT|MC_DIO_LOW); // limit+ 
      MCConfigureDigitalIO(hCtlr, 31, MC_DIO_INPUT|MC_DIO_LOW); // limit-

      MCEnableAxis(hCtlr, AxisNumber, TRUE);
      MCEnableAxis(hCtlr, AxisNumber, FALSE);
      MCEnableAxis(hCtlr, AxisNumber, TRUE);   
      
      break;
		   
   
   default:
      return -1;
   }
   
   return 0;

}


