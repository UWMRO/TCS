///////////////////////////////////////////////////////////////////////////
//
//  NAME
//    mcapi.h - motion control API function prototypes & macros
//
//  DESCRIPTION
//    Include this header file in your source code to provide prototypes
//    for the motion control API functions.
//
//    #include "mcapi.h"
//
//  RELEASE HISTORY
//    Copyright (c) 1995-2015 by Precision Micro Control Corp. All rights
//    reserved.
//
//    $Id: mcapi.h 884 2015-05-05 21:04:59Z brian $
//
//    Version 3.0.0		 1-Mar-01		Programmer: R. Brian Gaynor
//      - Added support for DCX-PCI300 controller
//      - Added constant for MC320 module type
//      - Added MCGetAxisConfiguration() for read-only axis configuration
//      - Added MCGetConfigurationEx() for extended controller
//        configuration information
//
//    Version 3.0.1		 1-May-01		Programmer: Brian Gaynor
//      - No changes to this module
//
//    Version 3.0.2		 6-Jun-01		Programmer: Brian Gaynor
//      - No changes to this module
//
//    Version 3.1.0		19-Sep-01		Programmer: Brian Gaynor
//      - Added support for the DCX-PCI100 controller
//      - Added prototypes and constants for Position Capture mode
//        MCEnableCapture(), MCGetCount()
//      - Added prototypes and constants for Position Compare mode
//        MCEnableCompare(), MCConfigureCompare(), MCGetCount()
//      - Added prototypes and constants for Digital Filter mode
//        MCEnableDigitalFilter(), MCGetDigitalFilter(),
//        MCSetDigitalFilter(), MCIsFilter(), MCGetCount()
//
//    Version 3.2.0		11-Jan-02		Programmer: Brian Gaynor
//      - Added additional argument-type constants for pmccmdex()
//      - Added prototypes and  constants for MCGetModuleInputMode() /
//        MCSetModuleInputMode()
//      - Added prototype and constants for MCGetOperatingMode()
//      - Added prototype and new data structure for MCGetMotionConfigEx()
//        and MCSetMotionConfigEx()
//      - Added prototype and new data structure for MCGetFilterConfigEx()
//        and MCSetFilterConfigEx()
//      - Added prototype and new data structure for MCSetCommutation()
//
//    Version 3.2.1		26-Apr-02		Programmer: Brian Gaynor
//      - No changes to this module
//
//    Version 3.3.0		15-Jan-03		Programmer: Brian Gaynor
//      - Added constants for MFX-PCI1000 series controllers
//      - Added prototypes, structures, and constants for MCGetStatusEX(),
//        MCSTATUSEX, and MCDecodeStatusEx()
//      - Added status word lookup constants MC_STAT_PRI_ENC_FAULT, 
//        MC_STAT_AUX_ENC_FAULT, MC_STAT_LOOK_AUX_IDX, MC_STAT_AUX_IDX_FND
//      - Structure tags added to provide better support for source code
//        browsing tools
//      - Added prototype for MCEanableInterrupt()
//      - Added prototype for MCInterruptOnPosition()
//
//    Version 3.4.0		 2-Jun-03		Programmer: Brian Gaynor
//      - Added some conditional typedefs for basic Windows data types so
//        this header can also be used with products like LabWindows/CVI
//      - Added MCEnableEncoderFault() and constants MC_ENC_FAULT_PRI,
//        MC_ENC_FAULT_SEC for encoder fault detection feature of
//        Multiflex series of controllers
//      - Added MCGetAnalogEx/()MCSetAnalogEx() to make it easier for
//        Visual Basic users to handle 16-bit unsigned values
//      - Added pmcgetramex() and pmcputramex() to support larger memory
//        space of the PCI controllers (32-bit address offset and size)
//      - Added new fields to MCAXISCONFIG and MCPARAMEX structures
//
//    Version 3.4.1		31-Oct-03		Programmer: Brian Gaynor
//      - No changes to this module
//
//    Version 3.4.2		 5-Jul-04		Programmer: Brian Gaynor
//      - No changes to this module
//
//    Version 3.5.0		19-Nov-04		Programmer: Brian Gaynor
//      - Added additional conditional typedefs for windows types used in
//        MCAPI that aren't normally defined in under linux
//      - Added MCGetModuleOutputMode()
//      - Added MCGetVelocityOverride() / MCSetVelocityOverride()
//      - Extended MCFILTEREX structure with position deadband, delay at
//        target, output offset, and output deadband fields (MFX only)
//      - Extended MCPARAMEX with fields descroibing controllers support 
//        of the new functions added in this release
//
//    Version 3.5.1		 1-Feb-05		Programmer: Brian Gaynor
//      - No changes to this module
//
//    Version 3.5.2		24-Feb-05		Programmer: Brian Gaynor
//      - No changes to this module
//
//    Version 4.0.0		16-Jan-06		Programmer: Brian Gaynor
//      - Cleaned up function prototypes and header comments
//      - Converted long int types to int, doesn't effect 32-bit code,
//        sizeof(long int) == sizeof(int), but this will make sure that 
//        parameter sizes don't swell under 64-bit builds
//      - Added MCGetDigitalIOEx(), can return status of 32 digital I/O
//        channels in one call (BR #121).
//
//    Version 4.0.1		27-Mar-06		Programmer: Brian Gaynor
//      - Removed very old version comments.
//
//    Version 4.0.2		21-Apr-06		Programmer: Brian Gaynor
//      - Added comments to this header that can be read by the doxygen 
//        documentation generator under Linux.
//
//    Version 4.0.3		17-Nov-06		Programmer: Brian Gaynor
//      - Cleaned up some comments
//
//    Version 4.0.4		16-May-07		Programmer: Brian Gaynor
//      - No changes to this module
//
//    Version 4.0.5		13-Jul-07		Programmer: Brian Gaynor
//      - No changes
//
//    Version 4.1.0		 1-Dec-08		Programmer: Brian Gaynor
//      - Added controller type for MultiFlex Ethernet.
//      - The MCAPI_LIB and MCDLG_LIB macros are now properly escaped for
//        use in UNICODE projects.
//      - Added constant MC_COMPARE_STROBE for new "strobe" output mode 
//        of compare function.
//      - Added new MCGetJogConfigEx() / MCSetJogConfig() prototypes and
//        MCJOGEX data structure declaration.
//      - Added new MCGetTrajectoryRate() / MCSetTrajectoryRate()
//        prototypes for checking/setting the trajectory rate on
//        the MFX-ETH.
//
//    Version 4.1.1		14-Jul-09		Programmer: Brian Gaynor
//      - Added an error constant for TCP/IP socket errors.
//      - Added a more generic MCERR_OS_ERROR error constant as an alias
//        of MCERR_WINDOWSERROR.
//
//    Version 4.1.2		25-Sep-09		Programmer: Brian Gaynor
//      - No changes
//
//    Version 4.2.0		 1-Apr-10		Programmer: Brian Gaynor
//      - Added the LineModeAscii flag to the PARAMEX structture, allows
//        programs to optimize I/O with line oriented controllers such as
//        the Ethernet controller.
//      - Updates to the module output mode flags.
//
//    Version 4.3.0		19-Dec-12		Programmer: Brian Gaynor
//      - Added pmccmdrpyex(), pmclock(), pmcunlock(), pmclookupvar()
//
//    Version 4.4.0		26-Apr-14		Programmer: Brian Gaynor
//      - Added MCGetCaptureSettings() to retrieve settings from the most
//        recent position recording
//      - Added support to MCGetCount() for the position recording current
//        recording index
//
//    Version 4.4.1		 8-May-15		Programmer: Brian Gaynor
//      - Performance improvements for MFX-ETH.
//
///////////////////////////////////////////////////////////////////////////

/// @file mcapi.h

#ifndef MCAPI_H
#define MCAPI_H

//
//  Motion Control API manifest constants
//
#define MC_ALL_AXES             0				///< Function should operate on all axes at once. Not valid for all functions, see function description.

#define MC_ABSOLUTE             0				///< Argument is an absolute position, used as an parameter to many MCAPI functions.
#define MC_RELATIVE             1				///< Argument is a relative position, used as an parameter to many MCAPI functions..

#define MC_BLOCK_COMPOUND       0				///< Block is a compound command for MCBlockBegin( ).
#define MC_BLOCK_TASK           1				///< Block is a task on multitasking controllers for MCBlockBegin( ).
#define MC_BLOCK_MACRO          2				///< Block is a macro definition for MCBlockBegin( ).
#define MC_BLOCK_RESETM         3				///< Block resets macro memory for MCBlockBegin( ).
#define MC_BLOCK_CANCEL         4				///< Cancels a block command for MCBlockBegin( ).
#define MC_BLOCK_CONTR_USER     5				///< Block is a user defined contour path motion for MCBlockBegin( ).
#define MC_BLOCK_CONTR_LIN      6				///< Block is a linear contour path motion for MCBlockBegin( ).
#define MC_BLOCK_CONTR_CW       7				///< Block is a clockwise arc contour path motion for MCBlockBegin( ).
#define MC_BLOCK_CONTR_CCW      8				///< Block is a counter-clockwise arc contour path motion for MCBlockBegin( ).

#define MC_CAPTURE_ACTUAL      16				///< Specifies captured actual position data for MCGetCaptureData( ) and MCGetAxisConfiguration( ).
#define MC_CAPTURE_ERROR       32				///< Specifies captured following error data for MCGetCaptureData( ) and MCGetAxisConfiguration( ).
#define MC_CAPTURE_OPTIMAL     64				///< Specifies captured optimal position data data for MCGetCaptureData( ) and MCGetAxisConfiguration( ).
#define MC_CAPTURE_TORQUE     128				///< Specifies captured torque data for MCGetCaptureData( ) and MCGetAxisConfiguration( ).
#define MC_CAPTURE_ADVANCED   256				///< Specifies axis supports advanced capture modes (delay and period) for and MCGetAxisConfiguration( ).
#define MC_CAPTURE_AUXILIARY  512				///< Specifies captured auxiliary encoder data for MCGetCaptureData( ) and MCGetAxisConfiguration( ) (MCAPI version 3.4.0 or later).
#define MC_CAPTURE_STATUS    1024				///< Specifies captured status word data for MCGetCaptureData( ) and MCGetAxisConfiguration( ) (MCAPI version 3.4.0 or later).

#define MC_CENTER_ABS           MC_ABSOLUTE     ///< use MC_ABSOLUTE in new code
#define MC_CENTER_REL           MC_RELATIVE     ///< use MC_RELATIVE in new code

#define MC_COMPARE_DISABLE      0				///< Disables the compare output for MCConfigureCompare( ).
#define MC_COMPARE_ENABLE       1				///< Same as MC_COMPARE_STATIC.
#define MC_COMPARE_STATIC       1				///< Set compare output to static mode for MCConfigureCompare( ).
#define MC_COMPARE_TOGGLE       2				///< Set compare output to toggle mode for MCConfigureCompare( ).
#define MC_COMPARE_ONESHOT      3				///< Set compare output to one-shot mode for MCConfigureCompare( ).
#define MC_COMPARE_STROBE       5				///< Set compare output to strobe mode for MCConfigureCompare( ).
#define MC_COMPARE_INVERT  0x0080				///< Inverts active level of compare output for MCConfigureCompare( ).

#define MC_COUNT_CAPTURE        1				///< MCGetCount( ) should retrieve the number of captured positions from high-speed capture mode.
#define MC_COUNT_COMPARE        2				///< MCGetCount( ) should retrieve the number of successful comparisons from high-speed compare mode.
#define MC_COUNT_CONTOUR        4				///< MCGetCount( ) should retrieve the index of the currently executing contour move from contouring mode.
#define MC_COUNT_FILTER         8				///< MCGetCount( ) should retrieve the number of digital filter coefficients currently loaded.
#define MC_COUNT_FILTERMAX     16				///< MCGetCount( ) should retrieve the maximum number of digital filter coefficients supported.
#define MC_COUNT_RECORD        32				///< MCGetCount( ) should retrieve the current number of position recording points recorded so far (MCAPI version 4.4.0 or later).

#define MC_CURRENT_FULL         1				///< Selects/indicates full current stepper operation in MCGetMotionConfigEx( ) / MCSetMotionConfigEx( ).
#define MC_CURRENT_HALF         2				///< Selects/indicates half current stepper operation in MCGetMotionConfigEx( ) / MCSetMotionConfigEx( ).

#define MC_DATA_ACTUAL          0               ///< Use MC_CAPTURE_ACTUAL in new code.
#define MC_DATA_OPTIMAL         1               ///< Use MC_CAPTURE_OPTIMAL in new code.
#define MC_DATA_ERROR           2               ///< Use MC_CAPTURE_ERROR in new code.
#define MC_DATA_TORQUE          3               ///< Use MC_CAPTURE_TORQUE in new code.

#define MC_DIO_FIXED          256               ///< Channel is a fixed input or output and cannot be changed using MCConfigureDigitalIO( ).
#define MC_DIO_INPUT            1               ///< Configures the channel for input.
#define MC_DIO_OUTPUT           2               ///< Configures the channel for output.
#define MC_DIO_HIGH             4               ///< Configures the channel for positive logic level.
#define MC_DIO_LOW              8               ///< Configures the channel for negative logic level.
#define MC_DIO_LATCH           16               ///< Configures the (input) channel for latched operation.
#define MC_DIO_LATCHABLE      512               ///< Input channel is capable of latched operation.
#define MC_DIO_STEPPER       1024               ///< Input channel has been dedicated to driving a stepper motor (DC2-PC or DC2-STN).

#define MC_DIR_POSITIVE         1               ///< Selects the positive travel direction for MCDirection( ).
#define MC_DIR_NEGATIVE         2               ///< Selects the negative travel direction for MCDirection( ).

#define MC_ENC_FAULT_PRI        1               ///< Enables encoder fault detection for the primary encoder with MCEnableEncoderFault( ).
#define MC_ENC_FAULT_AUX        2               ///< Enables encoder fault detection for the auxiliary encoder with MCEnableEncoderFault( ).

#define MC_INT_NORMAL           0               ///< Selects/indicates the normal (always on) operation of the integral term in MCGetFilterConfigEx( ) / MCSetFilterConfigEx( ).
#define MC_INT_FREEZE           1               ///< Selects/indicates freeze the integral term while moving in MCGetFilterConfigEx( ) / MCSetFilterConfigEx( ).
#define MC_INT_ZERO             2               ///< Selects/indicates zero and freeze the integral term while moving in MCGetFilterConfigEx( ) / MCSetFilterConfigEx( ).

#define MC_IM_OPENLOOP          0               ///< Selects/indicates open-loop mode stepper operation in MCGetModuleInputMode( ) / MCSetModuleInputMode( ).
#define MC_IM_CLOSEDLOOP        1               ///< Selects/indicates closed-loop mode stepper operation in MCGetModuleInputMode( ) / MCSetModuleInputMode( ).

#define MC_LIMIT_ABRUPT         4               ///< Limit stopping mode is set to abrupt (PID loop stops axis as quickly as possible), used with MCGetLimits( ) / MCSetLimits( ).
#define MC_LIMIT_BOTH           3               ///< Enables both the positive and negative limits, used with MCGetLimits( ) / MCSetLimits( ).
#define MC_LIMIT_INVERT    0x0080               ///< Inverts the polarity of the hardware limit switch inputs, used with MCGetLimits( ) / MCSetLimits( ).
#define MC_LIMIT_MINUS          2               ///< Enables the negative limit, used with MCGetLimits( ) / MCSetLimits( ).
#define MC_LIMIT_OFF            0               ///< Limit stopping mode is set to turn the motor off when a limit is tripped, used with MCGetLimits( ) / MCSetLimits( ).
#define MC_LIMIT_PLUS           1               ///< Enables the positive limit, used with MCGetLimits( ) / MCSetLimits( ).
#define MC_LIMIT_SMOOTH         8               ///< Limit stopping mode is set to smooth (axis executes pre-programmed deceleration), used with MCGetLimits( ) / MCSetLimits( )..
#define MC_LIMIT_HIGH           MC_LIMIT_PLUS   ///< use MC_LIMIT_PLUS in new code
#define MC_LIMIT_LOW            MC_LIMIT_MINUS  ///< use MC_LIMIT_MINUS in new code

#define MC_LRN_POSITION         1               ///< Indicates MCLearnPoint( ) should learn the current actual position for the specified axis.
#define MC_LRN_TARGET           2               ///< Indicates MCLearnPoint( ) should learns the current target position for the specified axis.

#define MC_MAX_ID              15				///< Controller ID must be less than or equal to this value.

#define MC_MODE_CONTOUR         0				///< Contouring mode operation, see MCGetOperatingMode( ) / MCSetOperatingMode( ).
#define MC_MODE_GAIN            1				///< Gain mode operation, see MCGetOperatingMode( ) / MCSetOperatingMode( ).
#define MC_MODE_POSITION        2				///< Position mode operation, see MCGetOperatingMode( ) / MCSetOperatingMode( ).
#define MC_MODE_TORQUE          3				///< Torque mode operation, see MCGetOperatingMode( ) / MCSetOperatingMode( ).
#define MC_MODE_VELOCITY        4				///< Unable to determine current mode of operation, see MCGetOperatingMode( ).
#define MC_MODE_UNKNOWN         5				///< Velocity mode operation, see MCGetOperatingMode( ) / MCSetOperatingMode( ).

#define MC_MODULE_TYPE     0x000f
#define MC_MODULE_SUBTYPE  0x00f0

#define MC_OM_BIPOLAR           0				///< Servo axis set to /in bipolar operation, see MCGetModuleOutputMode( ) / MCSetModuleOutputMode( ).
#define MC_OM_UNIPOLAR          1				///< Servo axis set to/in unipolar operation, see MCGetModuleOutputMode( ) / MCSetModuleOutputMode( ).
#define MC_OM_PULSE_DIR         0				///< Stepper axis set to/in pulse and direction output, see MCGetModuleOutputMode( ) / MCSetModuleOutputMode( ).
#define MC_OM_CW_CCW            1				///< Stepper axis set to/in clockwise and counter-clockwise operation, see MCGetModuleOutputMode( ) / MCSetModuleOutputMode( ).
#define MC_OM_BI_PWM            2				///< Servo axis set to/in bipolar PWM operation, see MCGetModuleOutputMode( ) / MCSetModuleOutputMode( ).
#define MC_OM_UNI_PWM           3				///< Servo axis set to/in unipolar PWM operation, see MCGetModuleOutputMode( ) / MCSetModuleOutputMode( ).
#define MC_OM_PIEZO             4				///< Servo axis set to/in piezo operation, see MCGetModuleOutputMode( ) / MCSetModuleOutputMode( ).
#define MC_OM_SINE_NOENC   0x8000				///< Sine commutation mode (encoder off), see MCGetModuleOutputMode( ) / MCSetModuleOutputMode( ).
#define MC_OM_SINE_ENC	   0xC000				///< Sine commutation mode (encoder on), see MCGetModuleOutputMode( ) / MCSetModuleOutputMode( ).

#define MC_OPEN_ASCII           1				///< Open controller ASCII interface parameter for MCOpen( ).
#define MC_OPEN_BINARY          2				///< Open controller ASCII interface parameter for MCOpen( ).
#define MC_OPEN_EXCLUSIVE  0x8000				///< Combine with MC_OPEN_ASCII or MCOPEN_BINARY for exclusive access to interface.

#define MC_PHASE_STD            0				///< Select/indicate standard encoder phasing in MCGetServoOutputPhase( ) / MCGetServoOutputPhase( ).
#define MC_PHASE_REV            1				///< Select/indicate reverse encoder phasing in MCGetServoOutputPhase( ) / MCGetServoOutputPhase( ).

#define MC_PROF_UNKNOWN         0				///< Returned when MCGetProfile( ) cannot determine the current profile setting.
#define MC_PROF_TRAPEZOID       1				///< Selects/indicates a trapezoidal accel/decel profile for MCGetProfile( ) / MCSetProfile( ).
#define MC_PROF_SCURVE          2				///< Selects/indicates that an S-curve accel/decel profile for MCGetProfile( ) / MCSetProfile( ).
#define MC_PROF_PARABOLIC       4				///< Selects/indicates that a parabolic accel/decel profile for MCGetProfile( ) / MCSetProfile( ).

#define MC_RATE_UNKNOWN         0				///< Returned when MCGetFilterConfigEx( ) cannot determine the current update rate.
#define MC_RATE_LOW             1				///< Selects/indicates the low range for feedback/step/trajectory rate, see MCGetFilterConfigEx( ) / MCSetFilterConfigEx( ) / MCGetTrajectoryRate( ) / MCSetTrajectoryRate( ).
#define MC_RATE_MEDIUM          2				///< Selects/indicates the medium range for feedback/step/trajectory rate, see MCGetFilterConfigEx( ) / MCSetFilterConfigEx( ) / MCGetTrajectoryRate( ) / MCSetTrajectoryRate( ).
#define MC_RATE_HIGH            4				///< Selects/indicates the high range for feedback/step/trajectory rate, see MCGetFilterConfigEx( ) / MCSetFilterConfigEx( ) / MCGetTrajectoryRate( ) / MCSetTrajectoryRate( ).

#define MC_STATUS_NOTIFY      "MCStatusNotify"  // message identifier
#define MC_STAT_BUSY            0
#define MC_STAT_MTR_ENABLE      1
#define MC_STAT_MODE_VEL        2
#define MC_STAT_TRAJ            3
#define MC_STAT_DIR             4
#define MC_STAT_JOG_ENAB        5
#define MC_STAT_HOMED           6
#define MC_STAT_ERROR           7
#define MC_STAT_LOOK_INDEX      8
#define MC_STAT_LOOK_EDGE       9
#define MC_STAT_BREAKPOINT     10
#define MC_STAT_FOLLOWING      11
#define MC_STAT_AMP_ENABLE     12
#define MC_STAT_AMP_FAULT      13
#define MC_STAT_PLIM_ENAB      14
#define MC_STAT_PLIM_TRIP      15
#define MC_STAT_MLIM_ENAB      16
#define MC_STAT_MLIM_TRIP      17
#define MC_STAT_PSOFT_ENAB     18
#define MC_STAT_PSOFT_TRIP     19
#define MC_STAT_MSOFT_ENAB     20
#define MC_STAT_MSOFT_TRIP     21
#define MC_STAT_INP_INDEX      22
#define MC_STAT_INP_HOME       23
#define MC_STAT_INP_AMP        24
#define MC_STAT_INP_AUX        25
#define MC_STAT_INP_PLIM       26
#define MC_STAT_INP_MLIM       27
#define MC_STAT_INP_USER1      28
#define MC_STAT_INP_USER2      29
#define MC_STAT_PHASE          30
#define MC_STAT_FULL_STEP      31
#define MC_STAT_HALF_STEP      32
#define MC_STAT_JOGGING        33
#define MC_STAT_PJOG_ENAB      34
#define MC_STAT_PJOG_ON        35
#define MC_STAT_MJOG_ENAB      36
#define MC_STAT_MJOG_ON        37
#define MC_STAT_INP_PJOG       38
#define MC_STAT_INP_MJOG       39
#define MC_STAT_STOPPING       40
#define MC_STAT_PROG_DIR       41
#define MC_STAT_AT_TARGET      42       // changed in v2.0d from MC_STAT_PWM_ENAB
#define MC_STAT_ACCEL          43  
#define MC_STAT_MODE_POS       44
#define MC_STAT_MODE_TRQE      45
#define MC_STAT_MODE_ARC       46
#define MC_STAT_MODE_CNTR      47
#define MC_STAT_MODE_SLAVE     48
#define MC_STAT_LMT_ABORT      49
#define MC_STAT_LMT_STOP       50
#define MC_STAT_CAPTURE        51
#define MC_STAT_RECORD         52
#define MC_STAT_SYNC           53
#define MC_STAT_MODE_LIN       54
#define MC_STAT_INDEX_FOUND    55
#define MC_STAT_POS_CAPT       56
#define MC_STAT_NULL           57
#define MC_STAT_EDGE_FOUND     58
#define MC_STAT_PRI_ENC_FAULT  59
#define MC_STAT_AUX_ENC_FAULT  60
#define MC_STAT_LOOK_AUX_IDX   61
#define MC_STAT_AUX_IDX_FND    62

#define MC_STEP_FULL            1				///< Selects full step stepper motor operation in MCGetMotionConfigEx( ) / MCSetMotionConfigEx( )
#define MC_STEP_HALF            2				///< Selects half step stepper motor operation in MCGetMotionConfigEx( ) / MCSetMotionConfigEx( )

#define MC_THREAD           0x100

#define MC_TYPE_NONE            0				///< Specifies no data for functions that accept varaible data types.
#define MC_TYPE_REG             1				///< Specifies data in controller register for functions that accept varaible data types. 
#define MC_TYPE_LONG            2				///< Specifies long integer (32-bit) data type for functions that accept varaible data types.
#define MC_TYPE_FLOAT           3				///< Specifies floating point (32-bit) data type for functions that accept varaible data types.
#define MC_TYPE_DOUBLE          4				///< Specifies double precision (64-bit) data type for functions that accept varaible data types.
#define MC_TYPE_STRING          5				///< Specifies string data type for functions that accept varaible data types.

#define MC_TYPE_SERVO           1				///< Axis is a servo motor.
#define MC_TYPE_STEPPER         2				///< Axis is a stepper motor. 

#define MC_LINEAR               1
#define MC_CIRC_CW              2
#define MC_CIRC_CCW             3

//
//  Controller specific manifest constants
//                     
#define NO_CONTROLLER           0
#define NONE                    NO_CONTROLLER    // old constant, use NO_CONTROLLER instead
#define DCXPC100                1
#define DCXAT100                2
#define DCXAT200                3
#define DC2PC100                4
#define DC2STN                  5
#define DCXAT300                6
#define DCXPCI300               7
#define DCXPCI100               8
#define MFXPCI1000              9
#define MFXETH1000             10

#define MC100                   5
#define MC110                   4
#define MC150                   6
#define MC160                   7
#define MC200                   0
#define MC210                  16
#define MC260                   1
#define MC300                   2
#define MC302                  22
#define MC320                 162
#define MC360                   3
#define MC362                  23
#define MC400                   8
#define MC500                  12
#define MF300                  10
#define MF310                   9
#define NO_MODULE              15
#define MFXSERVO              252
#define MFXSTEPPER            253
#define DC2SERVO              254
#define DC2STEPPER            255

//
//  Error code group masks
//
#define MCERRMASK_UNSUPPORTED 0x00000001L		///< Function not supported error mask.
#define MCERRMASK_HANDLE      0x00000002L		///< Bad handle error mask.
#define MCERRMASK_AXIS        0x00000004L		///< Bad axis number error mask.
#define MCERRMASK_PARAMETER   0x00000008L		///< Bad parameter error mask.
#define MCERRMASK_IO          0x00000010L		///< I/O problem error mask.
#define MCERRMASK_SYSTEM      0x00000020L		///< System level errors error mask.

#define MCERRMASK_STANDARD    0xFFFFFFFEL		///< Most common MCErrorNotify settings error mask, includes all errors except UNSUPPORTED.

#define MC_ERROR_NOTIFY       "MCErrorNotify"   ///< Message identifier string for use with MCErrorNotify( ).

//
//  Individual error codes
//

#define MCERR_NOERROR           0				///< Error code: no error.

//
//  MCERRMASK_SYSTEM group errors
//
#define MCERR_NO_CONTROLLER     1				///< Error code:  no controller assigned for this ID, MCERRMASK_SYSTEM group.
#define MCERR_OUT_OF_HANDLES    2				///< Error code:  driver out of handles, MCERRMASK_SYSTEM group.
#define MCERR_OPEN_EXCLUSIVE    3				///< Error code:  cannot open - exclusive, MCERRMASK_SYSTEM group.
#define MCERR_MODE_UNAVAIL      4				///< Error code:  controller already open in different mode, MCERRMASK_SYSTEM group.
#define MCERR_UNSUPPORTED_MODE  5				///< Error code:  controller doesn't support this mode, MCERRMASK_SYSTEM group.
#define MCERR_INIT_DRIVER       6				///< Error code:  couldn't initialize the device driver, MCERRMASK_SYSTEM group.
#define MCERR_NOT_PRESENT       7				///< Error code:  controller hardware not present, MCERRMASK_SYSTEM group.
#define MCERR_ALLOC_MEM         8				///< Error code:  memory allocation error, MCERRMASK_SYSTEM group.
#define MCERR_WINDOWSERROR      9				///< Error code:  windows function reported an error, MCERRMASK_SYSTEM group.
#define MCERR_OS_ERROR          9				///< Error code:  operating sytem function reported an error, MCERRMASK_SYSTEM group.

//
//  MCERRMASK_UNSUPPORTED group errors
//
#define MCERR_NOTSUPPORTED     11				///< Error code:  controller doesn't support this feature, MCERRMASK_UNSUPPORTED group.
#define MCERR_OBSOLETE         12				///< Error code:  function is obsolete, MCERRMASK_UNSUPPORTED group.

//
//  MCERRMASK_HANDLE group errors
//
#define MCERR_CONTROLLER       13				///< Error code:  invalid controller handle, MCERRMASK_HANDLE group errors.
#define MCERR_WINDOW           14				///< Error code:  invalid window handle, MCERRMASK_HANDLE group errors.

//
//  MCERRMASK_AXIS group errors
//
#define MCERR_AXIS_NUMBER      15				///< Error code:  axis number out of range, MCERRMASK_AXIS group.
#define MCERR_AXIS_TYPE        16				///< Error code:  axis type doesn't support this feature, MCERRMASK_AXIS group.
#define MCERR_ALL_AXES         17				///< Error code:  cannot select "ALL AXES" for function, MCERRMASK_AXIS group.
#define MCERR_AXIS_ACTIVE      31				///< Error code:  axis was enabled or moving, MCERRMASK_AXIS group.

//
//  MCERRMASK_PARAMETER group errors
//
#define MCERR_RANGE            18				///< Error code:  parameter was out of range, MCERRMASK_PARAMETER group.
#define MCERR_CONSTANT         19				///< Error code:  constant value inappropriate, MCERRMASK_PARAMETER group.
#define MCERR_NOT_INITIALIZED  30				///< Error code:  feature not initialized, MCERRMASK_PARAMETER group.

//
//  MCERRMASK_IO group errors
//                                
#define MCERR_UNKNOWN_REPLY    20				///< Error code:  unexpected or unknown reply, MCERRMASK_IO group.
#define MCERR_NO_REPLY         21				///< Error code:  controller failed to reply, MCERRMASK_IO group.
#define MCERR_REPLY_SIZE       22				///< Error code:  reply size incorrect, MCERRMASK_IO group.
#define MCERR_REPLY_AXIS       23				///< Error code:  wrong axis for reply, MCERRMASK_IO group.
#define MCERR_REPLY_COMMAND    24				///< Error code:  reply is for different command, MCERRMASK_IO group.
#define MCERR_TIMEOUT          25				///< Error code:  controller failed to respond, MCERRMASK_IO group.
#define MCERR_BLOCK_MODE       26				///< Error code:  block mode error, MCERRMASK_IO group.
#define MCERR_COMM_PORT        27				///< Error code:  communications port (RS232) error, MCERRMASK_IO group.
#define MCERR_CANCEL           28				///< Error code:  operation was canceled, MCERRMASK_IO group.
#define MCERR_NOT_FOUND        29				///< Error code:  restore operation could not find data, MCERRMASK_IO group.
#define MCERR_SOCKET           32				///< Error code:  tcp/ip socket error, MCERRMASK_IO group.

//
//  Types. We define some windows types if they aren't already defined so that
//  this header file may be used with environments like LabWindows/CVI or under unix-like
//  (i.e. linux) operating systems
//
typedef short int HCTRLR;

#ifndef _WINDEF_
  typedef long LONG;
  typedef unsigned short WORD;
  typedef unsigned long DWORD;
  typedef unsigned int UINT;
  typedef void* HANDLE;
  typedef HANDLE HINSTANCE;
  typedef unsigned long HWND;
  typedef void* LPVOID;
  typedef char CHAR;
  typedef CHAR *LPSTR;
  typedef const CHAR *LPCSTR;
#endif

#ifndef APIENTRY
  #ifdef _WIN32
  	#define APIENTRY __stdcall
  	#define PASCAL __stdcall
	#define CALLBACK __stdcall
  #else							// non-windows os
  	#define APIENTRY
  	#define PASCAL
	#define CALLBACK
  #endif
#endif

//
//  Specify the proper libraries for the platform
//
#ifdef UNICODE
	#ifdef _WIN64
		#define MCAPI_LIB L"mcapi64.dll"
		#define MCDLG_LIB L"mcdlg64.dll"
	#else
		#define MCAPI_LIB L"mcapi32.dll"
		#define MCDLG_LIB L"mcdlg32.dll"
	#endif
#else
	#ifdef _WIN64
		#define MCAPI_LIB "mcapi64.dll"
		#define MCDLG_LIB "mcdlg64.dll"
	#else
		#define MCAPI_LIB "mcapi32.dll"
		#define MCDLG_LIB "mcdlg32.dll"
	#endif
#endif

//
//  Data structures (set packing to 4-byte). Note that the MSDN documentation for this 
//  pragma is not correct (but our usage here is correct)!
//
#pragma pack(push,4)

//
//  Axis configuration structure
//
typedef struct _MCAXISCONFIG {
	int			cbSize;
	int			ModuleType;
	int			ModuleLocation;
	int			MotorType;
	int			CaptureModes;
	int			CapturePoints;
	int			CaptureAndCompare;
	double		HighRate;
	double		MediumRate;
	double		LowRate;
	double		HighStepMin;
	double		HighStepMax;
	double		MediumStepMin;
	double		MediumStepMax;
	double		LowStepMin;
	double		LowStepMax;
	int			AuxEncoder;				// added v3.4.0, axis has auxiliary encoder input
} MCAXISCONFIG;

//
//  Commutation parameters structure
//
typedef struct _MCCOMMUTATION {
	int			cbSize;
	double		PhaseA;
	double		PhaseB;
	int			Divisor;
	int			PreScale;
	int			Repeat;
} MCCOMMUTATION;

//
//  Contouring parameters structure
//
typedef struct _MCCONTOUR {
	double		VectorAccel;
	double		VectorDecel;
	double		VectorVelocity;
	double		VelocityOverride;
} MCCONTOUR;

//
//  PID Filter parameters structure (extended)
//
typedef struct _MCFILTEREX {
	int			cbSize;
	double		Gain;
	double		IntegralGain;
	double		IntegrationLimit;
	int			IntegralOption;
	double		DerivativeGain;
	double		DerSamplePeriod;
	double		FollowingError;
	double		VelocityGain;
	double		AccelGain;
	double		DecelGain;
	double		EncoderScaling;
	int			UpdateRate;
	double		PositionDeadband;		// added v3.5.0
	double		DelayAtTarget;			// added v3.5.0
	double		OutputOffset;			// added v3.5.0
	double		OutputDeadband;			// added v3.5.0
} MCFILTEREX;

//
//  PID Filter parameters structure (new programs should use MCFILTEREX)
//
typedef struct _MCFILTER {
	double		DerivativeGain;
	double		DerSamplePeriod;
	double		IntegralGain;
	double		IntegrationLimit;
	double		VelocityGain;
	double		AccelGain;
	double		DecelGain;
	double		FollowingError;
} MCFILTER;

//
//  Jog control parameters structure (added in version 4.1.0)
//
typedef struct _MCJOGEX {
	int			cbSize;
	double		Acceleration;
	double		MinVelocity;
	double		Deadband;
	double		Gain;
	double		Offset;
	int			Channel;
} MCJOGEX;

//
//  Jog control parameters structure (new programs should use MCJOGEX)
//
typedef struct _MCJOG {
	double		Acceleration;
	double		MinVelocity;
	double		Deadband;
	double		Gain;
	double		Offset;
} MCJOG;

//
//  Motion parameters structure (extended)
//
typedef struct _MCMOTIONEX {
	int			cbSize;
	double		Acceleration;
	double		Deceleration;
	double		Velocity;
	double		MinVelocity;
	int			Direction;
	double		Torque;
	double		Deadband;
	double		DeadbandDelay;
	int			StepSize;
	int			Current;
	int			HardLimitMode;
	int			SoftLimitMode;
	double		SoftLimitLow;
	double		SoftLimitHigh;
	int			EnableAmpFault;
} MCMOTIONEX;

//
//  Motion parameters structure (new programs should use MCMOTIONEX)
//
typedef struct _MCMOTION {
	double		Acceleration;
	double		Deceleration;
	double		Velocity;
	double		MinVelocity;
	short int	Direction;
	double		Gain;
	double		Torque;
	double		Deadband;
	double		DeadbandDelay;
	short int	StepSize;
	short int	Current;
	short int	HardLimitMode;
	short int	SoftLimitMode;
	double		SoftLimitLow;
	double		SoftLimitHigh;
	short int	EnableAmpFault;
	short int	Rate;
} MCMOTION;

//
//  Controller configuration structure (extended)
//
typedef struct _MCPARAMEX {
	int			cbSize;
	int			ID;
	int			ControllerType;
	int			NumberAxes;
	int			MaximumAxes;
	int			MaximumModules;
	int			Precision;
	int			DigitalIO;
	int			AnalogInput;
	int			AnalogOutput;
	int			PointStorage;
	int			CanDoScaling;
	int			CanDoContouring;
	int			CanChangeProfile;
	int			CanChangeRates;
	int			SoftLimits;
	int			MultiTasking;
	int			AmpFault;
	double		AnalogInpMin;			// added v3.4.0, motherboard analog inp min voltage	
	double		AnalogInpMax;			// added v3.4.0, motherboard analog inp max voltage	
	int			AnalogInpRes;			// added v3.4.0, motherboard analog inp resolution (bits)
	double		AnalogOutMin;			// added v3.4.0, motherboard analog out min voltage	
	double		AnalogOutMax;			// added v3.4.0, motherboard analog out max voltage	
	int			AnalogOutRes;			// added v3.4.0, motherboard analog out resolution (bits)
	int			OutputMode;				// added v3.5.0, supports MCGetModuleOutputMode()
	int			AtTarget;				// added v3.5.0, supports position deadband and delay at target
	int			OutputControl;			// added v3.5.0, supports output offset and output deadband
	int			LineModeAscii;			// added v4.1.3, can accept line oriented ASCII (e.g. TCP/IP controllers) 
} MCPARAMEX;

//
//  Controller configuration structure (new programs should use MCPARAMEX)
//
typedef struct _MCPARAM {
    short int	ID;
    short int	ControllerType;
    short int	NumberAxes;
    short int	DigitalIO;
    short int	AnalogInput;
    short int	AnalogOutput;
    short int	AxisType[8];
    short int	PointStorage;
    short int	CanDoScaling;
    short int	CanDoContouring;
    short int	CanChangeProfile;
    short int	CanChangeRates;
    short int	SoftLimits;
    short int	MultiTasking;
    short int	AmpFault;
} MCPARAM;

//
//  Scaling factors data structure
//
typedef struct _MCSCALE {
    double		Constant;
    double		Offset;
    double		Rate;
    double		Scale;
    double		Zero;
    double		Time;
} MCSCALE;

//
//  Status word data structure
//
typedef struct _MCSTATUSEX {
	int			cbSize;
	DWORD		*Status;
	DWORD		AuxStatus;
	DWORD		ProfileStatus;
	DWORD		ModeStatus;
} MCSTATUSEX;

//
//  Restore default packing
//
#pragma pack(pop)

#ifdef __cplusplus      // avoid c++ name mangling
  extern "C" {
#endif 

//
//  Interrupt callback function typedef
//
typedef void (MCINTERRUPTPROC)(HWND, HCTRLR, WORD, DWORD);

//
//  API Function Prototypes
//
extern void APIENTRY    		MCAbort(HCTRLR hCtlr, WORD axis);
extern int APIENTRY     		MCArcCenter(HCTRLR hCtlr, WORD axis, short int type, double position);
extern int APIENTRY     		MCArcEndAngle(HCTRLR hCtlr, WORD axis, short int type, double angle);
extern int APIENTRY     		MCArcRadius(HCTRLR hCtlr, WORD axis, double radius);
extern int APIENTRY     		MCBlockBegin(HCTRLR hCtlr, int mode, int num);
extern int APIENTRY     		MCBlockEnd(HCTRLR hCtlr, int* taskID);
extern int APIENTRY     		MCCancelTask(HCTRLR hCtlr, int taskID);
extern int APIENTRY     		MCCaptureData(HCTRLR hCtlr, WORD axis, int points, double period, double delay);
extern short int APIENTRY		MCClose(HCTRLR hCtlr);
extern int APIENTRY     		MCConfigureCompare(HCTRLR hCtlr, WORD axis, double* values, int num, double inc, int mode, double period);
extern short int APIENTRY		MCConfigureDigitalIO(HCTRLR hCtlr, WORD channel, WORD mode);
extern int APIENTRY     		MCContourDistance(HCTRLR hCtlr, WORD axis, double distance);
extern int APIENTRY     		MCContourPath(HCTRLR hCtlr, WORD axis, WORD wMode, char* buffer);
extern int APIENTRY     		MCDecodeStatus(HCTRLR hCtlr, DWORD status, int bit);
extern int APIENTRY     		MCDecodeStatusEx(HCTRLR hCtlr, MCSTATUSEX* status, int bit);
extern void APIENTRY    		MCDirection(HCTRLR hCtlr, WORD axis, WORD dir);
extern int APIENTRY     		MCEdgeArm(HCTRLR hCtlr, WORD axis, double position);
extern void APIENTRY    		MCEnableAxis(HCTRLR hCtlr, WORD axis, short int state);
extern int APIENTRY     		MCEnableBacklash(HCTRLR hCtlr, WORD axis, double backlash, short int state);
extern int APIENTRY     		MCEnableCapture(HCTRLR hCtlr, WORD axis, int count);
extern int APIENTRY     		MCEnableCompare(HCTRLR hCtlr, WORD axis, int count);
extern int APIENTRY     		MCEnableDigitalFilter(HCTRLR hCtlr, WORD axis, int state);
extern void APIENTRY    		MCEnableDigitalIO(HCTRLR hCtlr, WORD channel, short int state);
extern int APIENTRY     		MCEnableEncoderFault(HCTRLR hCtlr, WORD axis, int state);
extern void APIENTRY    		MCEnableGearing(HCTRLR hCtlr, WORD axis, WORD master, double ratio, short int state);
extern int APIENTRY     		MCEnableInterrupt(HWND hWnd, HCTRLR hCtlr, WORD axis, DWORD mask, MCINTERRUPTPROC lpIntFunc);
extern void APIENTRY    		MCEnableJog(HCTRLR hCtlr, WORD axis, short int state);
extern void APIENTRY    		MCEnableSync(HCTRLR hCtlr, WORD axis, short int state);
extern void APIENTRY    		MCErrorNotify(HWND hWnd, HCTRLR hCtlr, DWORD errormask);
extern int APIENTRY     		MCFindAuxEncIdx(HCTRLR hCtlr, WORD axis, double position);
extern int APIENTRY     		MCFindEdge(HCTRLR hCtlr, WORD axis, double position);
extern int APIENTRY     		MCFindIndex(HCTRLR hCtlr, WORD axis, double position);
extern int APIENTRY     		MCGetAccelerationEx(HCTRLR hCtlr, WORD axis, double* acceleration);
extern WORD APIENTRY    		MCGetAnalog(HCTRLR hCtlr, WORD channel);
extern int APIENTRY     		MCGetAnalogEx(HCTRLR hCtlr, int channel, DWORD* value);
extern int APIENTRY     		MCGetAuxEncIdxEx(HCTRLR hCtlr, WORD axis, double* index);
extern int APIENTRY     		MCGetAuxEncPosEx(HCTRLR hCtlr, WORD axis, double* position);
extern int APIENTRY     		MCGetAxisConfiguration(HCTRLR hCtlr, WORD axis, MCAXISCONFIG* axiscfg);
extern int APIENTRY     		MCGetBreakpointEx(HCTRLR hCtlr, WORD axis, double* breakpoint);
extern int APIENTRY     		MCGetCaptureData(HCTRLR hCtlr, WORD axis, int type, int start, int points, double* data);
extern int APIENTRY				MCGetCaptureSettings(HCTRLR hCtlr, WORD axis, int* points, double* period, double* delay, int* index);
extern void APIENTRY    		MCGetConfiguration(HCTRLR hCtlr, MCPARAM* param);
extern int APIENTRY     		MCGetConfigurationEx(HCTRLR hCtlr, MCPARAMEX* param);
extern short int APIENTRY		MCGetContourConfig(HCTRLR hCtlr, WORD axis, MCCONTOUR* contour);
extern int APIENTRY     		MCGetContouringCount(HCTRLR hCtlr, WORD axis);
extern int APIENTRY     		MCGetCount(HCTRLR hCtlr, WORD axis, int type, int* count);
extern int APIENTRY     		MCGetDecelerationEx(HCTRLR hCtlr, WORD axis, double* deceleration);
extern int APIENTRY     		MCGetDigitalFilter(HCTRLR hCtlr, WORD axis, double* coeff, int num, int* actual);
extern short int APIENTRY 		MCGetDigitalIO(HCTRLR hCtlr, WORD channel);
extern int APIENTRY				MCGetDigitalIOConfig(HCTRLR hCtlr, WORD channel, WORD* mode);
extern int APIENTRY				MCGetDigitalIOEx(HCTRLR hCtlr, WORD channel, unsigned int* state);
extern short int APIENTRY		MCGetError(HCTRLR hCtlr);
extern short int APIENTRY		MCGetFilterConfig(HCTRLR hCtlr, WORD axis, MCFILTER* filter);
extern int APIENTRY				MCGetFilterConfigEx(HCTRLR hCtlr, WORD axis, MCFILTEREX* filter);
extern int APIENTRY				MCGetFollowingError(HCTRLR hCtlr, WORD axis, double* error);
extern int APIENTRY				MCGetGain(HCTRLR hCtlr, WORD axis, double* gain);
extern int APIENTRY				MCGetIndexEx(HCTRLR hCtlr, WORD axis, double* index);
extern int APIENTRY				MCGetInstalledModules(HCTRLR hCtlr, int modules[], int size);
extern short int APIENTRY		MCGetJogConfig(HCTRLR hCtlr, WORD axis, MCJOG* jog);
extern int APIENTRY				MCGetJogConfigEx(HCTRLR hCtlr, WORD axis, MCJOGEX* jog);
extern int APIENTRY				MCGetLimits(HCTRLR hCtlr, WORD axis, short int* hardlimitmode, short int* softlimitmode,
											double* softlimitminus, double* softlimitplus);
extern int APIENTRY				MCGetModuleInputMode(HCTRLR hCtlr, WORD axis, int* mode);
extern int APIENTRY				MCGetModuleOutputMode(HCTRLR hCtlr, WORD axis, WORD* mode);
extern short int APIENTRY		MCGetMotionConfig(HCTRLR hCtlr, WORD axis, MCMOTION* motion);
extern int APIENTRY				MCGetMotionConfigEx(HCTRLR hCtlr, WORD axis, MCMOTIONEX* motion);
extern int APIENTRY				MCGetOperatingMode(HCTRLR hCtlr, WORD axis, int* mode);
extern int APIENTRY				MCGetOptimalEx(HCTRLR hCtlr, WORD axis, double* optimal);
extern int APIENTRY				MCGetPositionEx(HCTRLR hCtlr, WORD axis, double* position);
extern int APIENTRY				MCGetProfile(HCTRLR hCtlr, WORD axis, WORD* profile);
extern int APIENTRY				MCGetRegister(HCTRLR hCtlr, int reg, void* value, int type);
extern short int APIENTRY		MCGetScale(HCTRLR hCtlr, WORD axis, MCSCALE* scale);
extern int APIENTRY				MCGetServoOutputPhase(HCTRLR hCtlr, WORD axis, WORD* phase);
extern DWORD APIENTRY			MCGetStatus(HCTRLR hCtlr, WORD axis);
extern int APIENTRY				MCGetStatusEx(HCTRLR hCtlr, WORD axis, MCSTATUSEX* status);
extern int APIENTRY       		MCGetTargetEx(HCTRLR hCtlr, WORD axis, double* target);
extern int APIENTRY       		MCGetTorque(HCTRLR hCtlr, WORD axis, double* torque);
extern int APIENTRY				MCGetTrajectoryRate(HCTRLR hCtlr, int* rate);
extern int APIENTRY       		MCGetVectorVelocity(HCTRLR hCtlr, WORD axis, double* velocity);
extern int APIENTRY       		MCGetVelocityActual(HCTRLR hCtlr, WORD axis, double* velocity);
extern int APIENTRY       		MCGetVelocityEx(HCTRLR hCtlr, WORD axis, double* velocity);
extern int APIENTRY       		MCGetVelocityOverride(HCTRLR hCtlr, WORD axis, double* override);
extern DWORD APIENTRY     		MCGetVersion(HCTRLR hCtlr);
extern void APIENTRY			MCGo(HCTRLR hCtlr, WORD axis);
extern int APIENTRY       		MCGoEx(HCTRLR hCtlr, WORD axis, double param);
extern void APIENTRY      		MCGoHome(HCTRLR hCtlr, WORD axis);
extern int APIENTRY       		MCIndexArm(HCTRLR hCtlr, WORD axis, double position);
extern int APIENTRY       		MCInterruptOnPosition(HCTRLR hCtlr, WORD axis, int mode, double position);
extern int APIENTRY       		MCIsAtTarget(HCTRLR hCtlr, WORD axis, double timeout);
extern int APIENTRY       		MCIsDigitalFilter(HCTRLR hCtlr, WORD axis);
extern int APIENTRY       		MCIsEdgeFound(HCTRLR hCtlr, WORD axis, double timeout);
extern int APIENTRY       		MCIsIndexFound(HCTRLR hCtlr, WORD axis, double timeout);
extern int APIENTRY       		MCIsStopped(HCTRLR hCtlr, WORD axis, double timeout);
extern int APIENTRY       		MCLearnPoint(HCTRLR hCtlr, WORD axis, int index, WORD mode);
extern void APIENTRY      		MCMacroCall(HCTRLR hCtlr, WORD macro);
extern void APIENTRY      		MCMoveAbsolute(HCTRLR hCtlr, WORD axis, double position);
extern void APIENTRY      		MCMoveRelative(HCTRLR hCtlr, WORD axis, double distance);
extern int APIENTRY       		MCMoveToPoint(HCTRLR hCtlr, WORD axis, int index);
extern HCTRLR APIENTRY    		MCOpen(short int nID, WORD mode, LPCSTR name);
extern int APIENTRY       		MCReopen(HCTRLR hCtlr, WORD newmode);
extern int APIENTRY       		MCRepeat(HCTRLR hCtlr, int count);
extern void APIENTRY      		MCReset(HCTRLR hCtlr, WORD axis);
extern void APIENTRY      		MCSetAcceleration(HCTRLR hCtlr, WORD axis, double rate);
extern void APIENTRY      		MCSetAnalog(HCTRLR hCtlr, WORD channel, WORD value);
extern int APIENTRY       		MCSetAnalogEx(HCTRLR hCtlr, int channel, DWORD value);
extern void APIENTRY      		MCSetAuxEncPos(HCTRLR hCtlr, WORD axis, double position);
extern int APIENTRY       		MCSetCommutation(HCTRLR hCtlr, WORD axis, MCCOMMUTATION* commutation);
extern short int APIENTRY 		MCSetContourConfig(HCTRLR hCtlr, WORD axis, MCCONTOUR* contour);
extern void APIENTRY      		MCSetDeceleration(HCTRLR hCtlr, WORD axis, double rate);
extern int APIENTRY       		MCSetDigitalFilter(HCTRLR hCtlr, WORD axis, double* coeff, int num);
extern short int APIENTRY 		MCSetFilterConfig(HCTRLR hCtlr, WORD axis, MCFILTER* filter);
extern int APIENTRY       		MCSetFilterConfigEx(HCTRLR hCtlr, WORD axis, MCFILTEREX* filter);
extern int APIENTRY       		MCSetGain(HCTRLR hCtlr, WORD axis, double gain);
extern short int APIENTRY 		MCSetJogConfig(HCTRLR hCtlr, WORD axis, MCJOG* jog);
extern int APIENTRY 			MCSetJogConfigEx(HCTRLR hCtlr, WORD axis, MCJOGEX* jog);
extern int APIENTRY       		MCSetLimits(HCTRLR hCtlr, WORD axis, short int hardlimitmode, short int softlimitmode,
											double softlimitminus, double softlimitplus);
extern int APIENTRY       		MCSetModuleInputMode(HCTRLR hCtlr, WORD axis, int Mode);
extern void APIENTRY      		MCSetModuleOutputMode(HCTRLR hCtlr, WORD axis, WORD mode);
extern short int APIENTRY 		MCSetMotionConfig(HCTRLR hCtlr, WORD axis, MCMOTION* motion);
extern int APIENTRY       		MCSetMotionConfigEx(HCTRLR hCtlr, WORD axis, MCMOTIONEX* motion);
extern void APIENTRY      		MCSetOperatingMode(HCTRLR hCtlr, WORD axis, WORD caxis, WORD mode);
extern void APIENTRY      		MCSetPosition(HCTRLR hCtlr, WORD axis, double position);
extern void APIENTRY      		MCSetProfile(HCTRLR hCtlr, WORD axis, WORD mode);
extern int APIENTRY       		MCSetRegister(HCTRLR hCtlr, int reg, void* value, int type);
extern short int APIENTRY 		MCSetScale(HCTRLR hCtlr, WORD axis, MCSCALE* scale);
extern void APIENTRY      		MCSetServoOutputPhase(HCTRLR hCtlr, WORD axis, WORD phase);
extern int APIENTRY       		MCSetTimeoutEx(HCTRLR hCtlr, double timeout, double* oldtimeOut);
extern int APIENTRY       		MCSetTorque(HCTRLR hCtlr, WORD axis, double torque);
extern int APIENTRY				MCSetTrajectoryRate(HCTRLR hCtlr, int rate);
extern int APIENTRY       		MCSetVectorVelocity(HCTRLR hCtlr, WORD axis, double velocity);
extern void APIENTRY      		MCSetVelocity(HCTRLR hCtlr, WORD axis, double rate);
extern int APIENTRY       		MCSetVelocityOverride(HCTRLR hCtlr, WORD axis, double override);
extern void APIENTRY      		MCStop(HCTRLR hCtlr, WORD axis);
extern int APIENTRY       		MCTranslateErrorEx(short int nError, LPSTR buffer, int length);
extern void APIENTRY      		MCWait(HCTRLR hCtlr, double period);
extern void APIENTRY      		MCWaitForDigitalIO(HCTRLR hCtlr, WORD channel, short int state);
extern int APIENTRY       		MCWaitForEdge(HCTRLR hCtlr, WORD axis, short int state);
extern int APIENTRY       		MCWaitForIndex(HCTRLR hCtlr, WORD axis);
extern void APIENTRY      		MCWaitForPosition(HCTRLR hCtlr, WORD axis, double position);
extern void APIENTRY      		MCWaitForRelative(HCTRLR hCtlr, WORD axis, double distance);
extern void APIENTRY      		MCWaitForStop(HCTRLR hCtlr, WORD axis, double period);
extern void APIENTRY      		MCWaitForTarget(HCTRLR hCtlr, WORD axis, double period);

//
//  Low level controller access commands
//
extern short int APIENTRY		pmccmd(HCTRLR hCtlr, short int size, void* buffer);
extern int APIENTRY				pmccmdex(HCTRLR hCtlr, WORD axis, WORD command, void* argument, int type);
extern int APIENTRY				pmccmdrpyex(HCTRLR hCtlr, WORD axis, WORD cmd, void* arg, int arg_type, void* rpy, int rpy_type);
extern short int APIENTRY		pmcgetc(HCTRLR hCtlr);
extern void APIENTRY			pmcgetram(HCTRLR hCtlr, WORD offset, void* buffer, short int size);
extern int APIENTRY				pmcgetramex(HCTRLR hCtlr, DWORD offset, void* buffer, DWORD size);
extern short int APIENTRY		pmcgets(HCTRLR hCtlr, char* buffer, short int size);
extern DWORD APIENTRY			pmclock(HCTRLR hCtlr, DWORD wait_msec);
extern int APIENTRY				pmclookupvar(HCTRLR hCtlr, const char* varname, DWORD* address);
extern short int APIENTRY		pmcputc(HCTRLR hCtlr, short int character);
extern void APIENTRY			pmcputram(HCTRLR hCtlr, WORD offset, void* buffer, short int size);
extern int APIENTRY				pmcputramex(HCTRLR hCtlr, DWORD offset, void* buffer, DWORD size);
extern short int APIENTRY		pmcputs(HCTRLR hCtlr, const char* buffer);
extern short int APIENTRY		pmcrdy(HCTRLR hCtlr);
extern short int APIENTRY		pmcrpy(HCTRLR hCtlr, short int size, char* buffer);
extern int APIENTRY				pmcrpyex(HCTRLR hCtlr, void* reply, int type);
extern void APIENTRY			pmcunlock(HCTRLR hCtlr);

#ifdef __cplusplus
  }
#endif 

#endif			// MCAPI_H
