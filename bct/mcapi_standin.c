#include <stdio.h>

#include "mcapi_standin.h"

void MCStop(HCTRLR hCtlr, int axes)
{
    printf("MCStop()\n");
}

void MCReset(HCTRLR hCtlr, int axes)
{
    printf("MCReset()\n");
}

void MCClose(HCTRLR hCtlr)
{
    printf("MCClose()\n");
}

int MCOpen(int a, int b, const char *c)
{
    printf("MCOpen()\n");
    return 1;
}

void MCTranslateErrorEx(HCTRLR hCtlr, char *buf, int size)
{
    printf("MCTranslateErrorEx()\n");
}

void MCConfigureDigitalIO(HCTRLR hCtlr, int func, int mask)
{
    printf("MCConfigureDigitalIO()\n");
}

int MCGetPositionEx(HCTRLR hCtlr, int axis, double *posit)
{
    printf("MCGetPositionEx()\n");
    return 1;
}

void MCGetVelocityActual(HCTRLR hCtlr, int axis, double *velocity)
{
    printf("MCGetVelocityActual()\n");
}

short int MCGetDigitalIO(HCTRLR hCtlr, int channel)
{
    printf("MCGetDigitalIO()\n");
    return 1;
}

int MCGetError(HCTRLR hCtlr)
{
    printf("MCGetError()\n");
    return 0;
}

void MCSetPosition(HCTRLR hCtlr, int axis, double distance)
{
    printf("MCSetPosition()\n");
}

void MCAbort(HCTRLR hCtlr, int axis)
{
    printf("MCAbort()\n");
}

void MCEnableDigitalIO(HCTRLR hCtlr, bool enable, bool state)
{
    printf("MCEnableDigitalIO()\n");
}

bool MCIsStopped(HCTRLR hCtlr, int axis, int a)
{
    printf("MCIsStopped()\n");
    return true;
}

void MCSetVelocity(HCTRLR hCtlr, int axis, int vel)
{
    printf("MCSetVelocity()\n");
}

void MCSetOperatingMode(HCTRLR hCtlr, int axis, int a, int pos)
{
    printf("MCSetOperatingMode()\n");
}

void MCMoveRelative(HCTRLR hCtlr, int axis, double distance)
{
    printf("MCSetOperatingMode()\n");
}

void MCGetOperatingMode(HCTRLR hCtlr, int axis, int *mode)
{
    printf("MCGetOperationMode()\n");
}

void MCMoveAbsolute(HCTRLR hCtlr, int axis, double position)
{
    printf("MCMoveAbsolute()\n");
}

void MCDirection(HCTRLR hCtlr, int axis, int a)
{
    printf("MCDirection()\n");
}

void MCGoEx(HCTRLR hCtlr, int axis, double a)
{
    printf("MCGoEx()\n");
}

void MCEnableAxis(HCTRLR hCtlr, int axis, bool a)
{
    printf("MCEnableAxis()\n");
}

void MCGetStatusEx(HCTRLR hCtlr, int axis, MCSTATUSEX *status)
{
    printf("MCGetStatusEx()\n");
}

void MCDecodeStatusEx(HCTRLR hCtlr, MCSTATUSEX *new_stat, DWORD stat)
{
    printf("MCDecodeStatusEx()\n");
}

void MCGetMotionConfigEx(int a, int axis, MCMOTIONEX *p_motion)
{
    printf("MCGetMotionConfigEx()\n");
}

void MCSetMotionConfigEx(HCTRLR hCtlr, int axis, MCMOTIONEX *p_motion)
{
    printf("MCSetMotionConfigEx()\n");
}

void MCSetServoOutputPhase(HCTRLR hCtlr, int axis, int phase_rev)
{
    printf("MCSetServoOutputPhase()\n");
}

void MCGetFilterConfigEx(HCTRLR hCtlr, int axis, MCFILTEREX *p_filter)
{
    printf("MCGetFilterConfigEx()\n");
}

void MCSetFilterConfigEx(HCTRLR hCtlr, int axis, MCFILTEREX *p_filter)
{
    printf("MCSetFilterConfigEx()\n");
}

void MCSetProfile(HCTRLR hCtlr, int axis, int prof)
{
    printf("MCSetProfile()\n");
}

void MCSetLimits(HCTRLR hCtlr, int axis, int limit, int a, double b, double c)
{
    printf("MCSetLimits()\n");
}

extern void MCGetFollowingError(HCTRLR hCtlr, int axis, double *error)
{
    printf("MCGetFollowingError()\n");
}

extern void MCSetModuleInputMode(HCTRLR hCtlr, int axis, int a)
{
    printf("MCSetModuleInputMode()\n");
}

extern void MCSetModuleOutputMode(HCTRLR hCtlr, int axis, int a)
{
    printf("MCSetModuleOutputMode()\n");
}
