# Archive of previous Telescope Control Server software

The telescope control server software has a long, and occasionally twisted, history. Jesse Dosher wrote bct30, the driver for the PMC I/O card, for the previous telescope control system, GTCC. Alex McMaster started the current TCS project by attempting to SWIG the MCAPI for python and using INDI libraries (in original_version/), but eventually they stick with the bct30 and write "parser" and eventually develop TCCserver.cpp. Later we attempted to create a stub telescope driver based on the original version of bct30--these are bct_sim.cpp and bct_sim.h

Must of this code is duplicate, unused and/or poorly commented, so eventually we copied what was in use to TC_Server.
