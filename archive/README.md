# Archive of previous Telescope Control Server software

The telescope control server software has a long, and occasionally twisted, history. Jesse Dosher wrote bct30, the driver for the PMC I/O card, for the previous telescope control system, GTCC. Alex McMaster started the current TCS project by attempting to SWIG the MCAPI and using INDI libraries (in originals/) but eventually they write "parser" in C++ and eventually develope TCCServer.

Later we attempted to create a stub telescope driver based on the original version of bct30, these are bct_sim.cpp and bct_sim.h
