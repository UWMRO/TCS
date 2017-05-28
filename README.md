# Telescope Control Computer (TCC)
Check the Wiki Tab for more information.

## Purpose
This repository contains code for use at Manastash Ridge Observatory (MRO). It provides a
Graphical User Interface (GUI), Bifrost, built in Python 2.7 for controlling the primary Ritchey-Chretien Telescope. This GUI is intended to
allow control of the telescope as well as a new auto-guiding system being developed for MRO. The new TCC will see first 
use in Summer 2017.

## Feature Set
- Telescope Control
  --
  - Slewing (Complete)
  - Tracking (Complete)
  - Jogging (Complete)
  - Focusing (Complete)
  - Hand Paddle Control (Complete)
  - Status Display (Complete)
  - Precession (Complete)
  
- Target Selection
  --
  - Target Lists (Complete)
  - Target Alt-Az Plotting (Complete)
  - Target Airmass Plotting (Complete)
  - Target Assignment (Complete)
  - Target Finder Chart (Complete)
  
- Guider Control (Not Available in Current Release)
  -- 
  - Guider Exposure (In Development)
  - Guider Rotation (In Development)
  - Periscope Finder Chart (Complete)
  - Auto Find Guide Stars (In Development)
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
  - Pointing (Complete)
- Night Log (Not Available in Current Release)
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
