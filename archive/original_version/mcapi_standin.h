#pragma once
#include <stdint.h>

#define MC_ALL_AXES 0
#define MC_OPEN_BINARY 0
#define MC_DIO_INPUT 0
#define MC_DIO_OUTPUT 0
#define MC_DIO_LOW 0
#define MC_DIO_HIGH 0
#define MCERR_NOERROR 0
#define MC_MODE_POSITION 0
#define MC_MODE_VELOCITY 0
#define MC_DIR_NEGATIVE 0
#define MC_DIR_POSITIVE 0
#define MC_PHASE_REV 0
#define MC_PROF_SCURVE 0
#define MC_LIMIT_BOTH 0
#define MC_IM_OPENLOOP 0
#define MC_OM_PULSE_DIR 0
#define MC_STEP_FULL 0

typedef struct {
    int cbSize;
    int Acceleration;
    int Deceleration;
    int Velocity;
    double Torque;
    int MinVelocity;
    int StepSize;
} MCMOTIONEX;

typedef struct {
    int cbSize;
    double Gain;
    double IntegralGain;
    double DerivativeGain;
    double DerSamplePeriod;
    int FollowingError;
    int IntegrationLimit;
} MCFILTEREX;

typedef uint32_t HCTRLR;
typedef uint32_t MCPARAM;
typedef uint32_t MCSCALE;
typedef uint32_t WORD;
typedef uint32_t MCJOG;
typedef uint32_t MCSTATUSEX;

typedef int DWORD;

extern void MCStop(HCTRLR hCtlr, int axes);
extern void MCReset(HCTRLR hCtlr, int axes);
extern void MCClose(HCTRLR hCtlr);
int MCOpen(int a, int b, const char *c);
extern void MCTranslateErrorEx(HCTRLR hCtlr, char *buf, int size);
extern void MCConfigureDigitalIO(HCTRLR hCtlr, int func, int mask);
int MCGetPositionEx(HCTRLR hCtlr, int axis, double *posit);
extern void MCGetVelocityActual(HCTRLR hCtlr, int axis, double *velocity);
short int MCGetDigitalIO(HCTRLR hCtlr, int channel);
int MCGetError(HCTRLR hCtlr);
extern void MCSetPosition(HCTRLR hCtlr, int axis, double distance);
extern void MCAbort(HCTRLR hCtlr, int axis);
extern void MCEnableDigitalIO(HCTRLR hCtlr, bool enable, bool state);
bool MCIsStopped(HCTRLR hCtlr, int axis, int a);
extern void MCSetVelocity(HCTRLR hCtlr, int axis, int vel);
extern void MCSetOperatingMode(HCTRLR hCtlr, int axis, int a, int pos);
extern void MCMoveRelative(HCTRLR hCtlr, int axis, double distance);
extern void MCGetOperatingMode(HCTRLR hCtlr, int axis, int *mode);
extern void MCMoveAbsolute(HCTRLR hCtlr, int axis, double position);
extern void MCDirection(HCTRLR hCtlr, int axis, int a);
extern void MCGoEx(HCTRLR hCtlr, int axis, double a);
extern void MCEnableAxis(HCTRLR hCtlr, int axis, bool a);
extern void MCGetStatusEx(HCTRLR hCtlr, int axis, MCSTATUSEX *status);
extern void MCDecodeStatusEx(HCTRLR hCtlr, MCSTATUSEX *new_stat, DWORD stat);
extern void MCGetMotionConfigEx(int a, int axis, MCMOTIONEX *p_motion);
extern void MCSetMotionConfigEx(HCTRLR hCtlr, int axis, MCMOTIONEX *p_motion);
extern void MCSetServoOutputPhase(HCTRLR hCtlr, int axis, int phase_rev);
extern void MCGetFilterConfigEx(HCTRLR hCtlr, int axis, MCFILTEREX *p_filter);
extern void MCSetFilterConfigEx(HCTRLR hCtlr, int axis, MCFILTEREX *p_filter);
extern void MCSetProfile(HCTRLR hCtlr, int axis, int prof);
extern void MCSetLimits(HCTRLR hCtlr, int axis, int limit, int a, double b, double c);
extern void MCGetFollowingError(HCTRLR hCtlr, int axis, double *error);
extern void MCSetModuleInputMode(HCTRLR hCtlr, int axis, int a);
extern void MCSetModuleOutputMode(HCTRLR hCtlr, int axis, int a);
