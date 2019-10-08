# Telescope Control System (TCS)

This repository contains the assorted code for controlling telescope functsions at Manastash Ridge Observatory (MRO). It provides

- Bifrost, the GUI, built in Python 2.7, for controlling the primary Ritchey-Chretien Telescope. This GUI is intended to allow control of the telescope as well as a new auto-guiding system being developed for MRO. The new TCC saw first use in Summer 2017.
- TelescopePi, software for the Telescope-mounted Raspberry Pi that controls the filter wheel and (soon) various other telescope functions. 
- TelescopeServer, software that interprets commands from Bifrost and sends them to motor control board that communicates with the telescope hardware.

More information, including installation instructions, is available under "Developer Manual" the Wiki tab.
