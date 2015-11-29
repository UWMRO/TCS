

void MCStop(void *hCtlr, int axes);
void MCReset(void *hCtlr, int axes);
void MCClose(void *hCtlr);
int MCOpen(int a, int b, const char *c);
void MCTranslateErrorEx(void *hCtlr, char *buf, int size);
void MCConfigureDigitalIO(void *hCtlr, void *func, int mask);
int MCGetPositionEx(void *hCtlr, int axis, double *posit);
void MCGetVelocityActual(void *hCtlr, int axis, double *velocity);
short int MCGetDigitalIO(void *hCtlr, int channel);
int MCGetError(void *hCtlr);
void MCSetPosition(void *hCtlr, int axis, double distance);
void MCAbort(void *hCtlr, int axis);
void MCEnableDigitalIO(void *hCtlr, bool enable, bool state);
bool MCIsStopped(void *hCtlr, int axis, int a);
void MCSetVelocity(void *hCtlr, int axis, int vel);
void MCSetOperatingMode(void *hCtlr, int axis, int a, int pos);
void MCMoveRelative(void *hCtlr, int axis, double distance);
void MCGetOperatingMode(void *hCtlr, int axis, int *mode);
void MCMoveAbsolute(void *hCtlr, int axis, double position);
void MCGetVelocityActual(void *hCtlr, int axis, double *vel);
void MCDirection(void *hCtlr, int axis, int a);
void MCGoEx(void hCtlr, int axis, double a);
void MCEnableAxis(void *hCtlr, int axis, bool a);
void MCGetStatusEx(void *hCtlr, int axis, int *status);
void MCDecodeStatusEx(void *hCtlr, int *new_stat, DWORD stat);
void MCGetMotionConfigEx(int a, int axis, void *p_motion);
void MCSetMotionConfigEx(void *hCtlr, int axis, void *p_motion);
void MCSetServoOutputPhase(void *hCtlr, int axis, int phase_rev);
void MCGetFilterConfigEx(void *hCtlr, int axis, void *p_filter);
void MCSetFilterConfigEx(void *hCtlr, int axis, void *p_filter);
void MCSetProfile(void *hCtlr, int axis, int prof);
void MCSetLimits(void *hCtlr, int axis, int limit, int a, double b, double c);

