# Archive of previous Telescope Control Server software

The telescope control server software has a long, and occasionally twisted, history. Jesse Dosher wrote bct30, the driver for the PMC I/O card, for the previous telescope control system, GTCC. Alex McMaster started the current TCS project by attempting to SWIG the MCAPI for python and using INDI libraries (original_version/), but eventually gave up and wrote "parser" to use the existing bct30 driver, and eventually developed TCCserver.cpp. Later we attempted to create a stub telescope driver based on the original version of bct30--these are bct_sim.cpp and bct_sim.h

Most of this code is duplicate, unused and/or poorly commented, so eventually we copied just the telescope control server and it's dependancies to its own directory for further development.
