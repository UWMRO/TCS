%module bct30
%{
#include "bct30.h"
%}

class bct30
{
public:
	int bct30::getEncoderCnt(int AxisNumber, double *posit);
	int bct30::getPosition(int AxisNumber, double *degrees);
	void bct30::getVelocity(int AxisNumber, double *velocity);
	short int bct30::getDigitalIO(int channel);
	void bct30::TranslateError(char *buff, int buff_len);
	short int bct30::GetError();
	int bct30::setZenith(void);
	void bct30::setPosition(int AxisNumber, double *degrees);
	void bct30::stopSlew(int AxisNumber);
	void bct30::stopSlew();
	void bct30::estop(int AxisNumber);
	void bct30::estop(void);
	void bct30::enableAmp(int AxisNumber, bool state);
	bool bct30::IsAtTarget(int AxisNumber);
	bool bct30::IsStopped(int AxisNumber);
	void bct30::MoveRelative(int AxisNumber, double distance);
	int bct30::Jog(int AxisNumber, double distance);
	int bct30::moveTo(int AxisNumber, double *degrees);
	void bct30::MoveAbsolute(int AxisNumber, double position);
	void bct30::track(void);
	int bct30::track(int AxisNumber, double rate);
	void bct30::moveRelativeDegrees(int AxisNumber, double *degrees);
	int bct30::checkHandPaddle();
	void bct30::checkHandPaddle2();
	void bct30::GetFollowingError(int AxisNumber, double *error);
	void bct30::Reset(int AxisNumber);
	void bct30::getStatus(int AxisNumber, int *stat);
	void bct30::getMode(int AxisNumber, int *mode);
};
