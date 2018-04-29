# Telescope Control Computer (TCC)

More information is available under the Wiki tab.

## Purpose
This repository contains code for use at Manastash Ridge Observatory (MRO). It provides a
Graphical User Interface (GUI), Bifrost, built in Python 2.7 for controlling the primary Ritchey-Chretien Telescope. This GUI is intended to allow control of the telescope as well as a new auto-guiding system being developed for MRO. The new TCC saw first use in Summer 2017.

## Dependencies
- WxPython: https://wxpython.org/
- Astropy: http://www.astropy.org/
- Astroplan: https://astroplan.readthedocs.io/en/latest/
- Astroquery: https://astroquery.readthedocs.io/en/latest/
- Ephem: http://rhodesmill.org/pyephem/
- Numpy: http://www.numpy.org/
- Matplotlib: https://matplotlib.org/
- TwistedPython: https://twistedmatrix.com/trac/

## Try it!

On Ubuntu 17.10:
```
sudo git clone https://github.com/UWMRO/TCC.git

sudo apt-get install python-wxgtk3.0
sudo apt-get install python-astropy
sudo apt-get install python-ephem
(Apparently order is important for the next three steps...)
sudo apt-get install python-numpy (unnecessary as it turned out)
sudo apt-get install python-scipy
sudo apt-get install python-matplotlib
sudo apt-get install python-astroplan
sudo apt-get install python-twisted
sudo apt-get install python-astroquery

/TCC$ mkdir logs
/TCC$ tccv3.py
```
