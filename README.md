# Telescope Control System (TCS)

More information, including installation instructions, are available under the Wiki tab.

## Purpose
This repository contains the assorted code for controlling telescope functsions at Manastash Ridge Observatory (MRO). It provides

- Bifrost, the GUI, built in Python 2.7, for controlling the primary Ritchey-Chretien Telescope. This GUI is intended to allow control of the telescope as well as a new auto-guiding system being developed for MRO. The new TCC saw first use in Summer 2017.
- TelescopePi software, including a server for a Telescope-mounted Raspberry Pi that controls the filter wheel and (soon) various other telescope functions. 

## Bifrost Dependencies
- WxPython: https://wxpython.org/
- Astropy: http://www.astropy.org/
- Astroplan: https://astroplan.readthedocs.io/en/latest/
- Astroquery: https://astroquery.readthedocs.io/en/latest/
- Ephem: http://rhodesmill.org/pyephem/
- Numpy: http://www.numpy.org/
- Matplotlib: https://matplotlib.org/
- TwistedPython: https://twistedmatrix.com/trac/
