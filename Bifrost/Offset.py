import time
import wx
import os
import signal
from astropy.time import Time
import thread
import threading
import ephem
import matplotlib
import datetime as dati
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from matplotlib.image import AxesImage
import matplotlib.image as mpimg
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
from astroplan import Observer, FixedTarget
from astroplan.plots import plot_sky,plot_airmass
import astropy.units as u
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, FK5
from Finder_picker import plot_finder_image
from twisted.internet import wxreactor
from twisted.internet import reactor, protocol, defer
from twisted.protocols import basic
import subprocess
import Queue
from astroquery.skyview import SkyView
from astropy.wcs import WCS
import webbrowser
import glob

global pipe
pipe=None

def Noffset(self,event):
    """
    Jog Command; apply a coordinate offset in the North direction.

        Args:
            event: handler to allow function to be tethered to a wx widget. Tethered to the "N" button in the telescope control tab.

        Returns:
            None
    """
    self.control.jogWButton.Disable()
    self.control.jogEButton.Disable()
    self.control.jogNButton.Disable()
    self.control.jogSButton.Disable()
    if self.telescope_status.get("tracking") == True:
        #self.protocol.sendCommand("track off")
        self.command_queue.put("track off")
        print "Turning off Tracking"
        self.code_timer_N.Start(2000, oneShot = True)
        return
    elif self.telescope_status.get("tracking") == False:

        unit=self.control.jogUnits.GetValue()
        if unit == "arcsec":
            delta_arcs=float(self.control.jogIncrement.GetValue())
        if unit == "arcmin":
            delta_arcs=(float(self.control.jogIncrement.GetValue())*u.arcmin).to(u.arcsec).value
        if unit == 'deg':
            delta_arcs =(float(self.control.jogIncrement.GetValue()) * u.degree).to(u.arcsec).value

        #self.protocol.sendCommand("offset N "+str(delta_arcs))
        self.command_queue.put("offset N "+str(delta_arcs)+" "+str(self.mrolat.value))
        self.log('N' + ' ' + str(delta_arcs) + ' arcseconds')
        self.telescope_status['slewing'] = True
        thread.start_new_thread(self.velwatch,())
        return
 # ----------------------------------------------------------------------------------
def timeN(self,event):
    """
    After tracking is turned off, execute north jog.

        Args:
            event: handler to allow function to be tethered to a wx widget.

        Returns:
            None
    """
    print "Timer Ended"
    unit = self.control.jogUnits.GetValue()
    arcsec_to_enc_counts = 20.0
    if unit == "arcsec":
        delta_arcs = float(self.control.jogIncrement.GetValue())

    if unit == "arcmin":
        delta_arcs = (float(self.control.jogIncrement.GetValue()) * u.arcmin).to(u.arcsec).value
    if unit == 'deg':
        delta_arcs = (float(self.control.jogIncrement.GetValue()) * u.degree).to(u.arcsec).value

    #self.protocol.sendCommand("offset N "+str(delta_arcs))
    self.command_queue.put("offset N "+str(delta_arcs)+" "+str(self.mrolat.value))
    self.log('N' + ' ' + str(delta_arcs) + ' arcseconds')
    self.telescope_status['slewing'] = True
    thread.start_new_thread(self.velwatch,())
    return

# ----------------------------------------------------------------------------------
def Woffset(self,event, first = True):
    """
    Jog Command; apply a coordinate offset in the West direction.

        Args:
            event: handler to allow function to be tethered to a wx widget. Tethered to the "W" button in the telescope control tab.

        Returns:
            None
    """
    self.control.jogWButton.Disable()
    self.control.jogEButton.Disable()
    self.control.jogNButton.Disable()
    self.control.jogSButton.Disable()
    if self.telescope_status.get("tracking") == True:
        #self.protocol.sendCommand("track off")
        self.command_queue.put("track off")
        print "Turning off Tracking"
        self.code_timer_W.Start(self.stop_time, oneShot = True)
        return
    elif self.telescope_status.get("tracking") == False:

        unit = self.control.jogUnits.GetValue()
        arcsec_to_enc_counts = 20.0
        if unit == "arcsec":
            delta_arcs = float(self.control.jogIncrement.GetValue())
        if unit == "arcmin":
            delta_arcs = (float(self.control.jogIncrement.GetValue()) * u.arcmin).to(u.arcsec).value
        if unit == 'deg':
            delta_arcs = (float(self.control.jogIncrement.GetValue()) * u.degree).to(u.arcsec).value

        self.log('W' + ' ' + str(delta_arcs) + ' arcseconds')
        #self.protocol.sendCommand("offset W "+str(delta_arcs/15.0))
        self.LST=str(self.control.currentLSTPos.GetLabel())
        self.LST=self.LST.split(':')
        self.LST=float(self.LST[0])+float(self.LST[1])/60.+float(self.LST[2])/3600.
        self.command_queue.put("offset W "+str(delta_arcs)+" "+str(self.LST))
        self.telescope_status['slewing'] = True
        thread.start_new_thread(self.velwatch,())
        return
 # ----------------------------------------------------------------------------------
def timeW(self,event):
    """
    After tracking is turned off, execute west jog.

        Args:
            event: handler to allow function to be tethered to a wx widget.

        Returns:
            None
    """
    print "Timer Ended"
    unit = self.control.jogUnits.GetValue()
    arcsec_to_enc_counts = 20.0
    if unit == "arcsec":
        delta_arcs = float(self.control.jogIncrement.GetValue())
    if unit == "arcmin":
        delta_arcs = (float(self.control.jogIncrement.GetValue()) * u.arcmin).to(u.arcsec).value
    if unit == 'deg':
        delta_arcs = (float(self.control.jogIncrement.GetValue()) * u.degree).to(u.arcsec).value

    self.log('W' + ' ' + str(delta_arcs) + ' arcseconds')
    #self.protocol.sendCommand("offset W "+str(delta_arcs/15.0))
    self.LST=str(self.control.currentLSTPos.GetLabel())
    self.LST=self.LST.split(':')
    self.LST=float(self.LST[0])+float(self.LST[1])/60.+float(self.LST[2])/3600.
    self.command_queue.put("offset W "+str(delta_arcs)+ " "+str(self.LST))
    self.telescope_status['slewing'] = True
    thread.start_new_thread(self.velwatch,())
    return
# ----------------------------------------------------------------------------------
def Eoffset(self,event):
    """
    Jog Command; apply a coordinate offset in the East direction.

        Args:
            event: handler to allow function to be tethered to a wx widget.Tethered to the "E" button in the telescope control tab.

        Returns:
            None
    """


    self.control.jogWButton.Disable()
    self.control.jogEButton.Disable()
    self.control.jogNButton.Disable()
    self.control.jogSButton.Disable()
    if self.telescope_status.get("tracking") == True:
        #self.protocol.sendCommand("track off")
        self.command_queue.put("track off")
        print "Turning off Tracking"
        self.code_timer_E.Start(self.stop_time, oneShot = True)
    elif self.telescope_status.get("tracking") == False:
        unit = self.control.jogUnits.GetValue()
        if unit == "arcsec":
            delta_arcs = -1*float(self.control.jogIncrement.GetValue())
        if unit == "arcmin":
            delta_arcs = (float(self.control.jogIncrement.GetValue()) * u.arcmin).to(u.arcsec).value
        if unit == 'deg':
            delta_arcs = (float(self.control.jogIncrement.GetValue()) * u.degree).to(u.arcsec).value

        self.log('E' + ' ' + str(delta_arcs) + ' arcseconds')
        #self.protocol.sendCommand("offset E "+str(delta_arcs/15.0))
        self.command_queue.put("offset E "+str(delta_arcs))
        self.telescope_status['slewing'] = True
        thread.start_new_thread(self.velwatch,())
        return
 # ----------------------------------------------------------------------------------
def timeE(self,event):
    """
    After tracking is turned off, execute east jog.

        Args:
            event: handler to allow function to be tethered to a wx widget.

        Returns:
            None
    """
    print "Timer Ended"
    unit = self.control.jogUnits.GetValue()
    arcsec_to_enc_counts = 20.0
    if unit == "arcsec":
        delta_arcs = float(self.control.jogIncrement.GetValue())
    if unit == "arcmin":
        delta_arcs = (float(self.control.jogIncrement.GetValue()) * u.arcmin).to(u.arcsec).value
    if unit == 'deg':
        delta_arcs = (float(self.control.jogIncrement.GetValue()) * u.degree).to(u.arcsec).value

    self.log('E' + ' ' + str(delta_arcs) + ' arcseconds')
    #self.protocol.sendCommand("offset E "+str(delta_arcs/15.0))
    self.command_queue.put("offset E "+str(delta_arcs))
    self.telescope_status['slewing'] = True
    thread.start_new_thread(self.velwatch,())
    return
# ----------------------------------------------------------------------------------
def Soffset(self,event):
    """
    Jog Command; apply a coordinate offset in the South direction.

        Args:
            event: handler to allow function to be tethered to a wx widget.Tethered to the "S" button in the telescope control tab.

        Returns:
            None
    """

    self.control.jogWButton.Disable()
    self.control.jogEButton.Disable()
    self.control.jogNButton.Disable()
    self.control.jogSButton.Disable()
    if self.telescope_status.get("tracking") == True:
        #self.protocol.sendCommand("track off")
        self.command_queue.put("track off")
        print "Turning off Tracking"
        self.code_timer_S.Start(self.stop_time, oneShot = True)

    elif self.telescope_status.get("tracking") == False:
        unit = self.control.jogUnits.GetValue()
        if unit == "arcsec":
            delta_arcs = float(self.control.jogIncrement.GetValue())
        if unit == "arcmin":
            delta_arcs = (float(self.control.jogIncrement.GetValue()) * u.arcmin).to(u.arcsec).value
        if unit == 'deg':
            delta_arcs = (float(self.control.jogIncrement.GetValue()) * u.degree).to(u.arcsec).value

        self.log('S' + ' ' + str(delta_arcs) + ' arcseconds')
        #self.protocol.sendCommand("offset S "+str(delta_arcs))
        self.command_queue.put("offset S "+str(delta_arcs)+" "+str(self.mrolat.value))
        self.telescope_status['slewing'] = True
        thread.start_new_thread(self.velwatch,())
        return
# ----------------------------------------------------------------------------------
def timeS(self,event):
    """
    After tracking is turned off, execute south jog.

        Args:
            event: handler to allow function to be tethered to a wx widget.

        Returns:
            None
    """
    print "Timer Ended"
    unit = self.control.jogUnits.GetValue()
    arcsec_to_enc_counts = 20.0
    if unit == "arcsec":
        delta_arcs = float(self.control.jogIncrement.GetValue())
    if unit == "arcmin":
        delta_arcs = (float(self.control.jogIncrement.GetValue()) * u.arcmin).to(u.arcsec).value
    if unit == 'deg':
        delta_arcs = (float(self.control.jogIncrement.GetValue()) * u.degree).to(u.arcsec).value

    self.log('S' + ' ' + str(delta_arcs) + ' arcseconds')
    #self.protocol.sendCommand("offset S "+str(delta_arcs))
    self.command_queue.put("offset S "+str(delta_arcs)+" "+str(self.mrolat.value))
    self.telescope_status['slewing'] = True
    thread.start_new_thread(self.velwatch,())
    return
# ----------------------------------------------------------------------------------
