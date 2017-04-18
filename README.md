# Telescope Control Computer (TCC)


## Purpose
This repository contains code for use at Manastash Ridge Observatory (MRO). It provides a
Graphical User Interface (GUI), Bifrost, built in Python 2.7 for controlling the primary Ritchey-Chretien Telescope. This GUI is intended to
allow control of the telescope as well as a new auto-guiding system being developed for MRO. The new TCC will see first 
use in Summer 2017.

## Feature Set
- Telescope Control
  --
  - Slewing (Ready for On-Sky Testing)
  - Tracking (Ready for On-Sky Testing)
  - Jogging (Ready for On-Sky Testing)
  - Focusing (Ready for On-Sky Testing)
  - Hand Paddle Control (Complete)
  - Status Display (Complete)
  - Precession (Complete)
  
- Target Selection
  --
  - Target Lists (Complete)
  - Target Alt-Az Plotting (Complete)
  - Target Airmass Plotting (Complete)
  - Target Assignment (Complete)
  
- Guider Control
  -- 
  - Guider Exposure (In Development)
  - Guider Rotation (In Development)
  - Periscope Finder Chart (Complete)
  - Auto Find Guide Stars (In Development
  - Guiding (In Development)
  - Jog Guide Field (In Development)
  - Focus Guider (In Development)
- Initialization
  --
  - Park Telescope (Complete)
  - Cover Position (Complete)
  - Initialize Telescope Systems (Complete)
  - Tracking Rate Assignment (Complete)
  - Guiding Parameters (In Development)
  - Set Telescope Position (Complete)
  - Load Zenith Coordinates (Complete)
  - Pointing (Ready for On-Sky Testing)
- Night Log
  --
  - Log Fields (In Development)
  - Save and Send Logs (In Development)
  
## Dependencies
- WxPython: https://wxpython.org/
- Astropy: http://www.astropy.org/
- Astroplan: https://astroplan.readthedocs.io/en/latest/
- Astroquery: https://astroquery.readthedocs.io/en/latest/
- Ephem: http://rhodesmill.org/pyephem/
- Numpy: http://www.numpy.org/
- Matplotlib: https://matplotlib.org/
- TwistedPython: https://twistedmatrix.com/trac/
